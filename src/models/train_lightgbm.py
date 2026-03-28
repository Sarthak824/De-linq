import os
import sys

import joblib

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

MODEL_PATH = os.path.join(BASE_DIR, "artifacts", "lightgbm_model.pkl")


def _require_lightgbm():
    try:
        from lightgbm import LGBMClassifier
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "LightGBM is not installed in the active environment. Add it with "
            "`pip install lightgbm` or install from requirements.txt before running this benchmark."
        ) from exc

    return LGBMClassifier


def run_training():
    LGBMClassifier = _require_lightgbm()

    _, X, y = load_training_frame()
    X_train, X_test, y_train, y_test = split_training_frame(X, y)

    scale_pos_weight = y_train.value_counts()[0] / y_train.value_counts()[1]
    model = LGBMClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.85,
        colsample_bytree=0.85,
        reg_alpha=0.2,
        reg_lambda=1.2,
        random_state=42,
        scale_pos_weight=scale_pos_weight,
        objective="binary",
        verbose=-1,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    metrics = compute_classification_metrics(y_test, y_pred, y_prob)
    metrics["feature_importance"] = summarize_feature_importance(model, X.columns)

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    metrics_path = save_metrics("lightgbm", metrics)

    print("✅ LightGBM model saved at:", MODEL_PATH)
    print("✅ Metrics saved at:", metrics_path)
    print("🎯 ROC-AUC Score:", metrics["roc_auc"])

    return model


if __name__ == "__main__":
    run_training()
