"""
Generates a publication-grade PDF handbook of the 20-Slide Capstone Presentation Scripts
for K.R. Mangalam University B.Tech Defense using Mistune and Chrome Headless.
Reads directly from presentation/CAPSTONE_PRESENTATION_SPEAKER_SCRIPTS.md to ensure 100% synchrony.
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

print(f"[1/3] Reading Markdown content from: {MD_PATH}...")
with open(MD_PATH, "r", encoding="utf-8") as f:
    md_content = f.read()

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
