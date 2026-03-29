import json
import os
import sys

from sklearn.metrics import roc_auc_score
from sklearn.model_selection import ParameterSampler, StratifiedKFold

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.models.training_utils import load_training_frame, split_training_frame
from src.models.train_xgboost import BEST_PARAMS_PATH, build_model

SEARCH_SPACE = {
    "n_estimators": [200, 250, 300, 350],
    "max_depth": [3, 4, 5, 6],
    "learning_rate": [0.03, 0.05, 0.07],
    "subsample": [0.75, 0.85, 0.95],
    "colsample_bytree": [0.75, 0.85, 0.95],
    "min_child_weight": [1, 3, 5],
    "reg_alpha": [0.0, 0.1, 0.2, 0.4],
    "reg_lambda": [0.8, 1.2, 1.6, 2.0],
    "gamma": [0.0, 0.1, 0.2],
}

NUM_SAMPLES = 24
CV_FOLDS = 3


def evaluate_candidate(X_train, y_train, params):
    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=42)
    auc_scores = []

    for train_idx, val_idx in cv.split(X_train, y_train):
        fold_X_train = X_train.iloc[train_idx]
        fold_X_val = X_train.iloc[val_idx]
        fold_y_train = y_train.iloc[train_idx]
        fold_y_val = y_train.iloc[val_idx]
        scale_pos_weight = fold_y_train.value_counts()[0] / fold_y_train.value_counts()[1]

        model = build_model(scale_pos_weight=scale_pos_weight, params=params)
        model.fit(fold_X_train, fold_y_train)
        fold_scores = model.predict_proba(fold_X_val)[:, 1]
        auc_scores.append(roc_auc_score(fold_y_val, fold_scores))

    return sum(auc_scores) / len(auc_scores)


def run_tuning(num_samples=NUM_SAMPLES):
    _, X, y = load_training_frame()
    X_train, X_test, y_train, y_test = split_training_frame(X, y)

    best_params = None
    best_cv_auc = -1.0
    results = []

    sampler = ParameterSampler(SEARCH_SPACE, n_iter=num_samples, random_state=42)
    for candidate in sampler:
        cv_auc = evaluate_candidate(X_train, y_train, candidate)
        result = {
            "params": candidate,
            "cv_roc_auc": round(float(cv_auc), 6),
        }
        results.append(result)
        print(f"Candidate CV ROC-AUC={cv_auc:.6f} params={candidate}")
        if cv_auc > best_cv_auc:
            best_cv_auc = cv_auc
            best_params = candidate

    scale_pos_weight = y_train.value_counts()[0] / y_train.value_counts()[1]
    best_model = build_model(scale_pos_weight=scale_pos_weight, params=best_params)
    best_model.fit(X_train, y_train)
    test_auc = roc_auc_score(y_test, best_model.predict_proba(X_test)[:, 1])

    payload = {
        "best_params": best_params,
        "best_cv_roc_auc": round(float(best_cv_auc), 6),
        "test_roc_auc": round(float(test_auc), 6),
        "num_samples": num_samples,
        "cv_folds": CV_FOLDS,
        "search_results": sorted(results, key=lambda item: item["cv_roc_auc"], reverse=True),
    }

    os.makedirs(os.path.dirname(BEST_PARAMS_PATH), exist_ok=True)
    with open(BEST_PARAMS_PATH, "w") as output_file:
        json.dump(best_params, output_file, indent=2)

    summary_path = os.path.join(BASE_DIR, "artifacts", "metrics", "xgboost_tuning_results.json")
    os.makedirs(os.path.dirname(summary_path), exist_ok=True)
    with open(summary_path, "w") as output_file:
        json.dump(payload, output_file, indent=2)

    print("\nBest params:", best_params)
    print("Best CV ROC-AUC:", payload["best_cv_roc_auc"])
    print("Test ROC-AUC with tuned params:", payload["test_roc_auc"])
    print("Saved best params to:", BEST_PARAMS_PATH)
    print("Saved tuning summary to:", summary_path)


if __name__ == "__main__":
    run_tuning()
