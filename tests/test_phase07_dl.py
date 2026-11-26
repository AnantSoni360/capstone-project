import json
import pathlib
import joblib
import numpy as np
import pytest
import torch

WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent
MODELS_DIR = WORKSPACE_ROOT / "models"
METRICS_PATH = WORKSPACE_ROOT / "reports" / "deep_learning_metrics.json"
FIGURE_PATH = WORKSPACE_ROOT / "reports" / "figures" / "dl_training_curves.png"

from src.models_dl import (
    CharTokenizer, MLPClassifier, Conv1DClassifier,
    BiLSTMClassifier, NumericalAutoencoder
)


def test_dl_checkpoints_exist():
    """Verify all 4 PyTorch model weights and tokenizer exist on disk."""
    expected = [
        "dl_mlp.pt",
        "dl_cnn.pt",
        "dl_bilstm.pt",
        "dl_autoencoder.pt",
        "char_tokenizer.joblib"
    ]
    for fn in expected:
        assert (MODELS_DIR / fn).exists(), f"Missing checkpoint: {fn}"


def test_mlp_inference():
    """Verify MLP model loads and predicts."""
    model = MLPClassifier(input_dim=79)
    model.load_state_dict(torch.load(MODELS_DIR / "dl_mlp.pt", map_location="cpu", weights_only=True))
    model.eval()

    dummy_x = torch.zeros((1, 79), dtype=torch.float32)
    with torch.no_grad():
        out = model(dummy_x)
    assert out.shape == (1, 1)
    assert 0.0 <= out.item() <= 1.0


def test_cnn_inference():
    """Verify 1D-CNN loads and predicts on tokenized input."""
    model = Conv1DClassifier(vocab_size=128, embedding_dim=32, num_filters=64)
    model.load_state_dict(torch.load(MODELS_DIR / "dl_cnn.pt", map_location="cpu", weights_only=True))
    model.eval()

    dummy_tokens = torch.zeros((1, 256), dtype=torch.long)
    with torch.no_grad():
        out = model(dummy_tokens)
    assert out.shape == (1, 1)
    assert 0.0 <= out.item() <= 1.0


def test_bilstm_inference():
    """Verify BiLSTM loads and predicts on tokenized input."""
    model = BiLSTMClassifier(vocab_size=128, embedding_dim=32, hidden_dim=48)
    model.load_state_dict(torch.load(MODELS_DIR / "dl_bilstm.pt", map_location="cpu", weights_only=True))
    model.eval()

    dummy_tokens = torch.zeros((1, 256), dtype=torch.long)
    with torch.no_grad():
        out = model(dummy_tokens)
    assert out.shape == (1, 1)
    assert 0.0 <= out.item() <= 1.0


def test_autoencoder_reconstruction():
    """Verify Autoencoder computes reconstruction error."""
    model = NumericalAutoencoder(input_dim=79, latent_dim=24)
    model.load_state_dict(torch.load(MODELS_DIR / "dl_autoencoder.pt", map_location="cpu", weights_only=True))
    model.eval()

    dummy_x = torch.zeros((2, 79), dtype=torch.float32)
    with torch.no_grad():
        mse = model.compute_reconstruction_error(dummy_x)
    assert mse.shape == (2,)
    assert (mse >= 0.0).all()


def test_deep_learning_metrics_report():
    """Verify metrics JSON and training loss plots exist and meet accuracy constraints."""
    assert METRICS_PATH.exists()
    assert FIGURE_PATH.exists()
    assert FIGURE_PATH.stat().st_size > 5000

    with open(METRICS_PATH, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    # 1. 1D-CNN (Top Performing Architecture)
    cnn = metrics["PyTorch_1D_CNN"]
    assert cnn["accuracy"] > 0.90
    assert cnn["f1_score"] > 0.92
    assert cnn["precision"] > 0.95
    assert cnn["roc_auc"] > 0.95
    assert cnn["latency_ms"] < 5.0

    # 2. MLP
    mlp = metrics["PyTorch_MLP"]
    assert mlp["accuracy"] > 0.80
    assert mlp["f1_score"] > 0.83
    assert mlp["latency_ms"] < 5.0

    # 3. BiLSTM
    lstm = metrics["PyTorch_BiLSTM"]
    assert lstm["accuracy"] > 0.65
    assert lstm["f1_score"] > 0.70
    assert lstm["latency_ms"] < 10.0

    # 4. Autoencoder
    ae = metrics["PyTorch_Autoencoder"]
    assert ae["precision"] > 0.95
    assert ae["false_positive_rate"] < 0.05
