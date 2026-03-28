import json
import os
import sys
import argparse

import joblib
import numpy as np
from sklearn.metrics import accuracy_score, classification_report, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.sequence_model.generate_sequences import LSTM_WINDOWS_PATH
from src.models.mlflow_utils import log_json_artifact, start_run

ARTIFACTS_DIR = os.path.join(BASE_DIR, "artifacts")
LSTM_MODEL_PATH = os.path.join(ARTIFACTS_DIR, "lstm_model.pt")
LSTM_SCALER_PATH = os.path.join(ARTIFACTS_DIR, "lstm_scaler.pkl")
SEQUENCE_XGB_PATH = os.path.join(ARTIFACTS_DIR, "sequence_xgb_model.pkl")
LSTM_METADATA_PATH = os.path.join(ARTIFACTS_DIR, "lstm_metadata.json")

SEED = 42
HIDDEN_SIZE = 128
EPOCHS = 5
BATCH_SIZE = 512
EMBEDDING_BATCH_SIZE = 2048
TORCH_THREADS = 1
_TORCH_THREADS_CONFIGURED = False


def _require_torch():
    global _TORCH_THREADS_CONFIGURED

    try:
        import torch
        import torch.nn as nn
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "PyTorch is required for the sequence model. Install it in the project "
            "virtualenv before running train_lstm.py."
        ) from exc

    if not _TORCH_THREADS_CONFIGURED:
        torch.set_num_threads(TORCH_THREADS)
        if hasattr(torch, "set_num_interop_threads"):
            try:
                torch.set_num_interop_threads(TORCH_THREADS)
            except RuntimeError:
                pass
        _TORCH_THREADS_CONFIGURED = True

    return torch, nn


def load_lstm_windows(npz_path=LSTM_WINDOWS_PATH):
    if not os.path.exists(npz_path):
        raise FileNotFoundError(f"LSTM windows file not found: {npz_path}")

    artifact = np.load(npz_path, allow_pickle=True)
    return {
        "X": artifact["X"],
        "y": artifact["y"],
        "customer_ids": artifact["customer_ids"],
        "window_end_days": artifact["window_end_days"],
        "feature_names": artifact["feature_names"].tolist(),
    }


def split_by_customer(X, y, customer_ids, test_size=0.2, random_state=SEED):
    unique_customer_ids = np.unique(customer_ids)
    train_customer_ids, test_customer_ids = train_test_split(
        unique_customer_ids,
        test_size=test_size,
        random_state=random_state,
    )

    train_mask = np.isin(customer_ids, train_customer_ids)
    test_mask = np.isin(customer_ids, test_customer_ids)

    return (
        X[train_mask],
        X[test_mask],
        y[train_mask],
        y[test_mask],
        customer_ids[train_mask],
        customer_ids[test_mask],
    )


def validate_no_customer_overlap(train_customer_ids, test_customer_ids):
    train_set = set(np.unique(train_customer_ids))
    test_set = set(np.unique(test_customer_ids))
    overlap = train_set.intersection(test_set)

    if overlap:
        sample_overlap = sorted(list(overlap))[:5]
        raise ValueError(
            "Data leakage detected: train/test customer overlap found. "
            f"Example overlapping customer_ids: {sample_overlap}"
        )

    print(f"Leakage check passed: 0 overlapping customers across {len(train_set)} train and {len(test_set)} test customers.")


def summarize_split(y_train, y_test):
    train_positive_rate = float(np.mean(y_train))
    test_positive_rate = float(np.mean(y_test))
    print(f"Train positive rate: {train_positive_rate:.4f}")
    print(f"Test positive rate: {test_positive_rate:.4f}")


def subset_by_customer(X, y, customer_ids, max_customers=None, max_windows=None):
    if max_customers is not None:
        selected_customer_ids = np.unique(customer_ids)[:max_customers]
        mask = np.isin(customer_ids, selected_customer_ids)
        X = X[mask]
        y = y[mask]
        customer_ids = customer_ids[mask]

    if max_windows is not None:
        X = X[:max_windows]
        y = y[:max_windows]
        customer_ids = customer_ids[:max_windows]

    return X, y, customer_ids


def fit_sequence_scaler(X_train, X_test):
    scaler = StandardScaler()

    X_train_flat = X_train.reshape(-1, X_train.shape[2])
    X_test_flat = X_test.reshape(-1, X_test.shape[2])

    scaler.fit(X_train_flat)
    X_train_scaled = scaler.transform(X_train_flat).reshape(X_train.shape)
    X_test_scaled = scaler.transform(X_test_flat).reshape(X_test.shape)

    return X_train_scaled, X_test_scaled, scaler


def build_lstm_model(input_size, hidden_size=HIDDEN_SIZE):
    torch, nn = _require_torch()

    class LSTMModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
            self.fc = nn.Linear(hidden_size, 1)

        def forward(self, x):
            out, _ = self.lstm(x)
            out = out[:, -1, :]
            return self.fc(out)

    return LSTMModel()


def _train_epoch(model, data_loader, criterion, optimizer, torch):
    model.train()
    epoch_loss = 0.0

    for batch_x, batch_y in data_loader:
        preds = model(batch_x).squeeze()
        loss = criterion(preds, batch_y)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        epoch_loss += float(loss.item()) * len(batch_x)

    return epoch_loss / len(data_loader.dataset)


def train_lstm_embeddings(
    X_train,
    y_train,
    input_size,
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    hidden_size=HIDDEN_SIZE,
):
    torch, nn = _require_torch()

    torch.manual_seed(SEED)

    model = build_lstm_model(input_size=input_size, hidden_size=hidden_size)
    criterion = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    dataset = torch.utils.data.TensorDataset(
        torch.tensor(X_train, dtype=torch.float32),
        torch.tensor(y_train, dtype=torch.float32),
    )
    data_loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)

    for epoch in range(epochs):
        loss = _train_epoch(model, data_loader, criterion, optimizer, torch)
        print(f"Epoch {epoch + 1}, Loss: {loss:.4f}")

    return model


def extract_embeddings(model, X, batch_size=EMBEDDING_BATCH_SIZE):
    torch, _ = _require_torch()

    model.eval()
    batches = []
    with torch.no_grad():
        for start in range(0, len(X), batch_size):
            tensor = torch.tensor(X[start : start + batch_size], dtype=torch.float32)
            lstm_output, _ = model.lstm(tensor)
            batches.append(lstm_output[:, -1, :].numpy())

    return np.concatenate(batches, axis=0)


def train_sequence_xgb(train_embeddings, y_train):
    model = XGBClassifier(
        n_estimators=300,
        max_depth=2,
        learning_rate=0.03,
        subsample=0.7,
        colsample_bytree=0.7,
        reg_lambda=5,
        gamma=1,
        random_state=SEED,
        eval_metric="logloss",
    )
    model.fit(train_embeddings, y_train)
    return model


def evaluate_sequence_model(model, test_embeddings, y_test):
    y_prob = model.predict_proba(test_embeddings)[:, 1]
    y_pred = (y_prob >= 0.5).astype(int)

    print("\n📊 LSTM + XGB Classification Report:\n")
    print(classification_report(y_test, y_pred))
    print("\n🎯 Sequence ROC-AUC Score:", roc_auc_score(y_test, y_prob))

    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, y_prob)),
    }

    return y_prob, y_pred, metrics


def save_sequence_artifacts(lstm_model, scaler, xgb_model, metadata):
    torch, _ = _require_torch()

    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    torch.save(lstm_model.state_dict(), LSTM_MODEL_PATH)
    joblib.dump(scaler, LSTM_SCALER_PATH)
    joblib.dump(xgb_model, SEQUENCE_XGB_PATH)

    with open(LSTM_METADATA_PATH, "w") as metadata_file:
        json.dump(metadata, metadata_file, indent=2)

    print(f"\n✅ LSTM model saved at: {LSTM_MODEL_PATH}")
    print(f"✅ LSTM scaler saved at: {LSTM_SCALER_PATH}")
    print(f"✅ Sequence XGB model saved at: {SEQUENCE_XGB_PATH}")
    print(f"✅ LSTM metadata saved at: {LSTM_METADATA_PATH}")


def build_arg_parser():
    parser = argparse.ArgumentParser(description="Train the LSTM + XGBoost sequence model.")
    parser.add_argument("--epochs", type=int, default=EPOCHS)
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    parser.add_argument("--hidden-size", type=int, default=HIDDEN_SIZE)
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--max-customers", type=int, default=None)
    parser.add_argument("--max-windows", type=int, default=None)
    return parser


def run_training_pipeline(
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    hidden_size=HIDDEN_SIZE,
    test_size=0.2,
    max_customers=None,
    max_windows=None,
):
    with start_run("pytorch_sequence_training") as (mlflow, _):
        data = load_lstm_windows()

        X, y, customer_ids = subset_by_customer(
            data["X"],
            data["y"],
            data["customer_ids"],
            max_customers=max_customers,
            max_windows=max_windows,
        )

        X_train, X_test, y_train, y_test, train_customer_ids, test_customer_ids = split_by_customer(
            X,
            y,
            customer_ids,
            test_size=test_size,
        )
        validate_no_customer_overlap(train_customer_ids, test_customer_ids)

        X_train_scaled, X_test_scaled, scaler = fit_sequence_scaler(X_train, X_test)

        print("Train windows:", X_train_scaled.shape)
        print("Test windows:", X_test_scaled.shape)
        print("Train customers:", len(np.unique(train_customer_ids)))
        print("Test customers:", len(np.unique(test_customer_ids)))
        summarize_split(y_train, y_test)

        mlflow.log_params(
            {
                "seed": SEED,
                "hidden_size": hidden_size,
                "epochs": epochs,
                "batch_size": batch_size,
                "test_size": test_size,
                "max_customers": max_customers,
                "max_windows": max_windows,
                "train_customer_count": int(len(np.unique(train_customer_ids))),
                "test_customer_count": int(len(np.unique(test_customer_ids))),
                "train_window_count": int(len(X_train_scaled)),
                "test_window_count": int(len(X_test_scaled)),
            }
        )

        lstm_model = train_lstm_embeddings(
            X_train_scaled,
            y_train,
            input_size=X_train_scaled.shape[2],
            epochs=epochs,
            batch_size=batch_size,
            hidden_size=hidden_size,
        )

        train_embeddings = extract_embeddings(lstm_model, X_train_scaled)
        test_embeddings = extract_embeddings(lstm_model, X_test_scaled)

        xgb_model = train_sequence_xgb(train_embeddings, y_train)
        y_prob, y_pred, metrics = evaluate_sequence_model(xgb_model, test_embeddings, y_test)
        mlflow.log_metrics(metrics)

        metadata = {
            "seed": SEED,
            "hidden_size": hidden_size,
            "epochs": epochs,
            "batch_size": batch_size,
            "feature_names": data["feature_names"],
            "input_windows_path": LSTM_WINDOWS_PATH,
            "test_size": test_size,
            "max_customers": max_customers,
            "max_windows": max_windows,
            "train_customer_count": int(len(np.unique(train_customer_ids))),
            "test_customer_count": int(len(np.unique(test_customer_ids))),
            "train_positive_rate": float(np.mean(y_train)),
            "test_positive_rate": float(np.mean(y_test)),
            "leakage_check_passed": True,
        }
        save_sequence_artifacts(lstm_model, scaler, xgb_model, metadata)
        mlflow.log_artifact(LSTM_MODEL_PATH)
        mlflow.log_artifact(LSTM_SCALER_PATH)
        mlflow.log_artifact(SEQUENCE_XGB_PATH)
        mlflow.log_artifact(LSTM_METADATA_PATH)
        log_json_artifact(
            mlflow,
            {
                "classification_report": classification_report(y_test, y_pred, output_dict=True),
                "sequence_metrics": metrics,
                "metadata": metadata,
            },
            "sequence_training_report.json",
        )

    return {
        "lstm_model_path": LSTM_MODEL_PATH,
        "scaler_path": LSTM_SCALER_PATH,
        "sequence_xgb_path": SEQUENCE_XGB_PATH,
    }


if __name__ == "__main__":
    args = build_arg_parser().parse_args()
    run_training_pipeline(
        epochs=args.epochs,
        batch_size=args.batch_size,
        hidden_size=args.hidden_size,
        test_size=args.test_size,
        max_customers=args.max_customers,
        max_windows=args.max_windows,
    )
