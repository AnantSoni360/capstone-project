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
