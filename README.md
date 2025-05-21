# Kafka and PySpark Warehouse Monitoring

This project demonstrates a real-time data processing pipeline using Kafka and PySpark. It simulates sensor data (temperature and humidity) from multiple warehouses, processes this data, and provides a status report for each warehouse.

## Problem Overview
Sebuah perusahaan logistik mengelola beberapa gudang penyimpanan yang menyimpan barang sensitif seperti makanan, obat-obatan, dan elektronik. Untuk menjaga kualitas penyimpanan, gudang-gudang tersebut dilengkapi dengan dua jenis sensor:

- Sensor Suhu

- Sensor Kelembaban

Sensor akan mengirimkan data setiap detik. Perusahaan ingin memantau kondisi gudang secara real-time untuk mencegah kerusakan barang akibat suhu terlalu tinggi atau kelembaban berlebih.

## Arsitektur & Aliran Data

**`producer_suhu.py` & `producer_kelembaban.py`:**

* Bertanggung jawab untuk menghasilkan data sensor untuk suhu dan kelembapan.
* Data diformat dalam JSON.
* Data dikirim melalui Kafka ke dua topik berbeda: `sensor-suhu-gudang` dan `sensor-kelembaban-gudang`.

**Kafka:**

* Bertindak sebagai perantara pesan yang menerima data dari skrip produsen.
* Memisahkan aliran data suhu dan kelembapan ke dalam topik masing-masing.

**pyspark_consumer.py` (PySpark):**

* Aplikasi PySpark yang bertindak sebagai konsumen untuk topik Kafka `sensor-suhu-gudang` dan `sensor-kelembaban-gudang`.
* **Pemrosesan Suhu:**
* Membaca data suhu dari topik `sensor-suhu-gudang`. * Mengurai data JSON untuk mendapatkan nilai suhu dan informasi terkait (misalnya, ID gudang, stempel waktu).
* Menambahkan tanda air untuk menangani data yang datang terlambat.
* Menerapkan windowing (misalnya, jendela tumbling) untuk mengelompokkan data suhu dalam interval waktu tertentu.
* **Pemrosesan Kelembapan:**
* Membaca data kelembapan dari topik `sensor-kelembaban-gudang`.
* Mengurai data JSON untuk mendapatkan nilai kelembapan dan informasi terkait.
* Menambahkan tanda air untuk menangani data yang terlambat.
* Menerapkan windowing dengan durasi yang sama dengan windowing pada data suhu.
* **Gabungan `full_outer`:**
* Menggabungkan data suhu dan kelembapan yang diproses berdasarkan ID gudang dan jendela waktu.
* Menggunakan gabungan `full_outer` memastikan bahwa semua data suhu dan kelembapan dalam jendela yang sama dipertimbangkan, meskipun satu jenis sensor mungkin tidak mengirim data dalam interval waktu tertentu. * **Penentuan Status:**
* Setelah data suhu dan kelembapan berhasil digabungkan untuk setiap gudang dan jendela, logika bisnis diterapkan untuk menentukan `Status`.
* Kondisi penentuan status dapat melibatkan rentang nilai suhu dan kelembapan yang dianggap ideal, terlalu tinggi, atau terlalu rendah.
* **Keluaran ke Konsol:**
* Hasil akhir yang berisi informasi gudang, jendela waktu, suhu, kelembapan, dan `Status` ditampilkan ke konsol secara berkala (setiap 5 detik dalam kasus ini).

## Fungsi Utama
### 1. `docker-compose.yml`
File ini mendefinisikan dan mengkonfigurasi layanan yang dibutuhkan untuk menjalankan aplikasi:

- `zookeeper`: Menggunakan image `confluentinc/cp-zookeeper:7.4.0`. Zookeeper bertanggung jawab untuk manajemen konfigurasi dan sinkronisasi dalam cluster Kafka.

- kafka: Menggunakan image `confluentinc/cp-kafka:7.4.0`. Ini adalah broker pesan utama yang menerima, menyimpan, dan mengirimkan aliran data sensor. Konfigurasi `KAFKA_ADVERTISED_LISTENERS` memungkinkan koneksi ke Kafka baik dari dalam jaringan Docker (kafka:9092) maupun dari host (localhost:29092). Topik akan dibuat secara otomatis (`KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"`).

- kafka-ui: Menggunakan image `provectuslabs/kafka-ui:latest`. Menyediakan antarmuka pengguna berbasis web untuk memantau dan mengelola cluster Kafka, yang dapat diakses di `http://localhost:8080`.

### 2. `producer_suhu.py`
Skrip Python ini bertindak sebagai producer untuk data suhu:

- Terhubung ke Kafka pada `localhost:29092`.
- Secara periodik (setiap detik), menghasilkan data suhu acak (antara 70 dan 90) untuk tiga gudang (`G1`, `G2`, `G3`).
- Mengirimkan data ini dalam format JSON ke topik Kafka `sensor-suhu-gudang`.
- Mencetak pesan konfirmasi ke konsol setiap kali data dikirim.
```python
from kafka import KafkaProducer
import json
import time
import random

producer = KafkaProducer(
    bootstrap_servers='localhost:29092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

gudang_id = ['G1', 'G2', 'G3']


def kirim_suhu():
    while True:
        for gid in gudang_id:
            suhu = random.randint(70, 90)
            data = {"gudang_id": gid, "suhu": suhu}
            producer.send('sensor-suhu-gudang', value=data)
            print(f"[Suhu] Terkirim: {data}")
        time.sleep(1)


if __name__ == "__main__":
    kirim_suhu()

```

### 3. `producer_kelembaban.py`
Skrip Python ini bertindak sebagai producer untuk data kelembaban:

- Terhubung ke Kafka pada `localhost:29092`.
- Secara periodik (setiap detik), menghasilkan data kelembaban acak (antara 60 dan 80) untuk tiga gudang (`G1`, `G2`, `G3`).
- Mengirimkan data ini dalam format JSON ke topik Kafka `sensor-kelembaban-gudang`.
- Mencetak pesan konfirmasi ke konsol setiap kali data dikirim.
```python
from kafka import KafkaProducer
import json
import time
import random

producer = KafkaProducer(
    bootstrap_servers='localhost:29092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

gudang_id = ['G1', 'G2', 'G3']

def kirim_kelembaban():
    while True:
        for gid in gudang_id:
            kelembaban = random.randint(60, 80)
            data = {"gudang_id": gid, "kelembaban": kelembaban}
            producer.send('sensor-kelembaban-gudang', value=data)
            print(f"[Kelembaban] Terkirim: {data}")
        time.sleep(1)

if __name__ == "__main__":
    kirim_kelembaban()
```
4. `pyspark_consumer.py`
Aplikasi PySpark ini berfungsi sebagai consumer dan pemroses data:

- Membuat SparkSession dengan konfigurasi untuk terhubung ke Kafka.
- Mendefinisikan skema untuk data suhu (schema_suhu) dan kelembaban (schema_kelembaban).
- **Membaca Stream Suhu**:
    - Terhubung ke topik sensor-suhu-gudang di Kafka (localhost:29092).
    - Mengurai data JSON, menambahkan timestamp, dan menerapkan watermark (15 detik) untuk menangani data yang  terlambat.
    - Mengelompokkan data suhu ke dalam window waktu 10 detik.
- **Membaca Stream Kelembaban**:
    - Terhubung ke topik sensor-kelembaban-gudang di Kafka (localhost:29092).
    - Melakukan proses serupa seperti pada stream suhu (parsing, timestamp, watermark, windowing).
- **Menggabungkan Stream**:
    - Melakukan full_outer join pada stream suhu dan kelembaban berdasarkan gudang_id dan window. Ini memastikan semua data dari kedua sensor dipertimbangkan, bahkan jika salah satu sensor tidak mengirim data pada interval tertentu.
- **Menentukan Status**:
    - Menggunakan fungsi coalesce untuk menangani nilai NULL (jika salah satu sensor tidak mengirim data) dengan menggantinya menjadi 0.
    - Menerapkan logika kondisional (when) untuk menentukan status gudang (Aman, Suhu tinggi, kelembaban normal, Kelembaban tinggi, suhu aman, Bahaya tinggi! Barang berisiko rusak) berdasarkan nilai suhu dan kelembaban.
- **Output**:
    - Menulis hasil (Gudang, Suhu, Kelembaban, Status, window) ke konsol setiap 5 detik dalam mode append.