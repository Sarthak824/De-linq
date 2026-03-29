import argparse
import json
import os
import sys

import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.inference.predict import INPUT_PATH, load_model, score_customers
from src.models.mlflow_utils import log_json_artifact, start_run
from src.models.training_utils import METRICS_DIR, compute_score_metrics


DEFAULT_START = 0.1
DEFAULT_STOP = 0.9
DEFAULT_STEP = 0.05


def _build_thresholds(start, stop, step):
    thresholds = []
    current = start
    while current <= stop + 1e-9:
        thresholds.append(round(current, 4))
        current += step
    return thresholds


def run_threshold_sweep(
    input_path=INPUT_PATH,
    start=DEFAULT_START,
    stop=DEFAULT_STOP,
    step=DEFAULT_STEP,
    optimize_for="f1",
):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input dataset not found: {input_path}")

    df = pd.read_csv(input_path)
    if "label" not in df.columns:
        raise ValueError("Threshold sweep requires a labeled dataset with a `label` column.")

    model = load_model()
    scored_df = score_customers(df, model)

    results = []
    for threshold in _build_thresholds(start, stop, step):
        metrics = compute_score_metrics(scored_df["label"], scored_df["risk_score"], threshold=threshold)
        results.append(
            {
                "threshold": threshold,
                "accuracy": metrics["accuracy"],
                "precision": metrics["precision"],
                "recall": metrics["recall"],
                "f1": metrics["f1"],
                "roc_auc": metrics["roc_auc"],
            }
        )

    valid_objectives = {"accuracy", "precision", "recall", "f1", "roc_auc"}
    if optimize_for not in valid_objectives:
        raise ValueError(f"optimize_for must be one of {sorted(valid_objectives)}")

    ranked = sorted(
        results,
        key=lambda item: (item[optimize_for], item["roc_auc"], item["f1"], -abs(item["threshold"] - 0.5)),
        reverse=True,
    )
    best = ranked[0]

    payload = {
        "best": best,
        "optimize_for": optimize_for,
        "results": ranked,
    }

    os.makedirs(METRICS_DIR, exist_ok=True)
    output_path = os.path.join(METRICS_DIR, "combined_threshold_sweep.json")
    with open(output_path, "w") as output_file:
        json.dump(payload, output_file, indent=2)

    with start_run("combined_risk_threshold_sweep") as (mlflow, _):
        mlflow.log_params(
            {
                "threshold_start": start,
                "threshold_stop": stop,
                "threshold_step": step,
                "optimize_for": optimize_for,
                "candidates_evaluated": len(ranked),
                "best_threshold": best["threshold"],
            }
        )
        mlflow.log_metrics(
            {
                "best_threshold_accuracy": best["accuracy"],
                "best_threshold_precision": best["precision"],
                "best_threshold_recall": best["recall"],
                "best_threshold_f1": best["f1"],
                "best_threshold_roc_auc": best["roc_auc"],
            }
        )
        log_json_artifact(mlflow, payload, "combined_threshold_sweep.json")

    print("✅ Threshold sweep saved at:", output_path)
    print("🏆 Best threshold:", best)
    return payload


def build_arg_parser():
    parser = argparse.ArgumentParser(description="Sweep decision thresholds for the combined risk score.")
    parser.add_argument("--start", type=float, default=DEFAULT_START)
    parser.add_argument("--stop", type=float, default=DEFAULT_STOP)
    parser.add_argument("--step", type=float, default=DEFAULT_STEP)
    parser.add_argument("--optimize-for", default="f1")
    return parser


if __name__ == "__main__":
    args = build_arg_parser().parse_args()
    run_threshold_sweep(
        start=args.start,
        stop=args.stop,
        step=args.step,
        optimize_for=args.optimize_for,
    )
