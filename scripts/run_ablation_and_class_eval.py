"""
Ablation Study & Attack Subgroup (SQLi / XSS) Evaluation Script
Evaluates 6 architectural configurations on the untouched frozen test set (3,842 requests)
and computes granular detection rates for SQL Injection, XSS, CRLF, and Benign traffic.
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

from src.rules import TraditionalRuleEngine
from src.features import FeatureExtractor
from src.models_dl import Conv1DClassifier, CharTokenizer
from backend.decision_engine import WAFDecisionEngine

PROCESSED_DIR = WORKSPACE_ROOT / "data" / "processed"
MODELS_DIR = WORKSPACE_ROOT / "models"
FIGURES_DIR = WORKSPACE_ROOT / "reports" / "figures"
REPORTS_DIR = WORKSPACE_ROOT / "reports"

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
    print("[Ablation & Subgroup] Loading frozen test dataset (3,842 samples)...")
    test_df = pd.read_csv(PROCESSED_DIR / "test_frozen.csv")
    y_test = np.load(PROCESSED_DIR / "y_test.npy").astype(int)
    X_test_comb = sparse.load_npz(PROCESSED_DIR / "X_test_combined.npz")

    # Load components
    print("[Ablation & Subgroup] Initializing models and engines...")
    rule_engine = TraditionalRuleEngine()
    xgb_model = joblib.load(MODELS_DIR / "xgboost.joblib")
    tokenizer = joblib.load(MODELS_DIR / "char_tokenizer.joblib")

    cnn = Conv1DClassifier(vocab_size=128, embedding_dim=32, num_filters=64).to(device)
    cnn.load_state_dict(torch.load(MODELS_DIR / "dl_cnn.pt", map_location=device, weights_only=True))
    cnn.eval()

    decision_engine = WAFDecisionEngine()

    # Pre-compute component predictions
    print("[Ablation] 1. Computing Traditional Rule Engine predictions...")
    eval_rules_df = rule_engine.evaluate_dataframe(test_df)
    rule_scores = eval_rules_df["rule_score"].values.astype(float)
    rule_preds = (eval_rules_df["rule_verdict"] == "BLOCK").astype(int).values
    rule_latencies = eval_rules_df["rule_latency_ms"].tolist()

    print("[Ablation] 2. Computing XGBoost predictions on 579 features...")
    xgb_probs = xgb_model.predict_proba(X_test_comb)[:, 1]
    xgb_preds = (xgb_probs >= 0.50).astype(int)
    xgb_latencies = []
    for i in range(min(400, X_test_comb.shape[0])):
        t0 = time.perf_counter()
        _ = xgb_model.predict(X_test_comb[i])
        xgb_latencies.append((time.perf_counter() - t0) * 1000.0)

    print("[Ablation] 3. Computing PyTorch 1D-CNN predictions on character sequences...")
    X_test_tokens = tokenizer.encode_batch(test_df["full_payload"].fillna("").tolist())
    with torch.no_grad():
        cnn_probs = cnn(X_test_tokens).squeeze(-1).numpy()
    cnn_preds = (cnn_probs >= 0.50).astype(int)
    cnn_latencies = []
    with torch.no_grad():
        for i in range(300):
            t0 = time.perf_counter()
            _ = cnn(X_test_tokens[i:i+1])
            cnn_latencies.append((time.perf_counter() - t0) * 1000.0)

    print("[Ablation] 4. Computing Rules + XGBoost combination...")
    # High-severity rule overrides, otherwise weighted fusion
    rules_xgb_probs = np.where(rule_scores >= 0.85, rule_scores, 0.70 * xgb_probs + 0.30 * rule_scores)
    rules_xgb_preds = (rules_xgb_probs >= 0.50).astype(int)
    rules_xgb_latencies = [r + x for r, x in zip(rule_latencies[:300], xgb_latencies[:300])]

    print("[Ablation] 5. Computing XGBoost + PyTorch 1D-CNN combination...")
    xgb_cnn_probs = 0.55 * cnn_probs + 0.45 * xgb_probs
    xgb_cnn_preds = (xgb_cnn_probs >= 0.50).astype(int)
    xgb_cnn_latencies = [c + x for c, x in zip(cnn_latencies[:300], xgb_latencies[:300])]

    print("[Ablation] 6. Computing Full Hybrid Decision Engine (Rules + CNN + XGBoost + 3-Way Policy)...")
    ensemble_preds = []
    ensemble_probs = []
    ensemble_latencies = []
    
    # Run full decision engine across test set
    for _, row in test_df.iterrows():
        t0 = time.perf_counter()
        res = decision_engine.inspect_request(
            method=row["method"],
            url=row["raw_url"],
            body=str(row["body"]) if pd.notna(row["body"]) else ""
        )
        t_el = (time.perf_counter() - t0) * 1000.0
        ensemble_latencies.append(t_el)
        ensemble_probs.append(res["risk_score"])
        # In operational WAF, BLOCK and REVIEW are anomalous flags
        ensemble_preds.append(1 if res["verdict"] in ["BLOCK", "REVIEW"] else 0)

    ensemble_probs = np.array(ensemble_probs)
    ensemble_preds = np.array(ensemble_preds)

    # --------------------------------------------------------------------------
    # Store Ablation Results
    # --------------------------------------------------------------------------
    ablation_systems = {
        "Rule_Engine_Only": compute_metrics(y_test, rule_preds, rule_scores, rule_latencies),
        "XGBoost_Only": compute_metrics(y_test, xgb_preds, xgb_probs, xgb_latencies),
        "PyTorch_1D_CNN_Only": compute_metrics(y_test, cnn_preds, cnn_probs, cnn_latencies),
        "Rules_Plus_XGBoost": compute_metrics(y_test, rules_xgb_preds, rules_xgb_probs, rules_xgb_latencies),
        "XGBoost_Plus_CNN": compute_metrics(y_test, xgb_cnn_preds, xgb_cnn_probs, xgb_cnn_latencies),
        "Full_Hybrid_Ensemble": compute_metrics(y_test, ensemble_preds, ensemble_probs, ensemble_latencies[:500])
    }

    print("\n" + "="*80)
    print("ABLATION STUDY RESULTS (ON UNTOUCHED FROZEN TEST SET - 3,842 REQUESTS)")
    print("="*80)
    ablation_df = pd.DataFrame(ablation_systems).T
    print(ablation_df[["accuracy", "precision", "recall", "f1_score", "false_positive_rate", "false_negative_rate", "latency_ms"]])

    with open(REPORTS_DIR / "ablation_study_metrics.json", "w", encoding="utf-8") as f:
        json.dump(ablation_systems, f, indent=2)

    # --------------------------------------------------------------------------
    # Class-Specific Subgroup Breakdown (SQLi, XSS, CRLF, Benign)
    # --------------------------------------------------------------------------
    print("\n" + "="*80)
    print("ATTACK SUBGROUP RECALL BREAKDOWN (SQLi vs XSS vs CRLF vs BENIGN)")
    print("="*80)
    subgroups = ["SQL_INJECTION", "XSS", "CRLF_INJECTION", "GENERIC_ANOMALY", "BENIGN"]
    class_results = {}

    for grp in subgroups:
        mask = (test_df["diagnostic_category"] == grp).values
        n_samples = int(mask.sum())
        if n_samples == 0:
            continue

        if grp == "BENIGN":
            # For benign, evaluate False Positive Rate (FPR) = False Positives / Total Benign
            fp_rule = int((rule_preds[mask] == 1).sum())
            fp_xgb = int((xgb_preds[mask] == 1).sum())
            fp_cnn = int((cnn_preds[mask] == 1).sum())
            fp_ens = int((ensemble_preds[mask] == 1).sum())

            class_results[grp] = {
                "sample_count": n_samples,
                "rule_fpr": round(fp_rule / n_samples, 4),
                "xgb_fpr": round(fp_xgb / n_samples, 4),
                "cnn_fpr": round(fp_cnn / n_samples, 4),
                "ensemble_fpr": round(fp_ens / n_samples, 4),
                "ensemble_clean_allow_rate": round(1.0 - (fp_ens / n_samples), 4)
            }
            print(f"[{grp}] Samples: {n_samples} | Clean Pass Rate: Rules={1-fp_rule/n_samples:.2%}, XGB={1-fp_xgb/n_samples:.2%}, CNN={1-fp_cnn/n_samples:.2%}, Ensemble={1-fp_ens/n_samples:.2%}")
        else:
            # For attack categories, evaluate Detection Rate (Recall) = True Positives / Total In Category
            det_rule = int((rule_preds[mask] == 1).sum())
            det_xgb = int((xgb_preds[mask] == 1).sum())
            det_cnn = int((cnn_preds[mask] == 1).sum())
            det_ens = int((ensemble_preds[mask] == 1).sum())

            class_results[grp] = {
                "sample_count": n_samples,
                "rule_recall": round(det_rule / n_samples, 4),
                "xgb_recall": round(det_xgb / n_samples, 4),
                "cnn_recall": round(det_cnn / n_samples, 4),
                "ensemble_recall": round(det_ens / n_samples, 4),
                "detected_count_ensemble": det_ens,
                "missed_count_ensemble": n_samples - det_ens
            }
            print(f"[{grp}] Samples: {n_samples} | Recall: Rules={det_rule/n_samples:.2%}, XGB={det_xgb/n_samples:.2%}, CNN={det_cnn/n_samples:.2%}, Ensemble={det_ens/n_samples:.2%}")

    with open(REPORTS_DIR / "class_specific_metrics.json", "w", encoding="utf-8") as f:
        json.dump(class_results, f, indent=2)

    # --------------------------------------------------------------------------
    # Plot Visualizations
    # --------------------------------------------------------------------------
    # 1. Ablation Study Bar Plot
    fig, ax = plt.subplots(figsize=(12, 6))
    abl_metrics_plot = ablation_df[["accuracy", "precision", "recall", "f1_score"]].reset_index()
    abl_melt = pd.melt(abl_metrics_plot, id_vars=["index"], var_name="Metric", value_name="Score")
    abl_melt["index"] = abl_melt["index"].str.replace("_", " ")

    sns.barplot(data=abl_melt, x="index", y="Score", hue="Metric", palette="Blues_r", ax=ax)
    ax.set_title("Ablation Study: Architecture Comparison on Frozen Test Set (N=3,842)", fontsize=13, weight="bold")
    ax.set_ylabel("Score (0.0 - 1.0)", fontsize=11)
    ax.set_xlabel("System Configuration", fontsize=11)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=20, ha="right", fontsize=9)
    ax.set_ylim(0.0, 1.15)
    for p in ax.patches:
        height = p.get_height()
        if height > 0:
            ax.annotate(f"{height:.2f}", (p.get_x() + p.get_width() / 2., height + 0.015),
                        ha="center", va="bottom", fontsize=7.5, weight="bold")
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "ablation_study_comparison.png", dpi=300)
    plt.close(fig)

    # 2. Subgroup Detection Rate Plot
    fig, ax = plt.subplots(figsize=(10, 5))
    attack_grps = ["SQL_INJECTION", "XSS", "CRLF_INJECTION", "GENERIC_ANOMALY"]
    sub_data = []
    for g in attack_grps:
        r = class_results[g]
        sub_data.append({"Threat": g.replace("_", " "), "Model": "Rule Engine", "Recall": r["rule_recall"]})
        sub_data.append({"Threat": g.replace("_", " "), "Model": "XGBoost", "Recall": r["xgb_recall"]})
        sub_data.append({"Threat": g.replace("_", " "), "Model": "PyTorch 1D-CNN", "Recall": r["cnn_recall"]})
        sub_data.append({"Threat": g.replace("_", " "), "Model": "Hybrid Ensemble", "Recall": r["ensemble_recall"]})
    
    df_sub = pd.DataFrame(sub_data)
    sns.barplot(data=df_sub, x="Threat", y="Recall", hue="Model", palette=["#95a5a6", "#2980b9", "#d35400", "#27ae60"], ax=ax)
    ax.set_title("Detection Rate by Attack Category (Frozen Test Set)", fontsize=13, weight="bold")
    ax.set_ylabel("Recall / Detection Rate", fontsize=11)
    ax.set_ylim(0.0, 1.15)
    for p in ax.patches:
        height = p.get_height()
        if height > 0:
            ax.annotate(f"{height*100:.1f}%", (p.get_x() + p.get_width() / 2., height + 0.015),
                        ha="center", va="bottom", fontsize=7.5, weight="bold")
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "class_specific_detection_rates.png", dpi=300)
    plt.close(fig)

    print(f"\n[Ablation & Subgroup] Reports saved:")
    print(f"  - {REPORTS_DIR / 'ablation_study_metrics.json'}")
    print(f"  - {REPORTS_DIR / 'class_specific_metrics.json'}")
    print(f"  - {FIGURES_DIR / 'ablation_study_comparison.png'}")
    print(f"  - {FIGURES_DIR / 'class_specific_detection_rates.png'}")


if __name__ == "__main__":
    main()
