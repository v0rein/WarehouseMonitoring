# Kafka and PySpark Warehouse Monitoring

This project demonstrates a real-time data processing pipeline using Kafka and PySpark. It simulates sensor data (temperature and humidity) from multiple warehouses, processes this data, and provides a status report for each warehouse.

## Latar Belakang Masalah
Sebuah perusahaan logistik mengelola beberapa gudang penyimpanan yang menyimpan barang sensitif seperti makanan, obat-obatan, dan elektronik. Untuk menjaga kualitas penyimpanan, gudang-gudang tersebut dilengkapi dengan dua jenis sensor:

- Sensor Suhu

- Sensor Kelembaban

Sensor akan mengirimkan data setiap detik. Perusahaan ingin memantau kondisi gudang secara real-time untuk mencegah kerusakan barang akibat suhu terlalu tinggi atau kelembaban berlebih.

## Architecture & Data Flow

**`producer_suhu.py` & `producer_kelembaban.py`:**

*   Responsible for generating sensor data for temperature and humidity.
*   Data is formatted in JSON.
*   Data is sent via Kafka to two different topics: `sensor-suhu-gudang` and `sensor-kelembaban-gudang`.

**Kafka:**

*   Acts as a message broker that receives data from the producer scripts.
*   Separates the temperature and humidity data streams into their respective topics.

**`pyspark_consumer.py` (PySpark):**

*   A PySpark application that acts as a consumer for the Kafka topics `sensor-suhu-gudang` and `sensor-kelembaban-gudang`.
*   **Temperature Processing:**
    *   Reads temperature data from the `sensor-suhu-gudang` topic.
    *   Parses JSON data to get temperature values and related information (e.g., warehouse ID, timestamp).
    *   Adds a watermark to handle late-arriving data.
    *   Applies windowing (e.g., tumbling window) to group temperature data within specific time intervals.
*   **Humidity Processing:**
    *   Reads humidity data from the `sensor-kelembaban-gudang` topic.
    *   Parses JSON data to get humidity values and related information.
    *   Adds a watermark to handle late data.
    *   Applies windowing with the same duration as the windowing on temperature data.
*   **`full_outer` join:**
    *   Joins the processed temperature and humidity data based on warehouse ID and time window.
    *   Using `full_outer` join ensures that all temperature and humidity data within the same window are considered, even if one type of sensor might not send data in a particular time interval.
*   **Status Determination:**
    *   After temperature and humidity data are successfully joined for each warehouse and window, business logic is applied to determine the `Status`.
    *   Status determination conditions can involve temperature and humidity value ranges considered ideal, too high, or too low.
*   **Output to Console:**
    *   The final result containing warehouse information, time window, temperature, humidity, and `Status` is displayed to the console periodically (every 5 seconds in this case).

## Project Structure

-   [`docker-compose.yml`](d:\SEMESTER 4\Big Data dan Data Lakehouse\Kafka\docker-compose.yml): Defines the Kafka, Zookeeper, and Kafka-UI services.
-   [`producer_suhu.py`](d:\SEMESTER 4\Big Data dan Data Lakehouse\Kafka\producer_suhu.py): A Python script that produces random temperature data to a Kafka topic (`sensor-suhu-gudang`).
-   [`producer_kelembaban.py`](d:\SEMESTER 4\Big Data dan Data Lakehouse\Kafka\producer_kelembaban.py): A Python script that produces random humidity data to a Kafka topic (`sensor-kelembaban-gudang`).
-   [`pyspark_consumer.py`](d:\SEMESTER 4\Big Data dan Data Lakehouse\Kafka\pyspark_consumer.py): A PySpark application that consumes data from the Kafka topics, joins the temperature and humidity streams, determines the status of each warehouse, and prints the results to the console.

## Prerequisites

-   Docker and Docker Compose
-   Python 3
-   Apache Spark (ensure PySpark is configured in your environment)
-   Kafka Python library (`pip install kafka-python`)

## How to Run

1.  **Start Kafka Services:**
    Open a terminal in the project root directory and run:
    ````sh
    docker-compose up -d
    ````
    This will start Zookeeper, Kafka, and Kafka-UI. You can access Kafka-UI at `http://localhost:8080`.

2.  **Run the Kafka Producers:**
    Open two separate terminals.
    In the first terminal, run the temperature producer:
    ````sh
    python producer_suhu.py
    ````
    In the second terminal, run the humidity producer:
    ````sh
    python producer_kelembaban.py
    ````

3.  **Run the PySpark Consumer:**
    Open a new terminal. Ensure your Spark environment is active.
    Submit the PySpark application:
    ````sh
    spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.5 pyspark_consumer.py
    ````
    The consumer will start processing the data from Kafka and output the status of each warehouse to the console.

## Output

The [`pyspark_consumer.py`](d:\SEMESTER 4\Big Data dan Data Lakehouse\Kafka\pyspark_consumer.py) script will print a table to the console every 5 seconds, showing the `Gudang` (Warehouse ID), `Suhu` (Temperature), `Kelembaban` (Humidity), `Status`, and the `window` of time for the aggregation.

**Example Console Output:**

```
-------------------------------------------
Batch: ...
-------------------------------------------
+------+----+----------+------------------------------------+------------------------------------------+
|Gudang|Suhu|Kelembaban|Status                              |window                                    |
+------+----+----------+------------------------------------+------------------------------------------+
|G1    |85  |75        |Bahaya tinggi! Barang berisiko rusak|[2023-10-27 10:00:00, 2023-10-27 10:00:10]|
|G2    |75  |65        |Aman                                |[2023-10-27 10:00:00, 2023-10-27 10:00:10]|
|G3    |82  |68        |Suhu tinggi, kelembaban normal      |[2023-10-27 10:00:00, 2023-10-27 10:00:10]|
...
+------+----+----------+------------------------------------+------------------------------------------+
```

## Stopping the Services

To stop the Kafka services, run:
````sh
docker-compose down