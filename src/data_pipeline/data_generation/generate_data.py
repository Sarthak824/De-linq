import os
import random

import numpy as np
import pandas as pd

NUM_CUSTOMERS = 8000
SEED = 42

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
DATA_PATH = os.path.join(BASE_DIR, "data", "raw")
OUTPUT_PATH = os.path.join(DATA_PATH, "synthetic_raw.csv")


def set_random_seed(seed=SEED):
    random.seed(seed)
    np.random.seed(seed)


def clipped_normal(mean, std_dev, min_value, max_value):
    return float(np.clip(np.random.normal(mean, std_dev), min_value, max_value))


def pick_profile():
    return random.choices(
        population=["stable", "vulnerable", "distressed"],
        weights=[0.52, 0.27, 0.21],
        k=1,
    )[0]


def generate_customer(i):
    customer_id = f"CUST{str(i).zfill(6)}"
    profile = pick_profile()
    age = random.randint(21, 60)
    account_tenure = random.randint(1, 120)

    if profile == "stable":
        income = random.randint(45000, 220000)
        emi_ratio = clipped_normal(0.16, 0.035, 0.08, 0.24)
        credit_utilization = clipped_normal(0.17, 0.06, 0.03, 0.36)
        salary_delay = np.random.binomial(1, 0.01)
        job_loss = np.random.binomial(1, 0.01)
        missed_payments = np.random.poisson(0.02)
        bill_delay_count = np.random.poisson(0.08)
        balance_drop_ratio = clipped_normal(0.03, 0.025, 0.00, 0.08)
        atm_withdrawals = int(np.clip(np.random.poisson(1), 0, 6))
        spending_change = clipped_normal(0.08, 0.05, -0.05, 0.16)
        avg_balance_ratio = clipped_normal(2.95, 0.40, 1.7, 5.0)
        card_due_ratio = clipped_normal(0.08, 0.025, 0.02, 0.16)

        # Loan structure
        secured_loans = random.choices([0, 1, 2], [0.7, 0.2, 0.1])[0]
        personal_loans = random.choices([0, 1], [0.9, 0.1])[0]
        gold_loans = random.choices([0, 1], [0.95, 0.05])[0]
        loan_top_up_indicator = np.random.binomial(1, 0.02)

        # ── CRS raw fields (gig-worker income pattern proxies) ────────────────
        active_earning_days = int(np.clip(np.random.normal(24, 3), 18, 30))
        avg_earning_gap_days = round(clipped_normal(1.5, 0.8, 0.5, 4.0), 2)
        weekly_income_base = income / 4.33
        min_weekly_income = round(weekly_income_base * clipped_normal(0.82, 0.08, 0.65, 0.98))
        avg_weekly_income = round(weekly_income_base * clipped_normal(1.0, 0.05, 0.90, 1.10))
        income_std = round(income * clipped_normal(0.06, 0.03, 0.01, 0.15))
        income_sources = random.choices([1, 2, 3, 4], [0.45, 0.35, 0.15, 0.05])[0]

    elif profile == "vulnerable":
        income = random.randint(25000, 160000)
        emi_ratio = clipped_normal(0.45, 0.065, 0.28, 0.64)
        credit_utilization = clipped_normal(0.74, 0.08, 0.55, 0.95)
        salary_delay = np.random.binomial(1, 0.50)
        job_loss = np.random.binomial(1, 0.14)
        missed_payments = np.random.poisson(2.2)
        bill_delay_count = np.random.poisson(2.8)
        balance_drop_ratio = clipped_normal(0.42, 0.085, 0.22, 0.66)
        atm_withdrawals = int(np.clip(np.random.poisson(12), 4, 26))
        spending_change = clipped_normal(-0.14, 0.14, -0.58, 0.08)
        avg_balance_ratio = clipped_normal(0.68, 0.20, 0.12, 1.20)
        card_due_ratio = clipped_normal(0.35, 0.065, 0.16, 0.56)

        # Loan structure
        secured_loans = random.choices([0, 1], [0.8, 0.2])[0]
        personal_loans = random.choices([1, 2, 3], [0.6, 0.3, 0.1])[0]
        gold_loans = random.choices([0, 1], [0.8, 0.2])[0]
        loan_top_up_indicator = np.random.binomial(1, 0.15)

        # ── CRS raw fields ────────────────────────────────────────────────────
        active_earning_days = int(np.clip(np.random.normal(17, 4), 8, 26))
        avg_earning_gap_days = round(clipped_normal(4.0, 1.5, 1.5, 9.0), 2)
        weekly_income_base = income / 4.33
        min_weekly_income = round(weekly_income_base * clipped_normal(0.55, 0.12, 0.30, 0.75))
        avg_weekly_income = round(weekly_income_base * clipped_normal(0.95, 0.08, 0.80, 1.05))
        income_std = round(income * clipped_normal(0.22, 0.07, 0.08, 0.40))
        income_sources = random.choices([1, 2, 3], [0.55, 0.35, 0.10])[0]

    else:
        income = random.randint(18000, 120000)
        emi_ratio = clipped_normal(0.66, 0.06, 0.46, 0.85)
        credit_utilization = clipped_normal(0.96, 0.04, 0.82, 0.99)
        salary_delay = np.random.binomial(1, 0.90)
        job_loss = np.random.binomial(1, 0.36)
        missed_payments = np.random.poisson(4.1)
        bill_delay_count = np.random.poisson(4.8)
        balance_drop_ratio = clipped_normal(0.65, 0.05, 0.46, 0.85)
        atm_withdrawals = int(np.clip(np.random.poisson(16), 6, 36))
        spending_change = clipped_normal(-0.36, 0.12, -0.75, 0.00)
        avg_balance_ratio = clipped_normal(0.20, 0.08, 0.02, 0.48)
        card_due_ratio = clipped_normal(0.50, 0.06, 0.28, 0.72)

        # Loan structure
        secured_loans = random.choices([0, 1], [0.9, 0.1])[0]
        personal_loans = random.choices([2, 3, 4, 5], [0.4, 0.3, 0.2, 0.1])[0]
        gold_loans = random.choices([0, 1, 2], [0.7, 0.2, 0.1])[0]
        loan_top_up_indicator = np.random.binomial(1, 0.35)

        # ── CRS raw fields ────────────────────────────────────────────────────
        active_earning_days = int(np.clip(np.random.normal(8, 3), 2, 18))
        avg_earning_gap_days = round(clipped_normal(9.0, 2.2, 4.0, 16.0), 2)
        weekly_income_base = income / 4.33
        min_weekly_income = round(weekly_income_base * clipped_normal(0.28, 0.12, 0.05, 0.50))
        avg_weekly_income = round(weekly_income_base * clipped_normal(0.85, 0.10, 0.65, 1.00))
        income_std = round(income * clipped_normal(0.48, 0.09, 0.25, 0.70))
        income_sources = random.choices([1, 2], [0.75, 0.25])[0]

    emi = max(2000, int(income * emi_ratio))
    credit_card_due = max(1000, int(income * card_due_ratio))
    avg_balance = max(1000, int(income * avg_balance_ratio))

    return {
        "customer_id": customer_id,
        "age": age,
        "monthly_income": income,
        "emi": emi,
        "credit_card_due": credit_card_due,
        "emi_to_income_ratio": round(emi / income, 2),
        "credit_utilization": round(credit_utilization, 2),
        "missed_payments": int(missed_payments),
        "salary_delay": int(salary_delay),
        "job_loss": int(job_loss),
        "avg_balance": avg_balance,
        "balance_drop_ratio": round(balance_drop_ratio, 2),
        "atm_withdrawals": atm_withdrawals,
        "spending_change": round(spending_change, 2),
        "bill_delay_count": int(bill_delay_count),
        "account_tenure": account_tenure,
        "secured_loans": secured_loans,
        "personal_loans": personal_loans,
        "gold_loans": gold_loans,
        "active_loans": secured_loans + personal_loans + gold_loans,
        "loan_top_up_indicator": int(loan_top_up_indicator),
        "p2p_inflow_count": random.choices([0, 1, 2, 3, 4, 5], [0.5, 0.2, 0.1, 0.1, 0.05, 0.05] if profile == "stable" else [0.1, 0.2, 0.3, 0.2, 0.1, 0.1])[0],
        "small_deposit_count": random.randint(0, 3) if profile == "stable" else random.randint(3, 10),
        "days_before_emi_inflow": random.randint(5, 25) if profile == "stable" else random.randint(0, 5),
        "informal_borrowing_indicator": np.random.binomial(1, 0.05 if profile == "stable" else 0.4),
        "fd_break_flag": np.random.binomial(1, 0.02 if profile == "stable" else 0.25),
        "mf_liquidation_amount": random.randint(0, 5000) if profile == "stable" else random.randint(20000, 200000),
        "gold_loan_active": np.random.binomial(1, 0.05 if profile == "stable" else 0.35),
        "od_utilization_pct": round(random.uniform(0, 10) if profile == "stable" else random.uniform(40, 95), 2),
        "active_earning_days": active_earning_days,
        "total_days": 30,
        "avg_earning_gap_days": avg_earning_gap_days,
        "min_weekly_income": min_weekly_income,
        "avg_weekly_income": avg_weekly_income,
        "income_std": income_std,
        "income_sources": income_sources,
    }


def generate_dataset(n=NUM_CUSTOMERS):
    return pd.DataFrame([generate_customer(i) for i in range(n)])


def run_data_generation(n=NUM_CUSTOMERS, seed=SEED):
    set_random_seed(seed)
    os.makedirs(DATA_PATH, exist_ok=True)

    df = generate_dataset(n)
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"✅ Raw data generated: {df.shape}")
    print(f"📁 Saved to: {OUTPUT_PATH}")

    return df


if __name__ == "__main__":
    run_data_generation()
