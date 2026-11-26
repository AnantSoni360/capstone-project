"""
Mock Protected Target Web Application ("ABC Shopping") (Phase 11)
Simulates an upstream web application isolated behind the AI-WAF gateway.
Maintains an append-only access log to verify zero-arrival of blocked attacks.
"""

from datetime import datetime, timezone
import pathlib
import threading
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse

TARGET_ACCESS_LOG = pathlib.Path(__file__).resolve().parent / "target_app_access.log"
_log_lock = threading.Lock()


def log_backend_arrival(method: str, url: str, body: str):
    """Appends received request to access log."""
    now_str = datetime.now(timezone.utc).isoformat()
    entry = f"[{now_str}] {method} {url} | BODY: {body}\n"
    with _log_lock:
        with open(TARGET_ACCESS_LOG, "a", encoding="utf-8") as f:
            f.write(entry)


target_app = FastAPI(
    title="ABC Shopping - Protected Backend Application",
    description="Upstream e-commerce store operating behind the AI WAF reverse proxy."
)


@target_app.get("/")
def home_page(request: Request):
    log_backend_arrival("GET", str(request.url), "")
    return HTMLResponse("<h1>Welcome to ABC Shopping!</h1><p>Your connection is secure and verified by AI-WAF.</p>")


@target_app.get("/tienda1/publico/pagar.jsp")
def tienda_checkout(request: Request):
    log_backend_arrival("GET", str(request.url), "")
    return JSONResponse({"status": "checkout_success", "store": "tienda1"})


@target_app.get("/products")
def search_products(request: Request, category: str = "all", id: Optional[str] = None):
    log_backend_arrival("GET", str(request.url), f"category={category}&id={id}")
    return JSONResponse({
        "status": "success",
        "category": category,
        "results": [
            {"id": 1, "name": "Running Shoes", "price": 89.99},
            {"id": 2, "name": "Leather Boots", "price": 129.99}
        ]
    })


@target_app.post("/comment")
async def post_comment(request: Request):
    body = (await request.body()).decode("utf-8", errors="ignore")
    log_backend_arrival("POST", str(request.url), body)
    return JSONResponse({"status": "comment_posted", "message": "Thank you for your feedback!"})


@target_app.post("/login")
async def login(request: Request):
    body = (await request.body()).decode("utf-8", errors="ignore")
    log_backend_arrival("POST", str(request.url), body)
    return JSONResponse({"status": "authenticated", "user": "authorized_customer"})
