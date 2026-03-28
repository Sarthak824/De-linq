import os

import pandas as pd


DEFAULT_XGB_WEIGHT = float(os.environ.get("DELINQ_XGB_WEIGHT", "0.65"))
DEFAULT_SEQUENCE_WEIGHT = float(os.environ.get("DELINQ_SEQUENCE_WEIGHT", "0.35"))


def combine_risk_scores(
    xgb_risk_score,
    sequence_risk_score,
    xgb_weight=DEFAULT_XGB_WEIGHT,
    sequence_weight=DEFAULT_SEQUENCE_WEIGHT,
):
    if pd.isna(xgb_risk_score):
        raise ValueError("xgb_risk_score is required to compute a combined score")

    xgb_risk_score = float(xgb_risk_score)
    if pd.isna(sequence_risk_score):
        return round(xgb_risk_score, 4), "xgboost_only"

    sequence_risk_score = float(sequence_risk_score)
    total_weight = float(xgb_weight) + float(sequence_weight)
    if total_weight <= 0:
        raise ValueError("Combined risk-score weights must sum to a positive value")

    combined_score = (
        (float(xgb_weight) * xgb_risk_score) + (float(sequence_weight) * sequence_risk_score)
    ) / total_weight
    return round(float(combined_score), 4), "combined"
