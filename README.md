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
<pre><code>mosquitto -c mosquitto.conf -v</code></pre>

<hr>

<h2>🚀 Tutorial & Pengujian Skenario</h2>

<p>Untuk menguji sistem, kita perlu membuka <b>dua jendela terminal yang berbeda</b>. Terminal pertama selalu digunakan untuk menjalankan <i>Publisher</i>, sedangkan terminal kedua untuk menjalankan <i>Subscriber</i>.</p>

<h3>Langkah Persiapan</h3>
<p>Di <b>Terminal 1</b>, jalankan skrip publisher. Skrip ini akan terus mengirimkan simulasi data setiap 5 detik:</p>
<pre><code>python publisher.py</code></pre>

<p>Di <b>Terminal 2</b>, kita akan menjalankan skrip subscriber sesuai dengan skenario yang ingin dipelajari di bawah ini.</p>

<br>

<h3>▶ Skenario 1: Komunikasi Dasar</h3>
<p>Mendemonstrasikan cara berlangganan pada satu topik tunggal dengan tingkat QoS 0 (<i>Fire and Forget</i>).</p>
<pre><code>python subscriber.py --scenario 1</code></pre>
<ul>
  <li><b>Topik yang didengarkan:</b> <code>smarthome/room/temperature</code></li>
  <li><b>Hasil:</b> Kita hanya akan melihat aliran data suhu ruangan yang masuk tanpa data kelembapan atau status lainnya.</li>
</ul>

<h3>▶ Skenario 2: Konfigurasi QoS Berbeda</h3>
<p>Mendemonstrasikan penerimaan data dari berbagai topik yang memiliki tingkat jaminan pengiriman (QoS) yang bervariasi.</p>
<pre><code>python subscriber.py --scenario 2</code></pre>
<ul>
  <li><b>QoS 0:</b> Topik suhu (At most once).</li>
  <li><b>QoS 1:</b> Topik kelembapan (At least once). Pustaka Python akan menangani konfirmasi <code>PUBACK</code> di balik layar.</li>
  <li><b>QoS 2:</b> Topik status (Exactly once). Menjamin pengiriman data krusial tanpa duplikasi menggunakan <i>handshake</i> 4 langkah.</li>
</ul>

<h3>▶ Skenario 3: Multi-Topik Eksplisit</h3>
<p>Menguji kemampuan skrip untuk berlangganan pada daftar beberapa topik yang spesifik secara bersamaan.</p>
<pre><code>python subscriber.py --scenario 3</code></pre>
<ul>
  <li><b>Topik yang didengarkan:</b> Suhu, kelembapan, status, peringatan, dan payload JSON mentah (<code>smarthome/room/data</code>).</li>
  <li><b>Hasil:</b> Terminal akan menampilkan hasil penguraian (<i>parsing</i>) yang membedakan tipe data tunggal dan tipe data gabungan (JSON).</li>
</ul>

<h3>▶ Skenario 4: Single-level Wildcard ( <code>+</code> )</h3>
<p>Menggunakan karakter wildcard <code>+</code> untuk menangkap semua data dalam satu level hierarki spesifik.</p>
<pre><code>python subscriber.py --scenario 4</code></pre>
<ul>
  <li><b>Topik yang didengarkan:</b> <code>smarthome/room/+</code></li>
  <li><b>Hasil:</b> Kita akan menerima semua pesan dari topik seperti <code>smarthome/room/temperature</code> dan <code>smarthome/room/humidity</code>. Namun, jika ada topik <code>smarthome/room/sensor/1</code> (berada 2 level di bawah), pesan tersebut akan diabaikan.</li>
</ul>

<h3>▶ Skenario 5: Multi-level Wildcard ( <code>#</code> )</h3>
<p>Menggunakan karakter wildcard <code>#</code> untuk menangkap seluruh lalu lintas data di bawah direktori utama. Skenario ini adalah nilai bawaan (<i>default</i>).</p>
<pre><code>python subscriber.py</code></pre>
<ul>
  <li><b>Topik yang didengarkan:</b> <code>smarthome/#</code></li>
  <li><b>Hasil:</b> Kita memiliki visibilitas total. Pustaka akan menangkap semua pesan yang diawali dengan <code>smarthome/</code> tanpa mempedulikan seberapa dalam level hierarki topik tersebut dibuat oleh publisher.</li>
</ul>

<hr>

<h2>📌 Catatan Pengembangan</h2>
<ul>
  <li><b>QoS 2 Overhead:</b> Penggunaan QoS 2 memakan sumber daya jaringan (<i>bandwidth</i>) paling besar. Dalam implementasi dunia nyata, kita hanya menggunakannya untuk data yang sangat kritis (seperti aktuasi atau status peringatan bahaya).</li>
  <li><b>Keamanan Sistem:</b> Konfigurasi <code>allow_anonymous true</code> murni diterapkan untuk menyederhanakan tahap pengujian dan simulasi lokal. Untuk lingkungan produksi, arsitektur ini harus dikembangkan menggunakan autentikasi nama pengguna, kata sandi, dan enkripsi lalu lintas data (TLS/SSL).</li>
</ul>
