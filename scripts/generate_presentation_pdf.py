"""
Generates a publication-grade PDF handbook of the 20-Slide Capstone Presentation Scripts
for K.R. Mangalam University B.Tech Defense using Mistune and Chrome Headless.
"""

import os
import pathlib
import subprocess
import sys
import mistune

WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent

MD_PATH = WORKSPACE_ROOT / "presentation" / "CAPSTONE_PRESENTATION_SPEAKER_SCRIPTS.md"
HTML_PATH = WORKSPACE_ROOT / "presentation" / "CAPSTONE_PRESENTATION_SPEAKER_SCRIPTS.html"
PDF_PATH = WORKSPACE_ROOT / "presentation" / "CAPSTONE_PRESENTATION_SPEAKER_SCRIPTS.pdf"

md_content = """# 🎙️ B.Tech Capstone Presentation Defense Handbook & Speaker Scripts
## Comparative Analysis of Traditional and AI-Driven Threat Detection (AI-WAF)
### **K.R. Mangalam University • School of Engineering & Technology**
**Department of Computer Science & Engineering | Academic Session 2025–2026**

---

### **Project & Team Information**
* **Project Title:** Comparative Analysis of Traditional and AI-Driven Threat Detection Techniques in Cybersecurity: Design, Implementation, and Evaluation of an Autonomous, Low-Latency AI-Powered Web Application Firewall (AI-WAF)
* **Program:** Bachelor of Technology (B.Tech) — Computer Science & Engineering (AI / ML Specialization)
* **Project Team Members:**
  1. **Anant Soni** (Roll No: 2301730095)
  2. **Pabitra Giri** (Roll No: 2301730081)
  3. **Anurag Pandey** (Roll No: 2301730094)
  4. **Saksham Pachauri** (Roll No: 2301730060)
  5. **Piyush Gauswami** (Roll No: 2301730062)
* **Live Streamlit SOC Deployment:** [https://capstone-project-cc6nhqgmfapc7rvfrhwcub.streamlit.app/](https://capstone-project-cc6nhqgmfapc7rvfrhwcub.streamlit.app/)
* **GitHub Repository:** [https://github.com/AnantSoni360/capstone-project](https://github.com/AnantSoni360/capstone-project)

---

## ⏱️ Recommended 5-Member Team Presentation Strategy (20 Minutes Total)
To ensure balanced participation and smooth pacing (~1 minute per slide), the presentation is structured across 5 speaker slots (4 slides per speaker):

| Speaker | Team Member | Assigned Slides | Topics Covered |
| :---: | :--- | :---: | :--- |
| **Speaker 1** | **Anant Soni** | **Slides 1 – 4** | Title & Introduction, Executive Summary, The WAF Trilemma, System Architecture |
| **Speaker 2** | **Pabitra Giri** | **Slides 5 – 8** | Dataset Deduplication Hygiene, Dual-Domain Features, Classical ML Baselines, PyTorch 1D-CNN |
| **Speaker 3** | **Anurag Pandey** | **Slides 9 – 12** | Multi-Tier Decision Engine, Ablation Study, Granular Vulnerability Detection, Adversarial Robustness |
| **Speaker 4** | **Saksham Pachauri** | **Slides 13 – 16** | False-Positive Boundary Calibration, TreeSHAP Explainability, Concurrency Benchmarks, Zero-Bypass Gateway |
| **Speaker 5** | **Piyush Gauswami** | **Slides 17 – 20** | Live SOC Dashboard Demo, Comparative Synthesis Matrix, Hardware Profiling & Scope, Conclusion & Q&A |

---

<div class="page-break"></div>

# Slide-by-Slide Complete Speaker Scripts (~1 Minute Each)

---

### **Slide 1: Title & Team Introductions**
* **Assigned Speaker:** Speaker 1 (Anant Soni)
* **Timing:** ~50–55 seconds | **Word Count:** 125 words
* **Visuals on Screen:** University branding banner, project title, and team member roll numbers.

> *"Good morning, respected members of the evaluation committee and faculty guides. Today, our team is presenting our B.Tech Capstone Project titled: **'Comparative Analysis of Traditional and AI-Driven Threat Detection Techniques in Cybersecurity: Design, Implementation, and Evaluation of an Autonomous, Low-Latency AI-Powered Web Application Firewall'**.*
>
> *This work was conducted under the Department of Computer Science & Engineering at **K.R. Mangalam University**.*
>
> *Our project team consists of **Anant Soni, Pabitra Giri, Anurag Pandey, Saksham Pachauri, and Piyush Gauswami**, specializing in Artificial Intelligence and Machine Learning. Over the next twenty minutes, we will present the critical vulnerabilities in existing firewalls, our hybrid multi-model architecture, our verified empirical findings, and a live demonstration of our production security gateway."*

* **Anchor Takeaway for Examiners:** Establishes formal academic rigor and clear team ownership right from the start.

---

### **Slide 2: Executive Summary & Project Motivation**
* **Assigned Speaker:** Speaker 1 (Anant Soni)
* **Timing:** ~60 seconds | **Word Count:** 135 words
* **Visuals on Screen:** 4 Golden Metric Tiles (95.13% Acc, 0.41% FPR, 5.56ms Latency, 100% SQLi/XSS) + Problem vs Solution cards.

> *"To provide an executive summary: Web applications today account for over **43% of enterprise breaches**, primarily through injection attacks. The industry standard firewall—ModSecurity with OWASP Core Rules—relies on static regular expressions that suffer an alarming **78% evasion rate** when attackers use basic obfuscation.*
>
> *Conversely, monolithic deep learning models introduce heavy inference overhead exceeding 50 milliseconds, violating enterprise web latency budgets.*
>
> *Our capstone resolves this fundamental dilemma through an autonomous **Multi-Tier Hybrid Architecture**. As highlighted in our top metric cards, our system achieves a **95.13% overall test accuracy**, a **100% detection rate on real SQL injection and Cross-Site Scripting exploits**, and a near-zero **false-alarm rate of 0.41%**, while maintaining an ultra-fast average inline inspection latency of just **5.56 milliseconds**."*

* **Anchor Takeaway for Examiners:** Demonstrates awareness of real-world industry pain points with verified quantitative metrics.

---

### **Slide 3: Research Context & The WAF Trilemma**
* **Assigned Speaker:** Speaker 1 (Anant Soni)
* **Timing:** ~60 seconds | **Word Count:** 130 words
* **Visuals on Screen:** The WAF Trilemma breakdown + Comparative Research Gap Matrix Table.

> *"Every enterprise Web Application Firewall faces what we define as the **WAF Trilemma**: the constant trade-off between **High Detection Accuracy**, **Low Inline Latency (< 15 ms)**, and **Minimal False Positives (< 1%)**.*
>
> *If you tighten traditional regular expressions to catch attacks, you increase false positives and inadvertently block legitimate, paying customers. If you relax the rules, attackers bypass them using SQL comment injections, mixed-case lettering, and double URL encoding.*
>
> *As illustrated in our comparative matrix on the right, traditional rules fail under obfuscation with only 4.2% recall. Standalone machine learning models reduce blind spots but lack explainability. Our hybrid architecture is engineered specifically to eliminate these trade-offs, delivering sub-6ms latency, robust zero-day evasion resilience, and full mathematical explainability."*

* **Anchor Takeaway for Examiners:** Explains why you cannot simply add more regex rules—it destroys user experience.

---

### **Slide 4: System Architecture & End-to-End Pipeline**
* **Assigned Speaker:** Speaker 1 (Anant Soni)
* **Timing:** ~60 seconds | **Word Count:** 135 words
* **Visuals on Screen:** Defense-in-Depth network diagram + Component Mapping Table (Nginx, FastAPI, Docker bridge).

> *"This slide details our end-to-end gateway architecture. Rather than deploying as an application-level library, our system is engineered as an **infrastructure reverse proxy gateway**.*
>
> *External clients connect to an **Nginx reverse proxy** on Port 80. For every incoming request, Nginx triggers a synchronous subrequest via the native `auth_request` directive to our **FastAPI AI inspection microservice**.*
>
> *Here is the critical security guarantee: the target web application has **zero open host ports**—it is physically isolated on an internal Docker bridge network (`waf_internal`). If our inspection engine calculates a threat score of 0.65 or above, Nginx immediately terminates the connection with an HTTP 403 Forbidden. The malicious payload **never physically reaches the target origin server**, guaranteeing zero-bypass security.*
>
> *Now, I hand over to Pabitra to walk through our dataset engineering and machine learning pipeline."*

* **Anchor Takeaway for Examiners:** The target application is physically unreachable from the outside; only inspected traffic can pass.

---

<div class="page-break"></div>

### **Slide 5: Dataset Engineering & CSIC 2010 Deduplication**
* **Assigned Speaker:** Speaker 2 (Pabitra Giri)
* **Timing:** ~60 seconds | **Word Count:** 140 words
* **Visuals on Screen:** CSIC 2010 processing pipeline + Class Distribution Chart (`class_distribution.png`).

> *"Thank you, Anant. A critical contribution of our project lies in rigorous dataset hygiene. We evaluated our system on the benchmark **CSIC 2010 HTTP Dataset**, comprising 61,065 raw requests.*
>
> *During exploratory data analysis, we discovered a massive academic flaw in the raw corpus: **35,457 requests—representing 58.06% of the dataset—were exact synthetic duplicates**.*
>
> *If a project trains and tests on duplicated data, the model simply memorizes hashes, causing severe **Data Leakage** and reporting falsely inflated 99% accuracy. We eliminated all duplicates to establish **25,608 unique real-world requests**.*
>
> *As shown in the class distribution chart on the right, we partitioned this into 70% Train, 15% Validation, and 15% Frozen Test ($N = 3,842$), verifying **0.00% leakage overlap** across all partitions for true academic rigor."*

* **Anchor Takeaway for Examiners:** You detected and solved a real data hygiene flaw; your 95% accuracy is honest and generalizable.

---

### **Slide 6: Dual-Domain Feature Engineering**
* **Assigned Speaker:** Speaker 2 (Pabitra Giri)
* **Timing:** ~60 seconds | **Word Count:** 135 words
* **Visuals on Screen:** 22 Handcrafted tabular features breakdown + 256-token character ASCII embeddings + Special Character Frequency Chart.

> *"To feed HTTP traffic into machine learning models, we developed a **Dual-Domain Feature Pipeline**.*
>
> *For our tabular boosting model, we extract **22 handcrafted statistical features**. This includes **Shannon Information Entropy** to quantify randomness—since obfuscated shellcode exhibits entropy above 4.2 compared to standard text around 3.0. We also extract special delimiter ratios for single quotes, semicolons, dashes, and slashes, alongside SQL and XSS keyword counters.*
>
> *For our deep learning model, we normalize sequences into a fixed 256-character window, mapping 100 printable ASCII tokens into **64-dimensional learned continuous embeddings**.*
>
> *The figure on the right demonstrates the sharp statistical divergence in special character density between benign traffic in green and attack traffic in red."*

* **Anchor Takeaway for Examiners:** You combine domain-knowledge cybersecurity statistics with raw character sequence embeddings.

---

### **Slide 7: Classical ML Exploration & Baselines**
* **Assigned Speaker:** Speaker 2 (Pabitra Giri)
* **Timing:** ~60 seconds | **Word Count:** 130 words
* **Visuals on Screen:** Benchmark comparison of 5 classical algorithms + Classical Performance & ROC Curves Chart (`ml_models_comparison.png`).

> *"On this slide, we present our exploration of classical supervised algorithms evaluated across our 22 tabular features.*
>
> *We benchmarked Logistic Regression, Linear SVM, Random Forest, LightGBM, and XGBoost. While Logistic Regression was fast, its linear hyperplane could not resolve non-linear delimiter combinations, stalling at 79.2% accuracy. Random Forest achieved strong recall but had a 45 MB memory footprint and slower tree traversal.*
>
> *As seen in the ROC curves on the right, **XGBoost emerged as our clear classical champion**, achieving an **AUC of 0.9732, 90.94% accuracy, 96.42% precision, and a blistering 0.45 ms inference latency**. This performance earned XGBoost its place as our Tier 2 tabular engine."*

* **Anchor Takeaway for Examiners:** XGBoost was chosen after empirical benchmarking against 4 other classical models.

---

### **Slide 8: Deep Learning Architecture (PyTorch 1D-CNN)**
* **Assigned Speaker:** Speaker 2 (Pabitra Giri)
* **Timing:** ~60 seconds | **Word Count:** 135 words
* **Visuals on Screen:** 1D-CNN layer specifications + Training & Validation Loss Curves (`dl_training_curves.png`).

> *"To catch attacks that bypass word-level statistics, we engineered a custom **character-level PyTorch 1D-CNN**. We avoided recurrent LSTMs because their sequential token processing causes latency bottlenecks.*
>
> *Our 1D-CNN uses parallel convolutional filters with kernel sizes of **3, 5, and 7**, acting as multi-scale n-gram detectors that capture 3-letter tokens like `OR `, 5-letter tokens like `UNION`, and 7-letter tags like `<SCRIPT>` anywhere in the string.*
>
> *These features are batch-normalized, pooled via Adaptive Max Pooling, and passed through regularized dense layers with Dropout.*
>
> *As demonstrated in the training curves on the right, our 1D-CNN achieves smooth convergence without overfitting, delivering **94.35% test accuracy, 99.86% precision, and only 0.596 ms latency**.*
>
> *I now invite Anurag to present our decision consensus and experimental ablation results."*

* **Anchor Takeaway for Examiners:** Kernels 3, 5, and 7 extract character n-grams in parallel with sub-millisecond execution.

---

<div class="page-break"></div>

### **Slide 9: Enforcement Engine & Tri-State Policy**
* **Assigned Speaker:** Speaker 3 (Anurag Pandey)
* **Timing:** ~60 seconds | **Word Count:** 135 words
* **Visuals on Screen:** Cascaded triage workflow + Tri-State Policy Matrix Table (ALLOW, REVIEW, BLOCK).

> *"Thank you, Pabitra. This slide explains our cascaded decision logic and tri-state triage policy.*
>
> *When an HTTP request enters the gateway, it first encounters **Tier 1: a Heuristic Regex Fast Path**. Blatant, un-obfuscated CVE signatures are dropped immediately in **under 0.15 milliseconds**, without invoking AI.*
>
> *If ambiguous, the request enters **Tier 2 (XGBoost)** and **Tier 3 (1D-CNN)** in parallel, generating a fused threat probability: $P = 0.55 \cdot P_{\text{CNN}} + 0.45 \cdot P_{\text{XGBoost}}$.*
>
> *Rather than a rigid binary cutoff, we implement a **Calibrated Tri-State Policy**: scores under 0.35 are **ALLOWED**; scores of 0.65 and above are **BLOCKED**; and boundary scores between 0.35 and 0.65 are routed to **REVIEW**—passed with an alert header to protect legitimate user traffic."*

* **Anchor Takeaway for Examiners:** Dual-threshold calibration avoids the catastrophic false alarms of a single 0.50 cutoff.

---

### **Slide 10: Complete Ablation Study & Justification**
* **Assigned Speaker:** Speaker 3 (Anurag Pandey)
* **Timing:** ~60 seconds | **Word Count:** 140 words
* **Visuals on Screen:** Ablation metrics table + Ablation Performance Comparison Chart (`ablation_study_comparison.png`).

> *"To prove that every tier in our architecture is necessary, we conducted an exhaustive ablation study across our frozen test set of 3,842 requests.*
>
> *Looking at the table and chart on the right:
> * The **Rule Engine alone** achieves only 51.33% accuracy with a disastrous **78.08% False Negative Rate**—missing four out of five attacks.
> * **XGBoost alone** jumps to 90.94% accuracy but lacks spatial character awareness.
> * **1D-CNN alone** delivers 94.35% accuracy and 99.86% precision.
> * When combined into our **Full Hybrid Ensemble**, we achieve our state-of-the-art peak: **95.13% accuracy, 99.73% precision, 92.44% recall, and an inline latency of 5.56 milliseconds**.*
>
> *This empirically confirms that combining rules, boosting, and deep convolutions yields the most resilient defense."*

* **Anchor Takeaway for Examiners:** You have empirical evidence proving why every single component was added.

---

### **Slide 11: Granular Vulnerability Evaluation**
* **Assigned Speaker:** Speaker 3 (Anurag Pandey)
* **Timing:** ~60 seconds | **Word Count:** 130 words
* **Visuals on Screen:** Granular metrics breakdown + Detection Rate by Threat Category Bar Chart (`class_specific_detection_rates.png`).

> *"Here, we evaluate our system's granular detection rates across specific attack categories on the held-out test partition.*
>
> *As shown in the bar chart:
> * On **SQL Injection**, our Hybrid Ensemble detected **246 out of 246 attacks—a 100.0% detection rate** across error-based and boolean-blind vectors.
> * On **Cross-Site Scripting (XSS)**, the system caught **144 out of 144 attacks—also 100.0% detection** across reflected tags, event handlers, and iframe injections.
> * Crucially, out of 1,447 clean, benign production requests, **1,441 were correctly passed**, representing a **99.59% normal pass rate and a false-positive rate of just 0.41%**.*
>
> *Our firewall reliably stops dangerous exploits without degrading genuine user traffic."*

* **Anchor Takeaway for Examiners:** 100% detection on both SQLi and XSS on the frozen test partition.

---

### **Slide 12: Adversarial Robustness & Evasion Stress Test**
* **Assigned Speaker:** Speaker 3 (Anurag Pandey)
* **Timing:** ~60 seconds | **Word Count:** 140 words
* **Visuals on Screen:** 7 Mutation vectors breakdown + Comparative Degradation Curves (`robustness_degradation_comparison.png`).

> *"Next, we stress-tested our firewall against **7 adversarial evasion techniques**: URL percent encoding, double encoding, mixed casing, inline SQL comments, whitespace substitution, and HTML entities.*
>
> *The dual-panel graph on the right illustrates our findings:
> * Panel A shows that without normalization, traditional rules collapse from 21.9% down to an abysmal **4.2% detection rate**—letting 95% of attacks slip through.
> * Panel B shows the performance of our integrated pipeline with recursive unquoting and character convolutions. Our AI-WAF maintains an average detection rate of **91.8% across all evasion vectors**.*
>
> *Our preprocessor and character-level embeddings effectively neutralize syntactic obfuscation, proving that the model learns actual attack semantics rather than brittle keyword strings.*
>
> *I now hand over to Saksham to discuss false-positive boundary calibration and model explainability."*

* **Anchor Takeaway for Examiners:** Rules drop to 4.2% under mutation; our AI-WAF holds strong above 91%.

---

<div class="page-break"></div>

### **Slide 13: False-Positive Boundary Benchmark**
* **Assigned Speaker:** Speaker 4 (Saksham Pachauri)
* **Timing:** ~60 seconds | **Word Count:** 135 words
* **Visuals on Screen:** 160 Legitimate edge cases breakdown + Threat Score Distribution Chart (`false_positive_boundary_distribution.png`).

> *"Thank you, Anurag. In enterprise production, false alarms destroy revenue. If an e-commerce firewall blocks a customer whose name is *O'Connor* or who orders *L'Oreal* shampoo, that customer is lost.*
>
> *We evaluated **160 complex legitimate edge cases**: names with apostrophes, forum posts containing code syntax like `x < 5 and y > 2`, Base64 session cookies, and nested JSON payloads.*
>
> *As shown in the distribution chart, a standard single threshold at 0.50 blocked 30% of these benign requests. Our **calibrated dual-threshold policy** safely routes these boundary inputs into the REVIEW state, **eliminating 91% of false alarms** and keeping false blocks at just 0.41% while maintaining full attack coverage."*

* **Anchor Takeaway for Examiners:** Dual-threshold calibration protects paying customers while flagging edge cases for SOC audit.

---

### **Slide 14: Explainable AI (TreeSHAP Attribution)**
* **Assigned Speaker:** Speaker 4 (Saksham Pachauri)
* **Timing:** ~60 seconds | **Word Count:** 135 words
* **Visuals on Screen:** TreeSHAP mathematical formulation + Feature Attribution Beeswarm Plot (`shap_summary.png`).

> *"A critical requirement in modern cybersecurity compliance is explainability. Enterprise SOC teams refuse to deploy 'black-box' neural networks that cannot provide an audit trail for blocked requests.*
>
> *To solve this, we integrated **TreeSHAP (Shapley Additive Explanations)** based on cooperative game theory.*
>
> *The beeswarm plot on the right highlights the global risk drivers:
> * High special character ratios and SQL keyword frequencies exhibit strong positive SHAP values pushing predictions toward BLOCK.
> * Common alphanumeric paths exhibit negative SHAP values maintaining ALLOW.*
>
> *Whenever our gateway blocks a transaction, TreeSHAP calculates the exact marginal feature contributions in real time, rendering a visual explanation directly in the SOC dashboard."*

* **Anchor Takeaway for Examiners:** You provide mathematically grounded audit trails for every security decision.

---

### **Slide 15: Concurrency & Latency Benchmarking**
* **Assigned Speaker:** Speaker 4 (Saksham Pachauri)
* **Timing:** ~60 seconds | **Word Count:** 130 words
* **Visuals on Screen:** Latency percentiles vs concurrency curve + Throughput Scaling Bar Chart (`concurrency_latency_benchmark.png`).

> *"To prove enterprise throughput scalability, we benchmarked our gateway under increasing load up to **50 concurrent client connections**.*
>
> *Looking at the percentile curves on the left:
> * Median latency ($p_{50}$) is **5.12 milliseconds**.
> * 95th percentile latency ($p_{95}$) is **8.44 milliseconds**.
> * 99th percentile latency ($p_{99}$) is **11.28 milliseconds**—strictly below our 15.0 ms production SLA ceiling.*
>
> *As shown in the throughput bars on the right, the single-host gateway sustains **152 to 179 requests per second** under sustained load with zero dropped connections and a flat 1.15 GB RAM footprint, proving that our AI inference adds negligible overhead to production traffic."*

* **Anchor Takeaway for Examiners:** Throughput and p99 latency strictly adhere to production web performance budgets.

---

### **Slide 16: Zero-Bypass Gateway Security Verification**
* **Assigned Speaker:** Speaker 4 (Saksham Pachauri)
* **Timing:** ~60 seconds | **Word Count:** 135 words
* **Visuals on Screen:** Gateway protocol verification matrix table (GET, POST, PUT, JSON, Multipart, Malformed).

> *"This slide demonstrates our gateway security audit. We subjected our Nginx `auth_request` configuration to an exhaustive protocol verification matrix covering HTTP GET, POST, PUT, DELETE, JSON, and multipart form data, with payload sizes from 128 bytes to 10 megabytes.*
>
> *In every attack test scenario, the subrequest returned an HTTP 403 Forbidden in under 4 milliseconds. Because Nginx immediately drops the connection, our backend origin access logs recorded **exactly zero packet arrivals**.*
>
> *Furthermore, we verified fail-closed hardening: when corrupt headers or scanner timeouts were injected, the gateway safely defaulted to dropping the connection, ensuring that no request ever bypasses inspection.*
>
> *I now hand over to Piyush to present our live SOC dashboard and final synthesis."*

* **Anchor Takeaway for Examiners:** Attack payloads are dropped at the gateway; 0% packet leakage to upstream servers.

---

<div class="page-break"></div>

### **Slide 17: Interactive SOC Dashboard (Live Demo)**
* **Assigned Speaker:** Speaker 5 (Piyush Gauswami)
* **Timing:** ~60 seconds | **Word Count:** 135 words
* **Visuals on Screen:** Live Streamlit SOC Dashboard Screenshot (`dashboard_soc_screenshot.png`) + Public Cloud Deployment Link.

> *"Thank you, Saksham. To give security operators real-time observability, we developed a production-ready **Security Operations Center (SOC) dashboard** in Streamlit.*
>
> *As captured in the screenshot:
> * The top telemetry cards display live counts for Total Inspected, Legitimate Traffic, Blocked Attacks, and Review incidents.
> * The center bar chart breaks down detected attack vectors in real time.
> * The right panel provides live SLA latency gauges.*
>
> *The dashboard also features an **Interactive Payload Scanner** where analysts can paste raw HTTP requests to view instant model probabilities and SHAP feature waterfalls. It is deployed and publicly accessible right now on Streamlit Cloud at **capstone-project.streamlit.app**."*

* **Anchor Takeaway for Examiners:** You have a working, publicly deployed cloud demonstration ready for examiners to test live.

---

### **Slide 18: Comparative Paradigm Synthesis**
* **Assigned Speaker:** Speaker 5 (Piyush Gauswami)
* **Timing:** ~60 seconds | **Word Count:** 140 words
* **Visuals on Screen:** Master final benchmark across all systems chart (`master_model_benchmark.png`).

> *"This slide summarizes our core academic findings comparing all four threat detection paradigms:
> 1. **Traditional Regex (ModSecurity):** Incredibly fast at 0.12 ms, but completely blind to obfuscation with a 78% evasion rate.
> 2. **Standalone XGBoost:** High tabular accuracy at 90.94%, but vulnerable to novel character substitutions.
> 3. **Standalone PyTorch 1D-CNN:** Exceptional precision at 99.86%, but lacks fast-path heuristic shortcuts for obvious attacks.
> 4. **Our Proposed Hybrid AI-WAF:** The optimal engineering synthesis—achieving **95.13% accuracy, 100% recall on SQLi and XSS, a 0.41% false-alarm rate, and 5.56 ms latency**.*
>
> *As shown in the master benchmark chart, our hybrid ensemble outperforms every individual model across balanced F1-score and operational safety."*

* **Anchor Takeaway for Examiners:** High-level executive synthesis summarizing the entire experimental comparative study.

---

### **Slide 19: Hardware Constraints & Future Scope**
* **Assigned Speaker:** Speaker 5 (Piyush Gauswami)
* **Timing:** ~60 seconds | **Word Count:** 135 words
* **Visuals on Screen:** 3 Structured Cards: Hardware Profiling, Current Limitations, Future Research Scope.

> *"Regarding operational viability: our entire 4-container Docker stack was benchmarked on standard commodity laptop hardware—an Intel i5/i7 processor with 16 GB of RAM and an NVIDIA GTX 1650 GPU. Peak resource utilization remained under **1.2 GB of RAM and under 15% CPU**, demonstrating that small-to-medium enterprises can deploy this system without costly cloud infrastructure.*
>
> *For future research, we have identified three expansion pathways:
> 1. Packaging the inspection engine as an **Envoy sidecar proxy** for Kubernetes microservice meshes.
> 2. Integrating **quantized Transformer models like MiniLM** for deep semantic query parsing.
> 3. Implementing **continuous active learning** where analyst feedback on REVIEW events automatically fine-tunes decision thresholds."*

* **Anchor Takeaway for Examiners:** The system is lightweight, cost-effective, and has a clear research expansion roadmap.

---

### **Slide 20: Conclusion & Committee Viva Q&A**
* **Assigned Speaker:** Speaker 5 (Piyush Gauswami)
* **Timing:** ~60 seconds | **Word Count:** 130 words
* **Visuals on Screen:** Summary of contributions cards + Committee Q&A Invitation Banner.

> *"In conclusion, our capstone project demonstrates that an AI-driven, multi-tier Web Application Firewall can successfully bridge the gap between deterministic speed and deep learning resilience.*
>
> *By resolving the CSIC 2010 synthetic duplicate leakage, engineering a hybrid cascade of regex, XGBoost, and PyTorch 1D-CNN, and deploying a zero-bypass Nginx gateway with live Streamlit observability, we have delivered a mathematically validated, production-grade cybersecurity solution.*
>
> *Our full codebase, trained models, test suites, and documentation are publicly available on GitHub, and our live dashboard is accessible online.*
>
> *On behalf of our team—**Anant Soni, Pabitra Giri, Anurag Pandey, Saksham Pachauri, and Piyush Gauswami**—we thank you for your time, and we welcome questions from the evaluation committee."*

* **Anchor Takeaway for Examiners:** Confident, formal close inviting technical questions.

---

<div class="page-break"></div>

# 🎯 Top 10 Rapid-Fire Viva Defense Cheat Sheet

| Question | Winning Examiner Answer |
| :--- | :--- |
| **Q1: What is your final accuracy?** | **95.13% test accuracy** on the frozen, leak-free test partition ($N = 3,842$) derived from deduplicated CSIC 2010 data. |
| **Q2: What is your inspection latency?** | **5.56 ms average inline latency**, well below the enterprise SLA ceiling of 15.0 ms. |
| **Q3: What is your false-positive rate?** | **0.41%** (only 6 false alarms out of 1,447 clean production requests). |
| **Q4: How do you catch zero-days / obfuscation?** | Our preprocessor recursively decodes up to depth 3, and the PyTorch 1D-CNN captures character n-grams across kernels 3, 5, and 7, maintaining >91% accuracy against 7 mutation vectors. |
| **Q5: Why not use a Transformer (BERT/GPT)?** | Transformers require 30–100 ms per inference and multiple gigabytes of VRAM. Our 1D-CNN runs in 0.596 ms with a 0.23 MB weight footprint. |
| **Q6: How do you prove zero data leakage?** | We purged 35,457 duplicates (58.06% of raw CSIC 2010) and verified that the intersection between Train, Validation, and Test sets is strictly 0. |
| **Q7: What is the purpose of the REVIEW state?** | Boundary requests ($0.35 \le P < 0.65$) like names with apostrophes are allowed through with a warning header, eliminating 91% of false blocks without risking security. |
| **Q8: How does Nginx guarantee zero-bypass?** | The protected app container has no exposed host ports on `waf_internal`. Nginx uses `auth_request` to verify requests before proxying; blocked attacks never arrive. |
| **Q9: How do you explain blocks to SOC analysts?** | We integrate TreeSHAP to calculate exact game-theoretic Shapley contributions for special character counts, entropy, and keywords. |
| **Q10: Where is the live deployment?** | Deployed live on Streamlit Cloud at `https://capstone-project-cc6nhqgmfapc7rvfrhwcub.streamlit.app/`. |
"""

print(f"[1/3] Writing Markdown content to: {MD_PATH}...")
with open(MD_PATH, "w", encoding="utf-8") as f:
    f.write(md_content)

print(f"[2/3] Rendering HTML with Mistune and custom styling...")
html_body = mistune.html(md_content)

styled_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>B.Tech Capstone Presentation Defense Handbook & Speaker Scripts</title>
<style>
    @page {{
        size: A4;
        margin: 18mm 15mm 18mm 15mm;
        @bottom-right {{
            content: counter(page);
        }}
    }}
    body {{
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
        font-size: 10pt;
        line-height: 1.55;
        color: #1e293b;
        background-color: #ffffff;
    }}
    .page-break {{
        page-break-before: always;
    }}
    h1 {{
        color: #0f172a;
        font-size: 18pt;
        border-bottom: 2.5px solid #f59e0b;
        padding-bottom: 5px;
        margin-top: 15px;
        margin-bottom: 10px;
    }}
    h2 {{
        color: #d97706;
        font-size: 13pt;
        margin-top: 12px;
        margin-bottom: 6px;
    }}
    h3 {{
        color: #0f172a;
        font-size: 11pt;
        background-color: #fef3c7;
        border-left: 4px solid #f59e0b;
        padding: 5px 10px;
        margin-top: 15px;
        margin-bottom: 8px;
    }}
    blockquote {{
        background-color: #f8fafc;
        border-left: 4px solid #3b82f6;
        margin: 8px 0;
        padding: 10px 14px;
        font-size: 9.5pt;
        font-style: italic;
        color: #334155;
        line-height: 1.6;
    }}
    blockquote strong {{
        color: #0f172a;
        font-style: normal;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 10px 0 15px 0;
        font-size: 8.5pt;
    }}
    th {{
        background-color: #0f172a;
        color: #f8fafc;
        text-align: left;
        padding: 7px 10px;
        font-weight: 600;
        border: 1px solid #334155;
    }}
    td {{
        padding: 6px 10px;
        border: 1px solid #cbd5e1;
        vertical-align: top;
    }}
    tr:nth-child(even) td {{
        background-color: #f8fafc;
    }}
    ul, ol {{
        margin: 6px 0 10px 20px;
        padding: 0;
    }}
    li {{
        margin-bottom: 4px;
    }}
    strong {{
        color: #0f172a;
    }}
    code {{
        background-color: #f1f5f9;
        color: #b45309;
        padding: 2px 5px;
        border-radius: 4px;
        font-family: Consolas, monospace;
        font-size: 8.5pt;
    }}
    hr {{
        border: 0;
        height: 1px;
        background: #e2e8f0;
        margin: 15px 0;
    }}
</style>
</head>
<body>
{html_body}
</body>
</html>
"""

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(styled_html)
print(f"[SUCCESS] HTML written to: {HTML_PATH}")

print(f"[3/3] Printing PDF via Headless Chrome Engine...")
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
browser = chrome_path if os.path.exists(chrome_path) else edge_path

cmd = [
    browser,
    "--headless",
    "--disable-gpu",
    "--no-sandbox",
    "--run-all-compositor-stages-before-draw",
    "--no-pdf-header-footer",
    f"--print-to-pdf={PDF_PATH}",
    HTML_PATH.as_uri()
]

res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
if PDF_PATH.exists() and PDF_PATH.stat().st_size > 0:
    print("=" * 60)
    print(f"[SUCCESS] PDF Generated Successfully!")
    print(f"File Path: {PDF_PATH}")
    print(f"File Size: {PDF_PATH.stat().st_size:,} bytes ({PDF_PATH.stat().st_size / (1024 * 1024):.2f} MB)")
    print("=" * 60)
else:
    print(f"[ERROR] PDF generation failed: {res.stderr}")
    sys.exit(1)
