"""
FastAPI Request and Response Pydantic Schemas (Phase 10)
Defines standardized data models for WAF inspection, security events, and analytics.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ScanRequest(BaseModel):
    """Incoming HTTP request payload representation for WAF inspection."""
    method: str = Field(default="GET", description="HTTP Method (GET, POST, PUT, DELETE, etc.)")
    url: str = Field(..., description="Full URL or relative URI with query string")
    body: Optional[str] = Field(default="", description="Request body payload for POST/PUT")
    headers: Optional[Dict[str, str]] = Field(default_factory=dict, description="HTTP request headers")
    client_ip: Optional[str] = Field(default="127.0.0.1", description="Client IP address")


class RuleMatchItem(BaseModel):
    id: str
    name: str
    category: str
    weight: float
    matched_substring: str


class RuleEvidence(BaseModel):
    match_count: int
    matched_rules: List[RuleMatchItem]
    rule_score: float


class AIEvidence(BaseModel):
    primary_model: str
    attack_probability: float
    auxiliary_model: Optional[str] = None
    auxiliary_probability: Optional[float] = None


class ScanResponse(BaseModel):
    """Standardized decision output returned by the WAF engine."""
    request_id: str
    timestamp: str
    verdict: str = Field(..., description="ALLOW, BLOCK, or REVIEW")
    risk_score: float
    confidence: float
    rule_evidence: RuleEvidence
    ai_evidence: AIEvidence
    reason: str
    action_taken: str = Field(..., description="FORWARD_UPSTREAM, REJECT_403, or QUARANTINE_REVIEW")
    latency_ms: float
    http_status: int


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    models_loaded: bool
    active_models: List[str]
    rule_count: int
    uptime_seconds: float


class SecurityEventRecord(BaseModel):
    id: int
    request_id: str
    timestamp: str
    client_ip: str
    method: str
    url_path: str
    verdict: str
    risk_score: float
    attack_type: str
    action_taken: str
    latency_ms: float
