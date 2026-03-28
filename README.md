# De-linq

Pre-delinquency risk intelligence prototype with:

- XGBoost and scikit-learn for tabular risk scoring
- PyTorch for sequence modeling
- Kafka for event streaming
- Feast for online feature lookup
- Airflow DAG scaffolds for orchestration
- FastAPI for inspection and API access
- MLflow for local experiment tracking

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
npm install
```

## Core Pipeline

Build the local datasets:

```bash
python3 src/data_pipeline/run_pipeline.py
```

Create the Feast parquet source if needed:

```bash
python3 - <<'PY'
import pandas as pd
df = pd.read_csv("data/processed/final_cleaned.csv")
if "event_timestamp" not in df.columns:
    df["event_timestamp"] = pd.Timestamp.utcnow()
df.to_parquet("data/processed/final_cleaned.parquet", index=False)
PY
```

## Model Training

Train the tabular XGBoost model:

```bash
python3 src/models/train_xgboost.py
```

Train the LightGBM benchmark model:

```bash
python3 src/models/train_lightgbm.py
```

Train the sequence model:

```bash
python3 src/sequence_model/train_lstm.py
```

Train the TensorFlow sequence benchmark:

```bash
python3 src/sequence_model/train_lstm_tensorflow.py
```

## MLflow

Training metadata is logged to a local SQLite-backed MLflow store:

- metadata DB: `artifacts/mlflow.db`
- artifacts dir: `artifacts/mlruns/`

Start the MLflow UI:

```bash
source venv/bin/activate
mlflow ui --backend-store-uri sqlite:///artifacts/mlflow.db --default-artifact-root ./artifacts/mlruns
```

Open:

- `http://127.0.0.1:5000`

Current MLflow-integrated training scripts:

- [src/models/train_xgboost.py](/Users/yesharavani/Barclays/De-linq/src/models/train_xgboost.py)
- [src/models/train_lightgbm.py](/Users/yesharavani/Barclays/De-linq/src/models/train_lightgbm.py)
- [src/sequence_model/train_lstm.py](/Users/yesharavani/Barclays/De-linq/src/sequence_model/train_lstm.py)
- [src/sequence_model/train_lstm_tensorflow.py](/Users/yesharavani/Barclays/De-linq/src/sequence_model/train_lstm_tensorflow.py)

## Kafka + Feast Runtime

After Kafka is running and topics are created:

Apply and materialize the Feast repo:

```bash
cd feature_repo
feast apply
feast materialize-incremental $(date -u +"%Y-%m-%dT%H:%M:%S")
cd ..
```

Start the streaming components:

```bash
python3 src/streaming/risk_consumer.py
python3 src/streaming/intervention_consumer.py
python3 producer.py
```

## Airflow

Airflow DAGs now wrap the validated local flow instead of placeholder commands.

Available DAGs:

- [dags/data_ingestion_dag.py](/Users/yesharavani/Barclays/De-linq/dags/data_ingestion_dag.py)
  Runs:
  - data pipeline
  - parquet export
  - `feast apply`
  - `feast materialize-incremental`
  - Kafka producer backfill

- [dags/model_retraining_dag.py](/Users/yesharavani/Barclays/De-linq/dags/model_retraining_dag.py)
  Runs:
  - XGBoost training
  - LightGBM benchmark training
  - PyTorch sequence training

The DAGs assume:

- the repo is available at the same filesystem path
- the Python executable is `venv/bin/python3`
- the Feast CLI is `venv/bin/feast`

Override those with environment variables if Airflow runs in a different environment:

```bash
export DELINQ_PYTHON_BIN=/path/to/python3
export DELINQ_FEAST_BIN=/path/to/feast
```

## API

Start FastAPI:

```bash
uvicorn src.api.app:app --reload
```

Swagger UI:

- `http://127.0.0.1:8000/docs`

## BentoML

The primary XGBoost model can also be served through BentoML.

Install dependencies:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

Run the Bento service locally:

```bash
bentoml serve src.serving.bento_service:RiskScoringService --reload
```

Build a Bento package:

```bash
bentoml build
```

This uses:

- [src/serving/bento_service.py](/Users/yesharavani/Barclays/De-linq/src/serving/bento_service.py)
- [bentofile.yaml](/Users/yesharavani/Barclays/De-linq/bentofile.yaml)
