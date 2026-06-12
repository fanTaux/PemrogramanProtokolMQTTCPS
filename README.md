<div align="center">
  <h1>🍃 Smart Room Monitoring — Protokol MQTT</h1>
  <p>
    <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
    <a href="https://mosquitto.org/"><img src="https://img.shields.io/badge/MQTT-Eclipse%20Mosquitto-blue" alt="MQTT"></a>
    <img src="https://img.shields.io/badge/Platform-Python%203-lightgrey" alt="Platform">
  </p>
  <p>
    <b>Proyek Akhir Cyber Physical System | Teknik Komputer | Universitas Brawijaya</b>
  </p>
  <p>
    Repositori ini merupakan implementasi simulasi perangkat lunak (<i>Software-in-the-Loop</i>) untuk sistem pemantauan kondisi ruangan cerdas menggunakan protokol <b>MQTT (Message Queuing Telemetry Transport)</b>. Fokus utama kita adalah mendemonstrasikan kapabilitas komunikasi <i>Publisher-Subscriber</i> dengan berbagai tingkat QoS (<i>Quality of Service</i>) dan penggunaan <i>Wildcard</i> pada hierarki topik MQTT menggunakan lingkungan murni Python.
  </p>
</div>

<hr>

<h2>🏛 Topologi Sistem</h2>

[Image of MQTT publish subscribe architecture]

<p>Sistem ini berpusat pada broker Mosquitto yang menjembatani simulasi perangkat keras virtual melalui skrip Python. Tidak ada koneksi langsung antara pengirim dan penerima; semuanya dikelola melalui perantara (<i>Broker</i>) secara asinkron.</p>

<pre>
  [ Python Publisher ]                          [ Python Subscriber ]
   (Simulasi Data Sensor)                       (Terminal / CLI Output)
          │                                              ▲
          │ PUBLISH                                      │ DELIVER
          ▼                                              │
  ┌────────────────────────────────────────────────────────────┐
  │                  ECLIPSE MOSQUITTO BROKER                  │
  │                        (Port 1883)                         │
  └────────────────────────────────────────────────────────────┘
</pre>

<hr>

<h2>📂 Struktur Repositori</h2>
<p>Kita membagi sistem menjadi dua entitas perangkat lunak utama:</p>
<table>
  <thead>
    <tr>
      <th>File</th>
      <th>Lingkungan</th>
      <th>Deskripsi Peran</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>📄 publisher.py</code></td>
      <td>Python 3</td>
      <td>Mensimulasikan pembacaan sensor suhu dan kelembapan, mengevaluasi status ruangan, dan mempublikasikan data ke berbagai topik MQTT secara periodik.</td>
    </tr>
    <tr>
      <td><code>📄 subscriber.py</code></td>
      <td>Python 3</td>
      <td>Skrip dinamis untuk menerima data dari broker. Memiliki argumen antarmuka baris perintah (CLI) untuk beralih di antara 5 mode pengujian (Skenario).</td>
    </tr>
  </tbody>
</table>

<hr>

<h2>🛠 Persiapan & Instalasi</h2>

<h3>1. Kebutuhan Perangkat Lunak</h3>
<ul>
  <li><b>Python 3.8+</b></li>
  <li><b>Broker Mosquitto:</b> <a href="https://mosquitto.org/download/">Unduh Eclipse Mosquitto</a>.</li>
</ul>

<h3>2. Instalasi Dependensi</h3>
<p>Kita memerlukan pustaka <code>paho-mqtt</code> untuk menangani protokol MQTT di Python. Jalankan perintah ini di terminal kita:</p>
<pre><code>pip install paho-mqtt</code></pre>

<h3>3. Konfigurasi Mosquitto Broker</h3>
<p>Agar simulasi dapat berjalan mulus di jaringan lokal (<i>localhost</i>), kita harus mengizinkan koneksi anonim. Buka atau buat file <code>mosquitto.conf</code> dan tambahkan baris berikut:</p>
<pre><code>listener 1883 0.0.0.0
allow_anonymous true</code></pre>
<p>Jalankan broker menggunakan konfigurasi tersebut:</p>
<pre><code>
