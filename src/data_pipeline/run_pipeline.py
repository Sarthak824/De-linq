import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

CURRENT_DIR = os.path.dirname(__file__)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from data_generation.generate_data import OUTPUT_PATH as RAW_OUTPUT_PATH
from data_generation.generate_data import run_data_generation
from features.feature_engineering import OUTPUT_PATH as FEATURES_OUTPUT_PATH
from features.feature_engineering import run_feature_engineering
from labeling.label_data import OUTPUT_PATH as LABELED_OUTPUT_PATH
from labeling.label_data import run_labeling
from validation.clean_data import OUTPUT_PATH as CLEAN_OUTPUT_PATH
from validation.clean_data import run_cleaning


def run_pipeline():
    print("🚀 Starting synthetic risk-data pipeline")

    print("\n[1/4] Generating raw data...")
    run_data_generation()

    print("\n[2/4] Applying labels...")
    run_labeling()

    print("\n[3/4] Engineering features...")
    run_feature_engineering()

    print("\n[4/4] Cleaning and validating data...")
    run_cleaning()

    print("\n✅ Pipeline completed successfully")
    print("Final outputs:")
    print(f"- Raw data: {RAW_OUTPUT_PATH}")
    print(f"- Labeled data: {LABELED_OUTPUT_PATH}")
    print(f"- Features: {FEATURES_OUTPUT_PATH}")
    print(f"- Clean dataset: {CLEAN_OUTPUT_PATH}")


if __name__ == "__main__":
    run_pipeline()
