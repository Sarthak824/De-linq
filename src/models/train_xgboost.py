import os
import sys
import json

import joblib
from xgboost import XGBClassifier

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.models.training_utils import (
    compute_classification_metrics,
    load_training_frame,
    save_metrics,
    split_training_frame,
    summarize_feature_importance,
)

print("XGBoost loaded")

MODEL_PATH = os.path.join(BASE_DIR, "artifacts/xgb_model.pkl")
BEST_PARAMS_PATH = os.path.join(BASE_DIR, "artifacts", "xgb_best_params.json")

DEFAULT_XGB_PARAMS = {
    "n_estimators": 250,
    "max_depth": 4,
    "learning_rate": 0.05,
    "subsample": 0.85,
    "colsample_bytree": 0.85,
    "min_child_weight": 3,
    "reg_alpha": 0.2,
    "reg_lambda": 1.2,
    "gamma": 0.0,
}


def load_best_params(best_params_path=BEST_PARAMS_PATH):
    if not os.path.exists(best_params_path):
        return DEFAULT_XGB_PARAMS.copy()

    with open(best_params_path) as input_file:
        params = json.load(input_file)

    merged = DEFAULT_XGB_PARAMS.copy()
    merged.update(params)
    return merged


def build_model(scale_pos_weight, params=None):
    resolved_params = DEFAULT_XGB_PARAMS.copy()
    if params:
        resolved_params.update(params)

    return XGBClassifier(
        **resolved_params,
        random_state=42,
        scale_pos_weight=scale_pos_weight,
        eval_metric="logloss",
    )

def run_training():
    _, X, y = load_training_frame()
    X_train, X_test, y_train, y_test = split_training_frame(X, y)
    print("Train size:", X_train.shape)
    print("Test size:", X_test.shape)

    print("Train label distribution:\n", y_train.value_counts())
    print("Test label distribution:\n", y_test.value_counts())

    scale_pos_weight = y_train.value_counts()[0] / y_train.value_counts()[1]
    best_params = load_best_params()
    print("Training params:", best_params)

    model = build_model(scale_pos_weight=scale_pos_weight, params=best_params)

    model.fit(X_train, y_train)

    importance = summarize_feature_importance(model, X.columns)
    print("\nFeature Importance:\n", importance)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    metrics = compute_classification_metrics(y_test, y_pred, y_prob)

    print("\n📊 Classification Report:\n")
    print(metrics["classification_report"])
    print("\n🎯 ROC-AUC Score:", metrics["roc_auc"])

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    metrics_path = save_metrics("xgboost", metrics)

    print("\n✅ Model saved at:", MODEL_PATH)
    print("✅ Metrics saved at:", metrics_path)

    return model


if __name__ == "__main__":
    run_training()
