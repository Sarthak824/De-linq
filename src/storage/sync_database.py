import os
import sys

import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.inference.predict import INPUT_PATH, OUTPUT_PATH
from src.storage.database import sync_csv_sources_to_database

INTERVENTION_HISTORY_PATH = os.path.join(BASE_DIR, "data", "output", "intervention_history.csv")


def _read_if_exists(path):
    if not os.path.exists(path):
        return pd.DataFrame()
    return pd.read_csv(path)


def sync_database():
    profiles_df = _read_if_exists(INPUT_PATH)
    predictions_df = _read_if_exists(OUTPUT_PATH)
    interventions_df = _read_if_exists(INTERVENTION_HISTORY_PATH)
    sync_csv_sources_to_database(
        profiles_df=profiles_df,
        predictions_df=predictions_df,
        interventions_df=interventions_df,
    )
    print("✅ Database synchronized from available CSV sources")


if __name__ == "__main__":
    sync_database()
