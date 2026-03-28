import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
VENV_PYTHON = os.environ.get("DELINQ_PYTHON_BIN", f"{BASE_DIR}/venv/bin/python3")

default_args = {
    "owner": "delinq",
    "depends_on_past": False,
    "start_date": datetime(2026, 3, 28),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "model_training_pipeline",
    default_args=default_args,
    description="Train the production XGBoost model, run the LightGBM benchmark, and retrain the PyTorch sequence model with MLflow tracking.",
    schedule_interval="@weekly",
    catchup=False,
) as dag:
    train_xgboost = BashOperator(
        task_id="train_xgboost",
        bash_command=f"cd {BASE_DIR} && {VENV_PYTHON} src/models/train_xgboost.py",
    )

    train_lightgbm = BashOperator(
        task_id="train_lightgbm",
        bash_command=f"cd {BASE_DIR} && {VENV_PYTHON} src/models/train_lightgbm.py",
    )

    train_sequence_model = BashOperator(
        task_id="train_sequence_model",
        bash_command=f"cd {BASE_DIR} && {VENV_PYTHON} src/sequence_model/train_lstm.py",
    )

    train_xgboost >> train_lightgbm >> train_sequence_model
