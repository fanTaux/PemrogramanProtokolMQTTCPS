# Smart Room Monitoring — MQTT
## Pemetaan File & Skenario

### File yang Disertakan
| File | Platform | Peran |
|---|---|---|
| `esp32_publisher.ino` | Arduino IDE (ESP32) | Publisher hardware (DHT11 D15) |
| `esp32_subscriber.ino` | Arduino IDE (ESP32) | Subscriber display |
| `publisher.py` | Python 3 | Publisher simulasi/PC |
| `subscriber.py` | Python 3 | Subscriber semua skenario |

---

## Topologi MQTT

```
ESP32 Publisher          Mosquitto Broker         ESP32 Subscriber
(DHT11 D15)    ─PUBLISH─►  (port 1883)  ─DELIVER─► (Serial Monitor)
                                │
Python Publisher ─PUBLISH─►    │         ─DELIVER─► Python Subscriber
```

---

## Pemetaan 5 Skenario

### Skenario 1 — Komunikasi Dasar Publisher–Subscriber
- **ESP32 Publisher** publish `smarthome/room/temperature` (QoS 0)
- **Python Subscriber**: `python subscriber.py --scenario 1`
- Subscribe 1 topik saja, tampilkan nilai suhu

### Skenario 2 — QoS Berbeda (0, 1, 2)
- **Python Publisher** publish dengan:
  - `TOPIC_TEMP` → QoS 0 (at most once)
  - `TOPIC_HUM`  → QoS 1 (at least once)
  - `TOPIC_STATUS` → QoS 2 (exactly once)
- **Python Subscriber**: `python subscriber.py --scenario 2`
- Subscribe masing-masing topik dengan QoS yang sama

### Skenario 3 — Beberapa Topik
- Publisher publish ke: temperature, humidity, status, alert, data (JSON)
- **Python Subscriber**: `python subscriber.py --scenario 3`
- Subscribe daftar topik eksplisit sekaligus

### Skenario 4 — Wildcard `+`
- **Python Subscriber**: `python subscriber.py --scenario 4`
- Subscribe: `smarthome/room/+`
- Menangkap: `smarthome/room/temperature`, `smarthome/room/humidity`, dll.
- TIDAK menangkap: `smarthome/room/sensor/1` (2 level)

### Skenario 5 — Wildcard `#`
- **Python Subscriber**: `python subscriber.py --scenario 5`
- Subscribe: `smarthome/#`
- Menangkap SEMUA topik di bawah `smarthome/` tanpa batas level

---

## Konfigurasi Cepat

### ESP32 (kedua file .ino)
```cpp
const char* WIFI_SSID    = "NAMA_WIFI_KAMU";
const char* WIFI_PASSWORD = "PASSWORD_WIFI_KAMU";
const char* MQTT_BROKER  = "192.168.1.100";  // IP broker
```

### Python (publisher.py & subscriber.py)
```python
BROKER_HOST = "localhost"   # atau IP broker jika remote
BROKER_PORT = 1883
```

---

## Library yang Dibutuhkan

### Arduino IDE
Pasang via Library Manager:
- `PubSubClient` by Nick O'Leary
- `DHT sensor library` by Adafruit
- `Adafruit Unified Sensor`

### Python
```bash
pip install paho-mqtt
```
Versi yang diuji: paho-mqtt >= 2.0.0

---

## Catatan Penting

1. **QoS di ESP32 (PubSubClient)**: Library PubSubClient tidak mendukung
   publish QoS 1/2 secara penuh dari sisi client. Kode menggunakan `retain=true`
   sebagai pendekatan praktis. Untuk QoS penuh di ESP32, gunakan library
   `esp-mqtt` berbasis ESP-IDF.

2. **IP Broker**: Pastikan ESP32 dan PC berada di jaringan yang sama.
   Jalankan `ipconfig` (Windows) atau `ip addr` (Linux) untuk cek IP.

3. **Mosquitto Config** — tambahkan di `mosquitto.conf` jika koneksi ditolak:
   ```
   listener 1883
   allow_anonymous true
   ```
