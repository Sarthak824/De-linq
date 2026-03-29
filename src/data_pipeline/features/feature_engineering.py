import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
INPUT_PATH = os.path.join(BASE_DIR, "data/processed/synthetic_labeled.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "data/processed/features_advanced.csv")

def run_feature_engineering():
    if not os.path.exists(INPUT_PATH):
        raise FileNotFoundError(f"Labeled dataset not found: {INPUT_PATH}")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df = pd.read_csv(INPUT_PATH)

    if "label" not in df.columns:
        raise ValueError("❌ Label column missing BEFORE feature engineering!")

    df["total_obligations"] = df["emi"] + df["credit_card_due"]
    df["debt_stress_ratio"] = df["total_obligations"] / df["monthly_income"]
    df["liquidity_buffer"] = df["monthly_income"] - df["emi"]
    df["spending_instability"] = abs(df["spending_change"])
    df["payment_discipline"] = 1 / (1 + df["missed_payments"] + df["bill_delay_count"])

    df["financial_health_score"] = (
        (1 - df["credit_utilization"]) * 0.3
        + (1 - df["balance_drop_ratio"]) * 0.3
        + df["payment_discipline"] * 0.4
    )

    df["shock_flag"] = (
        (df["job_loss"] == 1) | (df["balance_drop_ratio"] > 0.4)
    ).astype(int)

    df["credit_dependency"] = df["credit_utilization"] * df["credit_card_due"]

    df["early_risk_flag"] = (
        (df["credit_utilization"] > 0.75) & (df["emi_to_income_ratio"] > 0.35)
    ).astype(int)

    df["stability_score"] = (
        df["account_tenure"] / 120 + df["avg_balance"] / (df["monthly_income"] + 1)
    ) / 2

    # New 2nd Layer Model: Credit Exposure Analyzer
    df["credit_exposure_score"] = (
        (df["active_loans"] / 5) * 0.3
        + (df["loan_top_up_indicator"] * 0.2)
        + (df["emi_to_income_ratio"] * 0.3)
        + (df["credit_utilization"] * 0.2)
    ).clip(0, 1)

    # 2nd Layer Model: Hidden Distress Behavior Engine
    df["hidden_distress_score"] = (
        (df["p2p_inflow_count"] / 5) * 0.3
        + (df["small_deposit_count"] / 10) * 0.2
        + (1 - (df["days_before_emi_inflow"] / 25)) * 0.4
        + (df["informal_borrowing_indicator"] * 0.1)
    ).clip(0, 1)

    # 2nd Layer Model: Liquidity Stress & Asset Utilization Engine
    df["liquidity_stress_score"] = (
        (df["fd_break_flag"] * 0.4)
        + (df["gold_loan_active"] * 0.2)
        + ((df["mf_liquidation_amount"] / 200000) * 0.2)
        + ((df["od_utilization_pct"] / 100) * 0.2)
    ).clip(0, 1)

    # Cash Flow Reliability Score (CRS) Enrichment
    from src.intelligence.cash_flow_reliability import batch_compute_crs
    df = batch_compute_crs(df)

    df.to_csv(OUTPUT_PATH, index=False)

    print(f"✅ Advanced features created: {df.shape}")
    print(f"📁 Saved to: {OUTPUT_PATH}")

    return df


if __name__ == "__main__":
    run_feature_engineering()
