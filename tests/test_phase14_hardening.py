"""
Unit and Integration Tests for Phase 14: Production Hardening & System Verification
Verifies:
1. Configurable Fail-Open vs Fail-Closed policy enforcement during WAF failure.
2. Latency budget compliance (< 15ms per request).
3. End-to-end zero-arrival verification for blocked attacks.
4. Guaranteed pass-through for legitimate customer requests.
"""

import os
import pathlib
import time
from unittest.mock import patch
import httpx
import pytest

from backend.decision_engine import WAFDecisionEngine
from backend.mock_target_app import TARGET_ACCESS_LOG
from proxy.waf_proxy import waf_proxy_app


@pytest.fixture(autouse=True)
def clean_target_access_log():
    """Wipes target access log before and after each test."""
    if TARGET_ACCESS_LOG.exists():
        TARGET_ACCESS_LOG.unlink()
    yield
    if TARGET_ACCESS_LOG.exists():
        TARGET_ACCESS_LOG.unlink()


@pytest.mark.anyio
async def test_fail_closed_policy_on_waf_error():
    """
    NFR-04 / FR-09:
    When WAF_FAIL_OPEN=false, any failure in WAF inspection must reject traffic
    with HTTP 503 (fail-closed), preventing uninspected bypass.
    """
    with patch.dict(os.environ, {"WAF_FAIL_OPEN": "false"}):
        with patch.object(WAFDecisionEngine, "inspect_request", side_effect=RuntimeError("Simulated engine crash")):
            transport = httpx.ASGITransport(app=waf_proxy_app)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                res = await client.get("/products?category=shoes")
                
                assert res.status_code == 503
                assert res.headers.get("X-WAF-Fallback") == "fail-closed"
                assert "fail-closed" in res.json().get("policy", "")
                
                # Verify request did NOT reach target app
                assert not TARGET_ACCESS_LOG.exists() or len(TARGET_ACCESS_LOG.read_text()) == 0


@pytest.mark.anyio
async def test_fail_open_policy_on_waf_error():
    """
    NFR-04 / FR-09:
    When WAF_FAIL_OPEN=true, an outage allows legitimate traffic to proceed
    with explicit audit fallback headers.
    """
    with patch.dict(os.environ, {"WAF_FAIL_OPEN": "true"}):
        with patch.object(WAFDecisionEngine, "inspect_request", side_effect=RuntimeError("Simulated engine crash")):
            transport = httpx.ASGITransport(app=waf_proxy_app)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                res = await client.get("/products?category=shoes")
                
                assert res.status_code == 200
                assert res.headers.get("X-WAF-Fallback") == "fail-open"
                assert "WAF error" in res.headers.get("X-WAF-Warning", "")
                
                # Verify request DID reach target app under fail-open
                assert TARGET_ACCESS_LOG.exists()
                log_content = TARGET_ACCESS_LOG.read_text(encoding="utf-8")
                assert "category=shoes" in log_content


def test_steady_state_latency_budget():
    """
    NFR-01:
    Verify that mean inspection latency is strictly under the 15ms per request budget.
    """
    engine = WAFDecisionEngine()
    
    # Warmup
    for _ in range(5):
        engine.inspect_request(
            method="GET",
            url="http://example.com/tienda1/publico/anadir.jsp?id=1",
            body=""
        )
        
    test_urls = [
        "http://example.com/tienda1/publico/pagar.jsp",
        "http://example.com/products?category=footwear&size=10",
        "http://example.com/search?q=leather+jacket",
        "http://example.com/items?id=102&sort=asc",
        "http://example.com/user/profile?view=summary"
    ]
    
    latencies = []
    for _ in range(50):
        url = test_urls[_ % len(test_urls)]
        t0 = time.perf_counter()
        res = engine.inspect_request(method="GET", url=url, body="")
        t1 = time.perf_counter()
        latencies.append((t1 - t0) * 1000.0)
        assert res["verdict"] in ("ALLOW", "REVIEW")
        
    mean_latency = sum(latencies) / len(latencies)
    sorted_lat = sorted(latencies)
    p95_latency = sorted_lat[int(len(latencies) * 0.95)]
    
    print(f"\n[LATENCY BENCHMARK] Mean: {mean_latency:.3f} ms | P95: {p95_latency:.3f} ms")
    assert mean_latency < 15.0, f"Mean latency {mean_latency:.3f} ms exceeds 15.0 ms budget!"
    assert p95_latency < 25.0, f"P95 latency {p95_latency:.3f} ms exceeds 25.0 ms budget!"


@pytest.mark.anyio
async def test_end_to_end_zero_arrival_security_proof():
    """
    Completion Gate 04:
    Execute representative SQLi and XSS payloads against the WAF proxy.
    Verify 100% of them receive HTTP 403 Forbidden AND zero entries appear in target access logs.
    """
    attack_payloads = [
        ("GET", "/products?id=1%27%20OR%201=1--", ""),
        ("GET", "/products?id=1%27%20UNION%20SELECT%20null,username,password%20FROM%20users--", ""),
        ("GET", "/search?q=%3Cscript%3Ealert(document.cookie)%3C%2Fscript%3E", ""),
        ("POST", "/comment", "comment=<img src=x onerror=alert('XSS')>"),
        ("GET", "/login?user=admin%27%20--", "")
    ]
    
    transport = httpx.ASGITransport(app=waf_proxy_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        for method, path, body in attack_payloads:
            if method == "GET":
                res = await client.get(path)
            else:
                res = await client.post(path, content=body)
                
            assert res.status_code == 403, f"Payload {path} | {body} was not blocked!"
            assert "Request Blocked" in res.text or "Blocked by AI-WAF" in res.text or "REJECT_403" in res.text
            assert res.headers.get("X-WAF-Verdict") == "BLOCK"
            
    # Check target app access log
    if TARGET_ACCESS_LOG.exists():
        log_content = TARGET_ACCESS_LOG.read_text(encoding="utf-8")
        for _, path, body in attack_payloads:
            if body:
                assert body not in log_content, f"Attack body '{body}' leaked to target log!"
            assert "UNION SELECT" not in log_content
            assert "alert(" not in log_content
            assert "OR 1=1" not in log_content


@pytest.mark.anyio
async def test_legitimate_traffic_pass_through():
    """
    Completion Gate 01:
    Verify legitimate customer requests pass through with HTTP 200 and appear in target access log.
    """
    legit_requests = [
        ("GET", "/products?category=shoes", ""),
        ("GET", "/tienda1/publico/pagar.jsp", ""),
        ("POST", "/comment", "I love this product, very fast shipping!"),
        ("POST", "/login", "username=alice&password=CleanPassword123!")
    ]
    
    transport = httpx.ASGITransport(app=waf_proxy_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        for method, path, body in legit_requests:
            if method == "GET":
                res = await client.get(path)
            else:
                res = await client.post(path, content=body)
                
            assert res.status_code == 200, f"Legitimate request {path} was erroneously blocked!"
            
    # Verify all legitimate requests reached target app access log
    assert TARGET_ACCESS_LOG.exists()
    log_content = TARGET_ACCESS_LOG.read_text(encoding="utf-8")
    assert "category=shoes" in log_content
    assert "pagar.jsp" in log_content
    assert "CleanPassword123!" in log_content
