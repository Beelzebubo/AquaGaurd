"""Pydantic request schemas for all AquaGuard API endpoints.

Validates input, provides type coercion, rejects unknown fields,
and produces accurate OpenAPI documentation for /docs.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class PredictRequest(BaseModel):
    station_id: Optional[str] = None
    temperature: Optional[float] = None
    rainfall: Optional[float] = None
    humidity: Optional[float] = None
    river_flow: Optional[float] = None
    rolling_flow: Optional[float] = None
    live_weather: bool = False

    model_config = ConfigDict(extra="forbid")


class ComplianceRequest(BaseModel):
    river_flow: Optional[float] = None
    current_flow: Optional[float] = None
    station_id: str = ""
    eco_threshold: Optional[float] = None

    model_config = ConfigDict(extra="forbid")


class AlertsRequest(BaseModel):
    rainfall: float = 0
    river_flow: float = 0
    rolling_flow: float = 0
    eco_threshold: Optional[float] = None

    model_config = ConfigDict(extra="forbid")


class AnalyticsRequest(BaseModel):
    rainfall: float = 0
    humidity: float = 50
    temperature: float = 20
    river_flow: float = Field(default=1.0, alias="riverFlow")
    station_id: str = Field(default="melamchi", alias="stationId")
    compliance_score: float = Field(default=80, alias="complianceScore")
    anomaly_detected: bool = Field(default=False, alias="anomalyDetected")
    head_height: Optional[float] = Field(default=None, alias="headHeight")

    model_config = ConfigDict(populate_by_name=True, extra="forbid")
