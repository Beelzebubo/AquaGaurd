"""AquaGuard FastAPI backend entrypoint.

Mounts static directories, configures CORS + rate limiting + optional
API-key authentication, and registers all route modules.
"""
import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import API_AUTH_KEY, ALLOWED_ORIGINS
from app.routes.prediction import router as prediction_router
from app.routes.compliance import router as compliance_router
from app.routes.analytics import router as analytics_router
from app.routes.alerts import router as alerts_router

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="AquaGuard",
    description="AI-Powered Hydropower ESG & IFC Compliance Monitoring",
    version="1.2.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS ─────────────────────────────────────────────────────────────
origins = [
    o.strip()
    for o in ALLOWED_ORIGINS.split(",")
    if o.strip()
]
if not origins:
    origins = ["http://localhost:5173", "http://localhost:8080"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST", "OPTIONS", "HEAD"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "X-API-Key",
        "Accept",
        "Origin",
    ],
    allow_credentials=True,
)

# ── Security headers ─────────────────────────────────────────────────

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )
        response.headers["Server"] = "AquaGuard"
        return response

app.add_middleware(SecurityHeadersMiddleware)


# ── Payload size limit (JSON bodies only) ────────────────────────────

MAX_PAYLOAD_BYTES = 1024 * 100  # 100 kB


@app.middleware("http")
async def limit_payload_size(request: Request, call_next):
    if request.method in ("POST", "PUT", "PATCH"):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_PAYLOAD_BYTES:
            return JSONResponse(
                status_code=413,
                content={"detail": "Request body too large"},
            )
    return await call_next(request)


# ── Request logging ──────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("aquaguard")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    if request.url.path not in ("/", "/health"):
        logger.info(
            "%s %s -> %s",
            request.method,
            request.url.path,
            response.status_code,
        )
    return response


# ── API-key authentication ───────────────────────────────────────────

if not API_AUTH_KEY:
    logger.warning(
        "API_AUTH_KEY is not set — all endpoints are UNPROTECTED. "
        "Set API_AUTH_KEY in your environment to enable authentication."
    )


@app.middleware("http")
async def api_auth_middleware(request: Request, call_next):
    if API_AUTH_KEY:
        if request.url.path in ("/", "/health"):
            return await call_next(request)
        auth = request.headers.get("X-API-Key", "")
        if auth != API_AUTH_KEY:
            return JSONResponse(
                status_code=401,
                content={"detail": "Unauthorized — provide a valid X-API-Key header"},
            )
    return await call_next(request)


# ── Routes ───────────────────────────────────────────────────────────

app.include_router(prediction_router)
app.include_router(compliance_router)
app.include_router(alerts_router)
app.include_router(analytics_router)


@app.get("/")
def root():
    return {"message": "AquaGuard API Running"}


@app.get("/health")
def health():
    return {"status": "ok", "version": "1.2.0"}
