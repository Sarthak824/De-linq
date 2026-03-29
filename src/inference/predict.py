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
from src.models.combined_risk import combine_risk_scores
from src.models.model_config import FEATURE_COLUMNS
from src.policy.decision_engine import apply_policy_engine
from src.persona.persona_builder import generate_personas
from src.intelligence.black_swan_engine import batch_analyze_black_swan
from src.intelligence.exposure_analyzer import analyze_exposure, batch_analyze_exposure
from src.intelligence.hidden_distress_engine import analyze_hidden_distress, batch_analyze_hidden_distress
from src.intelligence.liquidity_engine import analyze_liquidity_stress, batch_analyze_liquidity_stress
from src.intelligence.cash_flow_reliability import batch_compute_crs
from src.storage.database import save_customer_predictions, save_customer_profiles

MODEL_PATH = os.path.join(BASE_DIR, "artifacts", "xgb_model.pkl")
INPUT_PATH = os.path.join(BASE_DIR, "data", "processed", "final_cleaned.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "output")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "customer_risk_predictions.csv")
SEQUENCE_SCORES_PATH = os.path.join(OUTPUT_DIR, "customer_sequence_scores.csv")
LSTM_METADATA_PATH = os.path.join(BASE_DIR, "artifacts", "lstm_metadata.json")


def _as_string_list(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    if not text:
        return []
    if text.startswith("[") and text.endswith("]"):
        text = text[1:-1]
    parts = [item.strip().strip("'\"") for item in text.split(",")]
    return [item for item in parts if item]


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

    xgb_risk_scores = model.predict_proba(feature_frame)[:, 1]
    risk_predictions = model.predict(feature_frame)

    output_df = df.copy()
    output_df["xgb_risk_score"] = xgb_risk_scores.round(4)
    output_df["risk_prediction"] = risk_predictions.astype(int)

    if "sequence_risk_score" not in output_df.columns:
        output_df["sequence_risk_score"] = pd.NA

    sequence_scores_df = load_sequence_scores()
    if not sequence_scores_df.empty and "customer_id" in output_df.columns:
        latest_sequence_scores = (
            sequence_scores_df.drop_duplicates(subset=["customer_id"], keep="last")
            .set_index("customer_id")["sequence_risk_score"]
        )
        missing_mask = output_df["sequence_risk_score"].isna()
        output_df.loc[missing_mask, "sequence_risk_score"] = output_df.loc[missing_mask, "customer_id"].map(
            latest_sequence_scores
        )

    combined_scores = output_df.apply(
        lambda row: combine_risk_scores(row["xgb_risk_score"], row.get("sequence_risk_score")),
        axis=1,
    )
    output_df["risk_score"] = combined_scores.apply(lambda item: item[0])
    output_df["score_source"] = combined_scores.apply(lambda item: item[1])

    # 2nd Layer: Intelligence Engines (Optimized Batch Processing)
    output_df = batch_analyze_exposure(output_df)
    output_df = batch_analyze_hidden_distress(output_df)
    output_df = batch_analyze_liquidity_stress(output_df)
    output_df = batch_analyze_black_swan(output_df)
    output_df["risk_score"] = output_df["risk_score_after_shock"]

    # 3rd Layer: Post-inference enrichment (CRS)
    output_df = batch_compute_crs(output_df)

    # Intent detection depends on the derived intelligence layers.
    output_df = detect_intents(output_df)

    decisions = output_df.apply(
        lambda row: enrich_customer_decision(row, row["risk_score"]),
        axis=1,
        result_type="expand",
    )

    output_df = pd.concat([output_df, decisions], axis=1)
    output_df["top_reason_codes"] = output_df["top_reason_codes"].apply(lambda items: ", ".join(items))

    # Generate personas AFTER intelligence engines to include behavioral signals
    output_df = generate_personas(output_df)
    output_df = apply_policy_engine(output_df)
    output_df["recommended_intervention"] = output_df.apply(
        lambda row: enrich_customer_decision(row, row["risk_score"])["recommended_intervention"],
        axis=1,
    )

    return output_df


def format_prediction_row(row):
    return {
        "customer_id": row.get("customer_id"),
        "risk_score": float(row["risk_score"]),
        "xgb_risk_score": float(row["xgb_risk_score"]) if pd.notna(row.get("xgb_risk_score")) else None,
        "sequence_risk_score": float(row["sequence_risk_score"]) if pd.notna(row.get("sequence_risk_score")) else None,
        "score_source": row.get("score_source"),
        "risk_prediction": int(row["risk_prediction"]),
        "risk_band": row["risk_band"],
        "top_reason_codes": [item.strip() for item in row["top_reason_codes"].split(",")],
        "recommended_intervention": row["recommended_intervention"],
        "persona_label": row.get("persona_label"),
        "persona_signals": _as_string_list(row.get("persona_signals", "")),
        "financial_stress_level": row.get("financial_stress_level"),
        "intent_label": row.get("intent_label"),
        "policy_action": row.get("policy_action"),
        "policy_priority": row.get("policy_priority"),
        "recommended_channel": row.get("recommended_channel"),
        "credit_exposure_level": row.get("credit_exposure_level"),
        "credit_exposure_message": row.get("credit_exposure_message"),
        "debt_structure": row.get("debt_structure"),
        "active_loan_summary": row.get("active_loan_summary"),
        "exposure_score": float(row["exposure_score"]) if pd.notna(row.get("exposure_score")) else 0.0,
        "hidden_distress_level": row.get("hidden_distress_level"),
        "hidden_distress_message": row.get("hidden_distress_message"),
        "liquidity_pattern": row.get("liquidity_pattern"),
        "patchwork_index": float(row["patchwork_index"]) if pd.notna(row.get("patchwork_index")) else 0.0,
        "emi_buffer_days": int(row["emi_buffer_days"]) if pd.notna(row.get("emi_buffer_days")) else 0,
        "shock_score": int(row["shock_score"]) if pd.notna(row.get("shock_score")) else 0,
        "shock_severity": row.get("shock_severity"),
        "shock_signals": _as_string_list(row.get("shock_signals", "")),
        "shock_intervention_hint": row.get("shock_intervention_hint"),
        "liquidity_stress_level": row.get("liquidity_stress_level"),
        "liquidity_stress_message": row.get("liquidity_stress_message"),
        "asset_depletion_strategy": row.get("asset_depletion_strategy"),
        "depletion_index": float(row["depletion_index"]) if pd.notna(row.get("depletion_index")) else 0.0,
        "od_usage_pct": float(row["od_usage_pct"]) if pd.notna(row.get("od_usage_pct")) else 0.0,
        "crs_score": float(row["crs_score"]) if pd.notna(row.get("crs_score")) else 0.0,
        "crs_band": row.get("crs_band"),
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
        "at_risk_customers": int(len(scored_df[scored_df["risk_band"].str.contains("High", na=False)])),
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
        "xgb_risk_score",
        "sequence_risk_score",
        "score_source",
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
        "credit_exposure_level",
        "credit_exposure_message",
        "debt_structure",
        "active_loan_summary",
        "exposure_score",
        "hidden_distress_level",
        "hidden_distress_message",
        "liquidity_pattern",
        "patchwork_index",
        "emi_buffer_days",
        "shock_flag",
        "shock_score",
        "shock_severity",
        "shock_signals",
        "shock_intervention_hint",
        "liquidity_stress_level",
        "liquidity_stress_message",
        "asset_depletion_strategy",
        "depletion_index",
        "od_usage_pct",
        "crs_score",
        "crs_band",
    ]
    existing_columns = [col for col in output_columns if col in scored_df.columns]
    scored_df[existing_columns].to_csv(output_path, index=False)
    save_customer_profiles(df)
    save_customer_predictions(scored_df[existing_columns])

    print(f"✅ Batch scoring completed: {scored_df.shape}")
    print(f"📁 Saved to: {output_path}")

    return scored_df


if __name__ == "__main__":
    run_batch_inference()
