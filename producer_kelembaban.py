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
