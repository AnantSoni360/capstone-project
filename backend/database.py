"""
WAF Security Audit Database & Sanitization Module (Phase 10)
Provides thread-safe SQLite persistence for security logs and dashboard analytics
with automatic sanitization of sensitive credentials (passwords, tokens, cookies).
"""

import json
import pathlib
import re
import sqlite3
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

DB_PATH = pathlib.Path(__file__).resolve().parent / "waf_audit.db"
_lock = threading.Lock()


def init_db(db_file: Optional[pathlib.Path] = None):
    """Initializes the SQLite audit database schema."""
    target_db = db_file or DB_PATH
    with _lock:
        conn = sqlite3.connect(str(target_db), check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id TEXT UNIQUE NOT NULL,
                timestamp TEXT NOT NULL,
                client_ip TEXT NOT NULL,
                method TEXT NOT NULL,
                url_path TEXT NOT NULL,
                query_sanitized TEXT,
                body_sanitized TEXT,
                verdict TEXT NOT NULL,
                risk_score REAL NOT NULL,
                confidence REAL NOT NULL,
                attack_type TEXT NOT NULL,
                rule_matches TEXT,
                model_name TEXT NOT NULL,
                action_taken TEXT NOT NULL,
                latency_ms REAL NOT NULL
            )
        """)
        conn.commit()
        conn.close()


def sanitize_sensitive_data(text: Optional[str]) -> str:
    """
    Sanitizes passwords, tokens, cookies, and credit cards from logs before database storage.
    """
    if not text or not isinstance(text, str):
        return ""

    sanitized = text
    # Mask passwords
    sanitized = re.sub(r"(password|pwd|pass|secret)=[^& \n]*", r"\1=[FILTERED]", sanitized, flags=re.IGNORECASE)
    # Mask session cookies
    sanitized = re.sub(r"(JSESSIONID|sessionid|PHPSESSID)=[^;& \n]*", r"\1=[FILTERED]", sanitized, flags=re.IGNORECASE)
    # Mask bearer tokens
    sanitized = re.sub(r"(bearer\s+)[a-zA-Z0-9\-_.]+", r"\1[FILTERED]", sanitized, flags=re.IGNORECASE)
    # Mask credit card numbers (15-16 consecutive digits)
    sanitized = re.sub(r"\b(?:\d{4}[ -]?){3}\d{4}\b", "[CC_FILTERED]", sanitized)

    return sanitized


def log_security_event(
    request_id: str,
    client_ip: str,
    method: str,
    url_path: str,
    query: str,
    body: str,
    verdict: str,
    risk_score: float,
    confidence: float,
    attack_type: str,
    rule_matches: List[Dict[str, Any]],
    model_name: str,
    action_taken: str,
    latency_ms: float,
    db_file: Optional[pathlib.Path] = None
):
    """Persists a sanitized security event to the audit database."""
    target_db = db_file or DB_PATH
    clean_query = sanitize_sensitive_data(query)
    clean_body = sanitize_sensitive_data(body)
    rules_json = json.dumps([r["id"] for r in rule_matches])
    now_iso = datetime.now(timezone.utc).isoformat()

    with _lock:
        conn = sqlite3.connect(str(target_db), check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO security_events (
                request_id, timestamp, client_ip, method, url_path,
                query_sanitized, body_sanitized, verdict, risk_score,
                confidence, attack_type, rule_matches, model_name,
                action_taken, latency_ms
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            request_id, now_iso, client_ip, method, url_path,
            clean_query, clean_body, verdict, risk_score,
            confidence, attack_type, rules_json, model_name,
            action_taken, latency_ms
        ))
        conn.commit()
        conn.close()


def get_analytics_summary(db_file: Optional[pathlib.Path] = None) -> Dict[str, Any]:
    """Computes aggregated traffic metrics for the SOC dashboard."""
    target_db = db_file or DB_PATH
    with _lock:
        conn = sqlite3.connect(str(target_db), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as total FROM security_events")
        total = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) as cnt FROM security_events WHERE verdict = 'ALLOW'")
        allowed = cursor.fetchone()["cnt"]

        cursor.execute("SELECT COUNT(*) as cnt FROM security_events WHERE verdict = 'BLOCK'")
        blocked = cursor.fetchone()["cnt"]

        cursor.execute("SELECT COUNT(*) as cnt FROM security_events WHERE verdict = 'REVIEW'")
        review = cursor.fetchone()["cnt"]

        cursor.execute("SELECT attack_type, COUNT(*) as cnt FROM security_events WHERE verdict != 'ALLOW' GROUP BY attack_type")
        attack_dist = {row["attack_type"]: row["cnt"] for row in cursor.fetchall()}

        cursor.execute("SELECT AVG(latency_ms) as avg_lat FROM security_events")
        avg_lat_row = cursor.fetchone()
        avg_latency = round(float(avg_lat_row["avg_lat"] or 0.0), 3)

        conn.close()

    return {
        "total_requests": total,
        "allowed_requests": allowed,
        "blocked_requests": blocked,
        "review_requests": review,
        "attack_distribution": attack_dist,
        "average_latency_ms": avg_latency
    }


def get_recent_events(limit: int = 50, db_file: Optional[pathlib.Path] = None) -> List[Dict[str, Any]]:
    """Retrieves the latest security events for dashboard streaming."""
    target_db = db_file or DB_PATH
    with _lock:
        conn = sqlite3.connect(str(target_db), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, request_id, timestamp, client_ip, method, url_path,
                   query_sanitized, verdict, risk_score, attack_type, action_taken, latency_ms
            FROM security_events
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
    return rows
