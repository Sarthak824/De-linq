import json
import os

import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split

from src.models.model_config import FEATURE_COLUMNS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "final_cleaned.csv")
METRICS_DIR = os.path.join(BASE_DIR, "artifacts", "metrics")


def load_training_frame(data_path=DATA_PATH):
    df = pd.read_csv(data_path)
    return df, df[FEATURE_COLUMNS], df["label"]


def split_training_frame(X, y, test_size=0.2, random_state=42):
    return train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=y)


def compute_classification_metrics(y_true, y_pred, y_prob):
    report = classification_report(y_true, y_pred, output_dict=True)
    return {
        "roc_auc": round(float(roc_auc_score(y_true, y_prob)), 6),
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 6),
        "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 6),
        "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 6),
        "f1": round(float(f1_score(y_true, y_pred, zero_division=0)), 6),
        "classification_report": report,
    }


def compute_score_metrics(y_true, y_score, threshold=0.5):
    y_pred = (pd.Series(y_score).astype(float) >= threshold).astype(int)
    return compute_classification_metrics(y_true, y_pred, y_score)


def save_metrics(model_name, metrics):
    os.makedirs(METRICS_DIR, exist_ok=True)
    output_path = os.path.join(METRICS_DIR, f"{model_name}_metrics.json")
    with open(output_path, "w") as output_file:
        json.dump(metrics, output_file, indent=2)
    return output_path


def summarize_feature_importance(model, feature_names):
    if not hasattr(model, "feature_importances_"):
        return {}
    importance = pd.Series(model.feature_importances_, index=feature_names)
    return importance.sort_values(ascending=False).round(6).to_dict()
