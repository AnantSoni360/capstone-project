"""
Dual-Engine Decision Pipeline (Phase 10)
Combines Traditional Rules, PyTorch 1D-CNN, and XGBoost with calibrated
three-way decision logic (ALLOW, BLOCK, REVIEW).
"""

import pathlib
import sys
import time
from typing import Dict, Any, List, Optional
import joblib
import numpy as np
import torch

WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from src.parser import HTTPRequestParser
from src.rules import TraditionalRuleEngine
from src.features import FeatureExtractor
from src.models_dl import Conv1DClassifier, CharTokenizer

device = torch.device("cpu")


class WAFDecisionEngine:
    """
    Production WAF decision engine combining deterministic signatures
    and deep learning character pattern recognition.
    """

    def __init__(
        self,
        rule_config_path: Optional[str] = None,
        feature_extractor_path: Optional[str] = None,
        xgb_model_path: Optional[str] = None,
        cnn_weights_path: Optional[str] = None,
        tokenizer_path: Optional[str] = None,
    ):
        base_models = WORKSPACE_ROOT / "models"
        base_config = WORKSPACE_ROOT / "config"

        # 1. Rule Engine
        self.rule_engine = TraditionalRuleEngine(
            config_path=rule_config_path or str(base_config / "rules.json")
        )

        # 2. HTTP Request Parser & Normalizer
        self.parser = HTTPRequestParser(max_decode_depth=3)

        # 3. Feature Extractor & XGBoost
        self.feature_extractor = FeatureExtractor.load(
            feature_extractor_path or str(base_models / "feature_extractor.joblib")
        )
        self.xgb_model = joblib.load(
            xgb_model_path or str(base_models / "xgboost.joblib")
        )

        # 4. PyTorch 1D-CNN & Character Tokenizer
        self.tokenizer = joblib.load(
            tokenizer_path or str(base_models / "char_tokenizer.joblib")
        )
        self.cnn_model = Conv1DClassifier(vocab_size=128, embedding_dim=32, num_filters=64).to(device)
        self.cnn_model.load_state_dict(
            torch.load(cnn_weights_path or str(base_models / "dl_cnn.pt"), map_location=device, weights_only=True)
        )
        self.cnn_model.eval()

        # Calibrated decision thresholds
        self.block_threshold = 0.70
        self.review_threshold = 0.35

    def inspect_request(
        self,
        method: str,
        url: str,
        body: str = "",
        headers: Optional[Dict[str, str]] = None,
        client_ip: str = "127.0.0.1"
    ) -> Dict[str, Any]:
        """
        Executes end-to-end request parsing, rule evaluation, ML/DL scoring,
        and applies the calibrated three-way decision policy.
        """
        t_start = time.perf_counter()

        # Step 1: Canonicalization & Normalization
        parsed = self.parser.parse_single_request(
            method=method,
            raw_url=url,
            body=body,
            ground_truth=0  # Live inspection mode
        )

        # Step 2: Traditional Rule Engine Evaluation
        rule_res = self.rule_engine.evaluate_request_record(parsed)
        rule_score = float(rule_res["risk_score"])
        matched_rules = rule_res["matched_rules"]

        # Step 3: PyTorch 1D-CNN Inference (Primary Deep Learning Model)
        full_payload = parsed["full_payload"]
        tokens = self.tokenizer.encode_batch([full_payload])
        with torch.no_grad():
            cnn_prob = float(self.cnn_model(tokens.to(device)).item())

        # Step 4: XGBoost Inference (Auxiliary Classical Model)
        _, _, X_comb = self.feature_extractor.transform_single(parsed)
        xgb_prob = float(self.xgb_model.predict_proba(X_comb)[0, 1])

        # Step 5: Weighted Evidence Fusion & Risk Calibration
        if rule_score >= 0.85:
            # Deterministic high-severity signature overrides
            composite_risk = max(rule_score, cnn_prob, xgb_prob)
            reason = f"High-confidence signature triggered: {matched_rules[0]['name']}"
        else:
            # Probabilistic ensemble favoring 1D-CNN (top test set performer: 94.35% Acc, 99.86% Prec)
            composite_risk = (0.50 * cnn_prob) + (0.30 * xgb_prob) + (0.20 * rule_score)
            if composite_risk >= self.block_threshold:
                reason = "AI detection engine flagged anomalous payload pattern"
            elif composite_risk >= self.review_threshold:
                reason = "Suspicious payload pattern requires security review"
            else:
                reason = "Request verified legitimate (no threat indicators detected)"

        # Step 6: 3-Way Decision Verdict with False-Positive Dampening
        has_threat_syntax = (len(matched_rules) > 0) or (parsed.get("diagnostic_category") not in ("BENIGN", None))

        if composite_risk >= self.block_threshold or rule_score >= self.block_threshold:
            if not has_threat_syntax and rule_score == 0.0:
                # OOV / Statistical anomaly without explicit exploit syntax -> REVIEW to preserve UX
                verdict = "REVIEW"
                action_taken = "QUARANTINE_REVIEW"
                http_status = 200
                reason = "Statistical anomaly detected without active exploit syntax (held for review)"
            else:
                verdict = "BLOCK"
                action_taken = "REJECT_403"
                http_status = 403
        elif composite_risk >= self.review_threshold or rule_score >= self.review_threshold:
            verdict = "REVIEW"
            action_taken = "QUARANTINE_REVIEW"
            http_status = 200
        else:
            verdict = "ALLOW"
            action_taken = "FORWARD_UPSTREAM"
            http_status = 200

        latency_ms = (time.perf_counter() - t_start) * 1000.0

        # Determine diagnostic attack category for reporting
        if verdict == "ALLOW":
            attack_type = "BENIGN"
        elif matched_rules:
            attack_type = matched_rules[0]["category"]
        else:
            attack_type = parsed["diagnostic_category"]

        return {
            "verdict": verdict,
            "risk_score": round(composite_risk, 4),
            "confidence": round(max(cnn_prob, xgb_prob, rule_score), 4),
            "attack_type": attack_type,
            "reason": reason,
            "action_taken": action_taken,
            "http_status": http_status,
            "latency_ms": round(latency_ms, 3),
            "rule_evidence": {
                "match_count": len(matched_rules),
                "matched_rules": matched_rules,
                "rule_score": round(rule_score, 4)
            },
            "ai_evidence": {
                "primary_model": "PyTorch_1D_CNN",
                "attack_probability": round(cnn_prob, 4),
                "auxiliary_model": "XGBoost",
                "auxiliary_probability": round(xgb_prob, 4)
            },
            "parsed_metadata": {
                "path": parsed["path"],
                "query": parsed["query"],
                "body": parsed["body"],
                "payload_length": parsed["payload_length"]
            }
        }
