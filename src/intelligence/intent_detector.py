import pandas as pd


def detect_intent(row):
    payment_discipline = row.get("payment_discipline", 1.0)
    missed_payments = row.get("missed_payments", 0)
    salary_delay = row.get("salary_delay", 0)
    bill_delay_count = row.get("bill_delay_count", 0)
    job_loss = row.get("job_loss", 0)
    credit_utilization = row.get("credit_utilization", 0)
    app_activity_flag = row.get("app_activity_flag")

    if pd.isna(payment_discipline):
        payment_discipline = 1.0
    if pd.isna(app_activity_flag):
        app_activity_flag = 1

    if job_loss == 1 or (missed_payments >= 3 and credit_utilization >= 0.8):
        return "high_distress"

    if (missed_payments >= 2 or bill_delay_count >= 2) and app_activity_flag == 0:
        return "disengaged"

    if salary_delay == 1 or payment_discipline < 0.6 or credit_utilization >= 0.65:
        return "willing_but_stressed"

    return "stable"


def detect_intents(df):
    working_df = df.copy()
    working_df["intent_label"] = working_df.apply(detect_intent, axis=1)
    return working_df
