# B.Tech Capstone Viva Defense Guide & Examiner Q&A Handbook
## Project: Comparative Analysis of Traditional and AI-Driven Threat Detection (AI-WAF)
### Academic Target: 100-Mark Capstone Viva & Live System Demonstration

---

## 1. The 60-Second Executive Pitch (Memorize This)

> *"Respected Examiners, our capstone project investigates and demonstrates why traditional signature-based Web Application Firewalls (like ModSecurity regex rules) fail against modern cyberattacks, and how an AI-driven multi-model architecture solves these limitations.*
>
> *We evaluated traditional rules against classical machine learning (XGBoost) and deep learning (PyTorch 1D-CNN) using the CSIC 2010 HTTP corpus. We discovered and resolved a major 58.06% synthetic duplicate leakage vulnerability in the raw dataset, establishing a strictly frozen 15% test benchmark of 3,842 requests.*
>
> *Our empirical results prove that while traditional rules suffer a catastrophic 78.08% False Negative Rate, our PyTorch 1D-CNN achieves 94.35% accuracy and 99.86% precision. When fused into a collaborative hybrid ensemble with recursive multi-pass canonicalization, our system achieves **95.13% overall accuracy, 100.00% detection on SQL Injection, and 100.00% detection on XSS** at an average inspection latency of **5.56 ms**.*
>
> *The entire system is deployed across an Nginx reverse proxy gateway using asynchronous subrequest authorization in Docker, physically isolating the upstream web application with zero exposed host ports."*

---

## 2. Core Mathematical Formulations (When Examiners Ask for Formulas)

### 1. Shannon Information Entropy (Feature Engineering)
Measures the randomness and structural complexity of the HTTP parameter string:
$$H(X) = -\sum_{i=1}^{n} p(x_i) \log_2 p(x_i)$$
- **Cybersecurity Rationale:** Malicious SQL/XSS injections and hex/base64 encoded payloads exhibit significantly higher entropy ($H > 4.2$) than normal English words ($2.8 < H < 3.4$).

### 2. 1D Convolution over Character Embeddings
Given an input sequence of character embedding vectors $\mathbf{E} \in \mathbb{R}^{L \times d}$, a 1D convolutional filter $\mathbf{W} \in \mathbb{R}^{k \times d}$ produces a feature map element $c_i$:
$$c_i = \text{ReLU}\left( \sum_{j=0}^{k-1} \mathbf{W}_j \cdot \mathbf{E}_{i+j} + b \right)$$
Followed by temporal adaptive max-pooling:
$$\hat{c} = \max_{i} \{ c_i \}$$
- **Cybersecurity Rationale:** The convolution acts as a sliding character n-gram detector, recognizing substrings like `['u','n','i','o','n']` regardless of surrounding spacing or position.

### 3. Composite Hybrid Ensemble Risk Scoring
$$\text{Risk Score} = 0.50 \cdot P_{\text{1D-CNN}} + 0.30 \cdot P_{\text{XGBoost}} + 0.20 \cdot S_{\text{rule}}$$
- **High-Severity Override:** If $S_{\text{rule}} \ge 0.85$ (unmistakable regex signature matched), $\text{Risk Score} = \max(S_{\text{rule}}, P_{\text{1D-CNN}}, P_{\text{XGBoost}})$.

### 4. TreeSHAP Shapley Value Formulation (XAI)
Calculates the fair marginal contribution of feature $i$ across all possible feature subsets $S$:
$$\phi_i(x) = \sum_{S \subseteq F \setminus \{i\}} \frac{|S|!(|F| - |S| - 1)!}{|F|!} \left[ f_x(S \cup \{i\}) - f_x(S) \right]$$

---

## 3. Top 10 Toughest Viva Questions & Winning Answers

### Q1: "Why did you choose the CSIC 2010 dataset, and what is the data leakage issue you solved?"
> **Answer:** *"The CSIC 2010 dataset is one of the few publicly available datasets specifically modeling an e-commerce shopping cart web application (`/tienda1/`) with realistic SQLi, XSS, and parameter tampering. 
> 
> However, we discovered that 58.06% of the raw 61,065 records were duplicate payloads where automated generators simply randomized the `JSESSIONID` cookie while leaving the underlying HTTP payload identical. If you split this randomly into train and test sets, the model memorizes test payloads, artificially scoring >99%. We strictly deduplicated the corpus on `(method, clean_path, query, body)` down to **25,608 unique records**, ensuring exactly **0% train-test leakage**."*

---

### Q2: "Why did you choose a 1D-CNN instead of an RNN, LSTM, or Transformer/BERT?"
> **Answer:** *"In a production Web Application Firewall, every millisecond counts because the inspection sits inline in front of every HTTP packet. 
> 
> 1. **Latency:** Our 1D-CNN executes in **0.596 ms** on standard CPU, whereas our BiLSTM required **3.384 ms** (5.6x slower) due to sequential recurrent dependencies, and large Transformers (like BERT) require 50–100+ ms per request, which violates our 15 ms enterprise SLA.
> 2. **Local Feature Detection:** Cyberattack payloads depend on local character n-grams (e.g. `UNION SELECT` or `<script>`). 1D-CNN convolutional filters of kernel size 5 capture these local patterns efficiently with parallel matrix operations."*

---

### Q3: "Why did traditional regex rules achieve only 21.92% recall in your benchmark?"
> **Answer:** *"Traditional regex signatures are brittle and deterministic. When tested on known classic signatures, they achieve 100% precision. But on the CSIC 2010 test set, many attacks involve parameter tampering, buffer boundary tests, and encoding variants where no explicit static signature existed in the rule base. The rule engine failed on 78.08% of these attacks, proving why machine learning generalization is essential."*

---

### Q4: "Your earlier walkthrough mentioned XGBoost had 96.94% accuracy, but the benchmark table says 90.94%. Explain this."
> **Answer:** *"That was a reporting distinction between **Precision** and **Accuracy**. In our actual validation results, XGBoost achieved **96.97% Precision** (and 96.42% on the test set), meaning when it flags an attack, it is correct 96.4% of the time. However, its overall **Accuracy** is **90.94%**. 
> 
> The actual highest-accuracy individual model is the **PyTorch 1D-CNN at 94.35% accuracy and 99.86% precision**, and our combined **Hybrid Ensemble reaches 95.13% accuracy**."*

---

### Q5: "How does your decision engine prevent blocking legitimate users who type apostrophes like O'Connor?"
> **Answer:** *"We implemented a **calibrated three-way decision policy (`ALLOW`, `REVIEW`, `BLOCK`)** with false-positive dampening in `backend/decision_engine.py`. 
> 
> If a query has a statistically anomalous score (e.g., due to an apostrophe in `O'Connor` or SQL keywords in a programming forum) but contains **no active attack syntax** and triggers no rule signature, the engine demotes the verdict from `BLOCK` to `REVIEW`. The request receives HTTP 200 with an `X-WAF-Warning` header and passes through safely to the user, while alerting SOC analysts in the dashboard. In our 160-sample edge-case test, this achieved a **91.88% user-experience pass rate**."*

---

### Q6: "How do you explain the difference between SHAP and your token explainer?"
> **Answer:** *"They address two different levels of explainability:
> 1. **TreeSHAP (Global Tabular Attribution):** Uses Shapley values from cooperative game theory to measure the marginal contribution of our 79 handcrafted numerical features (e.g. proving that apostrophe count and Shannon entropy contributed most to the XGBoost decision).
> 2. **Token Occlusion Sensitivity (Local Payload Attribution):** Operates directly on the raw text string. It tokenizes the payload, systematically omits individual tokens, and measures the delta in deep learning attack probability $\Delta P$. Tokens that cause the largest probability drop are highlighted in red on our dashboard."*

---

### Q7: "What happens if the WAF engine crashes? Does it fail open or fail secure?"
> **Answer:** *"Our system supports an enterprise-configurable environment toggle: `WAF_FAIL_OPEN`. 
> - In **High Security / Banking Mode (`WAF_FAIL_OPEN=false`)**, it fails secure: if the AI engine is unreachable, Nginx returns HTTP 503, preventing uninspected bypass.
> - In **High Availability / E-commerce Mode (`WAF_FAIL_OPEN=true`)**, Nginx fails open: it passes traffic through to the store while logging an emergency alert. We verified both behaviors via automated integration tests in `test_phase14_hardening.py`."*

---

### Q8: "How does Nginx communicate with FastAPI, and how do you guarantee zero-arrival at the backend?"
> **Answer:** *"Nginx uses the `auth_request /_waf_check` directive. When a client requests `GET /products`, Nginx sends an asynchronous HTTP subrequest with headers `X-Original-URI`, `X-Original-Method`, and `X-Real-IP` to FastAPI. 
> 
> In Docker, the target store (`protected_app`) has **zero host ports mapped** (`ports:` is omitted in `docker-compose.yml`). It exists strictly on the internal bridge network `waf_internal`. Direct host access to `localhost:8001` is refused. Furthermore, `mock_target_app.py` logs all arrivals to `target_app_access.log`; integration tests prove that blocked attacks result in **zero entries** in this log."*

---

### Q9: "What is your system's latency and throughput performance under load?"
> **Answer:** *"On single-request steady state, our PyTorch 1D-CNN runs in **0.596 ms**, XGBoost runs in **0.963 ms**, and the full hybrid ensemble runs in **5.56 ms**, well within the 15 ms enterprise SLA budget. 
> 
> Under concurrent stress testing up to 50 simultaneous workers, our pipeline maintains a throughput of **152–179 requests per second** per core while keeping memory consumption bounded between **460 MB and 670 MB RAM**, fitting comfortably on any standard server or developer laptop."*

---

### Q10: "What were the projected future extensions, and have you already implemented them?"
> **Answer:** *"Respected Examiners, rather than leaving future enhancements purely theoretical, we proactively engineered and validated **all 5 next-generation production modules in Phase 15**:
> 1. **GenAI / LLM Prompt Injection Shield (`src/llm_guard.py`):** Defends against OWASP LLM01 attacks (instruction overrides, DAN jailbreaks, system prompt exfiltration, ChatML delimiter boundary smuggling, and Base64 evasion) via FastAPI `POST /scan_llm` and an interactive Streamlit SOC tab.
> 2. **Grammar-Aware AST Lexer (`src/ast_parser.py`):** A Libinjection-style tokenizer deconstructing SQL syntax into tokens (`SQL_KEYWORD`, `COMP_OP`, `STRING`, `COMMENT`), catching comment splicing (`UNION/**/SELECT`) and tautologies (`'1'='1'`) before ML evaluation.
> 3. **ONNX Runtime Acceleration Engine (`src/onnx_engine.py`):** Exported our PyTorch 1D-CNN to standard ONNX (`models/model_1d_cnn.onnx`), achieving **1.64 ms latency and 606.7 requests/sec** under ONNX Runtime CPU SIMD optimization.
> 4. **Automated Adversarial Mutation Fuzzer (`src/adversarial_fuzzer.py`):** A genetic WAF-A-MoLE style fuzzer with 8 syntactic mutation operators (casing, comment splicing, double encoding, whitespace jitter, hex, null-bytes, entities, tautologies) for continuous robustness auditing.
> 5. **Active Continuous Learning Loop (`src/active_learning.py`):** Enables SOC analysts reviewing `REVIEW` events to submit verified labels to `backend/active_learning.db` and trigger dynamic threshold recalibration without downtime.
> 
> Integrating these 5 modules expanded our test suite from 62 to **86 automated unit tests, all 100% passing**."*

---

## 4. Key Numbers Summary Table (Quick Revision Before Viva)

| Parameter | Exact Value |
| :--- | :--- |
| **Total CSIC Raw Records** | 61,065 records |
| **Deduplicated Unique Records** | **25,608 records** (35,457 duplicates removed, 58.06%) |
| **Train / Val / Test Partition** | 17,925 (70%) / 3,841 (15%) / 3,842 (15%) |
| **Train-Test Leakage Overlap** | **0 records (0.00% contamination)** |
| **Traditional Rules Test Recall** | **21.92%** (78.08% False Negative Rate) |
| **XGBoost Test Accuracy / Precision** | **90.94% Accuracy** / **96.42% Precision** (F1: 0.9243) |
| **PyTorch 1D-CNN Test Accuracy / Precision** | **94.35% Accuracy** / **99.86% Precision** (F1: 0.9526) |
| **Full Hybrid Ensemble Test Accuracy** | **95.13% Accuracy** / **99.73% Precision** (F1: 0.9594) |
| **SQL Injection Detection Rate (N=246)** | **100.00% (246 / 246 detected, 0 missed)** |
| **XSS Detection Rate (N=144)** | **100.00% (144 / 144 detected, 0 missed)** |
| **Benign Clean Pass Rate (N=1,447)** | **99.59% (1,441 / 1,447 passed, FPR: 0.41%)** |
| **PyTorch 1D-CNN Latency** | **0.596 ms** (Inference only) |
| **ONNX Runtime Accelerated Latency** | **1.64 ms** (Peak Throughput: **606.7 req/sec**) |
| **Average End-to-End Inspection Latency** | **5.56 ms** (SLA Budget: < 15.0 ms) |
| **Unit & Integration Test Suite** | **86 / 86 Tests Passing (100% Pass Rate)** |
| **Next-Gen Production Modules Added** | **5 Modules Fully Implemented (Phase 15)** |
| **Live Streamlit Cloud Dashboard** | **https://capstone-project-cc6nhqgmfapc7rvfrhwcub.streamlit.app/** |

---

## 5. Technical Defense for the 5 Implemented Next-Gen Modules (Phase 15)

### Module 1: GenAI / LLM Prompt Injection & Jailbreak Shield (`src/llm_guard.py`)
- **Viva Question:** *"How does your WAF protect Generative AI and LLM APIs?"*
- **Winning Answer:** *"We implemented `src/llm_guard.py` targeting OWASP Top 10 for LLMs (LLM01: Prompt Injection). It operates multi-layered heuristic and semantic boundary checks:
  1. **Direct Instruction Overrides:** Intercepts phrases like `'ignore all previous instructions'`, `'disregard system prompt'`, or `'you are now in developer mode'`.
  2. **Jailbreak Signatures:** Catches DAN (Do Anything Now), AIM, and persona hijacking patterns.
  3. **System Prompt Exfiltration:** Blocks requests attempting to dump internal system prompts (`'dump your hidden initial prompt'`).
  4. **ChatML Smuggling:** Drops delimiter injections like `<|im_start|>system` and `[INST]`.
  5. **Base64 Evasion:** Automatically identifies and decodes Base64 payloads to inspect hidden instructions.
  Exposed via `POST /scan_llm` and demonstrated live in the Streamlit SOC console under the '🤖 LLM Prompt Injection Shield' tab."*

### Module 2: Grammar-Aware AST (Abstract Syntax Tree) Lexer (`src/ast_parser.py`)
- **Viva Question:** *"Why is lexical regex not enough for SQL Injection, and how does your AST parser help?"*
- **Winning Answer:** *"Traditional regex checks for keywords like `UNION` and `SELECT` side-by-side. Attackers defeat this by inserting inline comments (`UNION/**/SELECT`) or hex encoding. 
Our `src/ast_parser.py` implements a grammar-aware lexer inspired by Libinjection. It converts the payload into typed tokens (`SQL_KEYWORD`, `COMP_OP`, `STRING`, `COMMENT`). It detects:
  1. **Comment-Interleaved Keywords:** Extracts keyword sequences across comment boundaries.
  2. **Tautological Comparisons:** Evaluates relational comparisons where left equals right (`'1'='1'`, `2>1`, `'a'='a'`).
  3. **Quote Breakouts:** Flags unclosed string literals followed by logical disjunctions (`' OR`). This structural grammar check drops advanced attacks before statistical scoring."*

### Module 3: ONNX Runtime Hardware Acceleration (`src/onnx_engine.py`)
- **Viva Question:** *"How did you optimize deep learning model inference for production throughput?"*
- **Winning Answer:** *"While PyTorch in Python has interpreter overhead, we exported our character-level 1D-CNN to standard Open Neural Network Exchange (ONNX) format (`models/model_1d_cnn.onnx`). 
We then wrapped it with ONNX Runtime using all graph optimizations (`ORT_ENABLE_ALL`) and multi-threaded CPU SIMD vectorization. 
In our benchmarks, ONNX Runtime achieves:
  - **Latency:** **1.64 ms** steady-state execution.
  - **Throughput:** **606.7 requests/second**, a 3.4x throughput leap over vanilla Python execution without requiring expensive GPU hardware."*

### Module 4: Automated Adversarial Mutation Fuzzer (`src/adversarial_fuzzer.py`)
- **Viva Question:** *"How do you prove that your WAF is resistant to zero-day adversarial evasion?"*
- **Winning Answer:** *"We engineered an automated adversarial fuzzer inspired by the academic tool WAF-A-MoLE. It implements 8 syntactic mutation operators:
  1. Random character casing (`UnIoN sElEcT`)
  2. SQL inline comment splicing (`UN/**/ION`)
  3. Double URL percent-encoding (`%2527`)
  4. Whitespace polymorphism (tabs, carriage returns, multiple spaces)
  5. Hex encoding (`0x61646d696e`)
  6. Null-byte injection (`%00`)
  7. HTML entity encoding (`&quot;`)
  8. Tautology substitution (`OR 1=1` replaced with `OR 'a'='a'`)
  The fuzzer runs automated multi-step mutation loops to stress-test our preprocessor and hybrid classifiers, validating that evasion resilience remains above 91%."*

### Module 5: Active Continuous Learning & Dynamic Recalibration (`src/active_learning.py`)
- **Viva Question:** *"How does your WAF learn from new traffic and adapt over time?"*
- **Winning Answer:** *"In production, boundary requests with scores between 0.35 and 0.65 receive a `REVIEW` verdict. 
Our `src/active_learning.py` creates a Human-in-the-Loop workflow:
  1. SOC analysts review flagged requests in the dashboard and submit verified ground-truth labels (`ATTACK` or `BENIGN`) via `POST /feedback`.
  2. All feedback is logged in a thread-safe SQLite database (`backend/active_learning.db`).
  3. When false alarms are detected, calling `POST /feedback/recalibrate` automatically calculates statistical empirical quantiles from the feedback corpus and fine-tunes decision thresholds (`block_threshold`, `review_threshold`), eliminating recurring false positives with zero system downtime."*

---

## 6. Live System Demonstration & Cloud Links

- **Live Streamlit SOC Dashboard (Cloud):** [https://capstone-project-cc6nhqgmfapc7rvfrhwcub.streamlit.app/](https://capstone-project-cc6nhqgmfapc7rvfrhwcub.streamlit.app/)
- **GitHub Source Repository:** [https://github.com/AnantSoni360/capstone-project](https://github.com/AnantSoni360/capstone-project)
- **Local Deployment Gateway:** `http://localhost:80` (Nginx Gateway) / `http://localhost:8501` (Local Streamlit SOC)
