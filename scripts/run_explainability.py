"""
Explainable AI (XAI) Execution Script (Phase 08)
Computes TreeSHAP feature attributions on XGBoost and LIME-style token perturbations
on representative SQLi, XSS, and Benign HTTP requests.
"""

import json
import pathlib
import sys
import time
from typing import Dict, Any, List, Tuple, Optional

WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import sparse
import shap

from src.features import FeatureExtractor
from src.parser import HTTPRequestParser
from src.explainability import WAFTreeSHAPExplainer, WAFPayloadExplainer

PROCESSED_DIR = WORKSPACE_ROOT / "data" / "processed"
MODELS_DIR = WORKSPACE_ROOT / "models"
FIGURES_DIR = WORKSPACE_ROOT / "reports" / "figures"
REPORT_PATH = WORKSPACE_ROOT / "reports" / "xai_sample_explanations.json"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def main():
    print("[Phase 08] Loading fitted FeatureExtractor and XGBoost model...")
    extractor = FeatureExtractor.load(str(MODELS_DIR / "feature_extractor.joblib"))
    xgb_model = joblib.load(MODELS_DIR / "xgboost.joblib")

    # Get feature names (79 handcrafted + 500 tfidf)
    tfidf_names = [f"tfidf_{ng}" for ng in extractor.tfidf_vectorizer.get_feature_names_out()]
    all_feature_names = extractor.feature_names + tfidf_names

    # 1. Initialize TreeSHAP
    print("[Phase 08] Initializing WAFTreeSHAPExplainer...")
    tree_explainer = WAFTreeSHAPExplainer(xgb_model, all_feature_names)

    # Compute global SHAP values on 200 validation samples
    print("[Phase 08] Computing global SHAP summary values...")
    X_val = sparse.load_npz(PROCESSED_DIR / "X_val_combined.npz")
    sub_indices = np.random.choice(X_val.shape[0], min(200, X_val.shape[0]), replace=False)
    X_sample_dense = X_val[sub_indices].toarray()

    shap_values = tree_explainer.explainer.shap_values(X_sample_dense)

    # Generate Publication SHAP Summary Plot
    plt.figure(figsize=(10, 6))
    shap.summary_plot(
        shap_values,
        X_sample_dense,
        feature_names=all_feature_names,
        max_display=15,
        show=False
    )
    plt.title("TreeSHAP Feature Attribution: Top 15 Global Risk Drivers", fontsize=12, weight="bold")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "shap_summary.png", dpi=300)
    plt.close()
    print(f"Saved SHAP summary plot: {FIGURES_DIR / 'shap_summary.png'}")

    # 2. Local Explanations for Real-World Scenarios
    print("[Phase 08] Generating local explanations for representative requests...")
    parser = HTTPRequestParser()
    sample_requests = [
        {
            "case": "SQL_INJECTION",
            "method": "GET",
            "raw_url": "http://localhost:8080/tienda1/publico/anadir.jsp?id=1%27%20UNION%20SELECT%20username,password%20FROM%20usuarios-- HTTP/1.1",
            "decoded_path": "/tienda1/publico/anadir.jsp",
            "decoded_query": "id=1' UNION SELECT username,password FROM usuarios--",
            "decoded_body": "",
            "full_payload": "/tienda1/publico/anadir.jsp ?id=1' UNION SELECT username,password FROM usuarios--",
            "param_count": 1
        },
        {
            "case": "XSS",
            "method": "POST",
            "raw_url": "http://localhost:8080/tienda1/miembros/editar.jsp HTTP/1.1",
            "decoded_path": "/tienda1/miembros/editar.jsp",
            "decoded_query": "",
            "decoded_body": "modo=registro&login=bob%40<script>alert('XSS')</script>",
            "full_payload": "/tienda1/miembros/editar.jsp modo=registro&login=bob@<script>alert('XSS')</script>",
            "param_count": 2
        },
        {
            "case": "BENIGN",
            "method": "GET",
            "raw_url": "http://localhost:8080/tienda1/publico/pagar.jsp?modo=insertar&precio=3714&B1=Confirmar HTTP/1.1",
            "decoded_path": "/tienda1/publico/pagar.jsp",
            "decoded_query": "modo=insertar&precio=3714&B1=Confirmar",
            "decoded_body": "",
            "full_payload": "/tienda1/publico/pagar.jsp ?modo=insertar&precio=3714&B1=Confirmar",
            "param_count": 3
        }
    ]

    # Wrapper prediction function for LIME payload perturbations
    def predict_payloads(payload_list: List[str]) -> np.ndarray:
        records = [
            parser.parse_single_request(method="GET", raw_url=p, body="")
            for p in payload_list
        ]
        df_temp = pd.DataFrame(records)
        _, _, X_comb = extractor.transform(df_temp)
        probs = xgb_model.predict_proba(X_comb)[:, 1]
        return probs

    payload_explainer = WAFPayloadExplainer(predict_fn=predict_payloads)

    case_explanations = {}
    for req in sample_requests:
        case_name = req["case"]
        # Extract features
        _, _, X_single = extractor.transform_single(req)
        model_prob = float(xgb_model.predict_proba(X_single)[0, 1])

        # SHAP attribution
        shap_res = tree_explainer.explain_single(X_single, top_k=6)

        # Token attribution
        token_res = payload_explainer.explain_payload(req["full_payload"], top_k=5)

        case_explanations[case_name] = {
            "request_url": req["raw_url"],
            "model_malicious_probability": round(model_prob, 4),
            "verdict": "BLOCK" if model_prob >= 0.70 else ("REVIEW" if model_prob >= 0.35 else "ALLOW"),
            "shap_attribution": shap_res,
            "token_attribution": token_res
        }

    report = {
        "xai_engine": "TreeSHAP + Localized Token Occlusion",
        "underlying_model": "XGBoost Classifier",
        "case_studies": case_explanations
    }

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\n[Phase 08] XAI sample explanations saved to: {REPORT_PATH}")
    print("\n=== XAI CASE STUDY PREVIEW ===")
    for case, cdata in case_explanations.items():
        print(f"\nCase: {case} -> Verdict: {cdata['verdict']} (Risk: {cdata['model_malicious_probability']})")
        print("Top SHAP Features:")
        for feat in cdata["shap_attribution"]["top_contributing_features"][:3]:
            print(f"  + {feat['feature']}: SHAP={feat['shap_value']}")
        print("Top Malicious Tokens:")
        for tok in cdata["token_attribution"]["top_attack_tokens"][:3]:
            print(f"  * '{tok['token']}': score drop={tok['importance_score']}")


if __name__ == "__main__":
    main()
