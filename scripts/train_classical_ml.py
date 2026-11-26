"""
Phase 06: Classical Machine Learning Training & Cross-Validation Pipeline
Trains and evaluates Logistic Regression, Random Forest, Linear SVM, and XGBoost
using stratified cross-validation on train and validation evaluation.
"""

import json
import pathlib
import sys
import time
from typing import Dict, Any, List, Tuple
import joblib
import matplotlib.pyplot as plt
import numpy as np
from scipy import sparse
import seaborn as sns
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix, roc_curve, precision_recall_curve
)
from sklearn.model_selection import StratifiedKFold
import xgboost as xgb

WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent
PROCESSED_DIR = WORKSPACE_ROOT / "data" / "processed"
MODELS_DIR = WORKSPACE_ROOT / "models"
FIGURES_DIR = WORKSPACE_ROOT / "reports" / "figures"
METRICS_PATH = WORKSPACE_ROOT / "reports" / "classical_ml_metrics.json"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def evaluate_classifier(model, X_val, y_val) -> Dict[str, Any]:
    """Calculate accuracy, precision, recall, F1, FPR, FNR, ROC-AUC, PR-AUC, and latency."""
    # Measure inference latency over 500 samples
    sample_indices = np.random.choice(X_val.shape[0], min(500, X_val.shape[0]), replace=False)
    X_sample = X_val[sample_indices]

    latencies = []
    for i in range(X_sample.shape[0]):
        t0 = time.perf_counter()
        _ = model.predict(X_sample[i])
        latencies.append((time.perf_counter() - t0) * 1000.0)
    avg_latency = float(np.mean(latencies))

    # Full validation predictions
    y_pred = model.predict(X_val)

    # Probabilities for AUC
    if hasattr(model, "predict_proba"):
        y_prob = model.predict_proba(X_val)[:, 1]
    elif hasattr(model, "decision_function"):
        df = model.decision_function(X_val)
        y_prob = 1.0 / (1.0 + np.exp(-df))
    else:
        y_prob = y_pred.astype(float)

    cm = confusion_matrix(y_val, y_pred)
    tn, fp, fn, tp = cm.ravel()

    accuracy = float(accuracy_score(y_val, y_pred))
    precision = float(precision_score(y_val, y_pred, zero_division=0))
    recall = float(recall_score(y_val, y_pred, zero_division=0))
    f1 = float(f1_score(y_val, y_pred, zero_division=0))
    roc_auc = float(roc_auc_score(y_val, y_prob))
    pr_auc = float(average_precision_score(y_val, y_prob))

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


def main():
    print("[Phase 06] Loading precomputed feature matrices...")
    X_train = sparse.load_npz(PROCESSED_DIR / "X_train_combined.npz")
    y_train = np.load(PROCESSED_DIR / "y_train.npy")

    X_val = sparse.load_npz(PROCESSED_DIR / "X_val_combined.npz")
    y_val = np.load(PROCESSED_DIR / "y_val.npy")

    print(f"Train Shape: {X_train.shape}, Val Shape: {X_val.shape}")

    models = {
        "Logistic_Regression": LogisticRegression(max_iter=1000, random_state=42, C=1.0),
        "Random_Forest": RandomForestClassifier(n_estimators=100, max_depth=16, random_state=42, n_jobs=-1),
        "Linear_SVM": SGDClassifier(loss="log_loss", penalty="l2", max_iter=1000, random_state=42),
        "XGBoost": xgb.XGBClassifier(n_estimators=120, max_depth=6, learning_rate=0.1, random_state=42, n_jobs=-1, eval_metric="logloss")
    }

    results = {}
    roc_data = {}

    for name, model in models.items():
        print(f"\n--- Training {name} ---")
        t_start = time.time()

        # Stratified 3-Fold Cross-Validation on Train to evaluate stability
        skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
        cv_scores = []
        for fold, (train_idx, cv_idx) in enumerate(skf.split(X_train, y_train)):
            model.fit(X_train[train_idx], y_train[train_idx])
            pred_cv = model.predict(X_train[cv_idx])
            cv_scores.append(f1_score(y_train[cv_idx], pred_cv))
        
        cv_f1_mean = float(np.mean(cv_scores))
        print(f"3-Fold CV F1 Score: {cv_f1_mean:.4f}")

        # Final fit on full training set
        model.fit(X_train, y_train)
        train_duration = round(time.time() - t_start, 2)

        # Evaluate on untouched validation set
        val_metrics = evaluate_classifier(model, X_val, y_val)
        val_metrics["cv_f1_mean"] = round(cv_f1_mean, 4)
        val_metrics["training_time_seconds"] = train_duration
        results[name] = val_metrics

        # Save model checkpoint
        save_path = MODELS_DIR / f"{name.lower()}.joblib"
        joblib.dump(model, save_path)
        print(f"Saved {name} to {save_path} in {train_duration}s")
        print(f"Validation F1: {val_metrics['f1_score']}, Precision: {val_metrics['precision']}, Recall: {val_metrics['recall']}, Latency: {val_metrics['latency_ms']} ms")

        # Compute ROC curve for plotting
        if hasattr(model, "predict_proba"):
            y_prob = model.predict_proba(X_val)[:, 1]
        elif hasattr(model, "decision_function"):
            df = model.decision_function(X_val)
            y_prob = 1.0 / (1.0 + np.exp(-df))
        else:
            y_prob = model.predict(X_val).astype(float)
        
        fpr, tpr, _ = roc_curve(y_val, y_prob)
        roc_data[name] = (fpr, tpr, val_metrics["roc_auc"])

    # Generate Comparison Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Subplot 1: Bar Chart of Key Metrics
    metrics_to_plot = ["accuracy", "precision", "recall", "f1_score", "roc_auc"]
    model_names = list(results.keys())
    x = np.arange(len(model_names))
    width = 0.15

    for idx, metric in enumerate(metrics_to_plot):
        values = [results[m][metric] for m in model_names]
        ax1.bar(x + idx * width, values, width, label=metric.upper().replace("_", "-"))

    ax1.set_title("Classical ML Performance Comparison (Validation Set)", weight="bold", fontsize=11)
    ax1.set_xticks(x + width * 2)
    ax1.set_xticklabels([m.replace("_", " ") for m in model_names], rotation=15)
    ax1.set_ylim(0.80, 1.02)
    ax1.set_ylabel("Score")
    ax1.legend(loc="lower right")

    # Subplot 2: ROC Curves
    for name, (fpr, tpr, auc_score) in roc_data.items():
        ax2.plot(fpr, tpr, label=f"{name.replace('_', ' ')} (AUC = {auc_score:.4f})", linewidth=1.5)

    ax2.plot([0, 1], [0, 1], "k--", alpha=0.6)
    ax2.set_title("Receiver Operating Characteristic (ROC) Curves", weight="bold", fontsize=11)
    ax2.set_xlabel("False Positive Rate")
    ax2.set_ylabel("True Positive Rate")
    ax2.legend(loc="lower right")

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "ml_models_comparison.png", dpi=300)
    plt.close(fig)

    # Save metrics JSON
    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\n[Phase 06] Classical ML Evaluation saved to: {METRICS_PATH}")
    print("\n=== CLASSICAL ML BENCHMARK SUMMARY ===")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
