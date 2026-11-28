# System Requirements & Specifications (Phase 00)
**Project Title:** AI-Based Web Application Firewall for SQL Injection and XSS Detection  
**System Standard:** Production-Style Architectural Prototype for Capstone Evaluation

---

## 1. Functional Requirements (FR)

- **FR-01 (Request Ingestion & Parsing):** The WAF must ingest raw HTTP requests, extract the HTTP method, URL path, query parameters, headers, and request body, and perform recursive URL decoding and character canonicalization.
- **FR-02 (Traditional Rule Engine Baseline):** The system must execute 15–20 documented deterministic security rules covering SQL Injection, XSS, and Path Traversal to generate a rule-match list and risk score.
- **FR-03 (AI-Powered Payload Inspection):** The system must compute feature matrices (lexical, character-level, keyword, and n-gram representations) and evaluate them using trained Machine Learning (Scikit-Learn/XGBoost) and Deep Learning (PyTorch) models.
- **FR-04 (Calibrated 3-Way Decision Engine):** The system must output one of three verdicts based on calibrated validation thresholds:
  - `ALLOW` (Risk < $\tau_{\text{allow}}$): Request forwarded to the protected application.
  - `BLOCK` (Risk $\ge \tau_{\text{block}}$ or critical rule match): Request dropped immediately; client receives HTTP 403 Forbidden.
  - `REVIEW` ($\tau_{\text{allow}} \le \text{Risk} < \tau_{\text{block}}$): Request flagged for enhanced auditing, challenged, or monitored based on operational policy.
- **FR-05 (Origin Server Isolation):** The protected application must reside entirely within an isolated private Docker network with no public host port bindings.
- **FR-06 (Inline Reverse Proxy Enforcement):** Nginx must inspect requests via an `auth_request` subrequest to the FastAPI WAF service before passing traffic to the upstream web application.
- **FR-07 (Explainable AI Diagnostics):** The system must generate human-interpretable explanations using SHAP (feature attribution) and LIME (character/token highlights) for flagged security events.
- **FR-08 (Security Operations Dashboard):** A Streamlit-based monitoring console must display live traffic statistics, recent security incidents, an interactive manual request scanner, and model performance metrics.
- **FR-09 (Sanitized Security Logging):** All incoming request metadata and scan results must be logged asynchronously to an audit database. Sensitive fields (passwords, authorization tokens, cookies) must be masked.
- **FR-10 (GenAI / LLM Prompt Injection & Jailbreak Defense):** The system must inspect upstream LLM prompts for OWASP LLM01 threats (direct overrides, DAN jailbreaks, system prompt exfiltration, delimiter injection, Base64 smuggling) via dedicated `/scan_llm` endpoint and Streamlit SOC view.
- **FR-11 (Grammar-Aware AST Tokenization):** The system must structurally deconstruct SQL payloads into lexical tokens to catch obfuscated keywords, comment interleaving (`UNION/**/SELECT`), and tautology expressions before statistical scoring.
- **FR-12 (ONNX Runtime Hardware Acceleration):** Deep sequence neural models must be deployable via ONNX Runtime to minimize CPU latency (< 2.0 ms) and maximize throughput (> 600 RPS).
- **FR-13 (Automated Adversarial Robustness Auditing):** The system must include an adversarial mutation fuzzer implementing 8 syntactic transformations to continuously evaluate bypass resilience.
- **FR-14 (Active Learning & Analyst Feedback Loop):** The system must allow SOC analysts to submit feedback on reviewed requests and trigger dynamic threshold recalibration to continuously suppress false positives.

---

## 2. Non-Functional Requirements (NFR)

- **NFR-01 (Inference Latency):** The total inspection pipeline (parsing, feature extraction, rule matching, and model scoring) must average $\le 15\text{ ms}$ per request under normal operational conditions.
- **NFR-02 (Resource Footprint):** All models and services must operate comfortably within the host machine profile (Intel Core i5-12450H, 16 GB RAM, NVIDIA GTX 1650 4 GB VRAM) with automatic CPU fallback.
- **NFR-03 (Zero Train-Test Leakage):** Preprocessing scalers, vectorizers, and feature selectors must be fitted strictly on the 70% training split. The 15% test split must remain untouched until final benchmark evaluation.
- **NFR-04 (Fail-Safe Resilience):** The WAF gateway must support configurable fail-open and fail-closed operational policies if the AI detection service experiences downtime or timeouts.
- **NFR-05 (Reproducibility):** Every training experiment must save random seeds, hyperparameters, metric logs, and model checkpoints (`models/*.joblib`, `models/*.pt`).

---

## 3. Operational Failure Mode Policies

| Scenario | Fail-Open Policy | Fail-Closed Policy (Default Security Mode) |
| :--- | :--- | :--- |
| **WAF API Timeout (>100ms)** | Allow request upstream, log timeout alert. | Return HTTP 504 Gateway Timeout, reject request. |
| **Model Service Crash** | Fallback immediately to Traditional Rule Engine. | Return HTTP 503 Service Unavailable, reject request. |
| **Database Disk Full** | Continue proxying in-memory, log alert to stderr. | Drop all requests until storage is recovered. |
