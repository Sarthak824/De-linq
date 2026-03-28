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

print("Streaming lightweight real-time customer payloads started (Feast Mode)...")

# Keep the dataframe to simulate reality by iterating over known IDs
df = pd.read_csv("data/processed/final_cleaned.csv")

for i, row in df.iterrows():
    # Only sent the primary key and an event payload!
    record = {
        "customer_id": row["customer_id"],
        "event_time": pd.Timestamp.now().isoformat(),
        "event_type": "balance_check",
    }

    producer.send('customer_events', record)

    if i % 10 == 0:
        print(f"Sent record {i}")
        time.sleep(random.uniform(0.1, 0.3))