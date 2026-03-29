import json
import os
from contextlib import contextmanager

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DEFAULT_TRACKING_DIR = os.path.join(BASE_DIR, "artifacts", "mlruns")
DEFAULT_TRACKING_DB = os.path.join(BASE_DIR, "artifacts", "mlflow.db")
DEFAULT_TRACKING_URI = f"sqlite:///{DEFAULT_TRACKING_DB}"
DEFAULT_EXPERIMENT_NAME = "delinq_risk_models"


class _NoOpRun:
    """Silent stub used when MLflow is not installed."""
    def __enter__(self): return self
    def __exit__(self, *args): pass


class _NoOpMlflow:
    """Mimics the MLflow API surface, doing nothing."""
    def set_tracking_uri(self, *a, **kw): pass
    def set_experiment(self, *a, **kw): pass
    def start_run(self, *a, **kw): return _NoOpRun()
    def log_params(self, *a, **kw): pass
    def log_metrics(self, *a, **kw): pass
    def log_artifact(self, *a, **kw): pass
    def log_metric(self, *a, **kw): pass
    def log_param(self, *a, **kw): pass


def _require_mlflow():
    try:
        import mlflow
        return mlflow
    except ModuleNotFoundError:
        print("⚠️  MLflow not installed — experiment tracking disabled.")
        return _NoOpMlflow()


def configure_mlflow(experiment_name=DEFAULT_EXPERIMENT_NAME, tracking_uri=None):
    mlflow = _require_mlflow()
    if isinstance(mlflow, _NoOpMlflow):
        return mlflow
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
    if isinstance(mlflow, _NoOpMlflow):
        yield mlflow, None
        return
    with mlflow.start_run(run_name=run_name) as run:
        yield mlflow, run


def log_json_artifact(mlflow, payload, artifact_name):
    if isinstance(mlflow, _NoOpMlflow):
        return None
    artifact_dir = os.path.join(BASE_DIR, "artifacts", "tmp_mlflow")
    os.makedirs(artifact_dir, exist_ok=True)
    artifact_path = os.path.join(artifact_dir, artifact_name)
    with open(artifact_path, "w") as artifact_file:
        json.dump(payload, artifact_file, indent=2)
    mlflow.log_artifact(artifact_path)
    return artifact_path
