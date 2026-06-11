/*
 * ============================================================
 *  Smart Room Monitoring — ESP32 SUBSCRIBER
 *  Komponen : ESP32 (tanpa sensor, hanya menerima data)
 *  Broker   : Mosquitto
 *
 *  Skenario yang dicakup:
 *    1 - Komunikasi dasar Subscriber
 *    3 - Subscribe beberapa topik eksplisit
 *    4 - Wildcard + (smarthome/room/+)
 *    5 - Wildcard # (smarthome/#)
 * ============================================================
 */

#include <WiFi.h>
#include <PubSubClient.h>

// ─── Konfigurasi WiFi ────────────────────────────────────────
const char* WIFI_SSID     = "NAMA_WIFI_KAMU";
const char* WIFI_PASSWORD = "PASSWORD_WIFI_KAMU";

// ─── Konfigurasi Broker ──────────────────────────────────────
const char* MQTT_BROKER    = "192.168.1.100";   // ← ganti IP broker
const int   MQTT_PORT      = 1883;
const char* MQTT_CLIENT_ID = "ESP32_Subscriber_Room";
const char* MQTT_USER      = "";
const char* MQTT_PASSWORD  = "";

// ─── Pilih Skenario Subscribe (uncomment satu) ───────────────
// Skenario 1 & 3: Subscribe topik spesifik
// #define SUBSCRIBE_MODE "SPECIFIC"

// Skenario 4: Wildcard + (satu level)
// #define SUBSCRIBE_MODE "WILDCARD_PLUS"

// Skenario 5: Wildcard # (semua level)
#define SUBSCRIBE_MODE "WILDCARD_HASH"

// ─── Objek Global ────────────────────────────────────────────
WiFiClient   espClient;
PubSubClient mqttClient(espClient);

// ─── Callback: Pesan Masuk ───────────────────────────────────
void onMessageReceived(char* topic, byte* payload, unsigned int length) {
  // Konversi payload ke String
  char message[length + 1];
  memcpy(message, payload, length);
  message[length] = '\0';

  Serial.println("╔═══════════════════════════════════════");
  Serial.printf ("║ [MQTT IN] Topik   : %s\n", topic);
  Serial.printf ("║           Pesan   : %s\n", message);
  Serial.printf ("║           Panjang : %d bytes\n", length);

  // ─── Parsing berdasarkan nama topik ──────────────────────
  String topicStr(topic);

  if (topicStr == "smarthome/room/temperature") {
    float temp = atof(message);
    Serial.printf("║           [Suhu]  : %.1f °C", temp);
    if (temp > 30.0) Serial.print("  ⚠ PANAS");
    Serial.println();
  }
  else if (topicStr == "smarthome/room/humidity") {
    float hum = atof(message);
    Serial.printf("║           [Hum]   : %.1f %%", hum);
    if (hum > 80.0) Serial.print("  ⚠ LEMBAP");
    Serial.println();
  }
  else if (topicStr == "smarthome/room/status") {
    Serial.printf("║           [Status]: %s\n", message);
  }
  else if (topicStr == "smarthome/room/alert") {
    if (strcmp(message, "OK") != 0) {
      Serial.printf("║           [ALERT] : *** %s ***\n", message);
    } else {
      Serial.printf("║           [ALERT] : %s\n", message);
    }
  }
  else {
    Serial.println("║           [INFO]  : Topik lain diterima.");
  }

  Serial.println("╚═══════════════════════════════════════");
}

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
      Serial.println("\n[WiFi] Gagal, restart...");
      ESP.restart();
    }
  }
  Serial.println();
  Serial.print("[WiFi] IP: ");
  Serial.println(WiFi.localIP());
}

// ─── Fungsi: Subscribe Berdasarkan Mode ─────────────────────
void doSubscribe() {
  #if defined(SUBSCRIBE_MODE) && SUBSCRIBE_MODE == "SPECIFIC"
    // Skenario 1 & 3: Topik eksplisit
    mqttClient.subscribe("smarthome/room/temperature");
    mqttClient.subscribe("smarthome/room/humidity");
    mqttClient.subscribe("smarthome/room/status");
    mqttClient.subscribe("smarthome/room/alert");
    Serial.println("[MQTT] Subscribe: Mode SPECIFIC (Skenario 1 & 3)");

  #elif defined(SUBSCRIBE_MODE) && SUBSCRIBE_MODE == "WILDCARD_PLUS"
    // Skenario 4: Wildcard + → hanya 1 level setelah room/
    mqttClient.subscribe("smarthome/room/+");
    Serial.println("[MQTT] Subscribe: smarthome/room/+ (Skenario 4 - Wildcard +)");

  #elif defined(SUBSCRIBE_MODE) && SUBSCRIBE_MODE == "WILDCARD_HASH"
    // Skenario 5: Wildcard # → semua topik di bawah smarthome/
    mqttClient.subscribe("smarthome/#");
    Serial.println("[MQTT] Subscribe: smarthome/# (Skenario 5 - Wildcard #)");
  #endif
}

// ─── Fungsi: Koneksi MQTT ────────────────────────────────────
void connectMQTT() {
  while (!mqttClient.connected()) {
    Serial.print("[MQTT] Menghubungkan...");
    bool connected = (strlen(MQTT_USER) > 0)
      ? mqttClient.connect(MQTT_CLIENT_ID, MQTT_USER, MQTT_PASSWORD)
      : mqttClient.connect(MQTT_CLIENT_ID);

    if (connected) {
      Serial.println(" Terhubung!");
      doSubscribe();
    } else {
      Serial.print(" Gagal, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" | Retry 3 detik...");
      delay(3000);
    }
  }
}

// ─── Setup ───────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  Serial.println("\n=== Smart Room Monitoring: SUBSCRIBER ===");
  Serial.printf ("    Mode: %s\n", SUBSCRIBE_MODE);

  connectWiFi();
  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  mqttClient.setCallback(onMessageReceived);
  mqttClient.setKeepAlive(60);
  mqttClient.setBufferSize(512);
}

// ─── Loop ────────────────────────────────────────────────────
void loop() {
  if (!mqttClient.connected()) connectMQTT();
  mqttClient.loop();
}
