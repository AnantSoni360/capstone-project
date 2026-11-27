import os
import sys
import base64
import subprocess
from pathlib import Path
import fitz

def encode_image_base64(filepath):
    if not os.path.exists(filepath):
        return ""
    with open(filepath, "rb") as f:
        data = f.read()
    return f"data:image/png;base64,{base64.b64encode(data).decode('utf-8')}"

def build_front_matter_html():
    logo_b64 = encode_image_base64("reports/figures/krmu_logo.png")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Front Matter - AI-WAF Report</title>
<style>
    @page {{
        size: A4 portrait;
        margin: 18mm 16mm 18mm 16mm;
    }}
    
    * {{
        box-sizing: border-box;
    }}

    body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        font-size: 9.5pt;
        line-height: 1.45;
        color: #0f172a;
        margin: 0;
        padding: 0;
        background: #fff;
    }}

    .page {{
        width: 100%;
        min-height: 258mm;
        max-height: 260mm;
        position: relative;
        page-break-after: always;
        display: flex;
        flex-direction: column;
    }}

    .footer-bar {{
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        display: flex;
        justify-content: space-between;
        font-size: 8pt;
        color: #64748b;
        border-top: 1px solid #e2e8f0;
        padding-top: 4px;
    }}

    /* PAGE 1 STYLING */
    .inst-header {{
        text-align: center;
        margin-bottom: 8px;
    }}
    .inst-name {{
        font-size: 13pt;
        font-weight: 800;
        color: #0b3c5d;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin: 2px 0;
    }}
    .inst-dept {{
        font-size: 9pt;
        font-weight: 600;
        color: #475569;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }}
    .inst-soet {{
        font-size: 11pt;
        font-weight: 800;
        color: #0f172a;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }}

    .logo-container {{
        text-align: center;
        margin: 6px 0;
    }}
    .krmu-logo {{
        height: 65px;
        width: auto;
    }}

    .badge-capsule {{
        text-align: center;
        margin: 8px 0;
    }}
    .badge-pill {{
        display: inline-block;
        background: #eff6fb;
        border: 1px solid #cbd5e1;
        border-radius: 9999px;
        padding: 4px 18px;
        font-size: 8.5pt;
        font-weight: 700;
        color: #1e40af;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }}

    .title-section {{
        text-align: center;
        margin: 8px 0 10px 0;
    }}
    .main-title {{
        font-size: 18pt;
        font-weight: 900;
        color: #0f172a;
        line-height: 1.22;
        margin: 0 0 6px 0;
    }}
    .sub-title {{
        font-size: 10.5pt;
        font-weight: 600;
        color: #2563eb;
        line-height: 1.35;
        margin: 0;
    }}

    .divider-line {{
        height: 1px;
        background: #cbd5e1;
        margin: 8px 0;
    }}

    .info-card {{
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px 16px;
        margin-top: 6px;
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px 20px;
    }}

    .info-col-item {{
        margin-bottom: 6px;
    }}
    .info-lbl {{
        font-size: 7.5pt;
        font-weight: 800;
        color: #64748b;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 2px;
    }}
    .info-val {{
        font-size: 8.5pt;
        color: #0f172a;
        line-height: 1.35;
    }}
    .info-val-bold {{
        font-weight: 700;
        color: #0f172a;
    }}
    .student-entry {{
        font-size: 8.5pt;
        color: #0f172a;
        line-height: 1.3;
    }}

    .bottom-meta {{
        text-align: center;
        margin-top: 10px;
        font-size: 8.5pt;
        color: #334155;
    }}
    .bottom-meta .date-line {{
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 2px;
    }}
    .bottom-meta .sub-line {{
        font-size: 8pt;
        color: #64748b;
    }}

    /* PAGE 2 STYLING */
    .section-h1 {{
        font-size: 14pt;
        font-weight: 900;
        color: #0f172a;
        border-bottom: 2.5px solid #2563eb;
        padding-bottom: 3px;
        margin-top: 0;
        margin-bottom: 10px;
    }}

    .legal-p {{
        font-size: 9pt;
        line-height: 1.5;
        color: #1e293b;
        text-align: justify;
        margin-bottom: 8px;
    }}

    .sig-row {{
        display: flex;
        justify-content: space-between;
        margin-top: 18px;
        margin-bottom: 22px;
    }}
    .sig-col {{
        width: 48%;
    }}
    .sig-rule {{
        border-top: 1.2px solid #0f172a;
        margin-bottom: 4px;
        width: 85%;
    }}
    .sig-role {{
        font-size: 8.5pt;
        font-weight: 800;
        color: #0f172a;
    }}
    .sig-dept {{
        font-size: 8pt;
        color: #475569;
        line-height: 1.3;
    }}

    .students-sig-grid {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px 10px;
        margin-top: 12px;
    }}
    .student-sig-block {{
        border-top: 1px solid #94a3b8;
        padding-top: 3px;
    }}
    .student-sig-name {{
        font-size: 8.5pt;
        font-weight: 700;
        color: #0f172a;
    }}
    .student-sig-roll {{
        font-size: 7.5pt;
        color: #64748b;
    }}

    /* PAGE 3 STYLING */
    .callout-box {{
        background: #f0fdf4;
        border-left: 3.5px solid #10b981;
        border-radius: 4px;
        padding: 8px 12px;
        margin: 10px 0;
    }}
    .callout-title {{
        font-size: 8.5pt;
        font-weight: 800;
        color: #065f46;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 3px;
    }}
    .callout-p {{
        font-size: 8.5pt;
        color: #1f2937;
        margin-bottom: 4px;
        line-height: 1.4;
    }}
    .code-badge {{
        display: inline-block;
        background: #f1f5f9;
        border: 1px solid #e2e8f0;
        border-radius: 3px;
        padding: 1px 5px;
        font-family: "Courier New", Courier, monospace;
        font-size: 8pt;
        color: #0f172a;
        margin: 1px 0;
    }}
</style>
</head>
<body>

<!-- ==================== PAGE 1 ==================== -->
<div class="page">
    <div class="inst-header">
        <div class="inst-soet">SCHOOL OF ENGINEERING AND TECHNOLOGY</div>
        <div class="inst-name">K.R. MANGALAM UNIVERSITY, GURUGRAM</div>
        <div class="inst-dept">DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING</div>
    </div>

    <div class="logo-container">
        <img class="krmu-logo" src="{logo_b64}" alt="K.R. Mangalam University Logo">
    </div>

    <div class="badge-capsule">
        <span class="badge-pill">B.Tech Major Capstone Project Report | 2025–2026</span>
    </div>

    <div class="title-section">
        <div class="main-title">Comparative Analysis of Traditional<br>and AI-Driven Threat Detection<br>Techniques in Cybersecurity</div>
        <div class="sub-title">Design, Implementation, and Empirical Evaluation of an Autonomous,<br>Low-Latency Web Application Firewall (AI-WAF)</div>
    </div>

    <div class="info-card">
        <!-- Left Column -->
        <div>
            <div class="info-col-item">
                <div class="info-lbl">Candidates / Team Members:</div>
                <div class="student-entry"><strong>Anant Soni</strong> (Roll No: 2301730095)</div>
                <div class="student-entry"><strong>Pabitra Giri</strong> (Roll No: 2301730081)</div>
                <div class="student-entry"><strong>Anurag Pandey</strong> (Roll No: 2301730094)</div>
                <div class="student-entry"><strong>Saksham Pachauri</strong> (Roll No: 2301730060)</div>
                <div class="student-entry"><strong>Piyush Gauswami</strong> (Roll No: 2301730062)</div>
            </div>
            <div class="info-col-item" style="margin-top: 6px;">
                <div class="info-lbl">Project Supervisor / Mentor:</div>
                <div class="info-val-bold">Ms. Deepika Garg</div>
                <div class="info-val" style="font-size: 8pt; color: #475569;">Assistant Professor, Department of CSE</div>
            </div>
            <div class="info-col-item">
                <div class="info-lbl">Course / Subject:</div>
                <div class="info-val">AI in Cybersecurity (Capstone Project)</div>
            </div>
        </div>

        <!-- Right Column -->
        <div>
            <div class="info-col-item">
                <div class="info-lbl">Degree & Specialization:</div>
                <div class="info-val-bold">B.Tech CSE (AI & Machine Learning / Cybersecurity)</div>
            </div>
            <div class="info-col-item">
                <div class="info-lbl">Project Repositories:</div>
                <div class="info-val" style="word-break: break-all; font-size: 8pt; font-family: monospace;">
                    • https://github.com/AnantSoni360/capstone-project<br>
                    • https://github.com/Anurag637/AI-Based-Web-Application-Firewall
                </div>
            </div>
            <div class="info-col-item">
                <div class="info-lbl">Deployment / Demo:</div>
                <div class="info-val">Streamlit SOC Cloud Dashboard (Live Public Access)</div>
            </div>
            <div class="info-col-item">
                <div class="info-lbl">Evaluation Corpus:</div>
                <div class="info-val">Spanish National Research Council (CSIC 2010 HTTP Dataset)</div>
            </div>
        </div>
    </div>

    <div class="bottom-meta">
        <div class="date-line">Academic Session: 2025 – 2026 &nbsp;|&nbsp; Submission Date: November 2026</div>
        <div class="sub-line">Submitted in partial fulfillment of the requirements for the award of the degree of Bachelor of Technology</div>
    </div>

    <div class="footer-bar">
        <span>AI-WAF: Comparative Analysis & Empirical Evaluation</span>
        <span>Page 1</span>
    </div>
</div>

<!-- ==================== PAGE 2 ==================== -->
<div class="page">
    <div class="section-h1">Certificate of Authenticity</div>
    <p class="legal-p">
        This is to certify that the project entitled <strong>"Comparative Analysis of Traditional and AI-Driven Threat Detection Techniques in Cybersecurity: Design, Implementation, and Empirical Evaluation of an Autonomous, Low-Latency Web Application Firewall (AI-WAF)"</strong> submitted by <strong>Anant Soni (2301730095), Pabitra Giri (2301730081), Anurag Pandey (2301730094), Saksham Pachauri (2301730060), and Piyush Gauswami (2301730062)</strong> in partial fulfillment of the requirements for the award of the degree of <strong>Bachelor of Technology in Computer Science & Engineering</strong> at <strong>School of Engineering & Technology, K.R. Mangalam University</strong>, is an authentic record of the candidates' own work carried out under guidance and supervision.
    </p>
    <p class="legal-p">
        The empirical findings, dataset deduplication protocols, model architectures (PyTorch 1D-CNN, XGBoost, Rule Engines), and reverse-proxy container topologies embodied in this report have not been submitted to any other University or Institution for the award of any degree or diploma.
    </p>

    <div class="sig-row">
        <div class="sig-col">
            <div class="sig-rule"></div>
            <div class="sig-role">Ms. Deepika Garg</div>
            <div class="sig-dept">Assistant Professor & Project Supervisor<br>Department of Computer Science & Engineering<br>School of Engineering & Technology<br>K.R. Mangalam University</div>
        </div>
        <div class="sig-col" style="text-align: right;">
            <div class="sig-rule" style="margin-left: auto;"></div>
            <div class="sig-role">Head of Department (CSE)</div>
            <div class="sig-dept">Department of Computer Science & Engineering<br>School of Engineering & Technology<br>K.R. Mangalam University</div>
        </div>
    </div>

    <div class="section-h1" style="margin-top: 15px;">Candidate Declaration</div>
    <p class="legal-p">
        We, <strong>Anant Soni, Pabitra Giri, Anurag Pandey, Saksham Pachauri, and Piyush Gauswami</strong>, hereby declare that the work presented in this Capstone Project Report is original and has been carried out by us under the academic framework of K.R. Mangalam University. Any text, algorithms, datasets, or software libraries referenced from prior academic literature or open-source repositories have been duly acknowledged and cited according to standard academic practices.
    </p>
    <p class="legal-p">
        We confirm that all empirical benchmarks reported on the CSIC 2010 dataset were conducted under strict zero-leakage conditions on a frozen test partition (N=3,842) and represent truthful system behavior.
    </p>

    <div style="margin-top: 14px;">
        <div style="font-size: 8.5pt; font-weight: 800; color: #475569; text-transform: uppercase; margin-bottom: 6px;">Submitted By (Candidate Signatures):</div>
        <div class="students-sig-grid">
            <div class="student-sig-block">
                <div class="student-sig-name">Anant Soni</div>
                <div class="student-sig-roll">Roll No: 2301730095</div>
            </div>
            <div class="student-sig-block">
                <div class="student-sig-name">Pabitra Giri</div>
                <div class="student-sig-roll">Roll No: 2301730081</div>
            </div>
            <div class="student-sig-block">
                <div class="student-sig-name">Anurag Pandey</div>
                <div class="student-sig-roll">Roll No: 2301730094</div>
            </div>
            <div class="student-sig-block">
                <div class="student-sig-name">Saksham Pachauri</div>
                <div class="student-sig-roll">Roll No: 2301730060</div>
            </div>
            <div class="student-sig-block">
                <div class="student-sig-name">Piyush Gauswami</div>
                <div class="student-sig-roll">Roll No: 2301730062</div>
            </div>
            <div class="student-sig-block" style="border: none;">
                <div class="student-sig-roll" style="color: #0f172a; font-weight: 600;">B.Tech CSE (AI/ML)<br>SOET, K.R. Mangalam Univ.</div>
            </div>
        </div>
    </div>

    <div class="footer-bar">
        <span>AI-WAF: Comparative Analysis & Empirical Evaluation</span>
        <span>Page 2</span>
    </div>
</div>

<!-- ==================== PAGE 3 ==================== -->
<div class="page">
    <div class="section-h1">Acknowledgements</div>
    <p class="legal-p">
        We express our deepest gratitude to our project supervisor, <strong>Ms. Deepika Garg</strong>, faculty mentors, and the Department of Computer Science & Engineering at <strong>K.R. Mangalam University</strong> for their invaluable guidance, encouragement, and intellectual support throughout the lifecycle of this capstone research.
    </p>
    <p class="legal-p">
        We are profoundly thankful to the cybersecurity and machine learning open-source communities—notably the developers of <strong>PyTorch, XGBoost, FastAPI, Nginx, SHAP, and Streamlit</strong>—whose robust foundational frameworks made the development of this enterprise-grade firewall architecture possible.
    </p>
    <p class="legal-p">
        Special appreciation is extended to the <strong>Spanish National Research Council (CSIC)</strong> for making the CSIC 2010 HTTP evaluation corpus publicly accessible for academic benchmarking, and to our peers and family for their unwavering motivation and patience.
    </p>

    <div class="callout-box">
        <div class="callout-title">Project Availability & Reproducibility</div>
        <div class="callout-p">
            This complete project, including source code, model weights, Docker topologies, unit test suites (62 passing tests), and interactive Streamlit SOC dashboard, is publicly hosted at:
        </div>
        <div>
            <span class="code-badge">https://github.com/AnantSoni360/capstone-project</span>
            <span class="code-badge">https://github.com/Anurag637/AI-Based-Web-Application-Firewall</span>
        </div>
        <div class="callout-p" style="margin-top: 4px;">
            Live Streamlit SOC Console: <span class="code-badge">https://capstone-project-cc6nhqgmfapc7rvfrhwcub.streamlit.app/</span>
        </div>
    </div>

    <div class="section-h1" style="margin-top: 14px;">Executive Summary & Abstract</div>
    <p class="legal-p">
        Web Application Firewalls (WAFs) constitute the primary perimeter defense shielding enterprise HTTP services against application-layer exploits. Traditional commercial and open-source WAFs (such as ModSecurity Core Rule Set) rely overwhelmingly on deterministic regular-expression signatures. While deterministic signatures deliver sub-millisecond execution and near-zero false alarms on known static exploits, they exhibit catastrophic false-negative rates (~78% evasion) against modern obfuscated, polymorphic, and zero-day attack payloads. Conversely, monolithic deep learning sequence models introduce significant inference latency overhead (>50 ms) that breaches production web latency budgets (< 15 ms).
    </p>
    <p class="legal-p">
        This capstone project engineers and empirically benchmarks <strong>AI-WAF</strong>, an autonomous, low-latency, defense-in-depth Web Application Firewall that harmonizes deterministic heuristic signatures with Machine Learning (XGBoost) and Deep Neural Networks (PyTorch 1D-CNN) inside an inline reverse-proxy gateway.
    </p>
    <div style="font-size: 8.5pt; font-weight: 800; color: #0f172a; margin-top: 6px;">Key Academic & Technical Highlights:</div>
    <div style="font-size: 8.5pt; color: #334155; line-height: 1.4; padding-left: 10px; margin-top: 3px;">
        • <strong>Dataset Leakage Resolution:</strong> Identified and eliminated a critical 58.06% synthetic session-cookie duplicate leakage vulnerability in the benchmark CSIC 2010 corpus, yielding a clean dataset of 25,608 unique records and a strictly disjoint 15% frozen test partition (N=3,842) with verified 0% train-test contamination.
    </div>

    <div class="footer-bar">
        <span>AI-WAF: Comparative Analysis & Empirical Evaluation</span>
        <span>Page 3</span>
    </div>
</div>

</body>
</html>
"""
    return html

def main():
    print("[1/4] Building updated front matter HTML for Pages 1, 2, 3...")
    html_content = build_front_matter_html()
    html_path = "reports/updated_front_matter.html"
    pdf_front_path = "reports/updated_front_matter.pdf"
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print("[2/4] Compiling updated front matter via Headless Chrome...")
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Users\Acer\AppData\Local\Google\Chrome\Application\chrome.exe"
    ]
    chrome_exe = None
    for p in chrome_paths:
        if os.path.exists(p):
            chrome_exe = p
            break
            
    if not chrome_exe:
        print("[ERROR] Chrome executable not found.")
        sys.exit(1)

    abs_html_uri = Path(os.path.abspath(html_path)).as_uri()
    abs_front_pdf = os.path.abspath(pdf_front_path)

    cmd = [
        chrome_exe,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--run-all-compositor-stages-before-draw",
        "--no-pdf-header-footer",
        f"--print-to-pdf={abs_front_pdf}",
        abs_html_uri
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0 or not os.path.exists(abs_front_pdf):
        print(f"[ERROR] Failed to compile front matter: {res.stderr}")
        sys.exit(1)

    print("[3/4] Merging with original 40-page PDF to produce 'report 2.pdf'...")
    src_pdf_path = r"C:\Users\Acer\.gemini\antigravity\brain\6880d1d1-621d-4622-bce5-13c0f47b0500\.user_uploaded\media_1795800107587_a56dfd7f.pdf"
    
    doc_src = fitz.open(src_pdf_path)
    doc_front = fitz.open(abs_front_pdf)

    print(f"Original doc page count: {len(doc_src)}")
    print(f"Front matter page count: {len(doc_front)}")

    # Create target document
    doc_out = fitz.open()

    # Insert the 3 new front matter pages
    for i in range(min(3, len(doc_front))):
        doc_out.insert_pdf(doc_front, from_page=i, to_page=i)

    # Insert pages 4 to 40 (0-indexed 3 to 39) from original
    doc_out.insert_pdf(doc_src, from_page=3, to_page=len(doc_src)-1)

    out_pdf_1 = "report 2.pdf"
    out_pdf_2 = "reports/report 2.pdf"

    doc_out.save(out_pdf_1)
    doc_out.save(out_pdf_2)
    doc_out.close()
    doc_src.close()
    doc_front.close()

    print("[4/4] Verifying generated 'report 2.pdf'...")
    chk = fitz.open(out_pdf_1)
    print("="*60)
    print(f"[SUCCESS] 'report 2.pdf' generated successfully!")
    print(f"Total Page Count: {len(chk)}")
    print(f"File 1: {os.path.abspath(out_pdf_1)} ({os.path.getsize(out_pdf_1):,} bytes)")
    print(f"File 2: {os.path.abspath(out_pdf_2)} ({os.path.getsize(out_pdf_2):,} bytes)")
    print("="*60)
    print("--- Page 1 verification ---")
    print(chk[0].get_text()[:400].strip())
    print("--- Page 2 verification ---")
    print(chk[1].get_text()[:400].strip())
    print("--- Page 3 verification ---")
    print(chk[2].get_text()[:400].strip())
    print("--- Page 4 verification (first line) ---")
    print(chk[3].get_text().splitlines()[0:3])

if __name__ == '__main__':
    main()
