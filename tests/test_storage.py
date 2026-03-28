import os
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

from src.models.benchmark_models import run_benchmark
from src.storage import database


class StorageTests(unittest.TestCase):
    def test_database_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = os.path.join(tmp_dir, "delinq.sqlite3")
            profiles_df = pd.DataFrame(
                [
                    {
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
                        "label": 0,
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
                ]
            )
            predictions_df = pd.DataFrame(
                [
                    {
                        "customer_id": "CUST000001",
                        "risk_score": 0.82,
                        "xgb_risk_score": 0.79,
                        "sequence_risk_score": 0.77,
                        "score_source": "combined",
                        "risk_prediction": 1,
                        "risk_band": "High",
                        "top_reason_codes": "job_loss_signal, high_emi_burden",
                        "recommended_intervention": "Offer EMI restructuring",
                        "persona_label": "Moderate User",
                        "persona_signals": "High debt-to-income stress",
                        "financial_stress_level": "High",
                        "intent_label": "high_distress",
                        "policy_action": "emi_restructure_review",
                        "policy_priority": "critical",
                        "recommended_channel": "WhatsApp",
                    }
                ]
            )
            intervention_event = {
                "execution_id": "exec-123",
                "customer_id": "CUST000001",
                "triggered_at": "2026-03-28T12:00:00+00:00",
                "risk_score": 0.82,
                "risk_band": "High",
                "intent_label": "high_distress",
                "persona_label": "Moderate User",
                "policy_action": "emi_restructure_review",
                "policy_priority": "critical",
                "recommended_channel": "WhatsApp",
                "recommended_intervention": "Offer EMI restructuring",
                "delivery_status": "sent",
            }

            database.save_customer_profiles(profiles_df, db_path=db_path)
            database.save_customer_predictions(predictions_df, db_path=db_path)
            database.append_intervention_event(intervention_event, db_path=db_path)

            analysis_df = database.load_customer_analysis(db_path=db_path)
            history_df = database.load_intervention_history(customer_id="CUST000001", db_path=db_path)

            self.assertEqual(len(analysis_df), 1)
            self.assertEqual(analysis_df.iloc[0]["risk_band"], "High")
            self.assertEqual(analysis_df.iloc[0]["xgb_risk_score"], 0.79)
            self.assertEqual(analysis_df.iloc[0]["score_source"], "combined")
            self.assertEqual(len(history_df), 1)
            self.assertEqual(history_df.iloc[0]["delivery_status"], "sent")

    def test_benchmark_skips_lightgbm_when_not_installed(self):
        with patch("src.models.benchmark_models.run_xgboost_training"):
            with patch(
                "src.models.benchmark_models._load_metrics",
                side_effect=[{"roc_auc": 0.91}, {"roc_auc": 0.88}],
            ):
                with patch(
                    "src.models.benchmark_models.run_lightgbm_training",
                    side_effect=RuntimeError("LightGBM is not installed"),
                ):
                    with patch("src.models.benchmark_models.run_combined_evaluation"):
                        results = run_benchmark()

        self.assertEqual(results["xgboost"]["roc_auc"], 0.91)
        self.assertEqual(results["lightgbm"]["status"], "skipped")
        self.assertEqual(results["combined"]["roc_auc"], 0.88)


if __name__ == "__main__":
    unittest.main()
