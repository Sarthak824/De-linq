import os
import random

import numpy as np
import pandas as pd

SEED = 42
LABEL_NOISE_STD = 0.03

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
INPUT_PATH = os.path.join(BASE_DIR, "data", "raw", "synthetic_raw.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "processed")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "synthetic_labeled.csv")


def set_random_seed(seed=SEED):
    random.seed(seed)
    np.random.seed(seed)


def compute_latent_risk(row):
    latent_risk = -2.35

    latent_risk += 2.5 * row["credit_utilization"]
    latent_risk += 2.1 * row["emi_to_income_ratio"]
    latent_risk += 1.75 * row["balance_drop_ratio"]
    latent_risk += 0.38 * min(row["missed_payments"], 4)
    latent_risk += 0.24 * min(row["bill_delay_count"], 5)
    latent_risk += 0.02 * min(row["atm_withdrawals"], 20)

    if row["salary_delay"] == 1:
        latent_risk += 0.90

    if row["job_loss"] == 1:
        latent_risk += 1.55

    if row["credit_utilization"] > 0.8 and row["balance_drop_ratio"] > 0.35:
        latent_risk += 1.22

    if row["emi_to_income_ratio"] > 0.45 and row["bill_delay_count"] >= 2:
        latent_risk += 1.12

    if row["salary_delay"] == 1 and row["missed_payments"] >= 2:
        latent_risk += 1.02

    if row["avg_balance"] < 0.45 * row["monthly_income"]:
        latent_risk += 0.60

    if row["account_tenure"] > 60:
        latent_risk -= 0.18

    if row["spending_change"] < -0.2:
        latent_risk += 0.38

    return latent_risk


def assign_label(row, noise_std=LABEL_NOISE_STD):
    latent_risk = compute_latent_risk(row)
    if noise_std > 0:
        latent_risk += np.random.normal(0, noise_std)
    prob_default = 1 / (1 + np.exp(-latent_risk))
    return int(random.random() < prob_default)


def run_labeling(seed=SEED):
    if not os.path.exists(INPUT_PATH):
        raise FileNotFoundError(f"Raw dataset not found: {INPUT_PATH}")

    set_random_seed(seed)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    df = pd.read_csv(INPUT_PATH)
    df["latent_risk_score"] = df.apply(compute_latent_risk, axis=1)
    noise = np.random.normal(0, LABEL_NOISE_STD, len(df)) if LABEL_NOISE_STD > 0 else 0
    df["default_probability"] = 1 / (1 + np.exp(-(df["latent_risk_score"] + noise)))
    df["label"] = df.apply(assign_label, axis=1)
    df.to_csv(OUTPUT_PATH, index=False)

    label_counts = df["label"].value_counts().sort_index()
    positive_rate = df["label"].mean()

    print(f"✅ Labeled data created: {df.shape}")
    print(f"📁 Saved to: {OUTPUT_PATH}")
    print("📊 Label distribution:")
    print(label_counts.to_string())
    print(f"📈 Positive rate: {positive_rate:.2%}")

    return df


if __name__ == "__main__":
    run_labeling()
