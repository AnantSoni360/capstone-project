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

### Q10: "What are the limitations of your system, and what would you improve next?"
> **Answer:** *"Three practical limitations and extensions:
> 1. **Lexical vs Abstract Syntax Tree (AST):** While 1D-CNN captures character n-grams well, integrating an AST parser (like Libinjection) would completely eliminate false positives on technical programming discussions containing raw SQL keywords.
> 2. **Continual Active Learning:** Connecting the Streamlit dashboard so that when an analyst labels a `REVIEW` event, it automatically feeds back into a retraining queue.
> 3. **Hardware Acceleration:** Compiling PyTorch models via ONNX Runtime with TensorRT would scale throughput beyond 5,000 requests per second."*

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
| **Average Single Inspection Latency** | **5.56 ms** (SLA Budget: < 15.0 ms) |
| **Unit & Integration Test Suite** | **62 / 62 Tests Passing (100%)** |
