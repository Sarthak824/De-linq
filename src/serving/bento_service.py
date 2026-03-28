import os
import sys
from typing import Optional

import bentoml
from pydantic import BaseModel, ConfigDict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.inference.predict import load_model, score_records


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
    sequence_risk_score: Optional[float] = None


class BatchPredictionRequest(BaseModel):
    customers: list[CustomerFeatures]


@bentoml.service(
    traffic={"timeout": 60},
)
class RiskScoringService:
    def __init__(self):
        self.model = load_model()

    @bentoml.api
    def health(self) -> dict:
        return {"status": "ok", "model": "xgboost"}

    @bentoml.api
    def predict(self, customer: CustomerFeatures) -> dict:
        return score_records([customer.model_dump()], self.model)[0]

    @bentoml.api
    def batch_predict(self, request: BatchPredictionRequest) -> dict:
        predictions = score_records(
            [customer.model_dump() for customer in request.customers],
            self.model,
        )
        return {"predictions": predictions}
