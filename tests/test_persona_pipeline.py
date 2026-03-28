import unittest

import pandas as pd

from src.interventions.recommend import recommend_intervention
from src.persona.persona_builder import build_persona, generate_personas
from src.policy.decision_engine import apply_policy_engine


def sample_row(**overrides):
    row = {
        "customer_id": "CUST_TEST_001",
        "risk_score": 0.82,
        "monthly_income": 85000,
        "emi": 22000,
        "credit_card_due": 6000,
        "emi_to_income_ratio": 0.26,
        "credit_utilization": 0.81,
        "missed_payments": 1,
        "salary_delay": 1,
        "job_loss": 0,
        "avg_balance": 92000,
        "balance_drop_ratio": 0.18,
        "atm_withdrawals": 4,
        "spending_change": -0.6,
        "bill_delay_count": 2,
        "account_tenure": 36,
        "total_obligations": 28000,
        "debt_stress_ratio": 0.71,
        "liquidity_buffer": 63000,
        "spending_instability": 0.6,
        "payment_discipline": 0.5,
        "financial_health_score": 0.72,
        "shock_flag": 0,
        "credit_dependency": 3660,
        "early_risk_flag": 0,
        "stability_score": 0.68,
        "credit_exposure_level": "Low",
        "hidden_distress_level": "Low",
        "loan_top_up_indicator": 0,
        "liquidity_pattern": "Stable",
        "intent_label": "stable",
        "risk_band": "High",
    }
    row.update(overrides)
    return row


class PersonaPipelineTests(unittest.TestCase):
    def test_build_persona_assigns_declining_gig_worker(self):
        persona = build_persona(sample_row())

        self.assertEqual(persona["persona_label"], "Declining Gig Worker")
        self.assertIn("High income variability detected", persona["key_signals"])
        self.assertIn("Irregular salary pattern detected", persona["key_signals"])

    def test_build_persona_uses_credit_dependency_level_in_rule(self):
        persona = build_persona(
            sample_row(
                spending_change=0.02,
                spending_instability=0.02,
                salary_delay=0,
                risk_score=0.76,
                debt_stress_ratio=0.72,
                credit_utilization=0.84,
                hidden_distress_level="Low",
                credit_exposure_level="Low",
            )
        )

        self.assertEqual(persona["persona_label"], "Credit Dependent Stressed User")

    def test_generate_personas_preserves_expected_output_columns(self):
        df = pd.DataFrame([sample_row()])

        output_df = generate_personas(df)

        for column in [
            "persona_json",
            "persona_label",
            "persona_signals",
            "financial_stress_level",
            "income_stability",
            "spending_behavior",
            "credit_dependency_level",
            "persona_confidence_score",
        ]:
            self.assertIn(column, output_df.columns)

    def test_policy_and_intervention_for_declining_gig_worker(self):
        df = pd.DataFrame(
            [
                {
                    "customer_id": "CUST_TEST_001",
                    "risk_band": "High",
                    "intent_label": "stable",
                    "persona_label": "Declining Gig Worker",
                    "financial_stress_level": "High",
                }
            ]
        )

        policy_df = apply_policy_engine(df)
        row = policy_df.iloc[0].to_dict()
        recommendation = recommend_intervention(row, 0.91)

        self.assertEqual(row["policy_action"], "temporary_relief_review")
        self.assertEqual(row["recommended_channel"], "WhatsApp")
        self.assertEqual(recommendation, "Offer temporary payment relief")

    def test_policy_and_intervention_for_volatile_gig_worker(self):
        df = pd.DataFrame(
            [
                {
                    "customer_id": "CUST_TEST_002",
                    "risk_band": "High",
                    "intent_label": "stable",
                    "persona_label": "Volatile Gig Worker",
                    "financial_stress_level": "High",
                }
            ]
        )

        policy_df = apply_policy_engine(df)
        row = policy_df.iloc[0].to_dict()
        recommendation = recommend_intervention(row, 0.84)

        self.assertEqual(row["policy_action"], "dynamic_emi_review")
        self.assertEqual(row["recommended_channel"], "WhatsApp")
        self.assertEqual(recommendation, "Review dynamic EMI adjustment")

    def test_policy_and_intervention_for_stable_gig_worker(self):
        df = pd.DataFrame(
            [
                {
                    "customer_id": "CUST_TEST_003",
                    "risk_band": "Medium",
                    "intent_label": "stable",
                    "persona_label": "Stable Gig Worker",
                    "financial_stress_level": "Moderate",
                }
            ]
        )

        policy_df = apply_policy_engine(df)
        row = policy_df.iloc[0].to_dict()
        recommendation = recommend_intervention(row, 0.58)

        self.assertEqual(row["policy_action"], "flexible_payment_window")
        self.assertEqual(row["recommended_channel"], "App")
        self.assertEqual(recommendation, "Offer flexible payment window")


if __name__ == "__main__":
    unittest.main()
