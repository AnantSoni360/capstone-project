"""
Generates a publication-grade PDF from reports/CAPSTONE_FINAL_SUBMISSION.md
using Mistune HTML conversion and Chrome Headless printing engine.
"""

import os
import pathlib
import subprocess
import sys
import mistune

WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent

MD_PATH = WORKSPACE_ROOT / "reports" / "CAPSTONE_FINAL_SUBMISSION.md"
HTML_PATH = WORKSPACE_ROOT / "reports" / "CAPSTONE_FINAL_SUBMISSION.html"
PDF_PATH = WORKSPACE_ROOT / "reports" / "CAPSTONE_FINAL_SUBMISSION.pdf"

print(f"[PDF Generator] Reading {MD_PATH}...")
with open(MD_PATH, "r", encoding="utf-8") as f:
    md_content = f.read()

# Render Markdown to HTML using Mistune
html_body = mistune.html(md_content)

# Professional Academic CSS Stylesheet
academic_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Comparative Analysis of Traditional and AI-Driven Threat Detection (AI-WAF)</title>
<style>
    @page {{
        size: A4;
        margin: 20mm 15mm 20mm 15mm;
        @bottom-right {{
            content: counter(page);
        }}
    }}
    body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #111827;
        line-height: 1.55;
        font-size: 11pt;
        background-color: #ffffff;
        margin: 0;
        padding: 20px 40px;
    }}
    h1 {{
        color: #111827;
        font-size: 20pt;
        border-bottom: 3px solid #F59E0B;
        padding-bottom: 8px;
        margin-top: 25px;
        margin-bottom: 15px;
        page-break-before: always;
    }}
    h1:first-of-type {{
        page-break-before: avoid;
        text-align: center;
        border-bottom: none;
    }}
    h2 {{
        color: #1F2937;
        font-size: 15pt;
        border-bottom: 1.5px solid #E5E7EB;
        padding-bottom: 5px;
        margin-top: 22px;
        margin-bottom: 12px;
    }}
    h3 {{
        color: #374151;
        font-size: 12pt;
        margin-top: 16px;
        margin-bottom: 8px;
    }}
    p, li {{
        text-align: justify;
        margin-bottom: 8px;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 16px 0;
        font-size: 9.5pt;
        page-break-inside: avoid;
    }}
    th {{
        background-color: #FEF3C7;
        color: #000000;
        font-weight: 800;
        border: 1.5px solid #F59E0B;
        padding: 7px 10px;
        text-align: left;
    }}
    td {{
        border: 1px solid #D1D5DB;
        padding: 6px 10px;
    }}
    tr:nth-child(even) {{
        background-color: #F9FAFB;
    }}
    code {{
        font-family: "Courier New", Courier, monospace;
        background-color: #FEF3C7;
        color: #000000;
        border: 1px solid #FCD34D;
        padding: 2px 5px;
        border-radius: 4px;
        font-size: 9.5pt;
        font-weight: 700;
    }}
    pre {{
        background-color: #1F2937;
        color: #F9FAFB;
        padding: 12px 16px;
        border-radius: 6px;
        overflow-x: auto;
        font-size: 9pt;
        line-height: 1.4;
        page-break-inside: avoid;
    }}
    pre code {{
        background-color: transparent;
        color: #F9FAFB;
        border: none;
        padding: 0;
        font-weight: normal;
    }}
    hr {{
        border: none;
        border-top: 1.5px solid #E5E7EB;
        margin: 20px 0;
    }}
    strong {{
        color: #000000;
        font-weight: 800;
    }}
</style>
</head>
<body>
{html_body}
</body>
</html>
"""

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(academic_template)

print(f"[PDF Generator] HTML rendered to: {HTML_PATH}")

# Convert HTML to PDF using Chrome Headless
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
browser = chrome_path if os.path.exists(chrome_path) else edge_path

cmd = [
    browser,
    "--headless=new",
    "--disable-gpu",
    "--no-sandbox",
    "--no-pdf-header-footer",
    f"--print-to-pdf={PDF_PATH}",
    f"file:///{HTML_PATH}"
]

print(f"[PDF Generator] Printing to PDF via {browser}...")
res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

if PDF_PATH.exists():
    print(f"[SUCCESS] Academic Report PDF generated at: {PDF_PATH} ({PDF_PATH.stat().st_size:,} bytes)")
else:
    print(f"[ERROR] PDF generation failed: {res.stderr}")
