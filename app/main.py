"""PeakFlow Analytics — FastAPI backend entrypoint.

Mounts static directories, configures CORS, and registers all route modules.
"""
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.routes.prediction import router as prediction_router
from app.routes.compliance import router as compliance_router
from app.routes.analytics import router as analytics_router
from app.routes.alerts import router as alerts_router

app = FastAPI(
    title="PeakFlow Analytics",
    description="AI-Powered Hydropower ESG & IFC Compliance Monitoring",
    version="1.1.0",
)

# CORS: allow the React frontend (any origin in dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure audio output directory exists (created by voice_service.py at runtime)
os.makedirs("audio", exist_ok=True)
app.mount("/audio", StaticFiles(directory="audio"), name="audio")

# Register all route modules
app.include_router(prediction_router)
app.include_router(compliance_router)
app.include_router(alerts_router)
app.include_router(analytics_router)


@app.get("/")
def root():
    return {"message": "PeakFlow Analytics API Running"}


@app.get("/health")
def health():
    """Quick health-check endpoint used by frontend and monitoring."""
    return {"status": "ok", "version": "1.1.0"}
