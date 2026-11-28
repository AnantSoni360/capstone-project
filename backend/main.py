"""
FastAPI Detection Service & Security Gateway (Phase 10)
Exposes low-latency HTTP inspection endpoints, security audit streams,
and system analytics for the WAF reverse proxy and dashboard.
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
import pathlib
import sys
import time
from typing import Dict, Any, List, Optional
import uuid

WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from fastapi import FastAPI, Request, Response, status, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

from backend.schemas import (
    ScanRequest, ScanResponse, HealthResponse,
    RuleEvidence, AIEvidence, SecurityEventRecord
)
from backend.database import (
    init_db, log_security_event, get_analytics_summary, get_recent_events
)
from backend.decision_engine import WAFDecisionEngine

# Global instances loaded at startup
decision_engine: Optional[WAFDecisionEngine] = None
app_start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes models and audit database upon application startup."""
    global decision_engine
    print("[FastAPI] Initializing WAF SQLite Audit Database...")
    init_db()

    print("[FastAPI] Pre-loading WAF Decision Engine (PyTorch 1D-CNN + XGBoost + Rules)...")
    decision_engine = WAFDecisionEngine()
    print("[FastAPI] Engine loaded successfully. Ready for incoming traffic.")
    yield
    print("[FastAPI] Shutting down WAF service.")


app = FastAPI(
    title="AI-Based Web Application Firewall (WAF) Gateway",
    description="Intelligent HTTP request inspection service using Rules, PyTorch 1D-CNN, and XGBoost.",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check():
    """Healthcheck endpoint for container orchestration and reverse proxies."""
    now_iso = datetime.now(timezone.utc).isoformat()
    uptime = time.time() - app_start_time
    loaded = decision_engine is not None
    rules_cnt = len(decision_engine.rule_engine.compiled_rules) if loaded else 0

    return HealthResponse(
        status="healthy" if loaded else "initializing",
        timestamp=now_iso,
        models_loaded=loaded,
        active_models=["PyTorch_1D_CNN", "XGBoost", "TraditionalRuleEngine"],
        rule_count=rules_cnt,
        uptime_seconds=round(uptime, 2)
    )


@app.api_route("/scan", methods=["GET", "POST"], response_model=ScanResponse, tags=["Inspection"])
async def scan_http_request(request: Request, response: Response):
    """
    Primary inspection endpoint invoked by Nginx reverse proxy subrequests or REST clients.
    Supports both JSON payloads (POST) and Nginx auth_request headers (GET/POST).
    Returns HTTP 200 (ALLOW / REVIEW) or HTTP 403 (BLOCK).
    """
    if decision_engine is None:
        raise HTTPException(status_code=503, detail="WAF engine initializing")

    request_id = f"req_{uuid.uuid4().hex[:10]}"
    now_iso = datetime.now(timezone.utc).isoformat()

    # Extract method, url, body from either JSON body or Nginx subrequest headers
    method = request.method.upper()
    url = "/"
    body = ""
    client_ip = request.client.host if request.client else "127.0.0.1"
    headers_dict = dict(request.headers)

    if request.method == "POST":
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            try:
                json_data = await request.json()
                if isinstance(json_data, dict):
                    method = json_data.get("method", method).upper()
                    url = json_data.get("url", url)
                    body = json_data.get("body", body) or ""
                    client_ip = json_data.get("client_ip", client_ip)
                    if "headers" in json_data and isinstance(json_data["headers"], dict):
                        headers_dict.update(json_data["headers"])
            except Exception:
                pass
        else:
            try:
                raw_body = await request.body()
                body = raw_body.decode("utf-8", errors="ignore")
            except Exception:
                pass

    # If Nginx auth_request forwarded original request headers, prioritize them
    if "x-original-uri" in request.headers:
        url = request.headers["x-original-uri"]
    if "x-original-method" in request.headers:
        method = request.headers["x-original-method"].upper()
    if "x-real-ip" in request.headers:
        client_ip = request.headers["x-real-ip"]

    # Execute inspection
    result = decision_engine.inspect_request(
        method=method,
        url=url,
        body=body,
        headers=headers_dict,
        client_ip=client_ip
    )

    # Set response HTTP status code according to decision
    response.status_code = result["http_status"]
    if result["verdict"] == "REVIEW":
        response.headers["X-WAF-Warning"] = "Request flagged for security review"

    # Async logging to database
    log_security_event(
        request_id=request_id,
        client_ip=client_ip,
        method=method,
        url_path=result["parsed_metadata"]["path"],
        query=result["parsed_metadata"]["query"],
        body=result["parsed_metadata"]["body"],
        verdict=result["verdict"],
        risk_score=result["risk_score"],
        confidence=result["confidence"],
        attack_type=result["attack_type"],
        rule_matches=result["rule_evidence"]["matched_rules"],
        model_name="Ensemble(1D-CNN+XGBoost+Rules)",
        action_taken=result["action_taken"],
        latency_ms=result["latency_ms"]
    )

    return ScanResponse(
        request_id=request_id,
        timestamp=now_iso,
        verdict=result["verdict"],
        risk_score=result["risk_score"],
        confidence=result["confidence"],
        rule_evidence=RuleEvidence(**result["rule_evidence"]),
        ai_evidence=AIEvidence(**result["ai_evidence"]),
        reason=result["reason"],
        action_taken=result["action_taken"],
        latency_ms=result["latency_ms"],
        http_status=result["http_status"]
    )


@app.post("/predict", tags=["Inspection"])
def predict_raw_payload(payload: str):
    """Direct testing endpoint for security scanners."""
    if decision_engine is None:
        raise HTTPException(status_code=503, detail="WAF engine initializing")
    result = decision_engine.inspect_request(method="GET", url=payload, body="")
    return {
        "verdict": result["verdict"],
        "risk_score": result["risk_score"],
        "attack_type": result["attack_type"],
        "action": result["action_taken"],
        "latency_ms": result["latency_ms"]
    }


@app.get("/analytics", tags=["Dashboard"])
def get_analytics():
    """Aggregated security metrics for Streamlit SOC dashboard."""
    return get_analytics_summary()


@app.get("/events", tags=["Dashboard"])
def get_events(limit: int = 50):
    """Latest security audit events for Streamlit live monitoring."""
    return get_recent_events(limit=limit)


@app.get("/rules", tags=["Configuration"])
def get_active_rules():
    """Returns active rule specifications and thresholds."""
    if decision_engine is None:
        raise HTTPException(status_code=503, detail="WAF engine initializing")
    return {
        "ruleset_version": "1.0.0",
        "block_threshold": decision_engine.block_threshold,
        "review_threshold": decision_engine.review_threshold,
        "rule_count": len(decision_engine.rule_engine.rules),
        "rules": decision_engine.rule_engine.rules
    }


@app.post("/scan_llm", tags=["LLM Gateway"])
def scan_llm_prompt(prompt: str):
    """
    Next-Gen AI Gateway Protection:
    Scans user prompts for Prompt Injections, Jailbreaks, and System Prompt Exfiltration.
    """
    from src.llm_guard import LLMGuard
    guard = LLMGuard()
    return guard.scan_prompt(prompt)


@app.post("/feedback", tags=["Active Learning"])
def submit_feedback(payload: str, assigned_verdict: str, true_label: int, notes: str = "", analyst_id: str = "SOC_ANALYST"):
    """Records human-in-the-loop analyst feedback on reviewed requests."""
    from src.active_learning import ActiveLearningEngine
    al = ActiveLearningEngine()
    return al.submit_feedback(payload, assigned_verdict, true_label, notes, analyst_id)


@app.get("/feedback/stats", tags=["Active Learning"])
def get_feedback_statistics():
    """Returns active learning training pool metrics and pending recalibration counts."""
    from src.active_learning import ActiveLearningEngine
    al = ActiveLearningEngine()
    return al.get_feedback_statistics()


@app.post("/feedback/recalibrate", tags=["Active Learning"])
def trigger_adaptive_recalibration():
    """Triggers automated threshold recalibration based on accumulated SOC analyst feedback."""
    from src.active_learning import ActiveLearningEngine
    al = ActiveLearningEngine()
    b_th = decision_engine.block_threshold if decision_engine else 0.65
    r_th = decision_engine.review_threshold if decision_engine else 0.35
    res = al.trigger_adaptive_recalibration(b_th, r_th)
    if decision_engine and res.get("status") == "recalibrated":
        decision_engine.block_threshold = res["new_block_thresh"]
        decision_engine.review_threshold = res["new_review_thresh"]
    return res
