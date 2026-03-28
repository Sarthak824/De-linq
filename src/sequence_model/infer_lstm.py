import os
import sys
import argparse

import joblib
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.sequence_model.generate_sequences import LSTM_WINDOWS_PATH
from src.sequence_model.train_lstm import (
    HIDDEN_SIZE,
    LSTM_METADATA_PATH,
    LSTM_MODEL_PATH,
    LSTM_SCALER_PATH,
    SEQUENCE_XGB_PATH,
    build_lstm_model,
    extract_embeddings,
    load_lstm_windows,
)

OUTPUT_DIR = os.path.join(BASE_DIR, "data", "output")
SEQUENCE_SCORES_PATH = os.path.join(OUTPUT_DIR, "customer_sequence_scores.csv")
INFERENCE_BATCH_SIZE = 2048


def _require_torch():
    try:
        import torch
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "PyTorch is required for sequence inference. Install it in the project "
            "virtualenv before running infer_lstm.py."
        ) from exc

    return torch


def load_sequence_artifacts():
    torch = _require_torch()

    if not os.path.exists(LSTM_METADATA_PATH):
        raise FileNotFoundError(f"LSTM metadata not found: {LSTM_METADATA_PATH}")

    scaler = joblib.load(LSTM_SCALER_PATH)
    xgb_model = joblib.load(SEQUENCE_XGB_PATH)

    with open(LSTM_METADATA_PATH, "r") as metadata_file:
        import json

        metadata = json.load(metadata_file)

    model = build_lstm_model(
        input_size=len(metadata["feature_names"]),
        hidden_size=metadata.get("hidden_size", HIDDEN_SIZE),
    )
    model.load_state_dict(torch.load(LSTM_MODEL_PATH, map_location="cpu"))
    model.eval()

    return model, scaler, xgb_model, metadata


def build_arg_parser():
    parser = argparse.ArgumentParser(description="Generate sequence risk scores from saved LSTM artifacts.")
    parser.add_argument("--output-path", default=SEQUENCE_SCORES_PATH)
    parser.add_argument("--max-customers", type=int, default=None)
    parser.add_argument("--max-windows", type=int, default=None)
    return parser


def score_sequence_windows(output_path=SEQUENCE_SCORES_PATH, max_customers=None, max_windows=None):
    data = load_lstm_windows(LSTM_WINDOWS_PATH)
    model, scaler, xgb_model, _ = load_sequence_artifacts()

    X = data["X"]
    customer_ids = data["customer_ids"]
    window_end_days = data["window_end_days"]

    if max_customers is not None:
        selected_customer_ids = np.unique(customer_ids)[:max_customers]
        mask = np.isin(customer_ids, selected_customer_ids)
        X = X[mask]
        customer_ids = customer_ids[mask]
        window_end_days = window_end_days[mask]

    if max_windows is not None:
        X = X[:max_windows]
        customer_ids = customer_ids[:max_windows]
        window_end_days = window_end_days[:max_windows]

    X_scaled = scaler.transform(X.reshape(-1, X.shape[2])).reshape(X.shape)
    embeddings = extract_embeddings(model, X_scaled, batch_size=INFERENCE_BATCH_SIZE)
    probabilities = xgb_model.predict_proba(embeddings)[:, 1]

    results = pd.DataFrame(
        {
            "customer_id": customer_ids,
            "window_end_day": window_end_days,
            "sequence_window_score": probabilities,
        }
    )

    latest_windows = results.sort_values(["customer_id", "window_end_day"]).groupby("customer_id").tail(1)
    window_counts = (
        results.groupby("customer_id")
        .agg(sequence_window_count=("sequence_window_score", "size"))
        .reset_index()
    )
    final_scores = latest_windows.merge(window_counts, on="customer_id", how="left")
    final_scores = final_scores.rename(columns={"sequence_window_score": "sequence_risk_score"})
    final_scores = final_scores[["customer_id", "window_end_day", "sequence_risk_score", "sequence_window_count"]]

    final_scores["sequence_risk_score"] = final_scores["sequence_risk_score"].round(4)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final_scores.to_csv(output_path, index=False)

    print(f"✅ Sequence scores created: {final_scores.shape}")
    print(f"📁 Saved to: {output_path}")

    return final_scores


if __name__ == "__main__":
    args = build_arg_parser().parse_args()
    score_sequence_windows(
        output_path=args.output_path,
        max_customers=args.max_customers,
        max_windows=args.max_windows,
    )
