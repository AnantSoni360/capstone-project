import pathlib
import pytest
from fastapi.testclient import TestClient

WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent

from backend.main import app as waf_backend_app
from backend.mock_target_app import target_app, TARGET_ACCESS_LOG
from proxy.waf_proxy import waf_proxy_app


@pytest.fixture(scope="module", autouse=True)
def setup_gateway():
    # Trigger lifespan to initialize decision engine
    with TestClient(waf_backend_app) as _:
        # Clear access log before testing
        if TARGET_ACCESS_LOG.exists():
            TARGET_ACCESS_LOG.unlink()
        yield


def test_benign_traffic_reaches_target_app():
    """Verify legitimate shopping request passes WAF and reaches target application."""
    client = TestClient(waf_proxy_app)
    response = client.get("/tienda1/publico/pagar.jsp?modo=insertar&precio=3155&B1=Pasar+por+caja")

    assert response.status_code == 200
    assert "checkout_success" in response.text

    # Verify log entry in target application access log
    assert TARGET_ACCESS_LOG.exists()
    with open(TARGET_ACCESS_LOG, "r", encoding="utf-8") as f:
        log_content = f.read()

    assert "GET" in log_content
    assert "/tienda1/publico/pagar.jsp" in log_content


def test_sqli_attack_blocked_and_never_reaches_target():
    """Verify SQL injection is blocked at the proxy and NEVER appears in target app log."""
    client = TestClient(waf_proxy_app)
    sqli_payload = "/tienda1/publico/pagar.jsp?id=1%27%20UNION%20SELECT%20null,%20password%20FROM%20usuarios--"
    response = client.get(sqli_payload)

    # 1. Client receives 403 Forbidden
    assert response.status_code == 403
    assert response.headers.get("X-WAF-Verdict") == "BLOCK"
    assert "Request Blocked" in response.text or "403" in response.text

    # 2. PROOF OF ZERO-ARRIVAL: Audit target app log
    if TARGET_ACCESS_LOG.exists():
        with open(TARGET_ACCESS_LOG, "r", encoding="utf-8") as f:
            log_content = f.read()
        assert "UNION SELECT" not in log_content
        assert "password FROM usuarios" not in log_content


def test_xss_attack_blocked_and_never_reaches_target():
    """Verify XSS attack is blocked at the proxy and NEVER appears in target app log."""
    client = TestClient(waf_proxy_app)
    xss_payload = "modo=insertar&nombre=%3Cscript%3Ealert(%27XSS%27)%3C/script%3E"
    response = client.post("/tienda1/publico/pagar.jsp", content=xss_payload, headers={"Content-Type": "application/x-www-form-urlencoded"})

    # 1. Client receives 403 Forbidden
    assert response.status_code == 403
    assert response.headers.get("X-WAF-Verdict") == "BLOCK"

    # 2. PROOF OF ZERO-ARRIVAL: Audit target app log
    if TARGET_ACCESS_LOG.exists():
        with open(TARGET_ACCESS_LOG, "r", encoding="utf-8") as f:
            log_content = f.read()
        assert "<script>alert('XSS')</script>" not in log_content
