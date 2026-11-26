import json
import pathlib
import joblib
import numpy as np
import pytest
from scipy import sparse

WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent
MODELS_DIR = WORKSPACE_ROOT / "models"
FIGURES_DIR = WORKSPACE_ROOT / "reports" / "figures"
REPORT_PATH = WORKSPACE_ROOT / "reports" / "xai_sample_explanations.json"

from src.features import FeatureExtractor
from src.explainability import WAFTreeSHAPExplainer, WAFPayloadExplainer


def test_tree_shap_single_explanation():
    """Verify WAFTreeSHAPExplainer computes local attribution."""
    extractor = FeatureExtractor.load(str(MODELS_DIR / "feature_extractor.joblib"))
    xgb_model = joblib.load(MODELS_DIR / "xgboost.joblib")

    tfidf_names = [f"tfidf_{ng}" for ng in extractor.tfidf_vectorizer.get_feature_names_out()]
    all_names = extractor.feature_names + tfidf_names
    explainer = WAFTreeSHAPExplainer(xgb_model, all_names)

    dummy_x = sparse.csr_matrix(np.zeros((1, len(all_names))))
    res = explainer.explain_single(dummy_x, top_k=5)

    assert "base_value" in res
    assert "top_contributing_features" in res
    assert "benign_stabilizing_features" in res
    assert "all_top_k" in res
    assert len(res["all_top_k"]) == 5


def test_payload_explainer_generates_html():
    """Verify WAFPayloadExplainer generates HTML markup and identifies tokens."""
    dummy_predict = lambda payloads: np.array([0.95 if "script" in p else 0.05 for p in payloads])
    explainer = WAFPayloadExplainer(predict_fn=dummy_predict)

    res = explainer.explain_payload("search?q=script")
    assert "highlighted_html" in res
    assert "<span" in res["highlighted_html"]
    assert "base_malicious_score" in res


def test_xai_artifacts_exist():
    """Verify SHAP summary plot and case study JSON exist."""
    assert (FIGURES_DIR / "shap_summary.png").exists()
    assert (FIGURES_DIR / "shap_summary.png").stat().st_size > 5000
    assert REPORT_PATH.exists()

    with open(REPORT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "case_studies" in data
    assert "SQL_INJECTION" in data["case_studies"]
    assert "XSS" in data["case_studies"]
    assert "BENIGN" in data["case_studies"]
    assert data["case_studies"]["SQL_INJECTION"]["verdict"] == "BLOCK"
    assert data["case_studies"]["BENIGN"]["verdict"] == "ALLOW"
