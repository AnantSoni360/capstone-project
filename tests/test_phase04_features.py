import json
import pathlib
import numpy as np
import pytest
from scipy import sparse

WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent
PROCESSED_DIR = WORKSPACE_ROOT / "data" / "processed"
MODELS_DIR = WORKSPACE_ROOT / "models"
FIGURES_DIR = WORKSPACE_ROOT / "reports" / "figures"
PIPELINE_PATH = MODELS_DIR / "feature_extractor.joblib"
METADATA_PATH = PROCESSED_DIR / "feature_metadata.json"

from src.features import FeatureExtractor


def test_pipeline_saved_and_inference_ready():
    """Verify FeatureExtractor can be loaded and transforms single requests."""
    assert PIPELINE_PATH.exists(), f"Missing pipeline file: {PIPELINE_PATH}"
    extractor = FeatureExtractor.load(str(PIPELINE_PATH))
    assert extractor.is_fitted, "Loaded extractor is not fitted"
    assert len(extractor.feature_names) > 50, "Expected >50 handcrafted features"

    sample_record = {
        "method": "GET",
        "raw_url": "http://localhost:8080/search?q=shoes HTTP/1.1",
        "decoded_path": "/search",
        "decoded_query": "q=shoes",
        "decoded_body": "",
        "full_payload": "/search ?q=shoes",
        "param_count": 1
    }
    X_num, X_tfidf, X_comb = extractor.transform_single(sample_record)

    assert X_num.shape[0] == 1
    assert X_num.shape[1] == len(extractor.feature_names)
    assert X_tfidf.shape[0] == 1
    assert X_comb.shape[0] == 1
    assert X_comb.shape[1] == len(extractor.feature_names) + 500


def test_sparse_matrices_and_dimensions():
    """Verify all saved matrices exist and have expected shapes."""
    X_train_comb = sparse.load_npz(PROCESSED_DIR / "X_train_combined.npz")
    X_val_comb = sparse.load_npz(PROCESSED_DIR / "X_val_combined.npz")
    X_test_comb = sparse.load_npz(PROCESSED_DIR / "X_test_combined.npz")

    y_train = np.load(PROCESSED_DIR / "y_train.npy")
    y_val = np.load(PROCESSED_DIR / "y_val.npy")
    y_test = np.load(PROCESSED_DIR / "y_test.npy")

    assert X_train_comb.shape == (17925, 579)
    assert X_val_comb.shape == (3841, 579)
    assert X_test_comb.shape == (3842, 579)

    assert len(y_train) == 17925
    assert len(y_val) == 3841
    assert len(y_test) == 3842


def test_feature_selection_artifacts():
    """Verify feature importance plot and metadata JSON exist."""
    assert (FIGURES_DIR / "feature_importance.png").exists()
    assert (FIGURES_DIR / "feature_importance.png").stat().st_size > 5000
    assert METADATA_PATH.exists()

    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)

    assert "top_10_features_by_rf_importance" in meta
    assert len(meta["top_10_features_by_rf_importance"]) == 10
