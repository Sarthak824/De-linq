# De-linq

Pre-delinquency risk intelligence prototype for detecting financially stressed customers before default, scoring risk, and recommending interventions.

## What Is Implemented

- Synthetic customer risk data generation
- Labeling and feature engineering pipeline
- Tabular risk model with XGBoost
- LightGBM benchmark path for model comparison
- Sequence risk model with PyTorch LSTM embeddings plus XGBoost
- FastAPI backend for scoring, analytics, and interventions
- SQLite-backed database layer for customer, prediction, and intervention storage
- React/Vite dashboard prototype

## Current Architecture

The main working path in this repository is:

1. Generate synthetic customer data
2. Label delinquency risk
3. Engineer advanced features
4. Clean and validate the dataset
5. Train the tabular model
6. Benchmark LightGBM against XGBoost
7. Generate sequence windows and train the sequence model
8. Score customers and generate intervention recommendations
9. Persist profiles, predictions, and interventions to a database
10. Serve results through FastAPI

Generated datasets and model artifacts are intentionally ignored by git. They remain local and should be regenerated when needed.

## Repository Structure

```text
src/
  api/                  FastAPI application
  data_pipeline/        Synthetic data generation, labeling, features, validation
  inference/            Batch and request-time scoring
  intelligence/         Intent detection logic
  interventions/        Recommendation and orchestration logic
  models/               Tabular model training and config
  persona/              Persona generation
  policy/               Intervention policy rules
  sequence_model/       Sequence generation, training, and inference
  storage/              SQLite storage and database sync utilities
financial_pipeline/
  intent_detection/     Experimental LLM-based intent module, not on the main path
```

## Environment

Recommended:

- Python 3.12
- Node.js 20+ or newer
- npm

Install Python dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Install frontend dependencies:

```bash
npm install
```

Notes:

- The saved XGBoost model requires `xgboost` to be installed in the active Python environment.
- On macOS, XGBoost may require `libomp`. If model loading fails, install it with:

```bash
brew install libomp
```

## Running The Project

### 1. Run the data pipeline

```bash
python3 src/data_pipeline/run_pipeline.py
```

Outputs are generated under `data/raw/`, `data/processed/`, and `data/output/`.

### 2. Train the tabular model

```bash
python3 src/models/train_xgboost.py
```

This creates the XGBoost artifact under `artifacts/`.

### 3. Train the sequence model

### 3. Benchmark XGBoost vs LightGBM

Run both tabular models and capture metrics:

```bash
python3 src/models/benchmark_models.py
```

Train only the LightGBM benchmark:

```bash
python3 src/models/train_lightgbm.py
```

Metrics are saved under `artifacts/metrics/`.

### 4. Train the sequence model

Generate sequence windows:

```bash
python3 src/sequence_model/generate_sequences.py
```

Train the LSTM plus sequence XGBoost stack:

```bash
python3 src/sequence_model/train_lstm.py
```

Generate sequence scores:

```bash
python3 src/sequence_model/infer_lstm.py
```

### 5. Run batch inference

```bash
python3 src/inference/predict.py
```

This creates:

- `data/output/customer_risk_predictions.csv`
- `data/output/customer_sequence_scores.csv`
- `data/output/personas.csv`
- `data/output/personas.json`

It also writes customer profiles and predictions into the SQLite database.

### 6. Synchronize database from CSV outputs

If you already have CSV outputs and want to backfill the database:

```bash
python3 src/storage/sync_database.py
```

Default local database path:

- `data/db/delinq.sqlite3`

Override with:

```bash
export DELINQ_DB_PATH=/path/to/delinq.sqlite3
```

### 7. Start the API

```bash
uvicorn src.api.app:app --reload
```

API docs:

- `http://127.0.0.1:8000/docs`

The API now prefers database-backed reads when the database has data, and falls back to CSV files otherwise.

### 8. Start the frontend

```bash
npm run dev
```

Default Vite URL:

- `http://localhost:5173`

## API Endpoints

Core endpoints in [src/api/app.py](/Users/yesharavani/Barclays/De-linq/src/api/app.py):

- `GET /health`
- `GET /customers`
- `GET /customers/{customer_id}`
- `GET /customers/{customer_id}/analysis`
- `GET /analytics/top-risks`
- `GET /analytics/reason-distribution`
- `GET /analytics/intervention-summary`
- `GET /model/info`
- `GET /model/feature-importance`
- `POST /predict-risk`
- `POST /batch-predict`
- `POST /interventions/recommend`
- `POST /interventions/trigger`
- `GET /interventions/history/{customer_id}`
- `GET /portfolio-summary`

## Testing

Run backend tests:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

Build the frontend:

```bash
npm run build
```

## Work In Progress

These areas are not yet productionized:

- Frontend is still a prototype UI
- Generated outputs are file-based, not database-backed
- SQLite is a practical local step, but bank-scale deployments should move to PostgreSQL, Redshift, or another production warehouse/OLTP split
- Streaming and real-time ingestion are not part of the core path yet
- Model registry, deployment packaging, and orchestration are not implemented yet
- The LLM intent module under `financial_pipeline/intent_detection` is experimental and separate from the main scoring flow

## Recommended Next Backend Steps

- Add model evaluation reporting and benchmarking
- Add LightGBM benchmark alongside XGBoost
- Add backend integration tests for more API flows
- Introduce experiment tracking and artifact versioning
- Replace CSV-backed outputs with persistent storage
