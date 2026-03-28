import os
import sys

import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

INPUT_PATH = os.path.join(BASE_DIR, "data", "processed", "final_cleaned.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "processed", "final_cleaned.parquet")


def export_parquet(input_path=INPUT_PATH, output_path=OUTPUT_PATH):
    df = pd.read_csv(input_path)
    if "event_timestamp" not in df.columns:
        df["event_timestamp"] = pd.Timestamp.utcnow()
    df.to_parquet(output_path, index=False)
    print(f"✅ Exported parquet source to: {output_path}")


if __name__ == "__main__":
    export_parquet()
