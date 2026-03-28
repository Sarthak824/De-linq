import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.models.training_utils import METRICS_DIR


def run_xgboost_training():
    from src.models.train_xgboost import run_training

    return run_training()


def run_lightgbm_training():
    from src.models.train_lightgbm import run_training

    return run_training()


def _load_metrics(model_name):
    metrics_path = os.path.join(METRICS_DIR, f"{model_name}_metrics.json")
    if not os.path.exists(metrics_path):
        return None
    with open(metrics_path, "r") as metrics_file:
        return json.load(metrics_file)


def run_benchmark():
    results = {}

    run_xgboost_training()
    results["xgboost"] = _load_metrics("xgboost")

    try:
        run_lightgbm_training()
        results["lightgbm"] = _load_metrics("lightgbm")
    except RuntimeError as exc:
        results["lightgbm"] = {"status": "skipped", "reason": str(exc)}

    print("\nBenchmark summary:")
    for model_name, payload in results.items():
        print(f"- {model_name}: {payload.get('roc_auc', payload)}")

    return results


if __name__ == "__main__":
    run_benchmark()
