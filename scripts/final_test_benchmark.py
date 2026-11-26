"""
Final Model Benchmark on Untouched Frozen Test Set (Phase 09)
Evaluates all 9 detection systems against test_frozen.csv (3,842 requests).
Outputs final publication metrics table, JSON report, and master benchmark plot.
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
from scipy import sparse
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix
)
import torch
from torch.utils.data import TensorDataset, DataLoader

from src.rules import TraditionalRuleEngine
from src.features import FeatureExtractor
from src.models_dl import (
    CharTokenizer, MLPClassifier, Conv1DClassifier,
    BiLSTMClassifier, NumericalAutoencoder
)

PROCESSED_DIR = WORKSPACE_ROOT / "data" / "processed"
MODELS_DIR = WORKSPACE_ROOT / "models"
FIGURES_DIR = WORKSPACE_ROOT / "reports" / "figures"
CSV_REPORT_PATH = WORKSPACE_ROOT / "reports" / "final_model_benchmark_test_set.csv"
JSON_REPORT_PATH = WORKSPACE_ROOT / "reports" / "final_model_benchmark.json"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)
device = torch.device("cpu")


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray, latencies: List[float]) -> Dict[str, Any]:
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()

    accuracy = float(accuracy_score(y_true, y_pred))
    precision = float(precision_score(y_true, y_pred, zero_division=0))
    recall = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))

    try:
        roc_auc = float(roc_auc_score(y_true, y_prob))
    except Exception:
        roc_auc = 0.5

    try:
        pr_auc = float(average_precision_score(y_true, y_prob))
    except Exception:
        pr_auc = 0.5

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
        "latency_ms": round(float(np.mean(latencies)), 3),
        "confusion_matrix": {
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "true_positives": int(tp)
        }
    }


def main():
    print("[Phase 09] Unfreezing final test set for empirical evaluation...")
    test_df = pd.read_csv(PROCESSED_DIR / "test_frozen.csv")
    y_test = np.load(PROCESSED_DIR / "y_test.npy").astype(int)

    X_test_comb = sparse.load_npz(PROCESSED_DIR / "X_test_combined.npz")
    X_test_num = np.load(PROCESSED_DIR / "X_test_num.npy")

    print(f"Test Set Count: {len(test_df)} requests.")

    benchmark_results = {}

    # 1. Traditional Rule-Based WAF
    print("\n--- Evaluating Traditional Rule-Based WAF ---")
    rule_engine = TraditionalRuleEngine()
    eval_rules_df = rule_engine.evaluate_dataframe(test_df)
    y_pred_rule = (eval_rules_df["rule_verdict"] == "BLOCK").astype(int).values
    rule_scores = eval_rules_df["rule_score"].values
    rule_latencies = eval_rules_df["rule_latency_ms"].tolist()
    benchmark_results["Traditional_Rule_WAF"] = compute_metrics(y_test, y_pred_rule, rule_scores, rule_latencies)

    # 2. Classical ML Models
    ml_models = ["logistic_regression", "random_forest", "linear_svm", "xgboost"]
    for mname in ml_models:
        print(f"\n--- Evaluating {mname} ---")
        model = joblib.load(MODELS_DIR / f"{mname}.joblib")

        # Measure latency
        latencies = []
        for i in range(min(400, X_test_comb.shape[0])):
            t0 = time.perf_counter()
            _ = model.predict(X_test_comb[i])
            latencies.append((time.perf_counter() - t0) * 1000.0)

        y_pred = model.predict(X_test_comb)
        if hasattr(model, "predict_proba"):
            y_prob = model.predict_proba(X_test_comb)[:, 1]
        elif hasattr(model, "decision_function"):
            df = model.decision_function(X_test_comb)
            y_prob = 1.0 / (1.0 + np.exp(-df))
        else:
            y_prob = y_pred.astype(float)

        label = mname.replace("_", " ").title().replace(" ", "_")
        benchmark_results[label] = compute_metrics(y_test, y_pred, y_prob, latencies)

    # 3. PyTorch Deep Learning Models
    tokenizer = joblib.load(MODELS_DIR / "char_tokenizer.joblib")
    X_test_tokens = tokenizer.encode_batch(test_df["full_payload"].fillna("").tolist())
    X_test_num_t = torch.tensor(X_test_num, dtype=torch.float32)

    # PyTorch MLP
    print("\n--- Evaluating PyTorch MLP ---")
    mlp = MLPClassifier(input_dim=79).to(device)
    mlp.load_state_dict(torch.load(MODELS_DIR / "dl_mlp.pt", map_location=device, weights_only=True))
    mlp.eval()
    with torch.no_grad():
        mlp_probs = mlp(X_test_num_t).squeeze(-1).numpy()
    mlp_preds = (mlp_probs >= 0.50).astype(int)
    mlp_latencies = []
    with torch.no_grad():
        for i in range(300):
            t0 = time.perf_counter()
            _ = mlp(X_test_num_t[i:i+1])
            mlp_latencies.append((time.perf_counter() - t0) * 1000.0)
    benchmark_results["PyTorch_MLP"] = compute_metrics(y_test, mlp_preds, mlp_probs, mlp_latencies)

    # PyTorch 1D-CNN
    print("\n--- Evaluating PyTorch 1D-CNN ---")
    cnn = Conv1DClassifier(vocab_size=128, embedding_dim=32, num_filters=64).to(device)
    cnn.load_state_dict(torch.load(MODELS_DIR / "dl_cnn.pt", map_location=device, weights_only=True))
    cnn.eval()
    with torch.no_grad():
        cnn_probs = cnn(X_test_tokens).squeeze(-1).numpy()
    cnn_preds = (cnn_probs >= 0.50).astype(int)
    cnn_latencies = []
    with torch.no_grad():
        for i in range(300):
            t0 = time.perf_counter()
            _ = cnn(X_test_tokens[i:i+1])
            cnn_latencies.append((time.perf_counter() - t0) * 1000.0)
    benchmark_results["PyTorch_1D_CNN"] = compute_metrics(y_test, cnn_preds, cnn_probs, cnn_latencies)

    # PyTorch BiLSTM
    print("\n--- Evaluating PyTorch BiLSTM ---")
    bilstm = BiLSTMClassifier(vocab_size=128, embedding_dim=32, hidden_dim=48).to(device)
    bilstm.load_state_dict(torch.load(MODELS_DIR / "dl_bilstm.pt", map_location=device, weights_only=True))
    bilstm.eval()
    with torch.no_grad():
        bilstm_probs = bilstm(X_test_tokens).squeeze(-1).numpy()
    bilstm_preds = (bilstm_probs >= 0.50).astype(int)
    bilstm_latencies = []
    with torch.no_grad():
        for i in range(150):
            t0 = time.perf_counter()
            _ = bilstm(X_test_tokens[i:i+1])
            bilstm_latencies.append((time.perf_counter() - t0) * 1000.0)
    benchmark_results["PyTorch_BiLSTM"] = compute_metrics(y_test, bilstm_preds, bilstm_probs, bilstm_latencies)

    # PyTorch Autoencoder
    print("\n--- Evaluating PyTorch Autoencoder ---")
    ae = NumericalAutoencoder(input_dim=79, latent_dim=24).to(device)
    ae.load_state_dict(torch.load(MODELS_DIR / "dl_autoencoder.pt", map_location=device, weights_only=True))
    ae.eval()
    with torch.no_grad():
        ae_mse = ae.compute_reconstruction_error(X_test_num_t).numpy()
    with open(WORKSPACE_ROOT / "reports" / "deep_learning_metrics.json", "r") as f:
        ae_thresh = json.load(f)["PyTorch_Autoencoder"]["calibrated_threshold"]
    ae_preds = (ae_mse >= ae_thresh).astype(int)
    ae_norm_probs = (ae_mse - ae_mse.min()) / (ae_mse.max() - ae_mse.min() + 1e-8)
    ae_latencies = []
    with torch.no_grad():
        for i in range(300):
            t0 = time.perf_counter()
            _ = ae.compute_reconstruction_error(X_test_num_t[i:i+1])
            ae_latencies.append((time.perf_counter() - t0) * 1000.0)
    benchmark_results["PyTorch_Autoencoder"] = compute_metrics(y_test, ae_preds, ae_norm_probs, ae_latencies)

    # Generate Tabular CSV Summary
    rows = []
    for model_name, m in benchmark_results.items():
        rows.append({
            "System": model_name.replace("_", " "),
            "Accuracy": m["accuracy"],
            "Precision": m["precision"],
            "Recall": m["recall"],
            "F1_Score": m["f1_score"],
            "ROC_AUC": m["roc_auc"],
            "PR_AUC": m["pr_auc"],
            "False_Positive_Rate": m["false_positive_rate"],
            "False_Negative_Rate": m["false_negative_rate"],
            "Latency_ms": m["latency_ms"]
        })
    df_results = pd.DataFrame(rows).sort_values(by="F1_Score", ascending=False)
    df_results.to_csv(CSV_REPORT_PATH, index=False)

    # Save JSON report
    with open(JSON_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(benchmark_results, f, indent=2)

    # Master Benchmark Plot
    fig, ax = plt.subplots(figsize=(14, 6))
    df_melt = pd.melt(df_results, id_vars=["System"], value_vars=["Accuracy", "Precision", "Recall", "F1_Score"], var_name="Metric", value_name="Score")
    sns.barplot(data=df_melt, x="System", y="Score", hue="Metric", palette="tab10", ax=ax)
    ax.set_title("Master Final Benchmark Across All Systems (Untouched 15% Frozen Test Set - 3,842 requests)", fontsize=13, weight="bold")
    ax.set_xlabel("Detection Engine")
    ax.set_ylabel("Score")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=25, ha="right")
    ax.set_ylim(0.0, 1.1)
    ax.legend(loc="lower right")
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "master_model_benchmark.png", dpi=300)
    plt.close(fig)

    print(f"\n[Phase 09] Master Benchmark CSV saved to: {CSV_REPORT_PATH}")
    print(f"[Phase 09] Master Benchmark JSON saved to: {JSON_REPORT_PATH}")
    print(f"[Phase 09] Master Benchmark Plot saved to: {FIGURES_DIR / 'master_model_benchmark.png'}")
    print("\n=== FINAL TEST BENCHMARK RANKINGS ===")
    print(df_results.to_string(index=False))


if __name__ == "__main__":
    main()
