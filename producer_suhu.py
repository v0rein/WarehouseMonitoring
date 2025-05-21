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
