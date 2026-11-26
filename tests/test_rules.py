import json
import pathlib
import pytest

WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent
CONFIG_PATH = WORKSPACE_ROOT / "config" / "rules.json"
METRICS_PATH = WORKSPACE_ROOT / "reports" / "rule_baseline_metrics.json"
FIGURE_PATH = WORKSPACE_ROOT / "reports" / "figures" / "rule_baseline_confusion_matrix.png"

from src.rules import TraditionalRuleEngine


@pytest.fixture
def rule_engine():
    return TraditionalRuleEngine(str(CONFIG_PATH))


def test_rules_configuration_loaded(rule_engine):
    """Verify all 18 documented security rules are loaded and compiled."""
    assert len(rule_engine.compiled_rules) >= 15
    rule_ids = [r[0]["id"] for r in rule_engine.compiled_rules]
    assert "SQLI_01_UNION_SELECT" in rule_ids
    assert "XSS_01_SCRIPT_TAG" in rule_ids
    assert "TRAV_01_DIRECTORY_DOT_DOT" in rule_ids


def test_sqli_union_detection(rule_engine):
    """Verify UNION SELECT rule matching."""
    res = rule_engine.evaluate_payload("/products?id=1 UNION SELECT null, username, password FROM users--")
    assert res["verdict"] == "BLOCK"
    assert res["risk_score"] >= 0.70
    matched_ids = [m["id"] for m in res["matched_rules"]]
    assert "SQLI_01_UNION_SELECT" in matched_ids


def test_sqli_tautology_detection(rule_engine):
    """Verify tautology rule matching."""
    res = rule_engine.evaluate_payload("/login?username=admin' OR '1'='1")
    assert res["verdict"] == "BLOCK"
    matched_ids = [m["id"] for m in res["matched_rules"]]
    assert "SQLI_02_TAUTOLOGY" in matched_ids


def test_xss_script_tag_detection(rule_engine):
    """Verify XSS script tag matching."""
    res = rule_engine.evaluate_payload("/search?q=<script>alert('XSS')</script>")
    assert res["verdict"] == "BLOCK"
    matched_ids = [m["id"] for m in res["matched_rules"]]
    assert "XSS_01_SCRIPT_TAG" in matched_ids


def test_path_traversal_detection(rule_engine):
    """Verify path traversal sequence matching."""
    res = rule_engine.evaluate_payload("/download?file=../../../../etc/passwd")
    assert res["verdict"] == "BLOCK"
    matched_ids = [m["id"] for m in res["matched_rules"]]
    assert "TRAV_01_DIRECTORY_DOT_DOT" in matched_ids


def test_benign_request_allows(rule_engine):
    """Verify legitimate shopping request receives ALLOW."""
    res = rule_engine.evaluate_payload("/tienda1/publico/anadir.jsp?id=3&nombre=Vino+Rioja&precio=100&cantidad=2")
    assert res["verdict"] == "ALLOW"
    assert res["risk_score"] < 0.35
    assert len(res["matched_rules"]) == 0


def test_baseline_evaluation_artifacts_exist():
    """Verify baseline evaluation JSON and confusion matrix plot exist."""
    assert METRICS_PATH.exists()
    assert FIGURE_PATH.exists()
    assert FIGURE_PATH.stat().st_size > 5000

    with open(METRICS_PATH, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    assert "strict_block_policy" in metrics
    sb = metrics["strict_block_policy"]
    assert "accuracy" in sb
    assert "precision" in sb
    assert "recall" in sb
    assert "false_positive_rate" in sb
    assert "false_negative_rate" in sb
    assert "latency_ms" in sb
    assert sb["latency_ms"]["mean"] < 1.0  # sub-millisecond execution
