import os
import sys

import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.inference.predict import INPUT_PATH, load_model, score_customers
from src.models.combined_risk import DEFAULT_SEQUENCE_WEIGHT, DEFAULT_XGB_WEIGHT
from src.models.mlflow_utils import log_json_artifact, start_run
from src.models.training_utils import compute_score_metrics, save_metrics


def evaluate_combined_risk(input_path=INPUT_PATH):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input dataset not found: {input_path}")

    df = pd.read_csv(input_path)
    if "label" not in df.columns:
        raise ValueError("Combined-score evaluation requires a labeled dataset with a `label` column.")

    model = load_model()
    scored_df = score_customers(df, model)

    metrics = compute_score_metrics(scored_df["label"], scored_df["risk_score"])
    metrics["score_coverage"] = round(float(scored_df["risk_score"].notna().mean()), 6)
    metrics["sequence_coverage"] = round(float(scored_df["sequence_risk_score"].notna().mean()), 6)
    metrics["combined_score_rate"] = round(float((scored_df["score_source"] == "combined").mean()), 6)
    metrics["xgboost_only_rate"] = round(float((scored_df["score_source"] == "xgboost_only").mean()), 6)

    metrics_path = save_metrics("combined", metrics)

    with start_run("combined_risk_evaluation") as (mlflow, _):
        mlflow.log_params(
            {
                "xgb_weight": DEFAULT_XGB_WEIGHT,
                "sequence_weight": DEFAULT_SEQUENCE_WEIGHT,
                "rows_evaluated": int(len(scored_df)),
            }
        )
        mlflow.log_metrics(
            {
                "combined_accuracy": metrics["accuracy"],
                "combined_precision": metrics["precision"],
                "combined_recall": metrics["recall"],
                "combined_f1": metrics["f1"],
                "combined_roc_auc": metrics["roc_auc"],
                "sequence_coverage": metrics["sequence_coverage"],
                "combined_score_rate": metrics["combined_score_rate"],
            }
        )
        log_json_artifact(mlflow, metrics, "combined_metrics.json")

    print("✅ Combined-score metrics saved at:", metrics_path)
    print("🎯 Combined ROC-AUC Score:", metrics["roc_auc"])
    print("📊 Combined Accuracy:", metrics["accuracy"])

    return metrics


if __name__ == "__main__":
    evaluate_combined_risk()
