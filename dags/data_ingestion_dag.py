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
    'data_ingestion_and_streaming',
    default_args=default_args,
    description='A DAG to ingest new customer records and trigger the Kafka producer',
    schedule_interval=timedelta(hours=1),
    catchup=False,
) as dag:

    # Example generic step to download/prepare data (simulated as bash command)
    prepare_data = BashOperator(
        task_id='prepare_data',
        bash_command=f'echo "Simulating fetching latest data into {BASE_DIR}/data/processed/final_cleaned.csv"',
    )

    # Step to run the Kafka producer.py script
    stream_to_kafka = BashOperator(
        task_id='stream_to_kafka',
        bash_command=f'cd {BASE_DIR} && python producer.py',
    )

    prepare_data >> stream_to_kafka
