import os
import sys

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import xgboost
from src.models.mlflow_utils import log_json_artifact, start_run
from src.models.model_config import FEATURE_COLUMNS

print("XGBoost loaded")

# -----------------------------
# PATH SETUP
# -----------------------------
DATA_PATH = os.path.join(BASE_DIR, "data/processed/final_cleaned.csv")
MODEL_PATH = os.path.join(BASE_DIR, "artifacts/xgb_model.pkl")

# -----------------------------
# LOAD DATA
# -----------------------------

def run_training():
    df = pd.read_csv(DATA_PATH)
    X = df[FEATURE_COLUMNS]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print("Train size:", X_train.shape)
    print("Test size:", X_test.shape)

    print("Train label distribution:\n", y_train.value_counts())
    print("Test label distribution:\n", y_test.value_counts())

    scale_pos_weight = y_train.value_counts()[0] / y_train.value_counts()[1]

    params = {
        "n_estimators": 250,
        "max_depth": 4,
        "learning_rate": 0.05,
        "subsample": 0.85,
        "colsample_bytree": 0.85,
        "min_child_weight": 3,
        "reg_alpha": 0.2,
        "reg_lambda": 1.2,
        "random_state": 42,
        "scale_pos_weight": float(scale_pos_weight),
        "eval_metric": "logloss",
    }

    with start_run("xgboost_training") as (mlflow, _):
        mlflow.log_params(params)
        mlflow.log_param("feature_count", len(FEATURE_COLUMNS))
        mlflow.log_param("train_rows", int(len(X_train)))
        mlflow.log_param("test_rows", int(len(X_test)))

        model = XGBClassifier(**params)
        model.fit(X_train, y_train)

        importance = pd.Series(model.feature_importances_, index=X.columns)
        importance_dict = importance.sort_values(ascending=False).round(6).to_dict()
        print("\nFeature Importance:\n", importance.sort_values(ascending=False))

        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]

        metrics = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred, zero_division=0)),
            "recall": float(recall_score(y_test, y_pred, zero_division=0)),
            "f1": float(f1_score(y_test, y_pred, zero_division=0)),
            "roc_auc": float(roc_auc_score(y_test, y_prob)),
        }
        mlflow.log_metrics(metrics)
        log_json_artifact(
            mlflow,
            {
                "classification_report": classification_report(y_test, y_pred, output_dict=True),
                "feature_importance": importance_dict,
            },
            "xgboost_report.json",
        )

        print("\n📊 Classification Report:\n")
        print(classification_report(y_test, y_pred))
        print("\n🎯 ROC-AUC Score:", metrics["roc_auc"])

        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        joblib.dump(model, MODEL_PATH)
        mlflow.log_artifact(MODEL_PATH)

        print("\n✅ Model saved at:", MODEL_PATH)

    return model


if __name__ == "__main__":
    run_training()
