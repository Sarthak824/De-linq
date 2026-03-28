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

    df.to_csv(OUTPUT_PATH, index=False)

    print(f"✅ Advanced features created: {df.shape}")
    print(f"📁 Saved to: {OUTPUT_PATH}")

    return df


if __name__ == "__main__":
    run_feature_engineering()
