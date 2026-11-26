"""
PyTorch Deep Learning Training & Evaluation Pipeline (Phase 07)
Trains MLP, 1D-CNN, BiLSTM, and Autoencoder.
Evaluates on validation split, benchmarks latency, and saves model checkpoints.
"""

import json
import pathlib
import sys
import time
from typing import Dict, Any, List

WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix
)
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader

from src.models_dl import (
    CharTokenizer, MLPClassifier, Conv1DClassifier,
    BiLSTMClassifier, NumericalAutoencoder
)

PROCESSED_DIR = WORKSPACE_ROOT / "data" / "processed"
MODELS_DIR = WORKSPACE_ROOT / "models"
FIGURES_DIR = WORKSPACE_ROOT / "reports" / "figures"
METRICS_PATH = WORKSPACE_ROOT / "reports" / "deep_learning_metrics.json"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Device selection: automatic CPU / CUDA check
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"[Phase 07] PyTorch execution device: {device}")


def evaluate_torch_model(model: nn.Module, X_tensor: torch.Tensor, y_true: np.ndarray, is_autoencoder: bool = False, ae_threshold: float = 0.0) -> Dict[str, Any]:
    """Evaluates a PyTorch model and computes cybersecurity metrics and latency."""
    model.eval()
    batch_size = 256
    dataset = TensorDataset(X_tensor)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

    probs = []
    with torch.no_grad():
        for (batch_x,) in loader:
            batch_x = batch_x.to(device)
            if is_autoencoder:
                mse = model.compute_reconstruction_error(batch_x)
                probs.extend(mse.cpu().numpy())
            else:
                out = model(batch_x).squeeze(-1)
                probs.extend(out.cpu().numpy())

    probs = np.array(probs)

    # Measure latency on single request samples (average over 300 samples)
    latencies = []
    sample_indices = np.random.choice(len(X_tensor), min(300, len(X_tensor)), replace=False)
    with torch.no_grad():
        for idx in sample_indices:
            single_x = X_tensor[idx:idx+1].to(device)
            t0 = time.perf_counter()
            _ = model(single_x)
            latencies.append((time.perf_counter() - t0) * 1000.0)
    avg_latency = float(np.mean(latencies))

    if is_autoencoder:
        y_pred = (probs >= ae_threshold).astype(int)
        # Normalize MSE to 0..1 range for AUC calculation
        norm_scores = (probs - probs.min()) / (probs.max() - probs.min() + 1e-8)
        y_prob = norm_scores
    else:
        y_pred = (probs >= 0.50).astype(int)
        y_prob = probs

    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()

    accuracy = float(accuracy_score(y_true, y_pred))
    precision = float(precision_score(y_true, y_pred, zero_division=0))
    recall = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    roc_auc = float(roc_auc_score(y_true, y_prob))
    pr_auc = float(average_precision_score(y_true, y_prob))

    fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
    fnr = float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0

    return {
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "roc_auc": round(roc_auc, 4),
        "pr_auc": round(pr_auc, 4),
        "false_positive_rate": round(fpr, 4),
        "false_negative_rate": round(fnr, 4),
        "latency_ms": round(avg_latency, 3),
        "confusion_matrix": {
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "true_positives": int(tp)
        }
    }


def train_model(model: nn.Module, loader: DataLoader, criterion: nn.Module, optimizer: torch.optim.Optimizer, epochs: int, name: str) -> List[float]:
    """Generic training loop tracking loss per epoch."""
    losses = []
    for epoch in range(1, epochs + 1):
        model.train()
        epoch_loss = 0.0
        for batch_x, batch_y in loader:
            batch_x = batch_x.to(device)
            batch_y = batch_y.to(device)

            optimizer.zero_grad()
            if isinstance(model, NumericalAutoencoder):
                recon = model(batch_x)
                loss = criterion(recon, batch_x)
            else:
                preds = model(batch_x).squeeze(-1)
                loss = criterion(preds, batch_y)

            loss.backward()
            optimizer.step()
            epoch_loss += loss.item() * batch_x.size(0)

        epoch_loss /= len(loader.dataset)
        losses.append(epoch_loss)
        if epoch % 2 == 0 or epoch == epochs:
            print(f"[{name}] Epoch {epoch}/{epochs} - Loss: {epoch_loss:.4f}")
    return losses


def main():
    torch.manual_seed(42)
    np.random.seed(42)

    print("[Phase 07] Loading data...")
    train_df = pd.read_csv(PROCESSED_DIR / "train.csv")
    val_df = pd.read_csv(PROCESSED_DIR / "val.csv")

    X_train_num = np.load(PROCESSED_DIR / "X_train_num.npy")
    y_train = np.load(PROCESSED_DIR / "y_train.npy").astype(np.float32)

    X_val_num = np.load(PROCESSED_DIR / "X_val_num.npy")
    y_val = np.load(PROCESSED_DIR / "y_val.npy").astype(np.float32)

    # Character-level tokenization for CNN and BiLSTM
    tokenizer = CharTokenizer(max_length=256)
    joblib.dump(tokenizer, MODELS_DIR / "char_tokenizer.joblib")

    print("Tokenizing payloads for CNN and LSTM sequences...")
    X_train_tokens = tokenizer.encode_batch(train_df["full_payload"].fillna("").tolist())
    X_val_tokens = tokenizer.encode_batch(val_df["full_payload"].fillna("").tolist())

    X_train_num_t = torch.tensor(X_train_num, dtype=torch.float32)
    y_train_t = torch.tensor(y_train, dtype=torch.float32)
    X_val_num_t = torch.tensor(X_val_num, dtype=torch.float32)

    results = {}
    loss_curves = {}

    # ==========================================
    # 1. Multi-Layer Perceptron (MLP)
    # ==========================================
    print("\n--- Training PyTorch MLP (79 Numerical Features) ---")
    mlp_loader = DataLoader(TensorDataset(X_train_num_t, y_train_t), batch_size=128, shuffle=True)
    mlp_model = MLPClassifier(input_dim=79).to(device)
    mlp_opt = torch.optim.Adam(mlp_model.parameters(), lr=0.001, weight_decay=1e-4)
    mlp_crit = nn.BCELoss()

    t0 = time.time()
    mlp_losses = train_model(mlp_model, mlp_loader, mlp_crit, mlp_opt, epochs=8, name="MLP")
    mlp_metrics = evaluate_torch_model(mlp_model, X_val_num_t, y_val.astype(int))
    mlp_metrics["training_time_seconds"] = round(time.time() - t0, 2)
    results["PyTorch_MLP"] = mlp_metrics
    loss_curves["MLP"] = mlp_losses
    torch.save(mlp_model.state_dict(), MODELS_DIR / "dl_mlp.pt")
    print(f"MLP Val F1: {mlp_metrics['f1_score']}, Accuracy: {mlp_metrics['accuracy']}, Latency: {mlp_metrics['latency_ms']} ms")

    # ==========================================
    # 2. 1D-CNN (Character Sequences)
    # ==========================================
    print("\n--- Training PyTorch 1D-CNN (Character Sequences) ---")
    cnn_loader = DataLoader(TensorDataset(X_train_tokens, y_train_t), batch_size=128, shuffle=True)
    cnn_model = Conv1DClassifier(vocab_size=128, embedding_dim=32, num_filters=64).to(device)
    cnn_opt = torch.optim.Adam(cnn_model.parameters(), lr=0.001)
    cnn_crit = nn.BCELoss()

    t0 = time.time()
    cnn_losses = train_model(cnn_model, cnn_loader, cnn_crit, cnn_opt, epochs=6, name="1D-CNN")
    cnn_metrics = evaluate_torch_model(cnn_model, X_val_tokens, y_val.astype(int))
    cnn_metrics["training_time_seconds"] = round(time.time() - t0, 2)
    results["PyTorch_1D_CNN"] = cnn_metrics
    loss_curves["1D-CNN"] = cnn_losses
    torch.save(cnn_model.state_dict(), MODELS_DIR / "dl_cnn.pt")
    print(f"1D-CNN Val F1: {cnn_metrics['f1_score']}, Accuracy: {cnn_metrics['accuracy']}, Latency: {cnn_metrics['latency_ms']} ms")

    # ==========================================
    # 3. BiLSTM (Character Sequences)
    # ==========================================
    print("\n--- Training PyTorch BiLSTM (Character Sequences) ---")
    lstm_loader = DataLoader(TensorDataset(X_train_tokens, y_train_t), batch_size=128, shuffle=True)
    bilstm_model = BiLSTMClassifier(vocab_size=128, embedding_dim=32, hidden_dim=48).to(device)
    bilstm_opt = torch.optim.Adam(bilstm_model.parameters(), lr=0.001)
    bilstm_crit = nn.BCELoss()

    t0 = time.time()
    bilstm_losses = train_model(bilstm_model, lstm_loader, bilstm_crit, bilstm_opt, epochs=4, name="BiLSTM")
    bilstm_metrics = evaluate_torch_model(bilstm_model, X_val_tokens, y_val.astype(int))
    bilstm_metrics["training_time_seconds"] = round(time.time() - t0, 2)
    results["PyTorch_BiLSTM"] = bilstm_metrics
    loss_curves["BiLSTM"] = bilstm_losses
    torch.save(bilstm_model.state_dict(), MODELS_DIR / "dl_bilstm.pt")
    print(f"BiLSTM Val F1: {bilstm_metrics['f1_score']}, Accuracy: {bilstm_metrics['accuracy']}, Latency: {bilstm_metrics['latency_ms']} ms")

    # ==========================================
    # 4. Unsupervised Autoencoder (Normal Traffic Only)
    # ==========================================
    print("\n--- Training PyTorch Numerical Autoencoder (Normal Traffic Only) ---")
    normal_mask = (y_train == 0)
    X_train_normal = X_train_num_t[normal_mask]
    ae_loader = DataLoader(TensorDataset(X_train_normal, X_train_normal), batch_size=64, shuffle=True)

    ae_model = NumericalAutoencoder(input_dim=79, latent_dim=24).to(device)
    ae_opt = torch.optim.Adam(ae_model.parameters(), lr=0.001)
    ae_crit = nn.MSELoss()

    t0 = time.time()
    ae_losses = train_model(ae_model, ae_loader, ae_crit, ae_opt, epochs=10, name="Autoencoder")

    # Calibrate anomaly threshold on normal validation samples (99th percentile targeting FPR <= 1%)
    val_normal_mask = (y_val == 0)
    X_val_normal = X_val_num_t[val_normal_mask].to(device)
    with torch.no_grad():
        norm_val_mse = ae_model.compute_reconstruction_error(X_val_normal).cpu().numpy()
    calibrated_threshold = float(np.percentile(norm_val_mse, 99.0))
    print(f"Calibrated Autoencoder Anomaly Threshold: {calibrated_threshold:.4f}")

    ae_metrics = evaluate_torch_model(ae_model, X_val_num_t, y_val.astype(int), is_autoencoder=True, ae_threshold=calibrated_threshold)
    ae_metrics["training_time_seconds"] = round(time.time() - t0, 2)
    ae_metrics["calibrated_threshold"] = round(calibrated_threshold, 4)
    results["PyTorch_Autoencoder"] = ae_metrics
    loss_curves["Autoencoder"] = ae_losses
    torch.save(ae_model.state_dict(), MODELS_DIR / "dl_autoencoder.pt")
    print(f"Autoencoder Val F1: {ae_metrics['f1_score']}, Accuracy: {ae_metrics['accuracy']}, Latency: {ae_metrics['latency_ms']} ms")

    # Plot Training Loss Curves
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    for ax, (model_name, losses) in zip(axes.flatten(), loss_curves.items()):
        ax.plot(range(1, len(losses) + 1), losses, marker="o", color="#e67e22")
        ax.set_title(f"{model_name} Training Loss", weight="bold")
        ax.set_xlabel("Epoch")
        ax.set_ylabel("Loss")
        ax.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "dl_training_curves.png", dpi=300)
    plt.close(fig)

    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\n[Phase 07] Deep Learning Evaluation saved to: {METRICS_PATH}")
    print("\n=== DEEP LEARNING BENCHMARK SUMMARY ===")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
