"""
Adversarial Robustness Testing Script (Phase 09)
Evaluates detection degradation of Traditional Rules, XGBoost, and PyTorch 1D-CNN
against 5 evasion vectors: double URL encoding, comment injection, case mixing,
whitespace substitution, and equivalent tautologies.
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
import seaborn as sns
import torch

from src.features import FeatureExtractor
from src.parser import HTTPRequestParser
from src.rules import TraditionalRuleEngine
from src.models_dl import Conv1DClassifier, CharTokenizer

MODELS_DIR = WORKSPACE_ROOT / "models"
FIGURES_DIR = WORKSPACE_ROOT / "reports" / "figures"
REPORT_PATH = WORKSPACE_ROOT / "reports" / "robustness_metrics.json"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)
device = torch.device("cpu")


# 20 Base SQLi and XSS attack payloads
BASE_PAYLOADS = [
    ("SQLI", "/publico/anadir.jsp?id=1' UNION SELECT username, password FROM usuarios--"),
    ("SQLI", "/publico/anadir.jsp?id=1' OR '1'='1"),
    ("SQLI", "/publico/anadir.jsp?id=1; DROP TABLE usuarios;--"),
    ("SQLI", "/publico/anadir.jsp?id=1' AND 1=1--"),
    ("SQLI", "/publico/anadir.jsp?id=1' UNION ALL SELECT null, null, null FROM datos--"),
    ("SQLI", "/publico/anadir.jsp?id=1' OR 'a'='a'--"),
    ("SQLI", "/publico/entrar.jsp?errorMsg=credenciales','0');waitfor delay '0:0:15';--"),
    ("SQLI", "/miembros/editar.jsp?login=admin'--&pwd=123"),
    ("SQLI", "/publico/anadir.jsp?id=1' AND id IN (SELECT id FROM admin)--"),
    ("SQLI", "/publico/anadir.jsp?id=1' OR 2>1--"),
    ("XSS", "/publico/anadir.jsp?nombre=<script>alert('XSS')</script>"),
    ("XSS", "/publico/anadir.jsp?nombre=<img src=x onerror=alert(1)>"),
    ("XSS", "/publico/anadir.jsp?nombre=<svg onload=confirm('PWNED')>"),
    ("XSS", "/publico/anadir.jsp?nombre=javascript:alert(document.cookie)"),
    ("XSS", "/publico/anadir.jsp?nombre=<iframe src='javascript:alert(1)'>"),
    ("XSS", "/publico/anadir.jsp?nombre=<body onload=alert('HACK')>"),
    ("XSS", "/publico/anadir.jsp?nombre=<a href='javascript:eval(1)'>click</a>"),
    ("XSS", "/publico/anadir.jsp?nombre=<input onfocus=alert(1) autofocus>"),
    ("XSS", "/publico/anadir.jsp?nombre=<video><source onerror=javascript:alert(1)>"),
    ("XSS", "/publico/anadir.jsp?nombre=<script src='//evil.com/xss.js'></script>"),
]


def apply_evasion_vector(payload: str, vector_type: str) -> str:
    """Applies a controlled adversarial transformation to the attack payload."""
    if vector_type == "double_url_encoding":
        # %27 becomes %2527, %3C becomes %253C, space becomes %2520
        return payload.replace("'", "%2527").replace("<", "%253C").replace(">", "%253E").replace(" ", "%2520")

    elif vector_type == "comment_injection":
        # Inject inline SQL comments into keywords
        res = payload.replace("UNION", "UN/**/ION").replace("SELECT", "SEL/**/ECT")
        res = res.replace("union", "un/**/ion").replace("select", "sel/**/ect")
        return res

    elif vector_type == "mixed_casing":
        # Randomly toggle letter casing
        chars = [c.upper() if idx % 2 == 0 else c.lower() for idx, c in enumerate(payload)]
        return "".join(chars)

    elif vector_type == "whitespace_substitution":
        # Replace spaces with tabs or plus signs
        return payload.replace(" ", "+")

    elif vector_type == "equivalent_tautologies":
        # Transform '1'='1' to 'x'='x' or 2>1
        return payload.replace("'1'='1'", "'x'='x'").replace("1=1", "2>1").replace("'a'='a'", "'z'='z'")

    return payload


def evaluate_system_recall(payloads: List[str], system_name: str, rule_engine, extractor, xgb_model, cnn_model, tokenizer) -> float:
    """Evaluates the recall of a detection system on a set of attack payloads."""
    detected = 0
    parser = HTTPRequestParser(max_decode_depth=3)

    for p in payloads:
        # Standardized request record
        rec = parser.parse_single_request(method="GET", raw_url=p, body="", ground_truth=1)

        if system_name == "Traditional_Rules":
            res = rule_engine.evaluate_request_record(rec)
            if res["verdict"] in ["BLOCK", "REVIEW"]:
                detected += 1

        elif system_name == "XGBoost":
            _, _, X_comb = extractor.transform_single(rec)
            prob = float(xgb_model.predict_proba(X_comb)[0, 1])
            if prob >= 0.50:
                detected += 1

        elif system_name == "PyTorch_1D_CNN":
            tokens = tokenizer.encode_batch([rec["full_payload"]])
            with torch.no_grad():
                prob = float(cnn_model(tokens.to(device)).item())
            if prob >= 0.50:
                detected += 1

    recall = detected / len(payloads)
    return float(round(recall, 4))


def main():
    print("[Phase 09] Loading models and pipeline for robustness testing...")
    rule_engine = TraditionalRuleEngine()
    extractor = FeatureExtractor.load(str(MODELS_DIR / "feature_extractor.joblib"))
    xgb_model = joblib.load(MODELS_DIR / "xgboost.joblib")
    tokenizer = joblib.load(MODELS_DIR / "char_tokenizer.joblib")

    cnn_model = Conv1DClassifier(vocab_size=128, embedding_dim=32, num_filters=64).to(device)
    cnn_model.load_state_dict(torch.load(MODELS_DIR / "dl_cnn.pt", map_location=device, weights_only=True))
    cnn_model.eval()

    clean_payloads = [p[1] for p in BASE_PAYLOADS]

    evasion_vectors = [
        "baseline_clean",
        "double_url_encoding",
        "comment_injection",
        "mixed_casing",
        "whitespace_substitution",
        "equivalent_tautologies"
    ]

    systems = ["Traditional_Rules", "XGBoost", "PyTorch_1D_CNN"]
    results = {sys_name: {} for sys_name in systems}

    print("\nRunning Evasion Tests:")
    for vec in evasion_vectors:
        if vec == "baseline_clean":
            test_batch = clean_payloads
        else:
            test_batch = [apply_evasion_vector(p, vec) for p in clean_payloads]

        print(f"\n--- Testing Vector: {vec} (Sample: {test_batch[0][:60]}...) ---")
        for sys_name in systems:
            rec = evaluate_system_recall(test_batch, sys_name, rule_engine, extractor, xgb_model, cnn_model, tokenizer)
            results[sys_name][vec] = rec
            print(f"  [{sys_name}] Recall: {rec * 100:.1f}%")

    # Plot Robustness Comparison Bar Chart
    df_plot = pd.DataFrame(results).reset_index().rename(columns={"index": "Evasion_Vector"})
    df_melt = pd.melt(df_plot, id_vars=["Evasion_Vector"], var_name="System", value_name="Recall")

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=df_melt, x="Evasion_Vector", y="Recall", hue="System", palette=["#34495e", "#2980b9", "#e67e22"], ax=ax)
    ax.set_title("Adversarial Evasion Robustness: Rule Engine vs XGBoost vs PyTorch 1D-CNN", fontsize=12, weight="bold")
    ax.set_ylabel("Detection Recall (True Positive Rate)")
    ax.set_xlabel("Adversarial Evasion Technique")
    ax.set_xticklabels([v.replace("_", " ").title() for v in evasion_vectors], rotation=15)
    ax.set_ylim(0.0, 1.15)
    for p in ax.patches:
        height = p.get_height()
        if height > 0:
            ax.annotate(f"{height*100:.0f}%", (p.get_x() + p.get_width() / 2., height + 0.02),
                        ha="center", va="bottom", fontsize=8, weight="bold")
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "robustness_comparison.png", dpi=300)
    plt.close(fig)

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\n[Phase 09] Robustness report saved to: {REPORT_PATH}")
    print(f"[Phase 09] Robustness plot saved to: {FIGURES_DIR / 'robustness_comparison.png'}")


if __name__ == "__main__":
    main()
