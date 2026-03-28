import json
import os
from contextlib import contextmanager

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DEFAULT_TRACKING_DIR = os.path.join(BASE_DIR, "artifacts", "mlruns")
DEFAULT_TRACKING_DB = os.path.join(BASE_DIR, "artifacts", "mlflow.db")
DEFAULT_TRACKING_URI = f"sqlite:///{DEFAULT_TRACKING_DB}"
DEFAULT_EXPERIMENT_NAME = "delinq_risk_models"


def _require_mlflow():
    try:
        import mlflow
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "MLflow is not installed in the active environment. Install it with "
            "`pip install mlflow` or reinstall from requirements.txt before running training."
        ) from exc

    return mlflow


def configure_mlflow(experiment_name=DEFAULT_EXPERIMENT_NAME, tracking_uri=None):
    mlflow = _require_mlflow()
    resolved_tracking_uri = tracking_uri or os.environ.get("MLFLOW_TRACKING_URI", DEFAULT_TRACKING_URI)
    os.makedirs(DEFAULT_TRACKING_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(DEFAULT_TRACKING_DB), exist_ok=True)
    mlflow.set_tracking_uri(resolved_tracking_uri)
    os.environ.setdefault("MLFLOW_ARTIFACT_URI", DEFAULT_TRACKING_DIR)
    mlflow.set_experiment(experiment_name)
    return mlflow


@contextmanager
def start_run(run_name, experiment_name=DEFAULT_EXPERIMENT_NAME, tracking_uri=None):
    mlflow = configure_mlflow(experiment_name=experiment_name, tracking_uri=tracking_uri)
    with mlflow.start_run(run_name=run_name) as run:
        yield mlflow, run


def log_json_artifact(mlflow, payload, artifact_name):
    artifact_dir = os.path.join(BASE_DIR, "artifacts", "tmp_mlflow")
    os.makedirs(artifact_dir, exist_ok=True)
    artifact_path = os.path.join(artifact_dir, artifact_name)
    with open(artifact_path, "w") as artifact_file:
        json.dump(payload, artifact_file, indent=2)
    mlflow.log_artifact(artifact_path)
    return artifact_path
