import os
import sqlite3
from contextlib import contextmanager

import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DEFAULT_DB_PATH = os.environ.get(
    "DELINQ_DB_PATH",
    os.path.join(BASE_DIR, "data", "db", "delinq.sqlite3"),
)

PROFILE_COLUMNS = [
    "customer_id",
    "age",
    "monthly_income",
    "emi",
    "credit_card_due",
    "emi_to_income_ratio",
    "credit_utilization",
    "missed_payments",
    "salary_delay",
    "job_loss",
    "avg_balance",
    "balance_drop_ratio",
    "atm_withdrawals",
    "spending_change",
    "bill_delay_count",
    "account_tenure",
    "label",
    "total_obligations",
    "debt_stress_ratio",
    "liquidity_buffer",
    "spending_instability",
    "payment_discipline",
    "financial_health_score",
    "shock_flag",
    "credit_dependency",
    "early_risk_flag",
    "stability_score",
    "secured_loans",
    "personal_loans",
    "gold_loans",
    "active_loans",
    "loan_top_up_indicator",
    "credit_exposure_score",
]

PREDICTION_COLUMNS = [
    "customer_id",
    "risk_score",
    "sequence_risk_score",
    "risk_prediction",
    "risk_band",
    "top_reason_codes",
    "recommended_intervention",
    "persona_label",
    "persona_signals",
    "financial_stress_level",
    "intent_label",
    "policy_action",
    "policy_priority",
    "recommended_channel",
    "credit_exposure_level",
    "credit_exposure_message",
    "debt_structure",
    "active_loan_summary",
    "exposure_score",
]

INTERVENTION_COLUMNS = [
    "execution_id",
    "customer_id",
    "triggered_at",
    "risk_score",
    "risk_band",
    "intent_label",
    "persona_label",
    "policy_action",
    "policy_priority",
    "recommended_channel",
    "recommended_intervention",
    "delivery_status",
]


def get_database_path(db_path=None):
    return db_path or DEFAULT_DB_PATH


@contextmanager
def get_connection(db_path=None):
    resolved_path = get_database_path(db_path)
    os.makedirs(os.path.dirname(resolved_path), exist_ok=True)
    connection = sqlite3.connect(resolved_path)
    try:
        yield connection
    finally:
        connection.close()


def init_database(db_path=None):
    with get_connection(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS customer_profiles (
                customer_id TEXT PRIMARY KEY,
                age INTEGER,
                monthly_income REAL,
                emi REAL,
                credit_card_due REAL,
                emi_to_income_ratio REAL,
                credit_utilization REAL,
                missed_payments INTEGER,
                salary_delay INTEGER,
                job_loss INTEGER,
                avg_balance REAL,
                balance_drop_ratio REAL,
                atm_withdrawals INTEGER,
                spending_change REAL,
                bill_delay_count INTEGER,
                account_tenure INTEGER,
                label INTEGER,
                total_obligations REAL,
                debt_stress_ratio REAL,
                liquidity_buffer REAL,
                spending_instability REAL,
                payment_discipline REAL,
                financial_health_score REAL,
                shock_flag INTEGER,
                credit_dependency REAL,
                early_risk_flag INTEGER,
                stability_score REAL,
                secured_loans INTEGER,
                personal_loans INTEGER,
                gold_loans INTEGER,
                active_loans INTEGER,
                loan_top_up_indicator INTEGER,
                credit_exposure_score REAL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS customer_predictions (
                customer_id TEXT PRIMARY KEY,
                risk_score REAL,
                sequence_risk_score REAL,
                risk_prediction INTEGER,
                risk_band TEXT,
                top_reason_codes TEXT,
                recommended_intervention TEXT,
                persona_label TEXT,
                persona_signals TEXT,
                financial_stress_level TEXT,
                intent_label TEXT,
                policy_action TEXT,
                policy_priority TEXT,
                recommended_channel TEXT,
                credit_exposure_level TEXT,
                credit_exposure_message TEXT,
                debt_structure TEXT,
                active_loan_summary TEXT,
                exposure_score REAL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS intervention_history (
                execution_id TEXT PRIMARY KEY,
                customer_id TEXT,
                triggered_at TEXT,
                risk_score REAL,
                risk_band TEXT,
                intent_label TEXT,
                persona_label TEXT,
                policy_action TEXT,
                policy_priority TEXT,
                recommended_channel TEXT,
                recommended_intervention TEXT,
                delivery_status TEXT
            )
            """
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_predictions_risk_score ON customer_predictions (risk_score DESC)"
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_interventions_customer_id ON intervention_history (customer_id, triggered_at DESC)"
        )
        connection.commit()


def _normalize_columns(df, columns):
    normalized = df.copy()
    for column in columns:
        if column not in normalized.columns:
            normalized[column] = None
    return normalized[columns]


def save_customer_profiles(df, db_path=None):
    init_database(db_path)
    normalized = _normalize_columns(df, PROFILE_COLUMNS)
    with get_connection(db_path) as connection:
        connection.execute("DELETE FROM customer_profiles")
        normalized.to_sql("customer_profiles", connection, if_exists="append", index=False)
        connection.commit()


def save_customer_predictions(df, db_path=None):
    init_database(db_path)
    normalized = _normalize_columns(df, PREDICTION_COLUMNS)
    with get_connection(db_path) as connection:
        connection.execute("DELETE FROM customer_predictions")
        normalized.to_sql("customer_predictions", connection, if_exists="append", index=False)
        connection.commit()


def append_intervention_event(event, db_path=None):
    init_database(db_path)
    event_df = pd.DataFrame([event])
    normalized = _normalize_columns(event_df, INTERVENTION_COLUMNS)
    with get_connection(db_path) as connection:
        normalized.to_sql("intervention_history", connection, if_exists="append", index=False)
        connection.commit()


def load_customer_profiles(db_path=None):
    init_database(db_path)
    with get_connection(db_path) as connection:
        return pd.read_sql_query("SELECT * FROM customer_profiles", connection)


def load_customer_predictions(db_path=None):
    init_database(db_path)
    with get_connection(db_path) as connection:
        return pd.read_sql_query(
            "SELECT customer_id, risk_score, sequence_risk_score, risk_prediction, risk_band, "
            "top_reason_codes, recommended_intervention, persona_label, persona_signals, "
            "financial_stress_level, intent_label, policy_action, policy_priority, recommended_channel "
            "FROM customer_predictions",
            connection,
        )


def load_intervention_history(customer_id=None, db_path=None):
    init_database(db_path)
    query = "SELECT * FROM intervention_history"
    params = []
    if customer_id:
        query += " WHERE customer_id = ?"
        params.append(customer_id)
    query += " ORDER BY triggered_at DESC"

    with get_connection(db_path) as connection:
        return pd.read_sql_query(query, connection, params=params)


def load_customer_analysis(limit=None, customer_id=None, db_path=None):
    init_database(db_path)
    query = """
        SELECT
            profiles.*,
            predictions.risk_score,
            predictions.sequence_risk_score,
            predictions.risk_prediction,
            predictions.risk_band,
            predictions.top_reason_codes,
            predictions.recommended_intervention,
            predictions.persona_label,
            predictions.persona_signals,
            predictions.financial_stress_level,
            predictions.intent_label,
            predictions.policy_action,
            predictions.policy_priority,
            predictions.recommended_channel
        FROM customer_profiles AS profiles
        LEFT JOIN customer_predictions AS predictions
            ON profiles.customer_id = predictions.customer_id
    """
    params = []

    if customer_id:
        query += " WHERE profiles.customer_id = ?"
        params.append(customer_id)

    query += " ORDER BY profiles.customer_id"
    if limit is not None:
        query += " LIMIT ?"
        params.append(limit)

    with get_connection(db_path) as connection:
        return pd.read_sql_query(query, connection, params=params)


def sync_csv_sources_to_database(profiles_df=None, predictions_df=None, interventions_df=None, db_path=None):
    init_database(db_path)
    if profiles_df is not None and not profiles_df.empty:
        save_customer_profiles(profiles_df, db_path=db_path)
    if predictions_df is not None and not predictions_df.empty:
        save_customer_predictions(predictions_df, db_path=db_path)
    if interventions_df is not None and not interventions_df.empty:
        normalized = _normalize_columns(interventions_df, INTERVENTION_COLUMNS)
        with get_connection(db_path) as connection:
            connection.execute("DELETE FROM intervention_history")
            normalized.to_sql("intervention_history", connection, if_exists="append", index=False)
            connection.commit()
