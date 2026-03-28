import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
VENV_PYTHON = os.environ.get("DELINQ_PYTHON_BIN", f"{BASE_DIR}/venv/bin/python3")
FEAST_BIN = os.environ.get("DELINQ_FEAST_BIN", f"{BASE_DIR}/venv/bin/feast")

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
    "data_and_feature_pipeline",
    default_args=default_args,
    description="Build processed data, export Feast parquet source, apply Feast definitions, materialize the online store, and optionally backfill Kafka events.",
    schedule_interval=timedelta(hours=1),
    catchup=False,
) as dag:
    run_data_pipeline = BashOperator(
        task_id="run_data_pipeline",
        bash_command=f"cd {BASE_DIR} && {VENV_PYTHON} src/data_pipeline/run_pipeline.py",
    )

    export_parquet = BashOperator(
        task_id="export_parquet",
        bash_command=f"cd {BASE_DIR} && {VENV_PYTHON} src/data_pipeline/export_parquet.py",
    )

    feast_apply = BashOperator(
        task_id="feast_apply",
        bash_command=f"cd {BASE_DIR}/feature_repo && {FEAST_BIN} apply",
    )

    feast_materialize = BashOperator(
        task_id="feast_materialize",
        bash_command=f"cd {BASE_DIR}/feature_repo && {FEAST_BIN} materialize-incremental $(date -u +\"%Y-%m-%dT%H:%M:%S\")",
    )

    kafka_backfill = BashOperator(
        task_id="kafka_backfill",
        bash_command=f"cd {BASE_DIR} && {VENV_PYTHON} producer.py",
    )

    run_data_pipeline >> export_parquet >> feast_apply >> feast_materialize >> kafka_backfill
