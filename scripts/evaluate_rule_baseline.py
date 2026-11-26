"""
Traditional Rule-Based WAF Evaluation Script (Phase 05)
Benchmarks deterministic rules against validation split to establish
an empirical baseline for accuracy, precision, recall, FPR, FNR, and latency.
"""

import json
import pathlib
import sys
import time
from typing import Dict, Any, List

WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

from src.rules import TraditionalRuleEngine

PROCESSED_DIR = WORKSPACE_ROOT / "data" / "processed"
FIGURES_DIR = WORKSPACE_ROOT / "reports" / "figures"
METRICS_PATH = WORKSPACE_ROOT / "reports" / "rule_baseline_metrics.json"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def calculate_cybersecurity_metrics(y_true: np.ndarray, y_pred: np.ndarray, latencies: List[float]) -> Dict[str, Any]:
    """Calculate accuracy, precision, recall, F1, FPR, FNR, and latency."""
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()

    accuracy = float(accuracy_score(y_true, y_pred))
    precision = float(precision_score(y_true, y_pred, zero_division=0))
    recall = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))

    fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
    fnr = float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0

    avg_latency = float(np.mean(latencies))
    p95_latency = float(np.percentile(latencies, 95))

    return {
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "false_positive_rate": round(fpr, 4),
        "false_negative_rate": round(fnr, 4),
        "confusion_matrix": {
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "true_positives": int(tp)
        },
        "latency_ms": {
            "mean": round(avg_latency, 3),
            "p95": round(p95_latency, 3)
        }
    }


def main():
    print("[Phase 05] Loading validation dataset for rule baseline evaluation...")
    val_df = pd.read_csv(PROCESSED_DIR / "val.csv")
    y_true = val_df["ground_truth"].values.astype(int)

    engine = TraditionalRuleEngine()
    print(f"Evaluating {len(val_df)} validation requests...")

    start_eval = time.time()
    evaluated_df = engine.evaluate_dataframe(val_df)
    total_eval_time = time.time() - start_eval

    # Binary prediction: BLOCK or REVIEW is considered flagged as anomaly (1)
    y_pred_block = (evaluated_df["rule_verdict"] == "BLOCK").astype(int).values
    y_pred_any_flag = (evaluated_df["rule_verdict"].isin(["BLOCK", "REVIEW"])).astype(int).values

    latencies = evaluated_df["rule_latency_ms"].tolist()

    metrics_strict_block = calculate_cybersecurity_metrics(y_true, y_pred_block, latencies)
    metrics_flagged = calculate_cybersecurity_metrics(y_true, y_pred_any_flag, latencies)

    # Plot Confusion Matrix
    cm = confusion_matrix(y_true, y_pred_block)
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False, ax=ax,
                xticklabels=["Allowed (0)", "Blocked (1)"],
                yticklabels=["Actual Normal (0)", "Actual Attack (1)"])
    ax.set_title("Traditional Rule-Based WAF: Confusion Matrix", fontsize=12, weight="bold")
    ax.set_xlabel("Predicted Verdict")
    ax.set_ylabel("Ground Truth")
    fig.savefig(FIGURES_DIR / "rule_baseline_confusion_matrix.png", dpi=300)
    plt.close(fig)

    report = {
        "evaluation_sample_count": len(val_df),
        "total_evaluation_time_seconds": round(total_eval_time, 2),
        "strict_block_policy": metrics_strict_block,
        "combined_flag_policy": metrics_flagged,
        "verdict_distribution": evaluated_df["rule_verdict"].value_counts().to_dict(),
        "key_limitations_documented": [
            "High false negative rate against parameter tampering and novel obfuscation",
            "Deterministic signatures cannot adapt to zero-day syntax without manual updates",
            "Provides an interpretable, ultra-low latency (<1ms) first-line security filter"
        ]
    }

    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"[Phase 05] Saved rule baseline report to: {METRICS_PATH}")
    print("\n=== TRADITIONAL RULE WAF BASELINE RESULTS ===")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
