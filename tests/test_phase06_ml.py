import json
import pathlib
import joblib
import numpy as np
import pytest
from scipy import sparse

WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent
MODELS_DIR = WORKSPACE_ROOT / "models"
METRICS_PATH = WORKSPACE_ROOT / "reports" / "classical_ml_metrics.json"
FIGURE_PATH = WORKSPACE_ROOT / "reports" / "figures" / "ml_models_comparison.png"

EXPECTED_MODELS = [
    "logistic_regression.joblib",
    "random_forest.joblib",
    "linear_svm.joblib",
    "xgboost.joblib"
]


def test_classical_model_checkpoints_exist():
    """Verify all 4 model joblib checkpoints exist and are loadable."""
    for model_filename in EXPECTED_MODELS:
        model_path = MODELS_DIR / model_filename
        assert model_path.exists(), f"Missing model checkpoint: {model_filename}"
        model = joblib.load(model_path)
        assert hasattr(model, "predict"), f"Model {model_filename} missing predict method"


def test_model_inference_on_sparse_vector():
    """Verify all models can infer on a sample 579-dimensional sparse vector."""
    dummy_x = sparse.csr_matrix(np.zeros((1, 579)))
    for model_filename in EXPECTED_MODELS:
        model = joblib.load(MODELS_DIR / model_filename)
        pred = model.predict(dummy_x)
        assert pred.shape == (1,)
        assert pred[0] in [0, 1]


def test_classical_ml_metrics_report():
    """Verify the metrics JSON report contains valid metrics for all models."""
    assert METRICS_PATH.exists()
    assert FIGURE_PATH.exists()
    assert FIGURE_PATH.stat().st_size > 5000

    with open(METRICS_PATH, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    for name in ["Logistic_Regression", "Random_Forest", "Linear_SVM", "XGBoost"]:
        assert name in metrics, f"Missing metrics for {name}"
        m = metrics[name]
        assert m["accuracy"] > 0.75, f"Accuracy too low for {name}: {m['accuracy']}"
        assert m["f1_score"] > 0.80, f"F1 too low for {name}: {m['f1_score']}"
        assert m["roc_auc"] > 0.85, f"ROC-AUC too low for {name}: {m['roc_auc']}"
        assert m["latency_ms"] < 50.0, f"Latency exceeds budget for {name}: {m['latency_ms']} ms"

    # Top performing model (XGBoost) checks
    xgb_m = metrics["XGBoost"]
    assert xgb_m["accuracy"] > 0.90
    assert xgb_m["f1_score"] > 0.91
    assert xgb_m["latency_ms"] < 5.0  # XGBoost is sub-millisecond
