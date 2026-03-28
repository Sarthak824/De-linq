import argparse
import json
import os
import sys

import joblib
import numpy as np
from sklearn.metrics import accuracy_score, classification_report, f1_score, precision_score, recall_score, roc_auc_score
from xgboost import XGBClassifier

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.models.mlflow_utils import log_json_artifact, start_run
from src.sequence_model.train_lstm import (
    ARTIFACTS_DIR,
    BATCH_SIZE,
    EPOCHS,
    HIDDEN_SIZE,
    LSTM_WINDOWS_PATH,
    SEED,
    fit_sequence_scaler,
    load_lstm_windows,
    split_by_customer,
    subset_by_customer,
    summarize_split,
    validate_no_customer_overlap,
)

TF_MODEL_PATH = os.path.join(ARTIFACTS_DIR, "tf_lstm_model.keras")
TF_SCALER_PATH = os.path.join(ARTIFACTS_DIR, "tf_lstm_scaler.pkl")
TF_SEQUENCE_XGB_PATH = os.path.join(ARTIFACTS_DIR, "tf_sequence_xgb_model.pkl")
TF_METADATA_PATH = os.path.join(ARTIFACTS_DIR, "tf_lstm_metadata.json")


def _require_tensorflow():
    try:
        import tensorflow as tf
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "TensorFlow is not installed in the active environment. Install it with "
            "`pip install tensorflow` or reinstall from requirements.txt before running this benchmark."
        ) from exc

    return tf


def build_tf_model(input_size, hidden_size=HIDDEN_SIZE):
    tf = _require_tensorflow()
    tf.random.set_seed(SEED)

    model = tf.keras.Sequential(
        [
            tf.keras.layers.Input(shape=(None, input_size)),
            tf.keras.layers.LSTM(hidden_size, name="sequence_embedding"),
            tf.keras.layers.Dense(1),
        ]
    )
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
    )
    return model


def train_tf_embeddings(
    X_train,
    y_train,
    input_size,
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    hidden_size=HIDDEN_SIZE,
):
    model = build_tf_model(input_size=input_size, hidden_size=hidden_size)
    history = model.fit(
        X_train,
        y_train,
        epochs=epochs,
        batch_size=batch_size,
        verbose=1,
    )
    return model, history.history


def extract_tf_embeddings(model, X, batch_size=BATCH_SIZE):
    tf = _require_tensorflow()
    embedding_layer = model.get_layer("sequence_embedding")
    embedding_model = tf.keras.Model(inputs=model.inputs, outputs=embedding_layer.output)
    return embedding_model.predict(X, batch_size=batch_size, verbose=0)


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

    print("\n📊 TensorFlow LSTM + XGB Classification Report:\n")
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


def save_sequence_artifacts(tf_model, scaler, xgb_model, metadata):
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    tf_model.save(TF_MODEL_PATH)
    joblib.dump(scaler, TF_SCALER_PATH)
    joblib.dump(xgb_model, TF_SEQUENCE_XGB_PATH)

    with open(TF_METADATA_PATH, "w") as metadata_file:
        json.dump(metadata, metadata_file, indent=2)

    print(f"\n✅ TensorFlow LSTM model saved at: {TF_MODEL_PATH}")
    print(f"✅ TensorFlow scaler saved at: {TF_SCALER_PATH}")
    print(f"✅ TensorFlow sequence XGB model saved at: {TF_SEQUENCE_XGB_PATH}")
    print(f"✅ TensorFlow metadata saved at: {TF_METADATA_PATH}")


def build_arg_parser():
    parser = argparse.ArgumentParser(description="Train the TensorFlow LSTM + XGBoost sequence model.")
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
    with start_run("tensorflow_sequence_training") as (mlflow, _):
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
                "framework": "tensorflow",
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

        tf_model, training_history = train_tf_embeddings(
            X_train_scaled,
            y_train,
            input_size=X_train_scaled.shape[2],
            epochs=epochs,
            batch_size=batch_size,
            hidden_size=hidden_size,
        )

        train_embeddings = extract_tf_embeddings(tf_model, X_train_scaled, batch_size=batch_size)
        test_embeddings = extract_tf_embeddings(tf_model, X_test_scaled, batch_size=batch_size)

        xgb_model = train_sequence_xgb(train_embeddings, y_train)
        _, y_pred, metrics = evaluate_sequence_model(xgb_model, test_embeddings, y_test)
        mlflow.log_metrics(metrics)

        metadata = {
            "framework": "tensorflow",
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
        save_sequence_artifacts(tf_model, scaler, xgb_model, metadata)
        mlflow.log_artifact(TF_MODEL_PATH)
        mlflow.log_artifact(TF_SCALER_PATH)
        mlflow.log_artifact(TF_SEQUENCE_XGB_PATH)
        mlflow.log_artifact(TF_METADATA_PATH)
        log_json_artifact(
            mlflow,
            {
                "classification_report": classification_report(y_test, y_pred, output_dict=True),
                "sequence_metrics": metrics,
                "metadata": metadata,
                "training_history": training_history,
            },
            "tensorflow_sequence_training_report.json",
        )

    return {
        "tf_model_path": TF_MODEL_PATH,
        "scaler_path": TF_SCALER_PATH,
        "sequence_xgb_path": TF_SEQUENCE_XGB_PATH,
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
