"""Cross-station flood prediction service.

Loads the retrained 12-feature model that generalises across rivers
via station-relative features (flow_zscore, flow_ratio_eco, …) plus
lag weather features and flow momentum signals.

v1.01 — adds BatchNorm/Dropout architecture, lag feature defaults,
and data-driven optimal decision threshold.
"""
import json
from pathlib import Path
from typing import Optional

import joblib
import numpy as np
import torch
import torch.nn as nn


# ── Model architecture (must match retrain_cross_station.py) ──────────


class CrossStationFloodModel(nn.Module):
    def __init__(self, input_size: int = 12):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_size, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 1),
        )

    def forward(self, x):
        return self.net(x)


# ── Paths ──────────────────────────────────────────────────────────────
BASE = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE / "models" / "cross_station_model.pth"
SCALER_PATH = BASE / "models" / "cross_station_scaler.pkl"
FEATURES_PATH = BASE / "models" / "cross_station_features.pkl"
STATS_PATH = BASE / "models" / "station_stats.json"
THRESHOLD_PATH = BASE / "models" / "optimal_threshold.json"


# ── Lazy loading ──────────────────────────────────────────────────────
_model: Optional[CrossStationFloodModel] = None
_scaler: Optional = None
_features: Optional[list[str]] = None
_station_stats: Optional[dict] = None
_optimal_threshold: float = 0.35


def _ensure_loaded():
    global _model, _scaler, _features, _station_stats, _optimal_threshold
    if _model is not None:
        return

    _model = CrossStationFloodModel()
    _model.load_state_dict(
        torch.load(MODEL_PATH, map_location="cpu", weights_only=True)
    )
    _model.eval()

    _scaler = joblib.load(SCALER_PATH)
    _features = joblib.load(FEATURES_PATH)

    with open(STATS_PATH) as f:
        _station_stats = json.load(f)

    if THRESHOLD_PATH.exists():
        with open(THRESHOLD_PATH) as f:
            _optimal_threshold = json.load(f).get("optimal_threshold", 0.35)
    else:
        _optimal_threshold = 0.35


def get_station_ids() -> list[str]:
    _ensure_loaded()
    return list(_station_stats.keys())


def predict_flood_risk(
    station_id: str,
    temperature: float,
    rainfall: float,
    humidity: float,
    river_flow: float,
    rolling_flow: Optional[float] = None,
) -> dict:
    """Predict flood risk for a specific station using the cross-station model.

    Args:
        station_id:   e.g. "chisapani", "melamchi"
        temperature:  °C
        rainfall:     mm (24h accumulated)
        humidity:     %
        river_flow:   m³/s (instantaneous)
        rolling_flow: m³/s (7-day rolling average). If None, computed via
                      a crude fallback (river_flow itself).

    Returns
        dict with keys: probability, risk_level, threshold_flow_m3s,
                        features_used
    """
    _ensure_loaded()

    if station_id not in _station_stats:
        raise ValueError(
            f"Unknown station '{station_id}'. "
            f"Known: {list(_station_stats.keys())}"
        )
    s = _station_stats[station_id]

    safe_std = max(s["std"], 1e-6)
    safe_eco = max(s["ecoThreshold"], 1e-6)
    safe_p95 = max(s["p95"], 1e-6)

    flow_zscore = (river_flow - s["mean"]) / safe_std
    flow_ratio_eco = river_flow / safe_eco
    flow_ratio_p95 = river_flow / safe_p95

    roll = rolling_flow if (rolling_flow and rolling_flow > 0) else river_flow
    flow_spike = river_flow / max(roll, 1e-6)

    # Lag feature defaults (no historical series at single-point inference)
    rain_3d = rainfall
    rain_7d = rainfall
    temp_3d = temperature
    flow_change = 0.0
    days_above_p90 = 0.0
    if river_flow > safe_p95 * 0.90:
        days_above_p90 = 1.0

    # Pack feature vector in the order the scaler expects
    raw = np.array(
        [
            [
                temperature,
                rainfall,
                humidity,
                flow_zscore,
                flow_ratio_eco,
                flow_ratio_p95,
                flow_spike,
                rain_3d,
                rain_7d,
                temp_3d,
                flow_change,
                days_above_p90,
            ]
        ]
    )

    scaled = _scaler.transform(raw)
    tensor = torch.tensor(scaled, dtype=torch.float32)

    with torch.no_grad():
        prob = float(torch.sigmoid(_model(tensor)).item())

    # Risk level bands using data-driven optimal threshold
    th = _optimal_threshold
    if prob >= th + 0.30:
        level = "HIGH"
    elif prob >= th:
        level = "MODERATE"
    else:
        level = "LOW"

    return {
        "probability": round(prob, 4),
        "risk_level": level,
        "threshold_flow_m3s": round(float(s["p95"]), 1),
        "threshold_eco_m3s": round(float(s["ecoThreshold"]), 1),
        "optimal_threshold": round(th, 4),
        "station_flow_stats": {
            "mean": round(float(s["mean"]), 1),
            "std": round(float(s["std"]), 1),
            "p50": round(float(s["p50"]), 1),
            "p95": round(float(s["p95"]), 1),
        },
        "features_used": _features,
    }
