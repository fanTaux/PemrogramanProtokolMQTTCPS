"""
Smart Room Monitoring — Python PUBLISHER
=========================================
Mensimulasikan data sensor DHT11 (suhu & kelembapan) dan
mempublish ke Mosquitto Broker menggunakan paho-mqtt.

Skenario yang dicakup:
  1 - Komunikasi dasar Publisher–Subscriber
  2 - Publish dengan QoS 0, 1, 2 pada topik berbeda
  3 - Publish ke beberapa topik sekaligus
  4 & 5 - Wildcard ditangani di sisi Subscriber

Instalasi:
  pip install paho-mqtt

Jalankan:
  python publisher.py
"""

import time
import json
import random
import logging
from datetime import datetime
import paho.mqtt.client as mqtt

# ─── Logging ─────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("Publisher")

# ─── Konfigurasi Broker ──────────────────────────────────────
BROKER_HOST  = "localhost"       # ganti IP jika broker di mesin lain
BROKER_PORT  = 1883
CLIENT_ID    = "Python_Publisher_Room"
MQTT_USER    = None              # isi string jika broker pakai auth
MQTT_PASS    = None
KEEPALIVE    = 60

# ─── Definisi Topik (Skenario 3: beberapa topik) ─────────────
TOPIC_TEMP      = "smarthome/room/temperature"
TOPIC_HUM       = "smarthome/room/humidity"
TOPIC_STATUS    = "smarthome/room/status"
TOPIC_ALERT     = "smarthome/room/alert"
TOPIC_COMPOSITE = "smarthome/room/data"       # JSON gabungan

# ─── Threshold ───────────────────────────────────────────────
TEMP_THRESHOLD = 30.0
HUM_THRESHOLD  = 80.0

# ─── Interval Publish ────────────────────────────────────────
PUBLISH_INTERVAL = 5   # detik

# ─── Callback Koneksi ────────────────────────────────────────
def on_connect(client, userdata, flags, rc, properties=None):
    codes = {
        0: "Terhubung ke broker",
        1: "Koneksi ditolak: versi protokol salah",
        2: "Koneksi ditolak: client ID tidak valid",
        3: "Koneksi ditolak: server tidak tersedia",
        4: "Koneksi ditolak: username/password salah",
        5: "Koneksi ditolak: tidak diotorisasi",
    }
    msg = codes.get(rc, f"Kode tidak dikenal: {rc}")
    if rc == 0:
        log.info(f"✅ {msg}")
    else:
        log.error(f"❌ {msg}")

def on_publish(client, userdata, mid, reason_code=None, properties=None):
    log.debug(f"  → Pesan mid={mid} terkonfirmasi diterima broker")

def on_disconnect(client, userdata, disconnect_flags, rc=None, properties=None):
    if rc != 0:
        log.warning(f"⚠ Koneksi terputus (rc={rc}), mencoba reconnect...")

# ─── Simulasi Sensor DHT11 ───────────────────────────────────
def read_sensor():
    """
    Mensimulasikan pembacaan DHT11.
    Ganti fungsi ini dengan pembacaan hardware nyata jika
    dijalankan di Raspberry Pi dengan sensor DHT11.
    """
    temperature = round(random.uniform(24.0, 34.0), 1)
    humidity    = round(random.uniform(55.0, 90.0), 1)
    return temperature, humidity

# ─── Evaluasi Status ─────────────────────────────────────────
def evaluate_status(temp, hum):
    if temp > TEMP_THRESHOLD and hum > HUM_THRESHOLD:
        return "PANAS_LEMBAP"
    if temp > TEMP_THRESHOLD:
        return "PANAS"
    if hum > HUM_THRESHOLD:
        return "LEMBAP"
    return "NORMAL"

# ─── Publish Semua Skenario ──────────────────────────────────
def publish_all(client, temp, hum):
    status    = evaluate_status(temp, hum)
    is_alert  = (temp > TEMP_THRESHOLD or hum > HUM_THRESHOLD)
    alert_msg = "PERINGATAN: Kondisi ruangan tidak normal!" if is_alert else "OK"
    timestamp = datetime.now().isoformat()

    print("\n" + "═" * 52)
    print(f"  📡 Publish — {datetime.now().strftime('%H:%M:%S')}")
    print(f"  Suhu: {temp}°C  |  Kelembapan: {hum}%  |  Status: {status}")
    print("═" * 52)

    # ── Skenario 2: QoS berbeda ──────────────────────────────
    # QoS 0 — At most once (tidak ada konfirmasi)
    result0 = client.publish(TOPIC_TEMP, str(temp), qos=0)
    log.info(f"[QoS 0] {TOPIC_TEMP} = {temp}°C  (mid={result0.mid})")

    # QoS 1 — At least once (konfirmasi PUBACK dari broker)
    result1 = client.publish(TOPIC_HUM, str(hum), qos=1)
    log.info(f"[QoS 1] {TOPIC_HUM} = {hum}%  (mid={result1.mid})")

    # QoS 2 — Exactly once (handshake 4 langkah)
    result2 = client.publish(TOPIC_STATUS, status, qos=2)
    log.info(f"[QoS 2] {TOPIC_STATUS} = {status}  (mid={result2.mid})")

    # ── Skenario 3: Topik tambahan ───────────────────────────
    client.publish(TOPIC_ALERT, alert_msg, qos=1)
    log.info(f"[QoS 1] {TOPIC_ALERT} = {alert_msg}")

    # JSON gabungan — berguna untuk subscriber yang ingin semua data sekaligus
    payload = json.dumps({
        "temperature": temp,
        "humidity":    hum,
        "status":      status,
        "alert":       is_alert,
        "timestamp":   timestamp
    })
    client.publish(TOPIC_COMPOSITE, payload, qos=1)
    log.info(f"[QoS 1] {TOPIC_COMPOSITE} = {payload}")

# ─── Main ────────────────────────────────────────────────────
def main():
    log.info("=== Smart Room Monitoring: PUBLISHER ===")
    log.info(f"Broker: {BROKER_HOST}:{BROKER_PORT}")
    log.info(f"Interval publish: {PUBLISH_INTERVAL} detik")

    # Buat client MQTT v5 (fallback ke v3.1.1 jika broker lama)
    client = mqtt.Client(
        client_id=CLIENT_ID,
        protocol=mqtt.MQTTv5,
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2
    )

    if MQTT_USER:
        client.username_pw_set(MQTT_USER, MQTT_PASS)

    client.on_connect    = on_connect
    client.on_publish    = on_publish
    client.on_disconnect = on_disconnect

    # Koneksi ke broker
    try:
        client.connect(BROKER_HOST, BROKER_PORT, KEEPALIVE)
    except Exception as e:
        log.error(f"Tidak dapat terhubung ke broker: {e}")
        return

    client.loop_start()
    time.sleep(1)   # beri waktu handshake selesai

    try:
        while True:
            temp, hum = read_sensor()
            publish_all(client, temp, hum)
            time.sleep(PUBLISH_INTERVAL)

    except KeyboardInterrupt:
        log.info("\nPublisher dihentikan oleh pengguna.")
    finally:
        client.loop_stop()
        client.disconnect()
        log.info("Koneksi broker ditutup.")

if __name__ == "__main__":
    main()