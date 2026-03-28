import json
import logging
import random
import time

import pandas as pd
from kafka import KafkaProducer

KAFKA_BROKER = "localhost:9092"
OUTPUT_TOPIC = "customer_events"
INPUT_PATH = "data/processed/final_cleaned.csv"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def build_producer():
    return KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
    )


def stream_customer_events():
    df = pd.read_csv(INPUT_PATH)
    producer = build_producer()

    logger.info("Streaming lightweight real-time customer payloads for Feast-backed scoring")

    try:
        for index, row in df.iterrows():
            record = {
                "customer_id": row["customer_id"],
                "event_time": pd.Timestamp.now().isoformat(),
                "event_type": "balance_check",
            }
            producer.send(OUTPUT_TOPIC, record)

            if index % 10 == 0:
                logger.info("Sent record %s for customer %s", index, row["customer_id"])
                time.sleep(random.uniform(0.1, 0.3))

        producer.flush()
    finally:
        producer.close()


if __name__ == "__main__":
    stream_customer_events()
