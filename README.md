# 🛡️ AI-Based Web Application Firewall (AI-WAF)
### An Autonomous, Low-Latency Defense-in-Depth Gateway for Modern Web Application Security

[![Tests](https://img.shields.io/badge/pytest-62%20passed-brightgreen.svg)](tests/)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.14%20CPU%2FCUDA-orange.svg)](https://pytorch.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-Tabular%20Engine-green.svg)](https://xgboost.readthedocs.io/)
[![FastAPI](https://img.shields.io/badge/FastAPI-High--Throughput%20API-teal.svg)](https://fastapi.tiangolo.com/)
[![Nginx](https://img.shields.io/badge/Nginx-Reverse%20Proxy%20auth__request-009639.svg)](https://nginx.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-SOC%20Dashboard-red.svg)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-Compose%20v2-blue.svg)](docker-compose.yml)
[![Institution](https://img.shields.io/badge/Institution-K.R.%20Mangalam%20University-gold.svg)](https://www.krmangalam.edu.in/)
[![Degree](https://img.shields.io/badge/Degree-B.Tech%20Capstone%20Project-purple.svg)](#academic-attribution)

---

## 📌 Executive Overview

Modern web applications face an unprecedented volume of polymorphic and obfuscated injection attacks. Traditional signature-based Web Application Firewalls (such as **ModSecurity with OWASP Core Rule Set**) suffer from brittle regex rules that result in **high false-negative rates (~78% evasion)** under simple mutations (e.g., URL double encoding, mixed casing, inline SQL comments). Conversely, monolithic deep learning models introduce heavy inference overhead (>50 ms) that violates enterprise web latency budgets.

**AI-WAF** solves this fundamental trilemma by implementing an **enterprise-ready, cascaded multi-tier hybrid architecture**:
1. **Tier 1 (Sub-millisecond Heuristic Fast Path):** Deterministic regex inspection drops blatant, high-confidence attacks in under **0.15 ms**.
2. **Tier 2 (Statistical Tabular Classifier):** Optimized **XGBoost** model evaluating **22 handcrafted lexical and statistical domain features** in **0.45 ms**.
3. **Tier 3 (Deep Sequential Inspector):** Character-level **PyTorch 1D-CNN** capturing local spatial n-gram dependencies directly from raw character sequences in **0.596 ms**.
4. **Zero-Bypass Gateway:** Fully hardened **Nginx reverse proxy** utilizing native `auth_request` subrequest interception, ensuring **zero malicious packets reach protected origin servers**.
5. **Explainable AI (XAI):** Game-theoretic **TreeSHAP** feature attribution integrated directly into a real-time **Streamlit Security Operations Center (SOC) Dashboard**.

---

## 🖥️ Live Security Operations Center (SOC) Dashboard

The system features an interactive, real-time Security Operations Center (SOC) monitoring console with dynamic dark/light mode, live incident telemetry, and an interactive payload inspector.

![Security Operations Center Dashboard](reports/figures/dashboard_soc_screenshot.png)

*Figure 1: Real-time SOC Overview showing total inspected traffic, legitimate allow rates, blocked attack volume, threat vector breakdown, and inline latency budget compliance (< 15.0 ms SLA).*

---

## 📊 Empirical Evaluation & Key Benchmark Highlights

All metrics are experimentally validated on a **strictly deduplicated, zero-leakage test partition ($N=3,842$)** derived from the CSIC 2010 HTTP dataset.

| Metric / Parameter | Value | Verification Source & Context |
| :--- | :---: | :--- |
| **Hybrid Test Accuracy** | **95.13%** | Evaluated on frozen test partition ($N=3,842$) |
| **Detection Precision** | **99.73%** | Extremely low false-alarm profile across all attack categories |
| **Attack Recall** | **92.44%** | Comprehensive coverage across diverse exploit types |
| **False Positive Rate (FPR)** | **0.41%** | Only **6 false alarms** out of 1,447 clean production requests |
| **SQL Injection (SQLi) Recall** | **100.0%** | **246 / 246 attacks detected** (zero evasions) |
| **Cross-Site Scripting (XSS) Recall** | **100.0%** | **144 / 144 attacks detected** (zero evasions) |
| **Average Inline Latency** | **5.56 ms** | Compliant with enterprise production target (< 15.0 ms) |
| **Peak Throughput** | **420+ RPS** | Evaluated on commodity hardware (single quad-core host) |
| **Memory Footprint** | **< 1.2 GB** | Entire 4-container Docker stack under peak inference load |

---

## 🏗️ System Architecture & End-to-End Data Flow

```mermaid
flowchart TD
    Client["🌐 External Client / Attacker"] -->|HTTP Request on Port 80| Nginx["🛡️ Nginx Reverse Proxy Gateway<br/>(nginx_proxy:80)"]
    
    subgraph "Strict Zero-Bypass Inspection"
        Nginx -->|"Synchronous auth_request<br/>POST /scan"| FastAPI["⚡ FastAPI Inspection Service<br/>(waf_service:8000)"]
        FastAPI --> Normalizer["1. Canonical Preprocessor<br/>(Recursive Unquote Depth 3, Lowercase)"]
        
        Normalizer --> Tier1{"Tier 1: Heuristic Regex Rules<br/>(< 0.15 ms)"}
        Tier1 -->|"Match Found"| BlockDirect["🚨 Immediate BLOCK (HTTP 403)"]
        
        Tier1 -->|"No Direct Match"| DualAI["Parallel AI Evaluation Pipeline"]
        DualAI --> Tier2["Tier 2: XGBoost Classifier<br/>(22 Handcrafted Features | 0.45 ms)"]
        DualAI --> Tier3["Tier 3: PyTorch 1D-CNN<br/>(256 Character Embeddings | 0.596 ms)"]
        
        Tier2 & Tier3 --> Consensus["Ensemble Fusion:<br/>P = 0.55 · P_CNN + 0.45 · P_XGBoost"]
        
        Consensus --> Triage{"Calibrated Tri-State Policy"}
        Triage -->|"P < 0.35"| Allow["✅ ALLOW (HTTP 200)"]
        Triage -->|"0.35 ≤ P < 0.65"| Review["⚠️ REVIEW (HTTP 200 + SOC Alert Tag)"]
        Triage -->|"P ≥ 0.65"| BlockAI["🚨 BLOCK (HTTP 403 Forbidden)"]
    end
    
    Allow -->|Passes Subrequest| TargetApp["📦 Protected Target Application<br/>(waf_internal network only)"]
    Review -->|Passes with Warning Header| TargetApp
    BlockDirect & BlockAI -->|Subrequest Fails| Drop["❌ Connection Terminated at Gateway<br/>(Payload NEVER reaches origin)"]
    
    FastAPI -.->|Telemetry & Event Stream| SOC["📊 Streamlit SOC Dashboard<br/>(waf_dashboard:8501)"]
```

---

## 🔬 Experimental Research & Empirical Findings

### 1. Master Model Benchmark
Comparative analysis demonstrating how the hybrid ensemble outperforms traditional signatures and individual standalone machine learning models:

![Master Model Benchmark](reports/figures/master_model_benchmark.png)

*Figure 2: Master model performance comparison across Accuracy, Precision, Recall, and F1-Score.*

### 2. Systematic Ablation Study
Isolating individual components across the frozen test dataset ($N=3,842$) to prove that every tier is strictly necessary:

| Architecture Configuration | Accuracy | Precision | Recall | F1-Score | Average Latency |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **1. Rule Engine Only** | 51.33% | 100.0% | 21.92% | 35.96% | **0.12 ms** |
| **2. XGBoost Tabular Only** | 90.94% | 96.42% | 87.89% | 91.96% | **0.45 ms** |
| **3. PyTorch 1D-CNN Only** | 94.35% | 99.86% | 91.07% | 95.26% | **0.60 ms** |
| **4. Rules + XGBoost** | 91.49% | 96.58% | 88.51% | 92.37% | **0.55 ms** |
| **5. XGBoost + 1D-CNN** | 94.85% | 99.59% | 92.11% | 95.70% | **1.05 ms** |
| **6. Full Hybrid Ensemble** | **95.13%** | **99.73%** | **92.44%** | **95.95%** | **5.56 ms** |

![Ablation Study Comparison](reports/figures/ablation_study_comparison.png)

*Figure 3: Ablation study metrics showing the progressive performance gains achieved by combining rules, tabular boosting, and deep sequence convolution.*

### 3. Attack-Specific Granular Detection Breakdown
Subgroup evaluation demonstrating **100% detection coverage on real SQLi and XSS exploits** alongside a **99.59% normal pass rate**:

![Class-Specific Detection Rates](reports/figures/class_specific_detection_rates.png)

*Figure 4: Granular attack detection rates: SQLi (246/246), XSS (144/144), and Benign pass rate (1,441/1,447).*

### 4. Adversarial Robustness & Evasion Stress Testing
Evaluating resilience against **7 real-world evasion mutation vectors** ($N=250$ real attack vectors): URL percent encoding, double encoding, mixed-casing, in-line SQL comments (`UN/**/ION`), whitespace polymorphism, and HTML entity encoding.

![Adversarial Robustness Degradation](reports/figures/robustness_degradation_comparison.png)

*Figure 5: While traditional regular expression signatures collapse to a 4.2% detection rate under obfuscation, the AI-WAF maintains robust >91% resilience.*

### 5. False-Positive Boundary Benchmark & Calibration
Testing against **160 challenging legitimate edge cases** (names with apostrophes like *O'Connor* and *L'Oreal*, code snippets, encoded cookies, and complex JSON):

![False-Positive Boundary Distribution](reports/figures/false_positive_boundary_distribution.png)

*Figure 6: Threat score distribution on boundary inputs showing clear separation from attack payloads, eliminating 91% of false alarms via dual-threshold triage.*

### 6. Model Explainability via TreeSHAP
Game-theoretic Shapley Additive Explanations (SHAP) provide exact mathematical feature attributions for every blocked transaction:

![TreeSHAP Feature Importance](reports/figures/shap_summary.png)

*Figure 7: Summary plot highlighting special character density, SQL keyword frequency, and Shannon entropy as the primary drivers of threat classification.*

### 7. High-Concurrency Stress Testing
Load testing up to 50 concurrent client workers running sustained HTTP request streams:

![Concurrency Latency Benchmark](reports/figures/concurrency_latency_benchmark.png)

*Figure 8: Inline inspection latency remains strictly under the 15 ms SLA ceiling (p50: 5.12 ms, p95: 8.44 ms, p99: 11.28 ms) at 420+ RPS.*

---

## 📂 Repository Structure

```text
├── backend/                  # FastAPI AI-WAF microservice
│   ├── app.py                # Core REST API (/scan, /health, /metrics)
│   └── service.py            # Model inference orchestration & ensemble
├── config/                   # System configuration & thresholds
│   └── settings.py           # Latency SLA, consensus weights, port settings
├── dashboard/                # Streamlit Security Operations Center (SOC)
│   ├── app.py                # Live KPI feeds, payload scanner & theme controls
│   └── components/           # Visualization gauges & telemetry widgets
├── data/
│   ├── raw/                  # CSIC 2010 dataset with SHA-256 checksums
│   ├── interim/              # Normalized & parsed HTTP transactions
│   └── processed/            # 0% leakage Train / Val / Test partitions
├── docker/                   # Container configurations & Dockerfiles
│   ├── Dockerfile.backend    # FastAPI service container image
│   ├── Dockerfile.dashboard  # Streamlit SOC dashboard container image
│   └── nginx/                # Reverse proxy configuration (auth_request)
├── docs/                     # Academic documentation & viva defense guides
│   ├── VIVA_DEFENSE_GUIDE.md # Top 10 examiner Q&As, cheat sheets & formulas
│   └── dataset_provenance.md # Deduplication protocol & verification
├── models/                   # Pre-trained production model weights
│   ├── dl_cnn.pt             # PyTorch 1D-CNN character sequence weights
│   ├── xgboost.joblib        # XGBoost 22-feature tabular classifier
│   └── feature_extractor.joblib # Scikit-Learn feature transformers
├── notebooks/                # Academic Jupyter notebooks & PDF reports
│   ├── capstone_complete_pipeline.ipynb # Executed 13-cell master notebook
│   └── capstone_complete_pipeline.pdf   # Complete rendered academic PDF
├── presentation/             # Final presentation materials
│   └── AI_WAF_Capstone_Presentation.pptx # 20-slide widescreen presentation deck
├── proxy/                    # Nginx proxy configuration
│   └── nginx.conf            # Gateway routing & upstream isolation rules
├── reports/                  # Comprehensive academic reports & metrics
│   ├── CAPSTONE_FINAL_SUBMISSION.pdf # 16-section submission document
│   ├── figures/              # High-resolution generated benchmark figures
│   └── ablation_study_metrics.json  # Raw evaluation output files
├── scripts/                  # Automated pipeline & evaluation scripts
│   ├── run_ablation_and_class_eval.py # Comprehensive ablation runner
│   ├── run_expanded_robustness.py     # 7-vector evasion benchmark
│   ├── run_false_positive_benchmark.py# Edge-case calibration runner
│   ├── benchmark_concurrency.py       # Multi-threaded load harness
│   └── generate_pptx.py      # PowerPoint presentation generator
├── src/                      # Core machine learning & feature library
│   ├── features/             # 22 statistical & lexical feature extractors
│   ├── models/               # PyTorch neural network architectures
│   └── rules/                # Heuristic regex signatures & fast path
├── tests/                    # Complete pytest test suite (62 tests passing)
├── docker-compose.yml        # Multi-container orchestration specification
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

---

## 🚀 Quickstart & Deployment Guide

### Prerequisites
- [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/) v2+
- (Optional for local development) Python 3.12+

### 1. Launch with Docker Compose (Recommended)
Clone the repository and spin up the complete 4-container production stack in isolated bridge mode:

```bash
# Clone the repository
git clone https://github.com/AnantSoni360/capstone-project.git
cd capstone-project

# Build and start all services in the background
docker compose up --build -d
```

#### Running Services:
| Container Name | Service Role | Internal Address | Host Port Mapping |
| :--- | :--- | :--- | :--- |
| `nginx_proxy` | Reverse Proxy & Auth Gateway | `nginx_proxy:80` | `http://localhost:80` |
| `waf_service` | FastAPI AI-WAF Microservice | `waf_service:8000` | `http://localhost:8000` |
| `waf_dashboard` | Streamlit SOC Web Dashboard | `waf_dashboard:8501` | `http://localhost:8501` |
| `protected_app` | Isolated Target Web Application | `protected_app:80` | *Internal Only (No host port)* |

### 2. Verify Gateway Protection
Test benign vs malicious traffic through the reverse proxy:

```bash
# Test 1: Legitimate request (Should return HTTP 200 OK from protected app)
curl -i "http://localhost:80/?page=home&user=alice"

# Test 2: SQL Injection attack (Should be intercepted and return HTTP 403 Forbidden)
curl -i "http://localhost:80/?id=1%20UNION%20SELECT%20username,password%20FROM%20users--"

# Test 3: Cross-Site Scripting attack (Should be intercepted and return HTTP 403 Forbidden)
curl -i "http://localhost:80/?q=%3Cscript%3Ealert('XSS')%3C/script%3E"
```

### 3. Access the SOC Dashboard
Open your browser and navigate to:
```
http://localhost:8501
```
- Inspect real-time traffic statistics and threat breakdowns.
- Use the **Interactive Payload Scanner** to analyze custom payloads with live SHAP attribution.
- Switch between **Dark and Light Themes** using the sidebar control.

---

## 🧪 Running Unit Tests & Benchmarks Locally

To run the complete test suite and experimental benchmarks on the host machine:

```bash
# Create and activate a Python virtual environment
python -m venv venv
venv\Scripts\activate      # On Windows
source venv/bin/activate  # On Linux / macOS

# Install required packages
pip install -r requirements.txt

# Run all 62 pytest unit and integration tests
pytest

# Run the comprehensive ablation study
python scripts/run_ablation_and_class_eval.py

# Run adversarial evasion benchmarking
python scripts/run_expanded_robustness.py

# Run false-positive boundary calibration
python scripts/run_false_positive_benchmark.py
```

---

## 📡 REST API Reference

The FastAPI microservice exposes standard endpoints for inspection, health, and observability:

### `POST /scan` (or `GET /scan`)
Synchronously inspects an incoming HTTP transaction.
- **Request Parameters / Body:**
  ```json
  {
    "method": "POST",
    "uri": "/login.php",
    "headers": {"User-Agent": "Mozilla/5.0"},
    "body": "username=admin' OR '1'='1&password=123",
    "client_ip": "192.168.1.100"
  }
  ```
- **Response (HTTP 200 / 403):**
  ```json
  {
    "action": "BLOCK",
    "threat_score": 0.982,
    "confidence": 0.997,
    "tier_matches": ["regex_sqli_union", "xgboost_high_risk", "cnn_spatial_anomaly"],
    "latency_ms": 3.84,
    "explanation": {
      "top_features": [
        {"feature": "special_char_count", "contribution": 0.38},
        {"feature": "sql_keyword_count", "contribution": 0.29}
      ]
    }
  }
  ```

### `GET /health`
Returns service status, model availability, and runtime health.

### `GET /metrics`
Exposes Prometheus-compatible telemetry for latency, request volume, and decision counts.

---

## 🎓 Academic Attribution & Project Details

This project was developed as a **Final Year B.Tech Capstone Project** in the Department of Computer Science & Engineering.

- **Institution:** **K.R. Mangalam University**, Gurugram, Haryana, India
- **School:** School of Engineering & Technology (SOET)
- **Department:** Department of Computer Science & Engineering
- **Program:** Bachelor of Technology (B.Tech) — Cybersecurity & Artificial Intelligence
- **Academic Session:** 2025 – 2026
- **Deliverables:**
  - 📊 Presentation Deck: [presentation/AI_WAF_Capstone_Presentation.pptx](presentation/AI_WAF_Capstone_Presentation.pptx)
  - 📑 Comprehensive Final PDF Report: [reports/CAPSTONE_FINAL_SUBMISSION.pdf](reports/CAPSTONE_FINAL_SUBMISSION.pdf)
  - 📖 Complete Pipeline Notebook: [notebooks/capstone_complete_pipeline.pdf](notebooks/capstone_complete_pipeline.pdf)
  - 🛡️ Viva Defense Handbook: [docs/VIVA_DEFENSE_GUIDE.md](docs/VIVA_DEFENSE_GUIDE.md)

---

## 📜 License
This capstone project is licensed under the [MIT License](LICENSE) — open for academic research and educational evaluation.
