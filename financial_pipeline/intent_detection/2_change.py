import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.sequence_model.train_lstm import run_training_pipeline


if __name__ == "__main__":
    print(
        "Deprecated entrypoint: financial_pipeline/intent_detection/2_change.py\n"
        "Use src/sequence_model/train_lstm.py instead."
    )
    run_training_pipeline()
