import os
import sys
from contextlib import asynccontextmanager
from typing import List, Optional

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.inference.predict import (
    INPUT_PATH,
    build_portfolio_summary,
    load_model,
    run_batch_inference,
    score_records,
)
from src.interventions.orchestrator import (
    get_intervention_history,
    recommend_intervention_payload,
    trigger_intervention,
)
from src.models.model_config import FEATURE_COLUMNS
from src.storage.database import (
    load_customer_analysis,
    load_customer_predictions as load_customer_predictions_db,
    load_customer_profiles as load_customer_profiles_db,
)

PREDICTIONS_PATH = os.path.join(BASE_DIR, "data", "output", "customer_risk_predictions.csv")


class CustomerFeatures(BaseModel):
    model_config = ConfigDict(extra="ignore")

    customer_id: Optional[str] = None
    age: int
    monthly_income: float
    emi: float
    credit_card_due: float
    emi_to_income_ratio: float
    credit_utilization: float
    missed_payments: int
    salary_delay: int
    job_loss: int
    avg_balance: float
    balance_drop_ratio: float
    atm_withdrawals: int
    spending_change: float
    bill_delay_count: int
    account_tenure: int
    total_obligations: float
    debt_stress_ratio: float
    liquidity_buffer: float
    spending_instability: float
    payment_discipline: float
    financial_health_score: float
    shock_flag: int
    credit_dependency: float
    early_risk_flag: int
    stability_score: float
    secured_loans: Optional[int] = 0
    personal_loans: Optional[int] = 0
    gold_loans: Optional[int] = 0
    active_loans: Optional[int] = 0
    loan_top_up_indicator: Optional[int] = 0
    credit_exposure_score: Optional[float] = 0.0


class PredictionResponse(BaseModel):
    customer_id: Optional[str]
    risk_score: float
    sequence_risk_score: Optional[float] = None
    risk_prediction: int
    risk_band: str
    top_reason_codes: List[str]
    recommended_intervention: str
    persona_label: Optional[str] = None
    persona_signals: List[str] = []
    financial_stress_level: Optional[str] = None
    intent_label: Optional[str] = None
    policy_action: Optional[str] = None
    policy_priority: Optional[str] = None
    recommended_channel: Optional[str] = None
    credit_exposure_level: Optional[str] = None
    credit_exposure_message: Optional[str] = None
    debt_structure: Optional[str] = None
    active_loan_summary: Optional[str] = None
    exposure_score: Optional[float] = 0.0
    hidden_distress_level: Optional[str] = None
    hidden_distress_message: Optional[str] = None
    liquidity_pattern: Optional[str] = None
    patchwork_index: Optional[float] = 0.0
    emi_buffer_days: Optional[int] = 0


class BatchPredictionRequest(BaseModel):
    customers: List[CustomerFeatures]


class BatchPredictionResponse(BaseModel):
    predictions: List[PredictionResponse]


class PortfolioSummaryResponse(BaseModel):
    total_customers: int
    average_risk_score: float
    risk_band_counts: dict
    intervention_counts: dict


class InterventionRecommendationResponse(BaseModel):
    customer_id: Optional[str]
    risk_score: float
    risk_band: str
    intent_label: Optional[str] = None
    persona_label: Optional[str] = None
    policy_action: Optional[str] = None
    policy_priority: Optional[str] = None
    recommended_channel: Optional[str] = None
    recommended_intervention: str
    top_reason_codes: List[str]


class InterventionTriggerRequest(BaseModel):
    customer: CustomerFeatures
    override_channel: Optional[str] = None
    override_action: Optional[str] = None


class InterventionExecutionResponse(BaseModel):
    execution_id: str
    customer_id: str
    triggered_at: str
    risk_score: Optional[float] = None
    risk_band: Optional[str] = None
    intent_label: Optional[str] = None
    persona_label: Optional[str] = None
    policy_action: str
    policy_priority: Optional[str] = None
    recommended_channel: str
    recommended_intervention: str
    delivery_status: str


class InterventionHistoryResponse(BaseModel):
    customer_id: str
    history: List[InterventionExecutionResponse]


class CustomerListItem(BaseModel):
    customer_id: str
    age: int
    monthly_income: float
    account_tenure: int
    risk_score: Optional[float] = None
    sequence_risk_score: Optional[float] = None
    risk_band: Optional[str] = None
    persona_label: Optional[str] = None
    intent_label: Optional[str] = None
    recommended_intervention: Optional[str] = None


class CustomerListResponse(BaseModel):
    total_customers: int
    customers: List[CustomerListItem]


class CustomerDetailResponse(BaseModel):
    customer_id: str
    profile: dict
    prediction: Optional[dict] = None


class CustomerAnalysisResponse(BaseModel):
    customer_id: str
    profile: dict
    prediction: Optional[dict] = None
    intervention_history: List[InterventionExecutionResponse]


class TopRisksResponse(BaseModel):
    customers: List[dict]


class DistributionResponse(BaseModel):
    distribution: dict


class ModelInfoResponse(BaseModel):
    model_name: str
    artifact_path: str
    feature_count: int
    feature_columns: List[str]


class FeatureImportanceItem(BaseModel):
    feature: str
    importance: float


class FeatureImportanceResponse(BaseModel):
    feature_importance: List[FeatureImportanceItem]


def _load_customer_profiles():
    profiles_df = load_customer_profiles_db()
    if not profiles_df.empty:
        return profiles_df
    return pd.read_csv(INPUT_PATH)


def _load_customer_predictions():
    predictions_df = load_customer_predictions_db()
    if not predictions_df.empty:
        return predictions_df
    if not os.path.exists(PREDICTIONS_PATH):
        return pd.DataFrame()
    return pd.read_csv(PREDICTIONS_PATH)


def _load_intervention_history_df():
    history_path = os.path.join(BASE_DIR, "data", "output", "intervention_history.csv")
    if not os.path.exists(history_path):
        return pd.DataFrame()
    return pd.read_csv(history_path)


def _build_customer_analysis_frame():
    analysis_df = load_customer_analysis()
    if not analysis_df.empty:
        return analysis_df

    profiles_df = _load_customer_profiles()
    predictions_df = _load_customer_predictions()

    if predictions_df.empty:
        return profiles_df

    return profiles_df.merge(predictions_df, on="customer_id", how="left")


def _get_customer_record(customer_id: str):
    analysis_df = _build_customer_analysis_frame()
    matches = analysis_df[analysis_df["customer_id"] == customer_id]
    if matches.empty:
        return None
    return matches.iloc[0].to_dict()


def _split_customer_payload(record: dict):
    prediction_keys = {
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
    }

    profile = {}
    prediction = {}

    for key, value in record.items():
        if key == "label":
            continue
        if key in prediction_keys:
            if pd.notna(value):
                prediction[key] = value
        else:
            if pd.notna(value):
                profile[key] = value

    if "top_reason_codes" in prediction and isinstance(prediction["top_reason_codes"], str):
        prediction["top_reason_codes"] = [item.strip() for item in prediction["top_reason_codes"].split(",") if item.strip()]
    if "persona_signals" in prediction and isinstance(prediction["persona_signals"], str):
        prediction["persona_signals"] = [item.strip() for item in prediction["persona_signals"].split(",") if item.strip()]

    return profile, prediction or None


def _load_model_feature_importance(model):
    if not hasattr(model, "feature_importances_"):
        return []

    importance_pairs = []
    for feature, importance in zip(FEATURE_COLUMNS, model.feature_importances_):
        importance_pairs.append(
            {
                "feature": feature,
                "importance": round(float(importance), 6),
            }
        )

    importance_pairs.sort(key=lambda item: item["importance"], reverse=True)
    return importance_pairs


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model = load_model()
    yield


app = FastAPI(title="DelinqAI Risk API", version="1.0.0", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/customers", response_model=CustomerListResponse)
def get_customers(limit: int = 100):
    try:
        analysis_df = _build_customer_analysis_frame().head(limit)
        customers = []

        for _, row in analysis_df.iterrows():
            customers.append(
                {
                    "customer_id": row["customer_id"],
                    "age": int(row["age"]),
                    "monthly_income": float(row["monthly_income"]),
                    "account_tenure": int(row["account_tenure"]),
                    "risk_score": float(row["risk_score"]) if "risk_score" in row and pd.notna(row["risk_score"]) else None,
                    "sequence_risk_score": float(row["sequence_risk_score"]) if "sequence_risk_score" in row and pd.notna(row["sequence_risk_score"]) else None,
                    "risk_band": row["risk_band"] if "risk_band" in row and pd.notna(row["risk_band"]) else None,
                    "persona_label": row["persona_label"] if "persona_label" in row and pd.notna(row["persona_label"]) else None,
                    "intent_label": row["intent_label"] if "intent_label" in row and pd.notna(row["intent_label"]) else None,
                    "recommended_intervention": row["recommended_intervention"] if "recommended_intervention" in row and pd.notna(row["recommended_intervention"]) else None,
                }
            )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"total_customers": int(len(_build_customer_analysis_frame())), "customers": customers}


@app.get("/customers/{customer_id}", response_model=CustomerDetailResponse)
def get_customer(customer_id: str):
    try:
        record = _get_customer_record(customer_id)
        if record is None:
            raise HTTPException(status_code=404, detail=f"Customer not found: {customer_id}")

        profile, prediction = _split_customer_payload(record)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"customer_id": customer_id, "profile": profile, "prediction": prediction}


@app.get("/customers/{customer_id}/analysis", response_model=CustomerAnalysisResponse)
def get_customer_analysis(customer_id: str):
    try:
        record = _get_customer_record(customer_id)
        if record is None:
            raise HTTPException(status_code=404, detail=f"Customer not found: {customer_id}")

        profile, prediction = _split_customer_payload(record)
        history = get_intervention_history(customer_id)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "customer_id": customer_id,
        "profile": profile,
        "prediction": prediction,
        "intervention_history": history,
    }


@app.get("/analytics/top-risks", response_model=TopRisksResponse)
def analytics_top_risks(limit: int = 10):
    try:
        predictions_df = _load_customer_predictions()
        if predictions_df.empty:
            return {"customers": []}

        top_df = predictions_df.sort_values("risk_score", ascending=False).head(limit)
        customers = top_df.to_dict(orient="records")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"customers": customers}


@app.get("/analytics/reason-distribution", response_model=DistributionResponse)
def analytics_reason_distribution():
    try:
        predictions_df = _load_customer_predictions()
        reason_counts = {}

        for reasons in predictions_df.get("top_reason_codes", pd.Series(dtype=str)).fillna(""):
            for reason in [item.strip() for item in str(reasons).split(",") if item.strip()]:
                reason_counts[reason] = reason_counts.get(reason, 0) + 1
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"distribution": reason_counts}


@app.get("/analytics/intervention-summary", response_model=DistributionResponse)
def analytics_intervention_summary():
    try:
        predictions_df = _load_customer_predictions()
        history_df = _load_intervention_history_df()

        distribution = {
            "recommended_interventions": predictions_df["recommended_intervention"].value_counts().to_dict()
            if not predictions_df.empty
            else {},
            "triggered_interventions": history_df["recommended_intervention"].value_counts().to_dict()
            if not history_df.empty
            else {},
            "delivery_status": history_df["delivery_status"].value_counts().to_dict()
            if not history_df.empty
            else {},
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"distribution": distribution}


@app.get("/model/info", response_model=ModelInfoResponse)
def model_info():
    return {
        "model_name": "XGBoost Risk Classifier",
        "artifact_path": os.path.join(BASE_DIR, "artifacts", "xgb_model.pkl"),
        "feature_count": len(FEATURE_COLUMNS),
        "feature_columns": FEATURE_COLUMNS,
    }


@app.get("/model/feature-importance", response_model=FeatureImportanceResponse)
def model_feature_importance():
    try:
        feature_importance = _load_model_feature_importance(app.state.model)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"feature_importance": feature_importance}


@app.post("/predict-risk", response_model=PredictionResponse)
def predict_risk(customer: CustomerFeatures):
    try:
        predictions = score_records([customer.model_dump()], app.state.model)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return predictions[0]


@app.post("/batch-predict", response_model=BatchPredictionResponse)
def batch_predict(request: BatchPredictionRequest):
    try:
        predictions = score_records(
            [customer.model_dump() for customer in request.customers],
            app.state.model,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"predictions": predictions}


@app.post("/interventions/recommend", response_model=InterventionRecommendationResponse)
def intervention_recommend(customer: CustomerFeatures):
    try:
        prediction = score_records([customer.model_dump()], app.state.model)[0]
        recommendation = recommend_intervention_payload(prediction)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return recommendation


@app.post("/interventions/trigger", response_model=InterventionExecutionResponse)
def intervention_trigger(request: InterventionTriggerRequest):
    try:
        prediction = score_records([request.customer.model_dump()], app.state.model)[0]
        execution = trigger_intervention(
            prediction,
            override_channel=request.override_channel,
            override_action=request.override_action,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return execution


@app.get("/interventions/history/{customer_id}", response_model=InterventionHistoryResponse)
def intervention_history(customer_id: str):
    try:
        history = get_intervention_history(customer_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"customer_id": customer_id, "history": history}


@app.get("/portfolio-summary", response_model=PortfolioSummaryResponse)
def portfolio_summary():
    try:
        scored_df = run_batch_inference(input_path=INPUT_PATH)
        summary = build_portfolio_summary(scored_df)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return summary
