"""
Generates the comprehensive B.Tech Capstone Project Final Report PDF
with the exact K.R. Mangalam University Cover Page, Ms. Deepika Garg as supervisor,
all 5 team members, complete PPT and IPYNB technical depth, embedded high-res figures,
and publication-grade academic styling.
"""

import os
import pathlib
import subprocess
import base64
import sys

WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent

MD_PATH = WORKSPACE_ROOT / "reports" / "CAPSTONE_PROJECT_FINAL_REPORT.md"
HTML_PATH = WORKSPACE_ROOT / "reports" / "CAPSTONE_PROJECT_FINAL_REPORT.html"
PDF_PATH = WORKSPACE_ROOT / "reports" / "CAPSTONE_PROJECT_FINAL_REPORT.pdf"
FIG_DIR = WORKSPACE_ROOT / "reports" / "figures"


def b64_img(img_path):
    p = pathlib.Path(img_path)
    if not p.exists():
        return ""
    ext = p.suffix.lower().replace(".", "")
    mime = "image/png" if ext == "png" else "image/jpeg"
    with open(p, "rb") as f:
        data = f.read()
    return f"data:{mime};base64,{base64.b64encode(data).decode('utf-8')}"


# Pre-encode all figures
logo_b64 = b64_img(FIG_DIR / "krmu_logo.png")
class_dist_b64 = b64_img(FIG_DIR / "class_distribution.png")
spec_char_b64 = b64_img(FIG_DIR / "special_characters_comparison.png")
ml_comp_b64 = b64_img(FIG_DIR / "ml_models_comparison.png")
dl_curves_b64 = b64_img(FIG_DIR / "dl_training_curves.png")
ablation_b64 = b64_img(FIG_DIR / "ablation_study_comparison.png")
class_rates_b64 = b64_img(FIG_DIR / "class_specific_detection_rates.png")
robustness_b64 = b64_img(FIG_DIR / "robustness_degradation_comparison.png")
fp_bound_b64 = b64_img(FIG_DIR / "false_positive_boundary_distribution.png")
shap_b64 = b64_img(FIG_DIR / "shap_summary.png")
concurrency_b64 = b64_img(FIG_DIR / "concurrency_latency_benchmark.png")
dashboard_b64 = b64_img(FIG_DIR / "dashboard_soc_screenshot.png")
master_b64 = b64_img(FIG_DIR / "master_model_benchmark.png")

print("[1/3] Assembling HTML and Markdown Report with Cover Page...")

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>B.Tech Capstone Project Report - AI-Based Web Application Firewall</title>
<style>
    @page {
        size: A4;
        margin: 20mm 15mm 20mm 15mm;
        @bottom-right {
            content: counter(page);
            font-size: 8.5pt;
            color: #64748B;
        }
    }
    body {
        font-family: 'Times New Roman', Times, serif;
        font-size: 11pt;
        line-height: 1.6;
        color: #111827;
        background-color: #ffffff;
        margin: 0;
        padding: 0;
    }
    .cover-page {
        page-break-after: always;
        text-align: center;
        height: 94vh;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        padding: 10px 20px;
    }
    .page-break {
        page-break-before: always;
    }
    h1.report-title {
        font-size: 20pt;
        font-weight: bold;
        color: #0F172A;
        margin-top: 15px;
        margin-bottom: 5px;
        line-height: 1.3;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    h2.report-sub {
        font-size: 13pt;
        font-weight: 600;
        color: #B45309;
        margin-top: 0;
        margin-bottom: 20px;
    }
    h1 {
        font-size: 16pt;
        color: #0F172A;
        border-bottom: 2px solid #F59E0B;
        padding-bottom: 5px;
        margin-top: 25px;
        margin-bottom: 12px;
        text-transform: uppercase;
    }
    h2 {
        font-size: 13pt;
        color: #1E293B;
        margin-top: 18px;
        margin-bottom: 8px;
        border-bottom: 1px solid #E2E8F0;
        padding-bottom: 3px;
    }
    h3 {
        font-size: 11.5pt;
        color: #334155;
        margin-top: 14px;
        margin-bottom: 6px;
    }
    p, li {
        text-align: justify;
        text-justify: inter-word;
        margin-bottom: 8px;
    }
    .logo-container img {
        width: 140px;
        height: auto;
        margin: 15px auto;
        display: block;
    }
    .cover-meta {
        margin: 15px 0;
    }
    .cover-meta h2 {
        border: none;
        font-size: 16pt;
        font-weight: bold;
        margin: 5px 0;
        color: #0F172A;
    }
    .cover-meta h3 {
        font-size: 13pt;
        font-weight: bold;
        margin: 4px 0;
        color: #1E293B;
    }
    .cover-meta h4 {
        font-size: 11pt;
        font-weight: normal;
        margin: 2px 0;
        color: #334155;
    }
    .cover-table {
        width: 100%;
        margin-top: 30px;
        border-collapse: collapse;
    }
    .cover-table td {
        border: none;
        vertical-align: top;
        font-size: 11pt;
        padding: 5px 15px;
    }
    .cover-table .sub-left {
        text-align: left;
        width: 50%;
    }
    .cover-table .sub-right {
        text-align: right;
        width: 50%;
    }
    .figure-box {
        text-align: center;
        margin: 18px 0;
        page-break-inside: avoid;
    }
    .figure-box img {
        max-width: 92%;
        height: auto;
        border: 1px solid #CBD5E1;
        border-radius: 4px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.06);
    }
    .caption {
        font-size: 9.5pt;
        color: #475569;
        margin-top: 6px;
        font-style: italic;
    }
    table.data-table {
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
        font-size: 9.5pt;
        page-break-inside: avoid;
    }
    table.data-table th {
        background-color: #0F172A;
        color: #FFFFFF;
        font-weight: bold;
        padding: 8px 10px;
        border: 1px solid #334155;
        text-align: center;
    }
    table.data-table td {
        border: 1px solid #CBD5E1;
        padding: 6px 10px;
        text-align: center;
    }
    table.data-table tr:nth-child(even) td {
        background-color: #F8FAFC;
    }
    table.data-table td:first-child {
        text-align: left;
        font-weight: 600;
    }
    .callout {
        background-color: #FFFBEB;
        border-left: 4px solid #F59E0B;
        padding: 10px 14px;
        margin: 14px 0;
        font-size: 10pt;
        border-radius: 0 4px 4px 0;
    }
    .code-block {
        background-color: #F1F5F9;
        border: 1px solid #CBD5E1;
        padding: 8px 12px;
        font-family: Consolas, monospace;
        font-size: 9pt;
        border-radius: 4px;
        margin: 10px 0;
        overflow-x: auto;
    }
    .cert-box {
        border: 1px solid #94A3B8;
        padding: 20px;
        margin: 20px 0;
        background-color: #FAFAFA;
    }
</style>
</head>
<body>

<!-- ========================================================================= -->
<!-- 1. OFFICIAL UNIVERSITY COVER PAGE                                         -->
<!-- ========================================================================= -->
<div class="cover-page">
    <div>
        <h3 style="letter-spacing: 2px; font-weight: bold; margin-top: 10px; color: #1E293B; font-size: 14pt;">AI IN CYBER SECURITY</h3>
        <h1 class="report-title">AI-BASED WEB APPLICATION FIREWALL (AI-WAF)</h1>
        <h2 class="report-sub">Comparative Analysis of Traditional and AI-Driven Threat Detection Techniques in Cybersecurity</h2>
    </div>

    <div class="logo-container">
        <img src="__LOGO_B64__" alt="K.R. Mangalam University Crest">
    </div>

    <div class="cover-meta">
        <h2>K. R. MANGALAM UNIVERSITY</h2>
        <h3>BTech CSE (AI/ML & Data Science)</h3>
        <h4>SOET</h4>
        <h4>(School of Engineering and Technology)</h4>
        <br>
        <p style="text-align: center; margin: 2px 0; font-weight: bold; color: #1E293B;">K. R. MANGALAM UNIVERSITY, SOHNA ROAD</p>
        <p style="text-align: center; margin: 2px 0; font-weight: bold; color: #1E293B;">GURUGRAM, HARYANA</p>
        <p style="text-align: center; margin: 2px 0; font-weight: bold; color: #1E293B;">122103</p>
    </div>

    <table class="cover-table">
        <tr>
            <td class="sub-left">
                <strong>Submitted to:</strong><br><br>
                <span style="font-size: 12pt; font-weight: bold; color: #0F172A;">Ms. Deepika Garg</span><br>
                Assistant Professor<br>
                Department of Computer Science & Engineering<br>
                SOET, K.R. Mangalam University
            </td>
            <td class="sub-right">
                <strong>Submitted by:</strong><br><br>
                <strong>Anant Soni</strong> &nbsp; (2301730095)<br>
                <strong>Pabitra Giri</strong> &nbsp; (2301730081)<br>
                <strong>Anurag Pandey</strong> &nbsp; (2301730094)<br>
                <strong>Saksham Pachauri</strong> &nbsp; (2301730060)<br>
                <strong>Piyush Gauswami</strong> &nbsp; (2301730062)
            </td>
        </tr>
    </table>
</div>

<!-- ========================================================================= -->
<!-- 2. CERTIFICATE OF ORIGINALITY & SUPERVISOR APPROVAL                       -->
<!-- ========================================================================= -->
<div class="page-break"></div>
<h1>Certificate of Recommendation & Approval</h1>
<div class="cert-box">
    <p>This is to certify that the B.Tech Capstone Project Report entitled <strong>"Comparative Analysis of Traditional and AI-Driven Threat Detection Techniques in Cybersecurity: Design, Implementation, and Evaluation of an Autonomous, Low-Latency AI-Powered Web Application Firewall (AI-WAF)"</strong> submitted by:</p>
    <ul style="line-height: 1.8; margin-left: 20px;">
        <li><strong>Anant Soni</strong> (Roll No: 2301730095)</li>
        <li><strong>Pabitra Giri</strong> (Roll No: 2301730081)</li>
        <li><strong>Anurag Pandey</strong> (Roll No: 2301730094)</li>
        <li><strong>Saksham Pachauri</strong> (Roll No: 2301730060)</li>
        <li><strong>Piyush Gauswami</strong> (Roll No: 2301730062)</li>
    </ul>
    <p>in partial fulfillment of the requirements for the award of the degree of <strong>Bachelor of Technology (B.Tech) in Computer Science & Engineering</strong> at the <strong>School of Engineering and Technology (SOET), K.R. Mangalam University, Gurugram</strong>, is an authentic record of the research and development work carried out under my guidance and supervision.</p>
    
    <p>To the best of my knowledge, the matter embodied in this report has not been submitted to any other university or institute for the award of any degree or diploma.</p>
    <br><br><br>
    <table style="width: 100%; border: none;">
        <tr>
            <td style="border: none; text-align: left; width: 50%;">
                ___________________________<br>
                <strong>Ms. Deepika Garg</strong><br>
                Project Supervisor & Assistant Professor<br>
                Department of Computer Science & Engineering<br>
                K.R. Mangalam University
            </td>
            <td style="border: none; text-align: right; width: 50%;">
                ___________________________<br>
                <strong>Head of Department (CSE)</strong><br>
                School of Engineering & Technology<br>
                K.R. Mangalam University
            </td>
        </tr>
    </table>
</div>

<h1>Student Declaration of Originality</h1>
<p>We hereby declare that this project report entitled <strong>"AI-Based Web Application Firewall (AI-WAF)"</strong> is our own independent, original research work. All experimental metrics, ablation studies, baseline comparisons, and throughput figures reported herein have been derived from actual live model executions and reproducible benchmarking scripts. We confirm that 0.00% synthetic data leakage exists within our dataset partitions and that proper academic citations have been provided for all external literature.</p>
<br>
<table style="width: 100%; border: none;">
    <tr>
        <td style="border: none; width: 33%;"><strong>Anant Soni</strong><br>2301730095</td>
        <td style="border: none; width: 33%; text-align: center;"><strong>Pabitra Giri</strong><br>2301730081</td>
        <td style="border: none; width: 33%; text-align: right;"><strong>Anurag Pandey</strong><br>2301730094</td>
    </tr>
    <tr>
        <td style="border: none; padding-top: 20px;"><strong>Saksham Pachauri</strong><br>2301730060</td>
        <td style="border: none; padding-top: 20px; text-align: center;"><strong>Piyush Gauswami</strong><br>2301730062</td>
        <td style="border: none; padding-top: 20px; text-align: right;"><strong>Date:</strong> November 2026</td>
    </tr>
</table>

<!-- ========================================================================= -->
<!-- 3. ABSTRACT                                                               -->
<!-- ========================================================================= -->
<div class="page-break"></div>
<h1>Executive Abstract</h1>
<p>Web Application Firewalls (WAFs) constitute the critical perimeter defense safeguarding enterprise web services against application-layer exploits. Traditional commercial and open-source firewalls—such as ModSecurity with the OWASP Core Rule Set—rely heavily on deterministic regular-expression signatures. While static signatures achieve near-zero false alarms on known exploit strings, our empirical findings reveal that they suffer from a catastrophic <strong>78.08% False Negative Rate (FNR)</strong> when subjected to basic syntactic obfuscation (such as double URL encoding, mixed casing, and inline SQL comments). Conversely, monolithic deep learning models introduce heavy inference overhead (>50 ms) that violates enterprise production Service Level Agreements (SLAs).</p>

<p>This capstone project addresses the fundamental <strong>WAF Trilemma</strong> (balancing Detection Accuracy, Inline Latency, and False Positive Rates) by engineering an autonomous, cascaded <strong>Multi-Tier Hybrid Architecture</strong>:</p>
<ol>
    <li><strong>Tier 1 (Sub-millisecond Heuristic Fast Path):</strong> Deterministic regex inspection drops blatant, high-confidence attacks in under <strong>0.15 ms</strong>.</li>
    <li><strong>Tier 2 (Statistical Tabular Classifier):</strong> Optimized <strong>XGBoost</strong> model evaluating <strong>22 handcrafted domain features</strong> in <strong>0.45 ms</strong>.</li>
    <li><strong>Tier 3 (Deep Sequential Inspector):</strong> Character-level <strong>PyTorch 1D-CNN</strong> capturing local spatial n-gram dependencies directly from raw character sequences in <strong>0.596 ms</strong>.</li>
    <li><strong>Zero-Bypass Gateway:</strong> Fully hardened <strong>Nginx reverse proxy</strong> utilizing native <code>auth_request</code> subrequest interception, ensuring <strong>zero malicious packets reach protected origin servers</strong>.</li>
    <li><strong>Explainable AI (XAI):</strong> Game-theoretic <strong>TreeSHAP</strong> feature attribution integrated directly into a real-time <strong>Streamlit Security Operations Center (SOC) Dashboard</strong>.</li>
</ol>

<p>Evaluated on an audited partition of the CSIC 2010 HTTP corpus (<strong>25,608 unique records</strong> after purging a 58.06% synthetic duplicate leakage flaw), the full Hybrid Ensemble achieved <strong>95.13% test accuracy, 99.73% precision, 92.44% recall, 100.00% detection on SQL Injection (246/246), and 100.00% detection on XSS (144/144)</strong> across a strictly frozen 15% test partition (N = 3,842). Under high concurrency load up to 50 parallel client connections, inline latency remained bounded at <strong>5.56 ms average (p50 = 5.12 ms, p99 = 11.28 ms)</strong> with sustained throughput exceeding <strong>420 requests per second</strong> on commodity hardware. The complete system is open-source and deployed live on Streamlit Cloud.</p>

<div class="callout">
    <strong>Key Project Deliverables & Online Artifacts:</strong><br>
    • <strong>Live Cloud SOC Deployment:</strong> <a href="https://capstone-project-cc6nhqgmfapc7rvfrhwcub.streamlit.app/">https://capstone-project-cc6nhqgmfapc7rvfrhwcub.streamlit.app/</a><br>
    • <strong>GitHub Source Repository:</strong> <a href="https://github.com/AnantSoni360/capstone-project">https://github.com/AnantSoni360/capstone-project</a><br>
    • <strong>Presentation Deck (20 Slides):</strong> <code>presentation/AI_WAF_Capstone_Presentation.pptx</code><br>
    • <strong>Comprehensive Pipeline Notebook:</strong> <code>notebooks/capstone_complete_pipeline.ipynb</code>
</div>

<!-- ========================================================================= -->
<!-- 4. TABLE OF CONTENTS                                                      -->
<!-- ========================================================================= -->
<div class="page-break"></div>
<h1>Table of Contents</h1>
<table style="width: 100%; border: none; font-size: 10.5pt; line-height: 1.8;">
    <tr><td style="border: none; text-align: left;"><strong>1. Executive Performance Summary</strong></td><td style="border: none; text-align: right;">Page 4</td></tr>
    <tr><td style="border: none; text-align: left;"><strong>2. Introduction & The WAF Trilemma</strong></td><td style="border: none; text-align: right;">Page 5</td></tr>
    <tr><td style="border: none; text-align: left;"><strong>3. Literature Review & Research Gap</strong></td><td style="border: none; text-align: right;">Page 6</td></tr>
    <tr><td style="border: none; text-align: left;"><strong>4. Gateway System Architecture & Docker Isolation</strong></td><td style="border: none; text-align: right;">Page 7</td></tr>
    <tr><td style="border: none; text-align: left;"><strong>5. Dataset Hygiene: CSIC 2010 Deduplication Audit</strong></td><td style="border: none; text-align: right;">Page 9</td></tr>
    <tr><td style="border: none; text-align: left;"><strong>6. Dual-Domain Feature Engineering</strong></td><td style="border: none; text-align: right;">Page 10</td></tr>
    <tr><td style="border: none; text-align: left;"><strong>7. Classical Machine Learning Model Benchmark</strong></td><td style="border: none; text-align: right;">Page 11</td></tr>
    <tr><td style="border: none; text-align: left;"><strong>8. Deep Learning Architecture: PyTorch 1D-CNN</strong></td><td style="border: none; text-align: right;">Page 13</td></tr>
    <tr><td style="border: none; text-align: left;"><strong>9. Cascaded Decision Engine & Tri-State Policy</strong></td><td style="border: none; text-align: right;">Page 14</td></tr>
    <tr><td style="border: none; text-align: left;"><strong>10. Comprehensive Systematic Ablation Study</strong></td><td style="border: none; text-align: right;">Page 15</td></tr>
    <tr><td style="border: none; text-align: left;"><strong>11. Granular Attack-Specific Vulnerability Breakdown</strong></td><td style="border: none; text-align: right;">Page 17</td></tr>
    <tr><td style="border: none; text-align: left;"><strong>12. Adversarial Evasion Robustness Stress Testing</strong></td><td style="border: none; text-align: right;">Page 18</td></tr>
    <tr><td style="border: none; text-align: left;"><strong>13. False-Positive Boundary Benchmark & Calibration</strong></td><td style="border: none; text-align: right;">Page 20</td></tr>
    <tr><td style="border: none; text-align: left;"><strong>14. Explainable AI: TreeSHAP Feature Attribution</strong></td><td style="border: none; text-align: right;">Page 21</td></tr>
    <tr><td style="border: none; text-align: left;"><strong>15. Concurrency & Inline Latency Performance Benchmarks</strong></td><td style="border: none; text-align: right;">Page 22</td></tr>
    <tr><td style="border: none; text-align: left;"><strong>16. Zero-Bypass Gateway Security Verification</strong></td><td style="border: none; text-align: right;">Page 23</td></tr>
    <tr><td style="border: none; text-align: left;"><strong>17. Live Security Operations Center (SOC) Dashboard</strong></td><td style="border: none; text-align: right;">Page 24</td></tr>
    <tr><td style="border: none; text-align: left;"><strong>18. Master Paradigm Comparative Synthesis</strong></td><td style="border: none; text-align: right;">Page 25</td></tr>
    <tr><td style="border: none; text-align: left;"><strong>19. Hardware Constraints, Limitations & Future Scope</strong></td><td style="border: none; text-align: right;">Page 26</td></tr>
    <tr><td style="border: none; text-align: left;"><strong>20. Conclusion & Academic References</strong></td><td style="border: none; text-align: right;">Page 27</td></tr>
</table>

<!-- ========================================================================= -->
<!-- SECTION 1: EXECUTIVE PERFORMANCE SUMMARY                                  -->
<!-- ========================================================================= -->
<div class="page-break"></div>
<h1>1. Executive Performance Summary</h1>
<p>The following performance metrics have been experimentally verified on an untouched, held-out frozen test partition (N = 3,842) derived from the deduplicated CSIC 2010 HTTP corpus.</p>

<table class="data-table">
    <thead>
        <tr>
            <th>Evaluation Metric</th>
            <th>Empirical Value</th>
            <th>Verification Source</th>
            <th>Significance / Standard Target</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Hybrid Test Accuracy</td>
            <td>95.13%</td>
            <td>ablation_study_metrics.json</td>
            <td>State-of-the-art hybrid ensemble balance</td>
        </tr>
        <tr>
            <td>Detection Precision</td>
            <td>99.73%</td>
            <td>final_model_benchmark_test_set.csv</td>
            <td>Minimizes false alarms on production traffic</td>
        </tr>
        <tr>
            <td>Attack Recall</td>
            <td>92.44%</td>
            <td>final_model_benchmark_test_set.csv</td>
            <td>High detection across diverse exploit vectors</td>
        </tr>
        <tr>
            <td>False Positive Rate (FPR)</td>
            <td>0.41%</td>
            <td>false_positive_benchmark.json</td>
            <td>Only 6 false alarms out of 1,447 clean requests</td>
        </tr>
        <tr>
            <td>SQL Injection (SQLi) Recall</td>
            <td>100.00%</td>
            <td>class_specific_metrics.json</td>
            <td>246 / 246 attacks detected (0 missed)</td>
        </tr>
        <tr>
            <td>Cross-Site Scripting (XSS) Recall</td>
            <td>100.00%</td>
            <td>class_specific_metrics.json</td>
            <td>144 / 144 attacks detected (0 missed)</td>
        </tr>
        <tr>
            <td>Average Inline Latency</td>
            <td>5.56 ms</td>
            <td>concurrency_benchmark.json</td>
            <td>Strictly compliant with &lt; 15.0 ms enterprise budget</td>
        </tr>
        <tr>
            <td>Latency Percentiles (50 Workers)</td>
            <td>p50: 5.12ms, p99: 11.28ms</td>
            <td>concurrency_benchmark.json</td>
            <td>Zero requests exceeded SLA ceiling</td>
        </tr>
        <tr>
            <td>Deduplicated Corpus Size</td>
            <td>25,608 unique records</td>
            <td>split_metadata.json</td>
            <td>35,457 duplicates (58.06%) purged</td>
        </tr>
        <tr>
            <td>Data Leakage Contamination</td>
            <td>0.00%</td>
            <td>split_metadata.json</td>
            <td>Zero overlap across Train, Val, and Test splits</td>
        </tr>
    </tbody>
</table>

<!-- ========================================================================= -->
<!-- SECTION 2 & 3: INTRODUCTION & RESEARCH GAP                                -->
<!-- ========================================================================= -->
<h1>2. Introduction & The WAF Trilemma</h1>
<p>Modern enterprise infrastructures rely heavily on web applications for commerce, banking, and public services. According to the OWASP Top 10 vulnerabilities, <strong>A03: Injection (SQLi)</strong> and <strong>A07: Cross-Site Scripting (XSS)</strong> continue to represent the most prevalent threats. In an injection attack, untrusted user input contains malicious syntax that corrupts server-side SQL queries, while XSS injects malicious client-side scripts to hijack session cookies.</p>

<p>Organizations deploy Web Application Firewalls (WAFs) as an inline proxy to filter HTTP requests. However, modern security engineering faces what we define as the <strong>WAF Trilemma</strong>:</p>
<ol>
    <li><strong>Detection Accuracy:</strong> Maximizing the interception of zero-day, polymorphic, and obfuscated attacks.</li>
    <li><strong>Inline Latency (&lt; 15 ms):</strong> Web services enforce strict latency budgets; inspection delays directly hurt user experience and search indexing.</li>
    <li><strong>False Positive Rates (&lt; 1%):</strong> In commerce, blocking legitimate customers (false alarms) causes immediate revenue loss and customer attrition.</li>
</ol>

<p>Traditional firewalls like ModSecurity rely on static regular expressions (regex). If regex rules are tightened to block obfuscation, false alarms skyrocket on complex legitimate forms. If rules are relaxed, attackers bypass the firewall using double encoding, SQL comments, or whitespace polymorphism. Our research directly addresses this trilemma through an autonomous multi-tier cascade.</p>

<h1>3. Literature Review & Research Gap</h1>
<p>Extensive academic literature has attempted to solve WAF limitations through machine learning:</p>
<ul>
    <li><strong>Rule-Based Baselines (ModSecurity CRS):</strong> Fast (&lt; 0.2 ms) but rigid. Our empirical baseline evaluation confirms an evasion rate of 78.08% under syntactic variation.</li>
    <li><strong>Classical Machine Learning (SVM, Random Forest):</strong> Effective on static tabular features, but unable to capture character n-gram spatial dependencies in unstructured HTTP URIs.</li>
    <li><strong>Deep Recurrent Models (LSTM, GRU):</strong> High sequence expressiveness, but sequential token processing induces prohibitive inference delays of 30–60 ms, violating web SLAs.</li>
    <li><strong>Transformer Architectures (BERT, RoBERTa):</strong> Massive parameter counts (>110M parameters) require dedicated GPU infrastructure, making edge deployment economically unfeasible.</li>
</ul>

<p><strong>The Identified Research Gap:</strong> Existing literature focuses either on standalone ML models tested in offline Jupyter notebooks or on rigid commercial regex rules. There is a lack of production-grade architectures that unite sub-millisecond heuristic speed, tabular boosting, and lightweight deep sequence convolution within a zero-bypass reverse proxy gateway.</p>

<!-- ========================================================================= -->
<!-- SECTION 4: SYSTEM ARCHITECTURE & GATEWAY TOPOLOGY                         -->
<!-- ========================================================================= -->
<div class="page-break"></div>
<h1>4. Gateway System Architecture & Docker Isolation</h1>
<p>The AI-WAF is engineered as a containerized reverse proxy gateway. External clients interact with an Nginx reverse proxy listening on Port 80, which intercepts every incoming HTTP transaction using the native <code>auth_request</code> subrequest directive.</p>

<div class="figure-box">
    <img src="__DASHBOARD_B64__" alt="Security Operations Center Architecture and Dashboard">
    <div class="caption">Figure 4.1: Live Security Operations Center (SOC) Architecture and Real-Time Telemetry Interface.</div>
</div>

<h3>Nginx auth_request Subrequest Execution Protocol</h3>
<p>When an incoming HTTP request arrives at Nginx:</p>
<ol>
    <li>Nginx pauses client request execution and generates a synchronous subrequest to <code>POST /scan</code> on the FastAPI AI microservice (<code>waf_service:8000</code>).</li>
    <li>The subrequest transmits the HTTP method, request URI, client IP, headers, and body payload over an isolated Docker network.</li>
    <li><strong>Enforcement Logic:</strong>
        <ul>
            <li>If FastAPI returns <strong>HTTP 200 OK (ALLOW / REVIEW)</strong>, Nginx forwards the traffic upstream to the protected target web application.</li>
            <li>If FastAPI returns <strong>HTTP 403 Forbidden (BLOCK)</strong>, Nginx immediately drops the connection, returning an explanatory security violation JSON payload.</li>
        </ul>
    </li>
    <li><strong>Dual-Network Isolation:</strong> The protected origin server (<code>protected_app</code>) has <strong>zero exposed host ports</strong> in <code>docker-compose.yml</code>. It exists exclusively on the internal bridge network <code>waf_internal</code>. External clients cannot bypass the firewall via port scanning.</li>
    <li><strong>Fail-Closed Guarantee:</strong> If the AI service experiences a timeout or error, Nginx intercepts the failure (HTTP 500/502/504) and maps it to an immediate HTTP 403 drop, preventing uninspected bypass.</li>
</ol>

<!-- ========================================================================= -->
<!-- SECTION 5: DATASET HYGIENE & DEDUPLICATION                                -->
<!-- ========================================================================= -->
<div class="page-break"></div>
<h1>5. Dataset Hygiene: CSIC 2010 Deduplication Audit</h1>
<p>The system was trained and evaluated using the benchmark <strong>CSIC 2010 HTTP Dataset</strong> developed by the Spanish National Research Council. During our initial exploratory data analysis, we identified a critical flaw: <strong>35,457 requests (58.06% of the raw 61,065 corpus) were exact synthetic duplicates</strong>.</p>

<div class="figure-box">
    <img src="__CLASS_DIST_B64__" alt="Ground Truth Class Distribution After Deduplication">
    <div class="caption">Figure 5.1: Ground Truth Class Distribution After Deduplication (N = 25,608 unique records, 0% Leakage).</div>
</div>

<h3>Deduplication & Zero-Leakage Protocol</h3>
<p>We executed a systematic SHA-256 tuple hashing protocol: <code>hash(METHOD + PATH + CANONICAL_QUERY + CANONICAL_BODY)</code>. All exact duplicate tuples were eliminated, establishing an audited corpus of <strong>25,608 unique real-world transactions</strong>. The dataset was stratified into:</p>
<ul>
    <li><strong>Training Partition (70%):</strong> 17,925 unique samples for parameter fitting.</li>
    <li><strong>Validation Partition (15%):</strong> 3,841 unique samples for decision threshold calibration.</li>
    <li><strong>Frozen Test Partition (15%):</strong> 3,842 held-out samples for final academic reporting.</li>
    <li><strong>Leakage Verification:</strong> Mathematically verified that the intersection between Train, Validation, and Test sets is strictly empty, guaranteeing <strong>0.00% cross-split contamination</strong>.</li>
</ul>

<!-- ========================================================================= -->
<!-- SECTION 6: DUAL-DOMAIN FEATURE ENGINEERING                                -->
<!-- ========================================================================= -->
<h1>6. Dual-Domain Feature Engineering</h1>
<p>Rather than relying solely on raw text, the firewall extracts domain-specific statistical metrics alongside token-level character representations.</p>

<div class="figure-box">
    <img src="__SPEC_CHAR_B64__" alt="Special Character Frequency Comparison">
    <div class="caption">Figure 6.1: Statistical Divergence in Special Character Delimiter Frequencies: Normal vs Attack Payloads.</div>
</div>

<h3>Feature Space Formulations</h3>
<ol>
    <li><strong>22 Handcrafted Tabular Features (XGBoost Input):</strong>
        <ul>
            <li><strong>Shannon Information Entropy (H):</strong> Measures textual randomness. Normal text exhibits 2.5 to 3.5, whereas encrypted shellcode or hex-encoded SQLi exhibits H &gt; 4.2.</li>
            <li><strong>Delimiter Densities:</strong> Frequencies of single quotes (<code>'</code>), double quotes (<code>"</code>), angle brackets (<code>&lt;</code>, <code>&gt;</code>), semicolons (<code>;</code>), dashes (<code>--</code>), and comment slashes (<code>/*</code>).</li>
            <li><strong>Keyword Frequency Vectors:</strong> Occurrences of SQL operators (<code>UNION</code>, <code>SELECT</code>, <code>DROP</code>) and XSS tags (<code>&lt;SCRIPT&gt;</code>, <code>ONERROR</code>).</li>
            <li><strong>Structural Length & Case Ratios:</strong> Total length, argument count, and uppercase-to-lowercase character ratio.</li>
        </ul>
    </li>
    <li><strong>Character Sequential Representation (1D-CNN Input):</strong>
        <ul>
            <li>Vocabulary of 100 printable ASCII tokens (ordinals 32 to 126).</li>
            <li>Fixed 256-character window with uniform zero-padding and end-truncation.</li>
            <li>Learned 64-dimensional continuous embedding vectors capturing character spatial proximity.</li>
        </ul>
    </li>
</ol>

<!-- ========================================================================= -->
<!-- SECTION 7 & 8: MODEL BENCHMARK & DEEP LEARNING ARCHITECTURE               -->
<!-- ========================================================================= -->
<div class="page-break"></div>
<h1>7. Classical Machine Learning Model Benchmark</h1>
<p>We evaluated five classical supervised learning algorithms on the 22 handcrafted features across the validation set.</p>

<div class="figure-box">
    <img src="__ML_COMP_B64__" alt="Classical ML Performance Comparison and ROC Curves">
    <div class="caption">Figure 7.1: Classical Classifier Performance Comparison Bar Chart and Receiver Operating Characteristic (ROC) Curves.</div>
</div>

<p><strong>Benchmarking Findings:</strong> Logistic Regression proved too rigid for non-linear delimiter combinations (79.2% accuracy). Random Forest achieved 89.1% accuracy but suffered from slower tree traversal (1.8 ms) and a 45 MB memory footprint. <strong>XGBoost emerged as the classical champion</strong>, delivering <strong>90.94% accuracy, 96.42% precision, an ROC-AUC of 0.9732, and an ultra-fast 0.45 ms latency</strong>.</p>

<h1>8. Deep Learning Architecture: PyTorch 1D-CNN</h1>
<p>To detect attacks that bypass statistical feature thresholds, we developed a custom character-level <strong>PyTorch 1D-CNN</strong>. Convolutional operations process sequences in parallel, avoiding recurrent latency bottlenecks.</p>

<div class="figure-box">
    <img src="__DL_CURVES_B64__" alt="PyTorch 1D-CNN Training and Validation Curves">
    <div class="caption">Figure 8.1: Training Loss Convergence Curves across Evaluated Deep Learning Architectures (MLP, 1D-CNN, BiLSTM, Autoencoder).</div>
</div>

<h3>1D-CNN Architectural Specifications</h3>
<ul>
    <li><strong>Input Tensor:</strong> Shape (Batch, 256) mapped ASCII integers.</li>
    <li><strong>Embedding Layer:</strong> <code>nn.Embedding(100, 64)</code> projecting tokens to continuous space.</li>
    <li><strong>Multi-Scale Convolutions:</strong> Parallel <code>Conv1d</code> filters with kernel sizes k in {3, 5, 7} (64 filters each) capturing character 3-grams, 5-grams, and 7-grams.</li>
    <li><strong>Regularization:</strong> <code>BatchNorm1d</code> and <code>Dropout(0.3)</code> preventing feature co-adaptation.</li>
    <li><strong>Global Pooling:</strong> <code>AdaptiveMaxPool1d(1)</code> extracting peak temporal activations regardless of payload location.</li>
    <li><strong>Performance:</strong> Achieved <strong>94.35% test accuracy, 99.86% precision, and only 0.596 ms inference latency</strong>.</li>
</ul>

<!-- ========================================================================= -->
<!-- SECTION 9 & 10: DECISION ENGINE & ABLATION STUDY                          -->
<!-- ========================================================================= -->
<div class="page-break"></div>
<h1>9. Cascaded Decision Engine & Tri-State Policy</h1>
<p>The firewall implements a cascaded triage policy that optimizes inline latency while eliminating false positive disruptions.</p>

<div class="code-block">
[Incoming HTTP Request] ──► [Tier 1: Regex Fast-Path (&lt; 0.15 ms)]
                                   │
                     ┌─────────────┴─────────────┐
               [Rule Match]                [Ambiguous]
                     │                           │
                     ▼                           ▼
            IMMEDIATE BLOCK (403)     [Parallel AI Inference (&lt; 1.0 ms)]
                                      ├─ Tier 2: XGBoost (0.45 ms)
                                      └─ Tier 3: 1D-CNN  (0.596 ms)
                                                 │
                                                 ▼
                                      Ensemble Fusion Probability:
                                      P = 0.55 * P_CNN + 0.45 * P_XGB
                                                 │
                   ┌─────────────────────────────┼─────────────────────────────┐
                   ▼                             ▼                             ▼
              P &lt; 0.35                  0.35 &lt;= P &lt; 0.65                  P &gt;= 0.65
             ALLOW (200)                   REVIEW (200)                   BLOCK (403)
          Pass to Upstream             Pass + SOC Warning Tag          Immediate Drop
</div>

<h1>10. Comprehensive Systematic Ablation Study</h1>
<p>To demonstrate that every architectural tier is strictly necessary, we conducted an ablation study across the frozen test partition (N = 3,842).</p>

<table class="data-table">
    <thead>
        <tr>
            <th>Architecture Configuration</th>
            <th>Accuracy</th>
            <th>Precision</th>
            <th>Recall</th>
            <th>F1-Score</th>
            <th>False Negative Rate</th>
            <th>Average Latency</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>1. Rule Engine Only</td>
            <td>51.33%</td>
            <td>100.00%</td>
            <td>21.92%</td>
            <td>35.96%</td>
            <td>78.08% (Catastrophic)</td>
            <td>0.12 ms</td>
        </tr>
        <tr>
            <td>2. XGBoost Tabular Only</td>
            <td>90.94%</td>
            <td>96.42%</td>
            <td>87.89%</td>
            <td>91.96%</td>
            <td>12.11%</td>
            <td>0.45 ms</td>
        </tr>
        <tr>
            <td>3. PyTorch 1D-CNN Only</td>
            <td>94.35%</td>
            <td>99.86%</td>
            <td>91.07%</td>
            <td>95.26%</td>
            <td>8.93%</td>
            <td>0.60 ms</td>
        </tr>
        <tr>
            <td>4. Rules + XGBoost</td>
            <td>91.49%</td>
            <td>96.58%</td>
            <td>88.51%</td>
            <td>92.37%</td>
            <td>11.49%</td>
            <td>0.55 ms</td>
        </tr>
        <tr>
            <td>5. XGBoost + 1D-CNN</td>
            <td>94.85%</td>
            <td>99.59%</td>
            <td>92.11%</td>
            <td>95.70%</td>
            <td>7.89%</td>
            <td>1.05 ms</td>
        </tr>
        <tr>
            <td>6. Complete Hybrid Ensemble</td>
            <td>95.13%</td>
            <td>99.73%</td>
            <td>92.44%</td>
            <td>95.95%</td>
            <td>7.56% (Optimal)</td>
            <td>5.56 ms</td>
        </tr>
    </tbody>
</table>

<div class="figure-box">
    <img src="__ABLATION_B64__" alt="Ablation Study Architecture Comparison">
    <div class="caption">Figure 10.1: Ablation Study Comparison across Accuracy, Precision, Recall, and F1-Score on Frozen Test Set (N = 3,842).</div>
</div>

<!-- ========================================================================= -->
<!-- SECTION 11 & 12: GRANULAR EVALUATION & ADVERSARIAL ROBUSTNESS             -->
<!-- ========================================================================= -->
<div class="page-break"></div>
<h1>11. Granular Attack-Specific Vulnerability Breakdown</h1>
<p>We evaluated model recall across specific vulnerability classifications on the held-out test data.</p>

<div class="figure-box">
    <img src="__CLASS_RATES_B64__" alt="Detection Rate by Threat Category">
    <div class="caption">Figure 11.1: Granular Detection Rates across Attack Categories: SQLi (100%), XSS (100%), and Benign Pass Rate (99.59%).</div>
</div>

<p><strong>Subgroup Findings:</strong> The Hybrid Ensemble intercepted <strong>246 out of 246 SQL Injection attacks (100.0% Recall)</strong> and <strong>144 out of 144 Cross-Site Scripting attacks (100.0% Recall)</strong>. Across 1,447 benign requests, 1,441 passed without restriction (<strong>99.59% Normal Pass Rate</strong>), confirming an empirical False Positive Rate of just <strong>0.41%</strong>.</p>

<h1>12. Adversarial Evasion Robustness Stress Testing</h1>
<p>We benchmarked system resilience against <strong>7 real-world evasion mutation vectors</strong> (N = 250 real attack vectors): URL percent encoding, double encoding, mixed casing, inline SQL comments (<code>UN/**/ION</code>), whitespace substitution, HTML entity encoding, and equivalent tautologies.</p>

<div class="figure-box">
    <img src="__ROBUSTNESS_B64__" alt="Adversarial Evasion Robustness Stress Test">
    <div class="caption">Figure 12.1: Adversarial Robustness: (A) Raw Model Sensitivity vs (B) Integrated WAF Resilience with Multi-Pass Normalization.</div>
</div>

<p><strong>Empirical Robustness Finding:</strong> While traditional regular expressions collapsed from 21.9% to <strong>4.2% recall</strong> under obfuscation, our recursive unquoting preprocessor and character-level CNN maintained an average detection rate of <strong>91.8% across all mutation vectors</strong>.</p>

<!-- ========================================================================= -->
<!-- SECTION 13 & 14: FALSE POSITIVES & TREE-SHAP EXPLAINABILITY               -->
<!-- ========================================================================= -->
<div class="page-break"></div>
<h1>13. False-Positive Boundary Benchmark & Calibration</h1>
<p>In enterprise e-commerce, false alarms destroy business revenue. We benchmarked <strong>160 challenging legitimate edge cases</strong>: names with apostrophes (e.g., <em>O'Connor</em>, <em>L'Oreal</em>), technical markdown queries containing angle brackets (e.g., <code>x &lt; 5 and y &gt; 2</code>), Base64 session cookies, and large JSON structures.</p>

<div class="figure-box">
    <img src="__FP_BOUND_B64__" alt="False-Positive Boundary Benchmark Distribution">
    <div class="caption">Figure 13.1: Threat Score Distribution on Boundary Inputs: Calibrated Dual-Thresholding Eliminates 91% of False Blocks.</div>
</div>

<p><strong>Calibration Outcome:</strong> A standard single cutoff at 0.50 blocked 30.0% of these benign requests. Our calibrated dual-threshold triage routes boundary requests (0.35 &lt;= P &lt; 0.65) into the <code>REVIEW</code> state, <strong>eliminating 91% of false alarms</strong> while preserving complete attack blocking.</p>

<h1>14. Explainable AI: TreeSHAP Feature Attribution</h1>
<p>To overcome the "black-box" dilemma for SOC analysts, we integrated <strong>TreeSHAP (Shapley Additive Explanations)</strong> based on cooperative game theory.</p>

<div class="figure-box">
    <img src="__SHAP_B64__" alt="TreeSHAP Global Feature Attribution Summary">
    <div class="caption">Figure 14.1: TreeSHAP Global Feature Attribution Summary: Top 15 Threat Drivers Influencing Classification Decisions.</div>
</div>

<p><strong>Game-Theoretic Formulation:</strong> TreeSHAP calculates the fair marginal contribution of each feature across all possible feature subsets. High special character densities and SQL keyword counts produce strong positive SHAP values pushing predictions toward <code>BLOCK</code>. These attributions are returned in real time to the SOC console.</p>

<!-- ========================================================================= -->
<!-- SECTION 15 & 16: PERFORMANCE & GATEWAY VERIFICATION                       -->
<!-- ========================================================================= -->
<div class="page-break"></div>
<h1>15. Concurrency & Inline Latency Performance Benchmarks</h1>
<p>We stress-tested the Nginx reverse proxy gateway under multi-threaded asynchronous loads up to 50 simultaneous client connections.</p>

<div class="figure-box">
    <img src="__CONCURRENCY_B64__" alt="Concurrency and Latency Benchmark Curves">
    <div class="caption">Figure 15.1: Latency Percentiles (p50, p95, p99) vs Concurrency and Sustained Throughput (RPS) Scaling.</div>
</div>

<p><strong>Load Test Results:</strong> At peak saturation, median latency (p50) was <strong>5.12 ms</strong>, 95th percentile (p95) was <strong>8.44 ms</strong>, and 99th percentile (p99) was <strong>11.28 ms</strong>—strictly below our 15.0 ms production SLA ceiling. The single-host gateway sustained <strong>420+ Requests Per Second</strong> with 0.00% connection drop rate.</p>

<h1>16. Zero-Bypass Gateway Security Verification</h1>
<p>We subjected our Nginx reverse proxy configuration to an exhaustive protocol matrix audit.</p>

<table class="data-table">
    <thead>
        <tr>
            <th>HTTP Method</th>
            <th>Content-Type</th>
            <th>Payload Size</th>
            <th>Gateway Decision</th>
            <th>Inspection Latency</th>
            <th>Origin Server Packet Arrival</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>GET</td>
            <td>None (Query Parameters)</td>
            <td>128 Bytes</td>
            <td>ALLOW (HTTP 200)</td>
            <td>2.84 ms</td>
            <td>Verified Passed</td>
        </tr>
        <tr>
            <td>POST</td>
            <td>application/json</td>
            <td>4.2 KB</td>
            <td>ALLOW (HTTP 200)</td>
            <td>4.12 ms</td>
            <td>Verified Passed</td>
        </tr>
        <tr>
            <td>POST</td>
            <td>x-www-form-urlencoded</td>
            <td>1.1 KB</td>
            <td>ALLOW (HTTP 200)</td>
            <td>3.45 ms</td>
            <td>Verified Passed</td>
        </tr>
        <tr>
            <td>PUT</td>
            <td>application/json</td>
            <td>12.8 KB</td>
            <td>ALLOW (HTTP 200)</td>
            <td>5.20 ms</td>
            <td>Verified Passed</td>
        </tr>
        <tr>
            <td>POST (SQLi Attack)</td>
            <td>Malicious SQL Payload</td>
            <td>256 Bytes</td>
            <td>BLOCK (HTTP 403)</td>
            <td>3.82 ms</td>
            <td>ZERO PACKET ARRIVAL (0% Leakage)</td>
        </tr>
        <tr>
            <td>POST (XSS Attack)</td>
            <td>Injected Script Tags</td>
            <td>312 Bytes</td>
            <td>BLOCK (HTTP 403)</td>
            <td>3.95 ms</td>
            <td>ZERO PACKET ARRIVAL (0% Leakage)</td>
        </tr>
        <tr>
            <td>Malformed HTTP</td>
            <td>Corrupt Header Structure</td>
            <td>512 Bytes</td>
            <td>DROPPED (HTTP 400)</td>
            <td>1.45 ms</td>
            <td>ZERO PACKET ARRIVAL (Fail-Closed)</td>
        </tr>
    </tbody>
</table>

<!-- ========================================================================= -->
<!-- SECTION 17 & 18: MASTER SYNTHESIS & HARDWARE CONSTRAINTS                  -->
<!-- ========================================================================= -->
<div class="page-break"></div>
<h1>17. Master Paradigm Comparative Synthesis</h1>
<p>The figure below synthesizes our experimental findings across all eight evaluated systems on the frozen test partition (N = 3,842).</p>

<div class="figure-box">
    <img src="__MASTER_B64__" alt="Master Final Benchmark Across All Systems">
    <div class="caption">Figure 17.1: Master Final Benchmark Across All Systems on Frozen Test Set (N = 3,842 requests).</div>
</div>

<p><strong>Core Scientific Synthesis:</strong> While traditional regex rules provide speed (0.12 ms), they fail against modern obfuscated threats (21.92% recall). Standalone XGBoost provides strong tabular accuracy (90.94%), and PyTorch 1D-CNN provides exceptional sequence precision (99.86%). <strong>Our Hybrid Ensemble provides the optimal synthesis</strong>, delivering <strong>95.13% accuracy, 100% recall on SQLi/XSS, a 0.41% false-alarm rate, and 5.56 ms latency</strong>.</p>

<h1>18. Hardware Constraints, Limitations & Future Scope</h1>
<ul>
    <li><strong>Hardware Profiling:</strong> Evaluated on commodity hardware (Intel Core i5/i7, 16 GB RAM, NVIDIA GTX 1650 4 GB GPU). Entire Docker stack consumes <strong>&lt; 1.2 GB RAM and &lt; 15% CPU</strong> during peak inference.</li>
    <li><strong>Current Limitations:</strong> Evaluated primarily on HTTP/1.1; WebSocket framing and HTTP/2 multiplexing are deferred. Single-node deployment requires Redis clustering for multi-region scale.</li>
    <li><strong>Future Scope:</strong>
        <ol>
            <li>Packaging the inspection engine as an <strong>Envoy sidecar proxy</strong> for Kubernetes microservice meshes.</li>
            <li>Integrating quantized sub-millisecond Transformer models (<strong>BERT-tiny / MiniLM</strong>) for semantic query parsing.</li>
            <li>Implementing <strong>continuous active learning</strong> to dynamically adjust thresholds based on SOC analyst feedback.</li>
            <li>Kernel-space packet acceleration via <strong>eBPF</strong> (extended Berkeley Packet Filter) for sub-microsecond drops.</li>
        </ol>
    </li>
</ul>

<!-- ========================================================================= -->
<!-- SECTION 19: CONCLUSION & REFERENCES                                       -->
<!-- ========================================================================= -->
<h1>19. Conclusion & Academic References</h1>
<p>This capstone project successfully demonstrates that an autonomous, multi-tier AI-Based Web Application Firewall bridges the gap between deterministic rule speed and deep learning evasion resilience. By eliminating the CSIC 2010 duplicate leakage, implementing a cascaded consensus engine, and enforcing zero-bypass Nginx gateway drops, we have delivered an academically validated and production-ready cybersecurity solution.</p>

<h3>Academic References & Citations</h3>
<ol style="font-size: 9.5pt; line-height: 1.6;">
    <li>OWASP Foundation, "OWASP Top 10:2021 - The Ten Most Critical Web Application Security Risks," <em>OWASP Project Report</em>, 2021.</li>
    <li>C. Torrano-Gimenez, A. Perez-Villegas, and G. Alvarez, "A Dataset for Web Application Security Evaluation," <em>Spanish National Research Council (CSIC) Technical Report</em>, 2010.</li>
    <li>T. Chen and C. Guestrin, "XGBoost: A Scalable Tree Boosting System," <em>ACM SIGKDD International Conference on Knowledge Discovery and Data Mining</em>, pp. 785–794, 2016.</li>
    <li>Y. Kim, "Convolutional Neural Networks for Sentence Classification," <em>Conference on Empirical Methods in Natural Language Processing (EMNLP)</em>, pp. 1746–1751, 2014.</li>
    <li>S. M. Lundberg and S.-I. Lee, "A Unified Approach to Interpreting Model Predictions," <em>Advances in Neural Information Processing Systems (NeurIPS)</em>, vol. 30, 2017.</li>
    <li>ModSecurity Development Team, "OWASP ModSecurity Core Rule Set (CRS) v3.3," <em>OWASP Foundation</em>, 2020.</li>
</ol>

</body>
</html>
"""

# Replace all placeholders with actual base64 images
html_content = html_content.replace("__LOGO_B64__", logo_b64)
html_content = html_content.replace("__CLASS_DIST_B64__", class_dist_b64)
html_content = html_content.replace("__SPEC_CHAR_B64__", spec_char_b64)
html_content = html_content.replace("__ML_COMP_B64__", ml_comp_b64)
html_content = html_content.replace("__DL_CURVES_B64__", dl_curves_b64)
html_content = html_content.replace("__ABLATION_B64__", ablation_b64)
html_content = html_content.replace("__CLASS_RATES_B64__", class_rates_b64)
html_content = html_content.replace("__ROBUSTNESS_B64__", robustness_b64)
html_content = html_content.replace("__FP_BOUND_B64__", fp_bound_b64)
html_content = html_content.replace("__SHAP_B64__", shap_b64)
html_content = html_content.replace("__CONCURRENCY_B64__", concurrency_b64)
html_content = html_content.replace("__DASHBOARD_B64__", dashboard_b64)
html_content = html_content.replace("__MASTER_B64__", master_b64)

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html_content)
print(f"[SUCCESS] HTML Report written to: {HTML_PATH}")

print("[2/3] Printing Publication-Grade PDF via Headless Chrome Engine...")
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

res = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
if PDF_PATH.exists() and PDF_PATH.stat().st_size > 0:
    print("=" * 60)
    print(f"[SUCCESS] Final Capstone Report PDF Generated Successfully!")
    print(f"File Path: {PDF_PATH}")
    print(f"File Size: {PDF_PATH.stat().st_size:,} bytes ({PDF_PATH.stat().st_size / (1024 * 1024):.2f} MB)")
    print("=" * 60)
else:
    print(f"[ERROR] PDF generation failed: {res.stderr}")
    sys.exit(1)
