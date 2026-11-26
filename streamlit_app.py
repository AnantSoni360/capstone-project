"""
Streamlit Cloud Entrypoint for AI-WAF Dashboard
Redirects execution to dashboard/app.py
"""
import runpy
import sys
import pathlib

# Ensure root workspace is on path
WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

# Execute the main dashboard application
target_app = WORKSPACE_ROOT / "dashboard" / "app.py"
runpy.run_path(str(target_app), run_name="__main__")
