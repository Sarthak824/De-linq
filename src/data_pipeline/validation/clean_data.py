import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
INPUT_PATH = os.path.join(BASE_DIR, "data/processed/features_advanced.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "data/processed/final_cleaned.csv")

def run_cleaning():
    if not os.path.exists(INPUT_PATH):
        raise FileNotFoundError(f"Feature dataset not found: {INPUT_PATH}")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df = pd.read_csv(INPUT_PATH)

    df = df[df["monthly_income"] > 0]
    df = df[(df["credit_utilization"] >= 0) & (df["credit_utilization"] <= 1)]
    df = df[df["emi_to_income_ratio"] <= 1]

    df["atm_withdrawals"] = df["atm_withdrawals"].clip(0, 50)
    df["bill_delay_count"] = df["bill_delay_count"].clip(0, 10)
    df = df.fillna(0)
    df = df.drop_duplicates(subset=["customer_id"])

    if "label" not in df.columns:
        raise ValueError("❌ Label lost during cleaning!")

    df.to_csv(OUTPUT_PATH, index=False)

    print(f"✅ Clean dataset ready: {df.shape}")
    print(f"📁 Saved to: {OUTPUT_PATH}")

    return df


if __name__ == "__main__":
    run_cleaning()
