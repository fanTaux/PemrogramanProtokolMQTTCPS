/*
 * ============================================================
 *  Smart Room Monitoring — ESP32 PUBLISHER
 *  Komponen : ESP32 + DHT11 (Pin D15)
 *  Broker   : Mosquitto (konfigurasi IP di bawah)
 *  Library  : PubSubClient, DHT sensor library
 *
 *  Topik yang dipublish:
 *    smarthome/room/temperature    → suhu (°C)
 *    smarthome/room/humidity       → kelembapan (%)
 *    smarthome/room/status         → status kondisi ruangan
 *    smarthome/room/alert          → peringatan jika threshold terlampaui
 *
 *  Skenario yang dicakup:
 *    1 - Komunikasi dasar Publisher–Subscriber
 *    2 - QoS 0, 1, 2 pada topik berbeda
 *    3 - Beberapa topik sekaligus
 *    4 & 5 - Wildcard ditangani di sisi Subscriber
 * ============================================================
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

// ─── Konfigurasi WiFi ────────────────────────────────────────
const char* WIFI_SSID     = "NAMA_WIFI_KAMU";
const char* WIFI_PASSWORD = "PASSWORD_WIFI_KAMU";

// ─── Konfigurasi Broker ──────────────────────────────────────
const char* MQTT_BROKER   = "192.168.1.100";   // ← ganti IP broker Mosquitto
const int   MQTT_PORT     = 1883;
const char* MQTT_CLIENT_ID = "ESP32_Publisher_Room";
// Isi jika broker memerlukan autentikasi, kosongkan jika tidak
const char* MQTT_USER     = "";
const char* MQTT_PASSWORD = "";

// ─── Konfigurasi DHT11 ───────────────────────────────────────
#define DHTPIN  15
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// ─── Definisi Topik ──────────────────────────────────────────
// Skenario 3: Beberapa topik
#define TOPIC_TEMP      "smarthome/room/temperature"
#define TOPIC_HUM       "smarthome/room/humidity"
#define TOPIC_STATUS    "smarthome/room/status"
#define TOPIC_ALERT     "smarthome/room/alert"

// ─── Threshold Peringatan ────────────────────────────────────
#define TEMP_THRESHOLD  30.0   // °C
#define HUM_THRESHOLD   80.0   // %

// ─── Interval Publish (ms) ───────────────────────────────────
#define PUBLISH_INTERVAL 5000

// ─── Objek Global ────────────────────────────────────────────
WiFiClient   espClient;
PubSubClient mqttClient(espClient);
unsigned long lastPublishTime = 0;

// ─── Fungsi: Koneksi WiFi ────────────────────────────────────
void connectWiFi() {
  Serial.print("[WiFi] Menghubungkan ke ");
  Serial.println(WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempt = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    if (++attempt > 20) {
      Serial.println("\n[WiFi] Gagal terhubung, restart...");
      ESP.restart();
    }
  }
  Serial.println();
  Serial.print("[WiFi] Terhubung. IP: ");
  Serial.println(WiFi.localIP());
}

// ─── Fungsi: Koneksi MQTT ────────────────────────────────────
void connectMQTT() {
  while (!mqttClient.connected()) {
    Serial.print("[MQTT] Mencoba koneksi ke broker...");
    bool connected = (strlen(MQTT_USER) > 0)
      ? mqttClient.connect(MQTT_CLIENT_ID, MQTT_USER, MQTT_PASSWORD)
      : mqttClient.connect(MQTT_CLIENT_ID);

    if (connected) {
      Serial.println(" Terhubung!");
    } else {
      Serial.print(" Gagal, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" | Mencoba ulang dalam 3 detik...");
      delay(3000);
    }
  }
}

// ─── Fungsi: Evaluasi Status Ruangan ─────────────────────────
String evaluateStatus(float temp, float hum) {
  if (temp > TEMP_THRESHOLD && hum > HUM_THRESHOLD) return "PANAS_LEMBAP";
  if (temp > TEMP_THRESHOLD)                         return "PANAS";
  if (hum  > HUM_THRESHOLD)                          return "LEMBAP";
  return "NORMAL";
}

// ─── Fungsi: Publish Semua Data ──────────────────────────────
void publishSensorData() {
  float temperature = dht.readTemperature();
  float humidity    = dht.readHumidity();

  // Validasi pembacaan sensor
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("[DHT11] Gagal membaca sensor!");
    return;
  }

  char tempStr[10], humStr[10];
  dtostrf(temperature, 4, 1, tempStr);
  dtostrf(humidity,    4, 1, humStr);

  String status = evaluateStatus(temperature, humidity);

  // ── Skenario 2: QoS berbeda per topik ──────────────────────
  // QoS 0 → temperatur (data high-frequency, loss toleran)
  mqttClient.publish(TOPIC_TEMP, tempStr, false);             // QoS 0 (default PubSubClient)
  Serial.printf("[PUB QoS0] %s = %s °C\n", TOPIC_TEMP, tempStr);

  // QoS 1 → kelembapan (setidaknya sekali terkirim)
  // PubSubClient tidak native QoS1/2 dari sisi publish —
  // gunakan broker retain=true sebagai pendekatan praktis di Arduino.
  // Untuk QoS 1 penuh, gunakan pustaka MQTT yang mendukung (misal: esp_mqtt IDF).
  mqttClient.publish(TOPIC_HUM, humStr, true);                // retain = true (simulasi persistensi)
  Serial.printf("[PUB QoS1*] %s = %s %%\n", TOPIC_HUM, humStr);

  // QoS 2 → status (exactly-once, paling kritis) — dicatat sebagai retained
  mqttClient.publish(TOPIC_STATUS, status.c_str(), true);
  Serial.printf("[PUB QoS2*] %s = %s\n", TOPIC_STATUS, status.c_str());

  // ── Skenario 3: Topik tambahan — alert ─────────────────────
  bool alert = (temperature > TEMP_THRESHOLD || humidity > HUM_THRESHOLD);
  const char* alertMsg = alert ? "PERINGATAN: Kondisi ruangan tidak normal!" : "OK";
  mqttClient.publish(TOPIC_ALERT, alertMsg, false);
  Serial.printf("[PUB ALERT] %s = %s\n", TOPIC_ALERT, alertMsg);

  Serial.println("─────────────────────────────────────");
}

// ─── Setup ───────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  Serial.println("\n=== Smart Room Monitoring: PUBLISHER ===");

  dht.begin();
  connectWiFi();

  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  mqttClient.setKeepAlive(60);
}

// ─── Loop ────────────────────────────────────────────────────
void loop() {
  if (!mqttClient.connected()) connectMQTT();
  mqttClient.loop();

  unsigned long now = millis();
  if (now - lastPublishTime >= PUBLISH_INTERVAL) {
    lastPublishTime = now;
    publishSensorData();
  }
}
