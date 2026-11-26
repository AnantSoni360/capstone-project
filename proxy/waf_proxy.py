"""
Standalone WAF Reverse Proxy Gateway (Phase 11)
Intercepts client requests, queries WAF decision engine, enforces ALLOW/BLOCK,
and proxies permitted requests to the upstream protected web application.
"""

import os
import pathlib
import sys
import time
from typing import Dict, Any, Optional
import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse

WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

import backend.main as waf_main
from backend.decision_engine import WAFDecisionEngine
from backend.mock_target_app import target_app

# HTML Block Screen
CUSTOM_403_HTML_PATH = pathlib.Path(__file__).resolve().parent / "custom_403.html"
with open(CUSTOM_403_HTML_PATH, "r", encoding="utf-8") as f:
    BLOCK_SCREEN_HTML = f.read()

waf_proxy_app = FastAPI(
    title="WAF Reverse Proxy Gateway",
    description="Inline enforcement gateway standing in front of ABC Shopping."
)


@waf_proxy_app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def reverse_proxy_handler(request: Request, path: str):
    """
    Main reverse proxy interceptor.
    Applies WAF inspection before forwarding to the protected target application.
    """
    method = request.method
    full_url = str(request.url)
    body_bytes = await request.body()
    body_str = body_bytes.decode("utf-8", errors="ignore")
    client_ip = request.client.host if request.client else "127.0.0.1"

    # Step 1 & 2: Intercept & Query WAF Decision Engine with Fail-Open/Fail-Closed Fault Tolerance
    try:
        engine = waf_main.decision_engine
        if engine is None:
            engine = WAFDecisionEngine()
            waf_main.decision_engine = engine

        scan_res = engine.inspect_request(
            method=method,
            url=full_url,
            body=body_str,
            headers=dict(request.headers),
            client_ip=client_ip
        )
    except Exception as exc:
        fail_open = os.getenv("WAF_FAIL_OPEN", "false").lower() in ("true", "1", "yes")
        if fail_open:
            # Fallback fail-open: allow request through with warning telemetry
            transport = httpx.ASGITransport(app=target_app)
            async with httpx.AsyncClient(transport=transport, base_url="http://target-app") as client:
                target_res = await client.request(
                    method=method,
                    url=f"/{path}?{request.url.query}" if request.url.query else f"/{path}",
                    content=body_bytes,
                    headers={"X-Forwarded-For": client_ip, "X-WAF-Enforced": "fallback-open"}
                )
            headers = dict(target_res.headers)
            headers["X-WAF-Fallback"] = "fail-open"
            headers["X-WAF-Warning"] = f"WAF error: {str(exc)}"
            return Response(
                content=target_res.content,
                status_code=target_res.status_code,
                headers=headers,
                media_type=target_res.headers.get("content-type")
            )
        else:
            # Fallback fail-closed: strictly reject traffic during inspection failure
            return JSONResponse(
                status_code=503,
                content={
                    "error": "WAF Inspection Service Unavailable",
                    "policy": "fail-closed",
                    "detail": "Request blocked by WAF policy during service disruption."
                },
                headers={"X-WAF-Fallback": "fail-closed"}
            )

    # Step 3: Enforce Blocking Policy
    if scan_res["verdict"] == "BLOCK":
        # Request is HALTED. It is NEVER forwarded to the target application.
        return HTMLResponse(
            content=BLOCK_SCREEN_HTML,
            status_code=403,
            headers={
                "X-WAF-Verdict": "BLOCK",
                "X-WAF-Attack-Type": scan_res["attack_type"],
                "X-WAF-Risk-Score": str(scan_res["risk_score"])
            }
        )

    # Step 4: Forward ALLOWED or REVIEWED request to Target Application
    transport = httpx.ASGITransport(app=target_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://target-app") as client:
        target_res = await client.request(
            method=method,
            url=f"/{path}?{request.url.query}" if request.url.query else f"/{path}",
            content=body_bytes,
            headers={"X-Forwarded-For": client_ip, "X-WAF-Enforced": "true"}
        )

    # Return upstream response to client
    headers = dict(target_res.headers)
    if scan_res["verdict"] == "REVIEW":
        headers["X-WAF-Review"] = "Flagged-for-Audit"

    return Response(
        content=target_res.content,
        status_code=target_res.status_code,
        headers=headers,
        media_type=target_res.headers.get("content-type")
    )
