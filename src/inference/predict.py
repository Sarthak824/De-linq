import os
import sys
import json

import joblib
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.interventions.recommend import enrich_customer_decision
from src.intelligence.intent_detector import detect_intents
from src.models.model_config import FEATURE_COLUMNS
from src.policy.decision_engine import apply_policy_engine
from src.persona.persona_builder import generate_personas

MODEL_PATH = os.path.join(BASE_DIR, "artifacts", "xgb_model.pkl")
INPUT_PATH = os.path.join(BASE_DIR, "data", "processed", "final_cleaned.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "output")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "customer_risk_predictions.csv")
SEQUENCE_SCORES_PATH = os.path.join(OUTPUT_DIR, "customer_sequence_scores.csv")
LSTM_METADATA_PATH = os.path.join(BASE_DIR, "artifacts", "lstm_metadata.json")


def load_model(model_path=MODEL_PATH):
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Model file not found: {model_path}. Train the model before running inference."
        )

    try:
        return joblib.load(model_path)
    except Exception as exc:
        raise RuntimeError(
            "Unable to load the saved model. If you are using XGBoost on macOS, "
            "install libomp with `brew install libomp` and retrain the model."
        ) from exc


def prepare_features(df):
    missing_columns = [column for column in FEATURE_COLUMNS if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required feature columns: {missing_columns}")
    return df[FEATURE_COLUMNS]


def load_sequence_scores(sequence_scores_path=SEQUENCE_SCORES_PATH):
    if not os.path.exists(sequence_scores_path):
        return pd.DataFrame()

    if not os.path.exists(LSTM_METADATA_PATH):
        return pd.DataFrame()

    with open(LSTM_METADATA_PATH, "r") as metadata_file:
        metadata = json.load(metadata_file)

    if metadata.get("max_customers") is not None or metadata.get("max_windows") is not None:
        print("Skipping sequence score merge because the available LSTM artifacts are from a subset smoke run.")
        return pd.DataFrame()

    if os.path.getmtime(sequence_scores_path) < os.path.getmtime(LSTM_METADATA_PATH):
        print("Skipping sequence score merge because the score file is older than the current LSTM metadata.")
        return pd.DataFrame()

    return pd.read_csv(sequence_scores_path)


def score_customers(df, model):
    feature_frame = prepare_features(df)

    risk_scores = model.predict_proba(feature_frame)[:, 1]
    risk_predictions = model.predict(feature_frame)

    output_df = df.copy()
    output_df["risk_score"] = risk_scores.round(4)
    output_df["risk_prediction"] = risk_predictions.astype(int)

    decisions = output_df.apply(
        lambda row: enrich_customer_decision(row, row["risk_score"]),
        axis=1,
        result_type="expand",
    )

    output_df = pd.concat([output_df, decisions], axis=1)
    output_df["top_reason_codes"] = output_df["top_reason_codes"].apply(lambda items: ", ".join(items))
    output_df = generate_personas(output_df)
    output_df = detect_intents(output_df)
    output_df = apply_policy_engine(output_df)
    output_df["recommended_intervention"] = output_df.apply(
        lambda row: enrich_customer_decision(row, row["risk_score"])["recommended_intervention"],
        axis=1,
    )

    sequence_scores_df = load_sequence_scores()
    if not sequence_scores_df.empty and "customer_id" in output_df.columns:
        output_df = output_df.merge(sequence_scores_df, on="customer_id", how="left")

    return output_df


def format_prediction_row(row):
    return {
        "customer_id": row.get("customer_id"),
        "risk_score": float(row["risk_score"]),
        "sequence_risk_score": float(row["sequence_risk_score"]) if pd.notna(row.get("sequence_risk_score")) else None,
        "risk_prediction": int(row["risk_prediction"]),
        "risk_band": row["risk_band"],
        "top_reason_codes": [item.strip() for item in row["top_reason_codes"].split(",")],
        "recommended_intervention": row["recommended_intervention"],
        "persona_label": row.get("persona_label"),
        "persona_signals": [item.strip() for item in str(row.get("persona_signals", "")).split(",") if item.strip()],
        "financial_stress_level": row.get("financial_stress_level"),
        "intent_label": row.get("intent_label"),
        "policy_action": row.get("policy_action"),
        "policy_priority": row.get("policy_priority"),
        "recommended_channel": row.get("recommended_channel"),
    }


def score_records(records, model):
    df = pd.DataFrame(records)
    scored_df = score_customers(df, model)
    return [format_prediction_row(row) for _, row in scored_df.iterrows()]


def build_portfolio_summary(scored_df):
    intervention_counts = scored_df["recommended_intervention"].value_counts().to_dict()
    risk_band_counts = scored_df["risk_band"].value_counts().to_dict()

    return {
        "total_customers": int(len(scored_df)),
        "average_risk_score": round(float(scored_df["risk_score"].mean()), 4),
        "risk_band_counts": risk_band_counts,
        "intervention_counts": intervention_counts,
    }


def run_batch_inference(input_path=INPUT_PATH, output_path=OUTPUT_PATH, model_path=MODEL_PATH):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input dataset not found: {input_path}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    model = load_model(model_path)
    df = pd.read_csv(input_path)
    scored_df = score_customers(df, model)

    output_columns = [
        "customer_id",
        "risk_score",
        "sequence_risk_score",
        "risk_prediction",
        "risk_band",
        "top_reason_codes",
        "recommended_intervention",
        "persona_label",
        "persona_signals",
        "financial_stress_level",
        "intent_label",
        "policy_action",
        "policy_priority",
        "recommended_channel",
    ]
    scored_df[output_columns].to_csv(output_path, index=False)

    print(f"✅ Batch scoring completed: {scored_df.shape}")
    print(f"📁 Saved to: {output_path}")

    return scored_df


if __name__ == "__main__":
    run_batch_inference()
