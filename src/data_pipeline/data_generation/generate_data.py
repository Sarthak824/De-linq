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
        weights=[0.58, 0.27, 0.15],
        k=1,
    )[0]


def generate_customer(i):
    customer_id = f"CUST{str(i).zfill(6)}"
    profile = pick_profile()
    age = random.randint(21, 60)
    account_tenure = random.randint(1, 120)

    if profile == "stable":
        income = random.randint(45000, 220000)
        emi_ratio = clipped_normal(0.23, 0.07, 0.08, 0.38)
        credit_utilization = clipped_normal(0.33, 0.12, 0.08, 0.60)
        salary_delay = np.random.binomial(1, 0.08)
        job_loss = np.random.binomial(1, 0.01)
        missed_payments = np.random.poisson(0.3)
        bill_delay_count = np.random.poisson(0.6)
        balance_drop_ratio = clipped_normal(0.10, 0.07, 0.00, 0.25)
        atm_withdrawals = int(np.clip(np.random.poisson(4), 0, 12))
        spending_change = clipped_normal(0.04, 0.10, -0.20, 0.25)
        avg_balance_ratio = clipped_normal(2.1, 0.6, 0.9, 4.0)
        card_due_ratio = clipped_normal(0.14, 0.06, 0.03, 0.30)
        
        # Loan structure
        secured_loans = random.choices([0, 1, 2], [0.7, 0.2, 0.1])[0]
        personal_loans = random.choices([0, 1], [0.9, 0.1])[0]
        gold_loans = random.choices([0, 1], [0.95, 0.05])[0]
        loan_top_up_indicator = np.random.binomial(1, 0.02)
        
    elif profile == "vulnerable":
        income = random.randint(25000, 160000)
        emi_ratio = clipped_normal(0.36, 0.08, 0.18, 0.55)
        credit_utilization = clipped_normal(0.61, 0.12, 0.35, 0.88)
        salary_delay = np.random.binomial(1, 0.34)
        job_loss = np.random.binomial(1, 0.06)
        missed_payments = np.random.poisson(1.2)
        bill_delay_count = np.random.poisson(1.8)
        balance_drop_ratio = clipped_normal(0.29, 0.11, 0.08, 0.52)
        atm_withdrawals = int(np.clip(np.random.poisson(8), 1, 20))
        spending_change = clipped_normal(-0.06, 0.18, -0.45, 0.30)
        avg_balance_ratio = clipped_normal(1.0, 0.35, 0.25, 1.8)
        card_due_ratio = clipped_normal(0.25, 0.08, 0.08, 0.45)
        
        # Loan structure
        secured_loans = random.choices([0, 1], [0.8, 0.2])[0]
        personal_loans = random.choices([1, 2, 3], [0.6, 0.3, 0.1])[0]
        gold_loans = random.choices([0, 1], [0.8, 0.2])[0]
        loan_top_up_indicator = np.random.binomial(1, 0.15)
        
    else:
        income = random.randint(18000, 120000)
        emi_ratio = clipped_normal(0.49, 0.10, 0.28, 0.70)
        credit_utilization = clipped_normal(0.84, 0.10, 0.58, 0.99)
        salary_delay = np.random.binomial(1, 0.68)
        job_loss = np.random.binomial(1, 0.18)
        missed_payments = np.random.poisson(2.5)
        bill_delay_count = np.random.poisson(3.2)
        balance_drop_ratio = clipped_normal(0.47, 0.09, 0.22, 0.70)
        atm_withdrawals = int(np.clip(np.random.poisson(12), 2, 28))
        spending_change = clipped_normal(-0.18, 0.20, -0.60, 0.22)
        avg_balance_ratio = clipped_normal(0.42, 0.18, 0.05, 0.95)
        card_due_ratio = clipped_normal(0.34, 0.10, 0.12, 0.60)
        
        # Loan structure
        secured_loans = random.choices([0, 1], [0.9, 0.1])[0]
        personal_loans = random.choices([2, 3, 4, 5], [0.4, 0.3, 0.2, 0.1])[0]
        gold_loans = random.choices([0, 1, 2], [0.7, 0.2, 0.1])[0]
        loan_top_up_indicator = np.random.binomial(1, 0.35)

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
