import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

default_args = {
    'owner': 'delinq',
    'depends_on_past': False,
    'start_date': datetime(2026, 3, 28),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'model_retraining_pipeline',
    default_args=default_args,
    description='A DAG to retrain ML models and log artifacts weekly',
    schedule_interval='@weekly',
    catchup=False,
) as dag:

    retrain_xgboost = BashOperator(
        task_id='retrain_xgboost',
        bash_command=f'cd {BASE_DIR} && python src/models/train_xgboost.py',
    )

    retrain_lstm = BashOperator(
        task_id='retrain_lstm',
        bash_command=f'cd {BASE_DIR} && python src/sequence_model/train_lstm.py',
    )

    retrain_xgboost >> retrain_lstm
