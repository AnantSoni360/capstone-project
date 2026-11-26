import pathlib
import pytest
from fastapi.testclient import TestClient

WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent

from backend.main import app
from backend.database import DB_PATH, get_recent_events


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_api_health_endpoint(client):
    """Verify health endpoint confirms service readiness."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["models_loaded"] is True
    assert data["rule_count"] >= 15


def test_api_scan_blocks_sqli(client):
    """Verify SQL injection payload is blocked with HTTP 403."""
    payload = {
        "method": "GET",
        "url": "/publico/anadir.jsp?id=1%27%20UNION%20SELECT%20null,%20username,%20password%20FROM%20usuarios--",
        "body": ""
    }
    # Warm-up call to eliminate first-request cold start
    client.get("/health")
    response = client.post("/scan", json=payload)
    assert response.status_code == 403
    data = response.json()
    assert data["verdict"] == "BLOCK"
    assert data["action_taken"] == "REJECT_403"
    assert data["risk_score"] >= 0.70
    assert data["rule_evidence"]["match_count"] > 0


def test_api_scan_blocks_xss(client):
    """Verify XSS payload is blocked with HTTP 403."""
    payload = {
        "method": "POST",
        "url": "/comment.jsp",
        "body": "author=attacker&comment=%3Cscript%3Ealert(%27XSS%27)%3C/script%3E"
    }
    response = client.post("/scan", json=payload)
    assert response.status_code == 403
    data = response.json()
    assert data["verdict"] == "BLOCK"
    assert data["action_taken"] == "REJECT_403"


def test_api_scan_allows_benign(client):
    """Verify legitimate shopping request receives HTTP 200 ALLOW."""
    payload = {
        "method": "GET",
        "url": "/tienda1/publico/pagar.jsp?modo=insertar&precio=3714&B1=Confirmar HTTP/1.1",
        "body": ""
    }
    response = client.post("/scan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] == "ALLOW"
    assert data["action_taken"] == "FORWARD_UPSTREAM"
    assert data["risk_score"] < 0.35


def test_sanitized_database_logging(client):
    """Verify passwords are masked before being written to the database."""
    secret_pass = "SuperSecretPassword123"
    payload = {
        "method": "POST",
        "url": "/tienda1/miembros/editar.jsp",
        "body": f"login=admin&password={secret_pass}&mode=update"
    }
    response = client.post("/scan", json=payload)
    assert response.status_code in [200, 403]

    events = get_recent_events(limit=5)
    assert len(events) > 0
    latest = events[0]
    # Check that plaintext password is NOT in database
    assert secret_pass not in latest.get("query_sanitized", "")
    assert secret_pass not in str(latest)


def test_analytics_and_rules_endpoints(client):
    """Verify dashboard analytics and rule listing endpoints."""
    res_analytics = client.get("/analytics")
    assert res_analytics.status_code == 200
    analytics_data = res_analytics.json()
    assert "total_requests" in analytics_data
    assert "allowed_requests" in analytics_data
    assert "blocked_requests" in analytics_data

    res_rules = client.get("/rules")
    assert res_rules.status_code == 200
    rules_data = res_rules.json()
    assert rules_data["rule_count"] >= 15
