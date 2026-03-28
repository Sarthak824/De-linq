import boto3
import pandas as pd
import json
import time

STREAM_NAME = "risk-stream"

kinesis = boto3.client("kinesis", region_name="ap-south-1")

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
FILE_PATH = os.path.join(BASE_DIR, "data/processed/synthetic_labeled.csv")

df = pd.read_csv(FILE_PATH).head(500)

for i, row in df.iterrows():
    data = row.to_json()

    kinesis.put_record(
        StreamName=STREAM_NAME,
        Data=data,
        PartitionKey=row["customer_id"]
    )

    # simulate streaming
    if i % 50 == 0:
        time.sleep(1)

print("✅ Data streamed safely")