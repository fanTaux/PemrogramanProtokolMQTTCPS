"""
Smart Room Monitoring — Python SUBSCRIBER
==========================================
Subscribe ke topik Mosquitto dan menampilkan data ruangan.
Mendukung 5 skenario via argumen --scenario.

Skenario:
  1 - Komunikasi dasar: subscribe 1 topik (temperature)
  2 - QoS berbeda: subscribe masing-masing topik dengan QoS berbeda
  3 - Beberapa topik: subscribe semua topik eksplisit
  4 - Wildcard +: subscribe smarthome/room/+
  5 - Wildcard #: subscribe smarthome/#

Jalankan:
  python subscriber.py --scenario 1
  python subscriber.py --scenario 4
  python subscriber.py           (default: skenario 5)
"""

import argparse
import json
import logging
from datetime import datetime
import paho.mqtt.client as mqtt

# ─── Logging ─────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("Subscriber")

# ─── Konfigurasi Broker ──────────────────────────────────────
BROKER_HOST = "localhost"
BROKER_PORT = 1883
MQTT_USER   = None
MQTT_PASS   = None
KEEPALIVE   = 60

# ─── Daftar Topik untuk Skenario 3 ───────────────────────────
EXPLICIT_TOPICS = [
    ("smarthome/room/temperature", 0),   # (topik, QoS)
    ("smarthome/room/humidity",    1),
    ("smarthome/room/status",      2),
    ("smarthome/room/alert",       1),
    ("smarthome/room/data",        1),
]

# ─── Warna Terminal (opsional, tidak kritis) ─────────────────
RED    = "\033[91m"
YELLOW = "\033[93m"
GREEN  = "\033[92m"
CYAN   = "\033[96m"
RESET  = "\033[0m"

# ─── Callback: Koneksi ───────────────────────────────────────
def on_connect(client, userdata, flags, rc, properties=None):
    scenario = userdata["scenario"]
    if rc == 0:
        log.info(f"✅ Terhubung ke broker ({BROKER_HOST}:{BROKER_PORT})")
        _subscribe_by_scenario(client, scenario)
    else:
        log.error(f"❌ Gagal terhubung (rc={rc})")

def _subscribe_by_scenario(client, scenario):
    """Pilih strategi subscribe berdasarkan nomor skenario."""

    if scenario == 1:
        # ── Skenario 1: Dasar — satu topik, QoS 0
        client.subscribe("smarthome/room/temperature", qos=0)
        log.info("[Skenario 1] Subscribe: smarthome/room/temperature (QoS 0)")

    elif scenario == 2:
        # ── Skenario 2: QoS berbeda per topik
        client.subscribe("smarthome/room/temperature", qos=0)
        log.info("[Skenario 2] Subscribe: smarthome/room/temperature (QoS 0)")
        client.subscribe("smarthome/room/humidity", qos=1)
        log.info("[Skenario 2] Subscribe: smarthome/room/humidity    (QoS 1)")
        client.subscribe("smarthome/room/status", qos=2)
        log.info("[Skenario 2] Subscribe: smarthome/room/status      (QoS 2)")
        client.subscribe("smarthome/room/alert", qos=2)
        log.info("[Skenario 2] Subscribe: smarthome/room/alert       (QoS 2)")

    elif scenario == 3:
        # ── Skenario 3: Beberapa topik sekaligus menggunakan subscribe_list
        client.subscribe(EXPLICIT_TOPICS)
        for topic, qos in EXPLICIT_TOPICS:
            log.info(f"[Skenario 3] Subscribe: {topic} (QoS {qos})")

    elif scenario == 4:
        # ── Skenario 4: Wildcard + (single-level)
        # smarthome/room/+ akan cocok dengan:
        #   smarthome/room/temperature ✓
        #   smarthome/room/humidity    ✓
        #   smarthome/room/status      ✓
        # TIDAK akan cocok dengan smarthome/room/sensor/1 (2 level)
        client.subscribe("smarthome/room/+", qos=1)
        log.info("[Skenario 4] Subscribe: smarthome/room/+ (Wildcard +, QoS 1)")
        log.info("             Cocok   : smarthome/room/<satu_segmen>")
        log.info("             TIDAK   : smarthome/room/sensor/1 (2 level)")

    elif scenario == 5:
        # ── Skenario 5: Wildcard # (multi-level)
        # smarthome/# akan cocok dengan SEMUA topik di bawah smarthome/
        #   smarthome/room/temperature ✓
        #   smarthome/room/sensor/1    ✓
        #   smarthome/floor2/temp      ✓
        client.subscribe("smarthome/#", qos=2)
        log.info("[Skenario 5] Subscribe: smarthome/# (Wildcard #, QoS 2)")
        log.info("             Cocok   : SEMUA topik di bawah smarthome/")

    else:
        log.error(f"Nomor skenario tidak valid: {scenario}")

# ─── Callback: Pesan Masuk ───────────────────────────────────
def on_message(client, userdata, msg):
    topic   = msg.topic
    payload = msg.payload.decode("utf-8", errors="replace")
    qos     = msg.qos
    retain  = msg.retain

    print()
    print(f"{'─'*56}")
    print(f"  {CYAN}📥 PESAN DITERIMA{RESET}  [{datetime.now().strftime('%H:%M:%S')}]")
    print(f"  Topik  : {topic}")
    print(f"  QoS    : {qos}  |  Retain: {'Ya' if retain else 'Tidak'}")
    print(f"  Payload: {payload}")

    # ── Parsing kontekstual ──────────────────────────────────
    if "temperature" in topic:
        try:
            val = float(payload)
            color = RED if val > 30 else GREEN
            print(f"  🌡  Suhu       : {color}{val:.1f} °C{RESET}", end="")
            if val > 30: print(f"  {RED}⚠ PANAS{RESET}", end="")
        except ValueError:
            pass
        print()

    elif "humidity" in topic:
        try:
            val = float(payload)
            color = YELLOW if val > 80 else GREEN
            print(f"  💧 Kelembapan : {color}{val:.1f} %{RESET}", end="")
            if val > 80: print(f"  {YELLOW}⚠ LEMBAP{RESET}", end="")
        except ValueError:
            pass
        print()

    elif "status" in topic:
        color = RED if payload != "NORMAL" else GREEN
        print(f"  📊 Status     : {color}{payload}{RESET}")

    elif "alert" in topic:
        color = RED if payload != "OK" else GREEN
        print(f"  🔔 Alert      : {color}{payload}{RESET}")

    elif "data" in topic:
        # Topik JSON gabungan
        try:
            data = json.loads(payload)
            print(f"  📦 Data JSON  :")
            print(f"       Suhu      : {data.get('temperature', 'N/A')} °C")
            print(f"       Kelembapan: {data.get('humidity',    'N/A')} %")
            print(f"       Status    : {data.get('status',      'N/A')}")
            print(f"       Alert     : {'Ya' if data.get('alert') else 'Tidak'}")
            print(f"       Timestamp : {data.get('timestamp',   'N/A')}")
        except json.JSONDecodeError:
            print(f"  ⚠ Gagal parse JSON: {payload}")

    print(f"{'─'*56}")

# ─── Callback: Disconnect ────────────────────────────────────
def on_disconnect(client, userdata, disconnect_flags, rc=None, properties=None):
    if rc != 0:
        log.warning(f"⚠ Terputus dari broker (rc={rc})")

# ─── Main ────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Smart Room MQTT Subscriber")
    parser.add_argument(
        "--scenario", "-s",
        type=int,
        choices=[1, 2, 3, 4, 5],
        default=5,
        help="Pilih skenario (1-5). Default: 5"
    )
    args = parser.parse_args()

    log.info("=== Smart Room Monitoring: SUBSCRIBER ===")
    log.info(f"Skenario aktif: {args.scenario}")

    skenario_info = {
        1: "Komunikasi Dasar — 1 topik, QoS 0",
        2: "QoS Berbeda — temperature(0), humidity(1), status(2)",
        3: "Beberapa Topik Eksplisit",
        4: "Wildcard + (single-level: smarthome/room/+)",
        5: "Wildcard # (multi-level: smarthome/#)",
    }
    log.info(f"Deskripsi: {skenario_info[args.scenario]}")

    client = mqtt.Client(
        client_id=f"Python_Subscriber_S{args.scenario}",
        protocol=mqtt.MQTTv5,
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        userdata={"scenario": args.scenario}
    )

    if MQTT_USER:
        client.username_pw_set(MQTT_USER, MQTT_PASS)

    client.on_connect    = on_connect
    client.on_message    = on_message
    client.on_disconnect = on_disconnect

    try:
        client.connect(BROKER_HOST, BROKER_PORT, KEEPALIVE)
    except Exception as e:
        log.error(f"Tidak dapat terhubung ke broker: {e}")
        return

    log.info("Menunggu pesan... (Ctrl+C untuk berhenti)")
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        log.info("\nSubscriber dihentikan.")
    finally:
        client.disconnect()
        log.info("Koneksi ditutup.")

if __name__ == "__main__":
    main()