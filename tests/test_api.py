import unittest
from types import SimpleNamespace
from unittest.mock import patch

import pandas as pd
from fastapi.testclient import TestClient

from src.api.app import app


def sample_customer_payload():
    return {
        "customer_id": "CUST000001",
        "age": 31,
        "monthly_income": 85000,
        "emi": 22000,
        "credit_card_due": 6000,
        "emi_to_income_ratio": 0.26,
        "credit_utilization": 0.61,
        "missed_payments": 1,
        "salary_delay": 0,
        "job_loss": 0,
        "avg_balance": 92000,
        "balance_drop_ratio": 0.18,
        "atm_withdrawals": 4,
        "spending_change": 0.05,
        "bill_delay_count": 1,
        "account_tenure": 36,
        "total_obligations": 28000,
        "debt_stress_ratio": 0.33,
        "liquidity_buffer": 63000,
        "spending_instability": 0.05,
        "payment_discipline": 0.5,
        "financial_health_score": 0.72,
        "shock_flag": 0,
        "credit_dependency": 3660,
        "early_risk_flag": 0,
        "stability_score": 0.68,
    }


class ApiTests(unittest.TestCase):
    def test_health_endpoint(self):
        with patch("src.api.app.load_model", return_value=SimpleNamespace(feature_importances_=[0.1] * 24)):
            with TestClient(app) as client:
                response = client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_predict_risk_endpoint(self):
        prediction = {
            "customer_id": "CUST000001",
            "risk_score": 0.82,
            "sequence_risk_score": 0.77,
            "risk_prediction": 1,
            "risk_band": "High",
            "top_reason_codes": ["job_loss_signal", "high_emi_burden"],
            "recommended_intervention": "Offer EMI restructuring",
            "persona_label": "Moderate User",
            "persona_signals": ["High debt-to-income stress"],
            "financial_stress_level": "High",
            "intent_label": "high_distress",
            "policy_action": "emi_restructure_review",
            "policy_priority": "critical",
            "recommended_channel": "WhatsApp",
        }

        with patch("src.api.app.load_model", return_value=SimpleNamespace(feature_importances_=[0.1] * 24)):
            with patch("src.api.app.score_records", return_value=[prediction]) as mock_score_records:
                with TestClient(app) as client:
                    response = client.post("/predict-risk", json=sample_customer_payload())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["risk_band"], "High")
        self.assertEqual(response.json()["recommended_intervention"], "Offer EMI restructuring")
        mock_score_records.assert_called_once()

    def test_customers_endpoint(self):
        analysis_df = pd.DataFrame(
            [
                {
                    "customer_id": "CUST000001",
                    "age": 31,
                    "monthly_income": 85000,
                    "account_tenure": 36,
                    "risk_score": 0.82,
                    "sequence_risk_score": 0.77,
                    "risk_band": "High",
                    "persona_label": "Moderate User",
                    "intent_label": "high_distress",
                    "recommended_intervention": "Offer EMI restructuring",
                },
                {
                    "customer_id": "CUST000002",
                    "age": 27,
                    "monthly_income": 64000,
                    "account_tenure": 18,
                    "risk_score": 0.22,
                    "sequence_risk_score": None,
                    "risk_band": "Low",
                    "persona_label": "Stable Planner",
                    "intent_label": "stable",
                    "recommended_intervention": "Send payment reminder",
                },
            ]
        )

        with patch("src.api.app.load_model", return_value=SimpleNamespace(feature_importances_=[0.1] * 24)):
            with patch("src.api.app._build_customer_analysis_frame", return_value=analysis_df):
                with TestClient(app) as client:
                    response = client.get("/customers?limit=2")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["total_customers"], 2)
        self.assertEqual(len(payload["customers"]), 2)
        self.assertEqual(payload["customers"][0]["customer_id"], "CUST000001")

    def test_intervention_recommend_endpoint(self):
        prediction = {
            "customer_id": "CUST000001",
            "risk_score": 0.59,
            "risk_band": "Medium",
            "intent_label": "willing_but_stressed",
            "persona_label": "Moderate User",
            "policy_action": "grace_period_offer",
            "policy_priority": "medium",
            "recommended_channel": "WhatsApp",
            "recommended_intervention": "Offer short grace period",
            "top_reason_codes": ["salary_delay_detected"],
        }

        with patch("src.api.app.load_model", return_value=SimpleNamespace(feature_importances_=[0.1] * 24)):
            with patch("src.api.app.score_records", return_value=[prediction]):
                with TestClient(app) as client:
                    response = client.post("/interventions/recommend", json=sample_customer_payload())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["recommended_channel"], "WhatsApp")
        self.assertEqual(response.json()["recommended_intervention"], "Offer short grace period")

    def test_intervention_trigger_endpoint(self):
        prediction = {
            "customer_id": "CUST000001",
            "risk_score": 0.59,
            "risk_band": "Medium",
            "intent_label": "willing_but_stressed",
            "persona_label": "Moderate User",
            "policy_action": "grace_period_offer",
            "policy_priority": "medium",
            "recommended_channel": "WhatsApp",
            "recommended_intervention": "Offer short grace period",
            "top_reason_codes": ["salary_delay_detected"],
        }
        execution = {
            "execution_id": "exec-123",
            "customer_id": "CUST000001",
            "triggered_at": "2026-03-28T12:00:00+00:00",
            "risk_score": 0.59,
            "risk_band": "Medium",
            "intent_label": "willing_but_stressed",
            "persona_label": "Moderate User",
            "policy_action": "grace_period_offer",
            "policy_priority": "medium",
            "recommended_channel": "WhatsApp",
            "recommended_intervention": "Offer short grace period",
            "delivery_status": "sent",
        }

        with patch("src.api.app.load_model", return_value=SimpleNamespace(feature_importances_=[0.1] * 24)):
            with patch("src.api.app.score_records", return_value=[prediction]):
                with patch("src.api.app.trigger_intervention", return_value=execution):
                    with TestClient(app) as client:
                        response = client.post(
                            "/interventions/trigger",
                            json={
                                "customer": sample_customer_payload(),
                                "override_channel": "WhatsApp",
                            },
                        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["execution_id"], "exec-123")
        self.assertEqual(response.json()["delivery_status"], "sent")


if __name__ == "__main__":
    unittest.main()
