import os
import random

import numpy as np
import pandas as pd

SEED = 42
TIMELINE_DAYS = 60
TIME_STEPS = 20
PREDICTION_HORIZON = 10
LABEL_GAP_DAYS = 3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
INPUT_PATH = os.path.join(BASE_DIR, "data", "processed", "synthetic_labeled.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "sequences")
DAILY_EVENTS_PATH = os.path.join(OUTPUT_DIR, "customer_daily_events.csv")
SEQUENCE_LABELS_PATH = os.path.join(OUTPUT_DIR, "customer_sequence_labels.csv")
LSTM_WINDOWS_PATH = os.path.join(OUTPUT_DIR, "lstm_windows.npz")

SEQUENCE_FEATURES = [
    "balance",
    "daily_spend",
    "atm_withdrawal_amount",
    "credit_utilization",
    "salary_credit_flag",
    "bill_paid_flag",
    "emi_paid_flag",
    "app_activity_flag",
    "days_since_salary_credit",
    "days_since_last_payment",
    "daily_cash_inflow",
    "daily_cash_outflow",
]


def set_random_seed(seed=SEED):
    random.seed(seed)
    np.random.seed(seed)


def infer_profile(row):
    risk_signal = (
        1.6 * float(row["credit_utilization"])
        + 1.2 * float(row["emi_to_income_ratio"])
        + 0.9 * float(row["balance_drop_ratio"])
        + 0.28 * min(float(row["missed_payments"]), 4)
        + 0.18 * min(float(row["bill_delay_count"]), 5)
        + 0.55 * float(row["salary_delay"])
        + 0.85 * float(row["job_loss"])
        + np.random.normal(0, 0.22)
    )

    if risk_signal >= 2.65:
        return "distressed"
    if risk_signal >= 1.45:
        return "vulnerable"
    return "stable"


def build_customer_behavior(row):
    profile = infer_profile(row)

    if profile == "stable":
        return {
            "profile": profile,
            "spend_ratio": float(np.random.uniform(0.39, 0.46)),
            "atm_ratio": float(np.random.uniform(0.14, 0.2)),
            "app_activity_base": float(np.random.uniform(0.8, 0.92)),
            "worsening_factor": float(np.random.uniform(0.08, 0.28)),
            "recovery_factor": float(np.random.uniform(0.05, 0.2)),
            "salary_delay_days": int(np.random.choice([0, 1], p=[0.85, 0.15])) if row["salary_delay"] else 0,
            "shock_probability": 0.12,
        }
    if profile == "vulnerable":
        return {
            "profile": profile,
            "spend_ratio": float(np.random.uniform(0.45, 0.53)),
            "atm_ratio": float(np.random.uniform(0.18, 0.26)),
            "app_activity_base": float(np.random.uniform(0.58, 0.76)),
            "worsening_factor": float(np.random.uniform(0.32, 0.65)),
            "recovery_factor": float(np.random.uniform(0.08, 0.28)),
            "salary_delay_days": int(np.random.choice([0, 1, 2, 3], p=[0.2, 0.35, 0.3, 0.15])) if row["salary_delay"] else int(np.random.choice([0, 1], p=[0.8, 0.2])),
            "shock_probability": 0.3,
        }
    return {
        "profile": profile,
        "spend_ratio": float(np.random.uniform(0.5, 0.58)),
        "atm_ratio": float(np.random.uniform(0.23, 0.32)),
        "app_activity_base": float(np.random.uniform(0.38, 0.58)),
        "worsening_factor": float(np.random.uniform(0.55, 0.95)),
        "recovery_factor": float(np.random.uniform(0.03, 0.18)),
        "salary_delay_days": int(np.random.choice([1, 2, 3, 4, 5], p=[0.15, 0.2, 0.25, 0.25, 0.15])),
        "shock_probability": 0.5,
    }


def simulate_customer_events(row, timeline_days=TIMELINE_DAYS):
    behavior = build_customer_behavior(row)
    monthly_income = float(row["monthly_income"])
    avg_balance = float(row["avg_balance"])
    starting_balance = max(avg_balance * (1 - float(row["balance_drop_ratio"]) * 0.35), 2500)
    daily_spend_base = monthly_income * behavior["spend_ratio"] / 30
    daily_atm_base = max(row["atm_withdrawals"], 1) * behavior["atm_ratio"]

    bill_due_day = 12 + (hash(row["customer_id"]) % 3)
    emi_due_day = 18 + (hash(row["customer_id"]) % 4)
    salary_cycle_day = 0
    salary_cycle_day_2 = 30

    worsening_start = timeline_days // 2
    credit_util = float(row["credit_utilization"]) * 0.92
    balance = starting_balance
    days_since_salary_credit = 0
    days_since_last_payment = 0
    recent_payment_stress = 0.0
    shock_start_day = None
    shock_end_day = None
    shock_severity = 0.0
    events = []

    if np.random.random() < behavior["shock_probability"]:
        shock_start_day = int(np.random.randint(8, timeline_days - 12))
        shock_length = int(np.random.randint(4, 12))
        shock_end_day = min(timeline_days - 1, shock_start_day + shock_length)
        shock_severity = float(np.random.uniform(0.12, 0.45))

    for day in range(timeline_days):
        cycle_position = day % 30
        deterioration = max(0, day - worsening_start) / max(1, timeline_days - worsening_start)
        shock_multiplier = 1.0
        if shock_start_day is not None and shock_start_day <= day <= shock_end_day:
            shock_multiplier += shock_severity
        recovery_multiplier = max(0.75, 1 - behavior["recovery_factor"] * max(0, day - (worsening_start + 6)) / max(1, timeline_days - worsening_start))
        stress_multiplier = (1 + behavior["worsening_factor"] * deterioration) * shock_multiplier * recovery_multiplier

        salary_credit_flag = 0
        salary_day_with_delay = (
            salary_cycle_day + behavior["salary_delay_days"]
            if day < 30
            else salary_cycle_day_2 + behavior["salary_delay_days"]
        )
        if day == salary_day_with_delay:
            salary_credit_flag = 1

        cash_inflow = monthly_income if salary_credit_flag else 0.0
        if row["job_loss"] == 1 and day >= worsening_start:
            cash_inflow *= 0.15

        spend_noise = np.random.normal(0, daily_spend_base * 0.08)
        daily_spend = max(0.0, daily_spend_base * stress_multiplier + spend_noise)

        atm_noise = np.random.normal(0, daily_atm_base * 0.12)
        atm_withdrawal_amount = max(0.0, daily_atm_base * stress_multiplier + atm_noise)

        bill_paid_flag = 1
        emi_paid_flag = 1
        delinquency_event_flag = 0
        made_payment_today = 0

        if cycle_position == bill_due_day:
            bill_risk = (
                0.14
                + 0.14 * float(row["bill_delay_count"])
                + 0.25 * float(row["salary_delay"])
                + 0.18 * float(row["balance_drop_ratio"])
                + 0.22 * deterioration
                + 0.16 * recent_payment_stress
            )
            if behavior["profile"] == "distressed":
                bill_risk += 0.16
            elif behavior["profile"] == "stable":
                bill_risk -= 0.05

            bill_risk += np.random.normal(0, 0.07)
            bill_miss_probability = float(np.clip(bill_risk, 0.03, 0.82))

            if np.random.random() < bill_miss_probability:
                bill_paid_flag = 0
                delinquency_event_flag = 1
            else:
                made_payment_today = 1

        if cycle_position == emi_due_day:
            emi_risk = (
                0.08
                + 0.52 * float(row["emi_to_income_ratio"])
                + 0.18 * float(row["credit_utilization"])
                + 0.16 * float(row["balance_drop_ratio"])
                + 0.12 * float(row["job_loss"])
                + 0.1 * deterioration
                + 0.18 * recent_payment_stress
            )
            if row["missed_payments"] >= 2:
                emi_risk += 0.14
            if behavior["profile"] == "distressed":
                emi_risk += 0.16
            elif behavior["profile"] == "stable":
                emi_risk -= 0.04

            emi_risk += np.random.normal(0, 0.07)
            emi_miss_probability = float(np.clip(emi_risk, 0.02, 0.88))

            if np.random.random() < emi_miss_probability:
                emi_paid_flag = 0
                delinquency_event_flag = 1
            else:
                made_payment_today = 1

        due_outflow = 0.0
        if cycle_position == bill_due_day and bill_paid_flag == 1:
            due_outflow += float(row["credit_card_due"])
        if cycle_position == emi_due_day and emi_paid_flag == 1:
            due_outflow += float(row["emi"])

        if not made_payment_today:
            partial_payment_probability = 0.08 + 0.08 * behavior["app_activity_base"] - 0.05 * recent_payment_stress
            if np.random.random() < max(0.02, partial_payment_probability):
                made_payment_today = 1
                due_outflow += float(np.random.uniform(150, 1200))

        daily_cash_outflow = daily_spend + atm_withdrawal_amount + due_outflow
        balance = max(0.0, balance + cash_inflow - daily_cash_outflow)

        if not salary_credit_flag:
            days_since_salary_credit += 1
        else:
            days_since_salary_credit = 0

        if made_payment_today:
            days_since_last_payment = 0
            recent_payment_stress = max(0.0, recent_payment_stress - 0.3)
        else:
            days_since_last_payment += 1
            recent_payment_stress = min(1.0, recent_payment_stress + 0.14)

        util_change = (daily_cash_outflow / max(monthly_income, 1)) * 0.07
        if delinquency_event_flag:
            util_change += 0.03
        util_change += recent_payment_stress * 0.015
        credit_util = float(
            np.clip(
                credit_util + util_change - (cash_inflow / max(monthly_income, 1)) * 0.28,
                0.05,
                0.99,
            )
        )

        app_drop = deterioration * 0.25 if behavior["profile"] != "stable" else deterioration * 0.08
        app_activity_prob = max(0.08, behavior["app_activity_base"] - app_drop - 0.08 * recent_payment_stress)
        app_activity_flag = int(np.random.binomial(1, app_activity_prob))

        events.append(
            {
                "customer_id": row["customer_id"],
                "day_index": day,
                "age": int(row["age"]),
                "monthly_income": monthly_income,
                "account_tenure": int(row["account_tenure"]),
                "base_profile": behavior["profile"],
                "balance": round(balance, 2),
                "daily_spend": round(daily_spend, 2),
                "atm_withdrawal_amount": round(atm_withdrawal_amount, 2),
                "credit_utilization": round(credit_util, 4),
                "salary_credit_flag": salary_credit_flag,
                "bill_paid_flag": bill_paid_flag,
                "emi_paid_flag": emi_paid_flag,
                "app_activity_flag": app_activity_flag,
                "days_since_salary_credit": days_since_salary_credit,
                "days_since_last_payment": days_since_last_payment,
                "daily_cash_inflow": round(cash_inflow, 2),
                "daily_cash_outflow": round(daily_cash_outflow, 2),
                "delinquency_event_flag": delinquency_event_flag,
                "snapshot_label": int(row["label"]),
            }
        )

    return events


def generate_daily_events(input_path=INPUT_PATH, timeline_days=TIMELINE_DAYS, seed=SEED):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input labeled dataset not found: {input_path}")

    set_random_seed(seed)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    input_df = pd.read_csv(input_path)
    all_events = []

    for _, row in input_df.iterrows():
        all_events.extend(simulate_customer_events(row, timeline_days=timeline_days))

    events_df = pd.DataFrame(all_events)
    events_df.to_csv(DAILY_EVENTS_PATH, index=False)

    print(f"✅ Daily sequence events created: {events_df.shape}")
    print(f"📁 Saved to: {DAILY_EVENTS_PATH}")

    return events_df


def build_sequence_labels(events_df, time_steps=TIME_STEPS, prediction_horizon=PREDICTION_HORIZON):
    label_rows = []

    for customer_id, group in events_df.groupby("customer_id"):
        ordered = group.sort_values("day_index").reset_index(drop=True)
        max_window_end = len(ordered) - prediction_horizon - LABEL_GAP_DAYS

        for window_end_day in range(time_steps - 1, max_window_end + 1):
            future_slice = ordered.iloc[
                window_end_day + 1 + LABEL_GAP_DAYS : window_end_day + 1 + LABEL_GAP_DAYS + prediction_horizon
            ]
            future_delinquency_count = int((future_slice["delinquency_event_flag"] == 1).sum())
            severe_future_stress = (
                float(future_slice["credit_utilization"].mean()) > 0.78
                or float(future_slice["days_since_last_payment"].max()) >= 7
            )
            future_label = int(
                future_delinquency_count >= 2
                or (future_delinquency_count >= 1 and severe_future_stress)
            )

            label_rows.append(
                {
                    "customer_id": customer_id,
                    "window_end_day": int(window_end_day),
                    "future_delinquency_label": future_label,
                }
            )

    labels_df = pd.DataFrame(label_rows)
    labels_df.to_csv(SEQUENCE_LABELS_PATH, index=False)

    print(f"✅ Sequence labels created: {labels_df.shape}")
    print(f"📁 Saved to: {SEQUENCE_LABELS_PATH}")
    print("📊 Sequence label distribution:")
    print(labels_df["future_delinquency_label"].value_counts().sort_index().to_string())

    return labels_df


def build_lstm_windows(events_df, labels_df, time_steps=TIME_STEPS):
    sequences = []
    labels = []
    customer_ids = []
    window_end_days = []

    labels_lookup = {
        (row.customer_id, row.window_end_day): row.future_delinquency_label
        for row in labels_df.itertuples(index=False)
    }

    for customer_id, group in events_df.groupby("customer_id"):
        ordered = group.sort_values("day_index").reset_index(drop=True)

        for window_end_day in range(time_steps - 1, len(ordered)):
            lookup_key = (customer_id, window_end_day)
            if lookup_key not in labels_lookup:
                continue

            window = ordered.iloc[window_end_day - time_steps + 1 : window_end_day + 1]
            sequences.append(window[SEQUENCE_FEATURES].to_numpy(dtype=np.float32))
            labels.append(labels_lookup[lookup_key])
            customer_ids.append(customer_id)
            window_end_days.append(window_end_day)

    X = np.array(sequences, dtype=np.float32)
    y = np.array(labels, dtype=np.int64)
    customer_ids_array = np.array(customer_ids)
    window_end_days_array = np.array(window_end_days, dtype=np.int64)
    feature_names = np.array(SEQUENCE_FEATURES)

    np.savez_compressed(
        LSTM_WINDOWS_PATH,
        X=X,
        y=y,
        customer_ids=customer_ids_array,
        window_end_days=window_end_days_array,
        feature_names=feature_names,
    )

    print(f"✅ LSTM windows created: X={X.shape}, y={y.shape}")
    print(f"📁 Saved to: {LSTM_WINDOWS_PATH}")

    return X, y


def run_sequence_pipeline(
    input_path=INPUT_PATH,
    timeline_days=TIMELINE_DAYS,
    time_steps=TIME_STEPS,
    prediction_horizon=PREDICTION_HORIZON,
    seed=SEED,
):
    events_df = generate_daily_events(input_path=input_path, timeline_days=timeline_days, seed=seed)
    labels_df = build_sequence_labels(
        events_df,
        time_steps=time_steps,
        prediction_horizon=prediction_horizon,
    )
    build_lstm_windows(events_df, labels_df, time_steps=time_steps)

    print("\n✅ Sequence pipeline completed successfully")
    print(f"- Daily events: {DAILY_EVENTS_PATH}")
    print(f"- Sequence labels: {SEQUENCE_LABELS_PATH}")
    print(f"- LSTM windows: {LSTM_WINDOWS_PATH}")


if __name__ == "__main__":
    run_sequence_pipeline()
