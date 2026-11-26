import pathlib
import py_compile
import pytest

WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent
DASHBOARD_APP_PATH = WORKSPACE_ROOT / "dashboard" / "app.py"
REPORTS_DIR = WORKSPACE_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
CONFIG_PATH = WORKSPACE_ROOT / "config" / "rules.json"


def test_dashboard_script_syntax():
    """Verify Streamlit app.py compiles without syntax errors."""
    assert DASHBOARD_APP_PATH.exists(), f"Missing dashboard script: {DASHBOARD_APP_PATH}"
    # Compile python file to check for syntax errors
    py_compile.compile(str(DASHBOARD_APP_PATH), doraise=True)


def test_dashboard_dependencies_and_artifacts():
    """Verify all files and figures referenced by the dashboard exist on disk."""
    assert (REPORTS_DIR / "final_model_benchmark_test_set.csv").exists()
    assert (FIGURES_DIR / "master_model_benchmark.png").exists()
    assert (FIGURES_DIR / "shap_summary.png").exists()
    assert (FIGURES_DIR / "robustness_comparison.png").exists()
    assert CONFIG_PATH.exists()


def test_dashboard_model_loader():
    """Verify WAF decision engine and XAI components load properly for dashboard."""
    from dashboard.app import load_waf_components
    engine, extractor, tree_explainer, payload_explainer = load_waf_components()

    assert engine is not None
    assert extractor.is_fitted
    assert tree_explainer is not None
    assert payload_explainer is not None

    # Test sample inspection through engine
    sample_res = engine.inspect_request("GET", "/tienda1/publico/pagar.jsp?modo=insertar&precio=3155&B1=Pasar+por+caja")
    assert sample_res["verdict"] == "ALLOW"
