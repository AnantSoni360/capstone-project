"""
Explainable AI (XAI) Module for WAF Security Diagnostics (Phase 08)
Integrates TreeSHAP for global/local feature attribution on tree models
and LIME-style token attribution for raw HTTP payload inspection.
"""

import html
import re
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
from scipy import sparse


class WAFTreeSHAPExplainer:
    """
    TreeSHAP explanation engine for XGBoost and Random Forest models.
    Provides mathematically sound Shapley value attributions for individual requests.
    """

    def __init__(self, model, feature_names: List[str]):
        import shap
        self.model = model
        self.feature_names = feature_names
        self.explainer = shap.TreeExplainer(model)

    def explain_single(self, X_sample: sparse.csr_matrix, top_k: int = 8) -> Dict[str, Any]:
        """
        Computes SHAP values for a single request vector and extracts top contributors.
        """
        # Convert sparse row to dense for SHAP TreeExplainer
        if sparse.issparse(X_sample):
            X_dense = X_sample.toarray()
        else:
            X_dense = np.asarray(X_sample)

        shap_values = self.explainer.shap_values(X_dense)

        # Handle binary classification output format differences in SHAP versions
        if isinstance(shap_values, list):
            sv = shap_values[1][0] if len(shap_values) > 1 else shap_values[0][0]
        elif len(shap_values.shape) == 3:
            sv = shap_values[0, :, 1]
        else:
            sv = shap_values[0]

        # Pair features with their SHAP contribution
        indexed_shap = []
        for i, val in enumerate(sv):
            fname = self.feature_names[i] if i < len(self.feature_names) else f"feature_{i}"
            indexed_shap.append((fname, float(val), float(X_dense[0, i])))

        # Sort by absolute SHAP value
        sorted_shap = sorted(indexed_shap, key=lambda x: abs(x[1]), reverse=True)
        top_features = sorted_shap[:top_k]

        positive_indicators = [
            {"feature": f, "shap_value": round(val, 4), "input_value": round(inp, 4)}
            for f, val, inp in top_features if val > 0
        ]
        negative_indicators = [
            {"feature": f, "shap_value": round(val, 4), "input_value": round(inp, 4)}
            for f, val, inp in top_features if val < 0
        ]

        base_value = float(self.explainer.expected_value[1] if isinstance(self.explainer.expected_value, (list, np.ndarray)) else self.explainer.expected_value)

        return {
            "base_value": round(base_value, 4),
            "top_contributing_features": positive_indicators,
            "benign_stabilizing_features": negative_indicators,
            "all_top_k": [
                {"feature": f, "shap_value": round(val, 4), "input_value": round(inp, 4)}
                for f, val, inp in top_features
            ]
        }


class WAFPayloadExplainer:
    """
    Token-level payload explainer using localized occlusion perturbations.
    Identifies which substrings in an HTTP payload most directly drive malicious scoring.
    """

    def __init__(self, predict_fn, tokenizer=None):
        self.predict_fn = predict_fn
        self.tokenizer = tokenizer

    def tokenize_payload(self, text: str) -> List[str]:
        """Splits payload into lexical tokens and punctuation boundaries."""
        tokens = re.findall(r"[\w]+|[^\w\s]|\s+", text)
        return tokens

    def explain_payload(self, payload: str, top_k: int = 6) -> Dict[str, Any]:
        """
        Computes perturbation-based sensitivity attribution for tokens in the payload.
        """
        if not payload or not isinstance(payload, str):
            return {"tokens": [], "highlighted_html": "", "top_attack_tokens": []}

        base_score = float(self.predict_fn([payload])[0])
        tokens = self.tokenize_payload(payload)

        if not tokens:
            return {"tokens": [], "highlighted_html": "", "top_attack_tokens": []}

        # Perturbation: leave-one-out masking
        token_attributions = []
        for i in range(len(tokens)):
            # Create perturbed string without token i
            perturbed = "".join(tokens[:i] + tokens[i+1:])
            perturbed_score = float(self.predict_fn([perturbed])[0])
            # If removing token i dropped the malicious score, token i was malicious (positive importance)
            importance = base_score - perturbed_score
            token_attributions.append((tokens[i], importance))

        # Sort tokens by importance
        sorted_tokens = sorted(
            [t for t in token_attributions if t[0].strip()],
            key=lambda x: x[1],
            reverse=True
        )
        top_tokens = [
            {"token": tok, "importance_score": round(imp, 4)}
            for tok, imp in sorted_tokens[:top_k] if imp > 0.01
        ]

        # Generate HTML highlighted markup with dual-theme contrast
        html_parts = []
        for tok, imp in token_attributions:
            escaped_tok = html.escape(tok)
            if imp > 0.05:
                # Strong malicious trigger (theme-adaptive red)
                html_parts.append(
                    f'<span class="token-malicious" style="background-color: rgba(239, 68, 68, 0.25); color: #DC2626; font-weight: bold; padding: 2px 6px; border-radius: 4px; border: 1px solid #EF4444;">{escaped_tok}</span>'
                )
            elif imp > 0.01:
                # Moderate indicator (theme-adaptive amber)
                html_parts.append(
                    f'<span class="token-suspicious" style="background-color: rgba(245, 158, 11, 0.25); color: #D97706; font-weight: bold; padding: 2px 6px; border-radius: 4px; border: 1px solid #F59E0B;">{escaped_tok}</span>'
                )
            else:
                html_parts.append(f'<span class="token-neutral">{escaped_tok}</span>')

        highlighted_html = "".join(html_parts)

        return {
            "base_malicious_score": round(base_score, 4),
            "top_attack_tokens": top_tokens,
            "highlighted_html": highlighted_html
        }
