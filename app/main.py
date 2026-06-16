"""AquaGuard — FastAPI backend entrypoint.

Mounts static directories, configures CORS + rate limiting + optional
API-key authentication, and registers all route modules.
"""
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

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
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.middleware("http")
async def api_auth_middleware(request: Request, call_next):
    if API_AUTH_KEY:
        if request.url.path in ("/", "/health", "/docs", "/openapi.json"):
            return await call_next(request)
        auth = request.headers.get("X-API-Key", "")
        if auth != API_AUTH_KEY:
            return JSONResponse(
                status_code=401,
                content={"detail": "Unauthorized — provide a valid X-API-Key header"},
            )
    return await call_next(request)


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
