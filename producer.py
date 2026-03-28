from kafka import KafkaProducer
import pandas as pd
import json
import time
import random


df = pd.read_csv("data/processed/final_cleaned.csv")

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print("Streaming started...")

for i, row in df.iterrows():
    record = row.to_dict()

    record["event_time"] = pd.Timestamp.now().isoformat()

    producer.send('hackathon-topic', record)

    print(f"Sent record {i}")

    time.sleep(random.uniform(0.2, 0.5))