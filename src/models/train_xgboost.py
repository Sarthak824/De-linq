import os
import sys

import joblib
import pandas as pd
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import xgboost
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

    model = XGBClassifier(
        n_estimators=250,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.85,
        colsample_bytree=0.85,
        min_child_weight=3,
        reg_alpha=0.2,
        reg_lambda=1.2,
        random_state=42,
        scale_pos_weight=scale_pos_weight,
        eval_metric="logloss",
    )

    model.fit(X_train, y_train)

    importance = pd.Series(model.feature_importances_, index=X.columns)
    print("\nFeature Importance:\n", importance.sort_values(ascending=False))

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    print("\n📊 Classification Report:\n")
    print(classification_report(y_test, y_pred))

    print("\n🎯 ROC-AUC Score:", roc_auc_score(y_test, y_prob))

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print("\n✅ Model saved at:", MODEL_PATH)

    return model


if __name__ == "__main__":
    run_training()
