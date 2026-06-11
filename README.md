<div align="center">
  <h1>🍃 Smart Room Monitoring — Protokol MQTT</h1>
  <p>
    <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
    <a href="https://mosquitto.org/"><img src="https://img.shields.io/badge/MQTT-Eclipse%20Mosquitto-blue" alt="MQTT"></a>
    <img src="https://img.shields.io/badge/Platform-ESP32%20%7C%20Python-lightgrey" alt="Platform">
  </p>
  <p>
    Proyek ini merupakan implementasi sistem pemantauan kondisi ruangan cerdas menggunakan protokol <b>MQTT (Message Queuing Telemetry Transport)</b>. Sistem ini dikembangkan untuk Proyek Akhir mata kuliah Cyber Physical System, Program Studi Teknik Komputer, Universitas Brawijaya.
  </p>
  <p>
    Fokus utama dari repositori ini adalah mendemonstrasikan kapabilitas komunikasi <i>Publisher-Subscriber</i> dengan berbagai tingkat QoS (Quality of Service) dan penggunaan <i>Wildcard</i> pada topik MQTT.
  </p>
</div>

<hr>

<h2>🏛 Topologi Sistem</h2>
<p>Sistem berpusat pada broker Mosquitto yang menjembatani perangkat keras (ESP32) dan simulasi perangkat lunak (Python).</p>
<pre>
  [ ESP32 Publisher ]                          [ ESP32 Subscriber ]
  (Sensor DHT11 - D15)                            (Serial Monitor)
          │                                              ▲
          │ PUBLISH                                      │ DELIVER
          ▼                                              │
  ┌────────────────────────────────────────────────────────────┐
  │                   ECLIPSE MOSQUITTO BROKER                 │
  │                         (Port 1883)                        │
  └────────────────────────────────────────────────────────────┘
          ▲                                              │
          │ PUBLISH                                      │ DELIVER
          │                                              ▼
 [ Python Publisher ]                         [ Python Subscriber ]
   (Simulasi Data)                           (Terminal / CLI output)
</pre>

<hr>

<h2>📂 Struktur Repositori</h2>
<p>Kita membagi sistem menjadi dua <i>environment</i> utama: mikrokontroler dan PC/Server.</p>
<table>
  <thead>
    <tr>
      <th>File / Direktori</th>
      <th>Lingkungan</th>
      <th>Deskripsi Peran</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>📁 esp32_publisher/</code></td>
      <td>Arduino IDE (ESP32)</td>
      <td>Membaca sensor DHT11 dan mengirim data suhu/kelembapan.</td>
    </tr>
    <tr>
      <td><code>📁 esp32_subscriber/</code></td>
      <td>Arduino IDE (ESP32)</td>
      <td>Menerima data dari broker untuk ditampilkan.</td>
    </tr>
    <tr>
      <td><code>📄 publisher.py</code></td>
      <td>Python 3</td>
      <td>Mensimulasikan publisher untuk pengujian cepat tanpa <i>hardware</i>.</td>
    </tr>
    <tr>
      <td><code>📄 subscriber.py</code></td>
      <td>Python 3</td>
      <td><i>Script</i> utama untuk menguji kelima skenario berlangganan (Subscribe).</td>
    </tr>
  </tbody>
</table>

<hr>

<h2>🎯 5 Skenario Pengujian</h2>
<p>Kita telah menyiapkan 5 skenario berbeda untuk mendemonstrasikan fitur-fitur MQTT:</p>
<ul>
  <li>
    <b>Komunikasi Dasar (Skenario 1)</b>
    <ul>
      <li>Berlangganan pada 1 topik tunggal: <code>smarthome/room/temperature</code>.</li>
      <li>Menampilkan pembacaan suhu ruangan dasar.</li>
    </ul>
  </li>
  <li>
    <b>QoS Berbeda (Skenario 2)</b>
    <ul>
      <li>Menguji tingkat keandalan pengiriman pesan:</li>
      <li><code>QoS 0</code> (At most once) pada topik suhu.</li>
      <li><code>QoS 1</code> (At least once) pada topik kelembapan.</li>
      <li><code>QoS 2</code> (Exactly once) pada status ruangan.</li>
    </ul>
  </li>
  <li>
    <b>Multi-Topik Eksplisit (Skenario 3)</b>
    <ul>
      <li>Berlangganan pada beberapa topik spesifik sekaligus (suhu, kelembapan, status, peringatan, dan raw JSON) menggunakan daftar berlangganan.</li>
    </ul>
  </li>
  <li>
    <b>Single-level Wildcard <code>+</code> (Skenario 4)</b>
    <ul>
      <li>Topik: <code>smarthome/room/+</code></li>
      <li>Menangkap semua data pada level <code>room</code>, namun mengabaikan hierarki di bawahnya (seperti <code>smarthome/room/sensor/1</code>).</li>
    </ul>
  </li>
  <li>
    <b>Multi-level Wildcard <code>#</code> (Skenario 5)</b>
    <ul>
      <li>Topik: <code>smarthome/#</code></li>
      <li>Menangkap seluruh lalu lintas data yang berada di bawah hierarki <code>smarthome/</code> tanpa batasan level.</li>
    </ul>
  </li>
</ul>

<hr>

<h2>🛠 Persiapan & Instalasi</h2>
<h3>1. Kebutuhan Perangkat Keras</h3>
<ul>
  <li>ESP32 Development Board</li>
  <li>Sensor Suhu & Kelembapan DHT11 (Pin Data terhubung ke <b>D15</b>)</li>
</ul>

<h3>2. Kebutuhan Perangkat Lunak</h3>
<ul>
  <li><b>Broker:</b> <a href="https://mosquitto.org/download/">Eclipse Mosquitto</a> terinstal dan berjalan.</li>
  <li><b>Arduino IDE Library:</b>
    <ul>
      <li><code>PubSubClient</code> (oleh Nick O'Leary)</li>
      <li><code>DHT sensor library</code> (oleh Adafruit)</li>
      <li><code>Adafruit Unified Sensor</code></li>
    </ul>
  </li>
  <li><b>Python:</b>
    <ul>
      <li>Modul <code>paho-mqtt</code> (Versi disarankan: <code>&gt;= 2.0.0</code>)</li>
      <li>Instalasi via pip: <code>pip install paho-mqtt</code></li>
    </ul>
  </li>
</ul>

<hr>

<h2>🚀 Panduan Penggunaan</h2>

<h3>Konfigurasi Jaringan</h3>
<p>Sebelum mengunggah kode atau menjalankan <i>script</i>, kita perlu memastikan konfigurasi IP dan WiFi sesuai dengan jaringan lokal:</p>

<b>Pada Arduino IDE (<code>.ino</code>)</b>
<pre><code>const char* WIFI_SSID     = "NAMA_WIFI_KITA";
const char* WIFI_PASSWORD = "PASSWORD_WIFI_KITA";
const char* MQTT_BROKER   = "192.168.x.x";  // Sesuaikan dengan IP PC yang menjalankan Mosquitto
</code></pre>

<b>Pada Python (<code>.py</code>)</b>
<pre><code>BROKER_HOST = "localhost"   # Gunakan IP lokal jika ESP32 mengakses ini dari jaringan
</code></pre>

<h3>Menjalankan Pengujian Python</h3>
<p>Buka terminal dan gunakan <i>flag</i> <code>--scenario</code> untuk memilih mode pengujian:</p>

<pre><code># Menjalankan Skenario 1 (Satu topik)
python subscriber.py --scenario 1

# Menjalankan Skenario 4 (Wildcard +)
python subscriber.py --scenario 4

# Menjalankan Skenario 5 (Wildcard #) - Default
python subscriber.py
</code></pre>

<h3>Konfigurasi Mosquitto (Penting)</h3>
<p>Jika koneksi ditolak (Connection Refused), kita perlu mengizinkan koneksi dari luar localhost. Tambahkan baris berikut pada file <code>mosquitto.conf</code>:</p>
<pre><code>listener 1883 0.0.0.0
allow_anonymous true
</code></pre>

<hr>

<h2>📌 Catatan Pengembangan</h2>
<ol>
  <li><b>Keterbatasan PubSubClient:</b> Library Arduino <code>PubSubClient</code> memiliki batasan dalam implementasi penuh untuk <i>publish</i> dengan QoS 1 dan QoS 2. Pada kode ini, kita menggunakan flag <code>retain=true</code> sebagai pendekatan praktis. Untuk standar industri yang mewajibkan QoS tingkat tinggi pada sisi <i>client</i>, disarankan untuk bermigrasi ke <code>esp-mqtt</code> (berbasis ESP-IDF).</li>
  <li><b>Keamanan:</b> Repositori ini saat ini diatur untuk <code>allow_anonymous true</code> demi kemudahan pengujian lokal. Pada tahap produksi, kita harus mengimplementasikan autentikasi <i>username/password</i> dan sertifikat TLS/SSL.</li>
</ol>
