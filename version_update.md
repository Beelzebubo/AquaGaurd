# PeakFlow Analytics — v1.01 Update

**Release date:** 2026-06-27

---

## Summary

v1.01 upgrades the cross-station flood prediction model with a richer feature set, improved training methodology, and a data-driven decision threshold. These changes significantly boost flood detection (recall) and overall balanced performance (F1 score).

---

## What's New

### 1. Lag & Momentum Features (7 → 12 input features)

The model now ingests five additional temporal features that give it short-term memory of recent conditions:

| Feature | Description | Why it helps |
|---------|-------------|--------------|
| `rain_3d` | 3-day rolling mean of rainfall | Captures short-duration rainfall build-up before a flood event |
| `rain_7d` | 7-day rolling mean of rainfall | Captures sustained monsoon saturation |
| `temp_3d` | 3-day rolling mean of temperature | Reflects warm-period snowmelt contributions |
| `flow_change` | Day-to-day percentage change in river discharge | Detects rapid flow escalations (flash-flood precursor) |
| `days_above_p90` | Consecutive days flow has stayed above the 90th percentile | Tracks prolonged high-flow episodes that often precede flooding |

### 2. Class-Weighted Loss

The training loss now uses `pos_weight` proportional to the negative-to-positive sample ratio (`BCEWithLogitsLoss(pos_weight=...)`). This counteracts the ~15:1 no-flood/flood class imbalance, ensuring the model learns to prioritise flood detection rather than defaulting to "no flood".

### 3. Chronological Train/Validation Split

The train/validation split is now strictly chronological (first 80% of data for training, last 20% for validation) rather than stratified random. This prevents temporal data leakage and gives a realistic estimate of out-of-sample performance on *future* data.

### 4. Improved Model Architecture

The feed-forward network has been upgraded:

- **Input:** 12 features (up from 7)
- **Hidden layers:** 128 → 64 units (up from 64 → 64)
- **Regularisation:** BatchNorm1d + Dropout(0.2) on each hidden layer
- **Parameters:** ~10K (up from ~4.7K)

BatchNorm stabilises training and Dropout reduces overfitting on the dominant no-flood class.

### 5. Optimal Decision Threshold (`optimal_threshold.json`)

A post-training threshold sweep searches the probability range [0.15, 0.74] in steps of 0.01 and selects the cutoff that maximises F1. The resulting threshold is saved to `app/models/optimal_threshold.json` and loaded at inference time, replacing the previous hardcoded 0.65/0.35 bands.

### 6. New Artefact: `optimal_threshold.json`

Alongside the existing model artefacts, the retrain script now also writes:

```
app/models/optimal_threshold.json   # { "optimal_threshold": <float> }
```

The inference service (`cross_station_service.py`) reads this file on startup and uses it to set risk-level decision boundaries dynamically.

---

## Updated Files

| File | Change |
|------|--------|
| `scripts/retrain_cross_station.py` | Lag features, chronological split, class-weighted loss, BatchNorm/Dropout architecture, threshold sweep, new artefact output |
| `scripts/evaluate.py` | Aligned 12-feature architecture and lag feature computation, threshold sweep enabled by default |
| `app/services/cross_station_service.py` | 12-feature model, lag feature defaults for single-point inference, dynamic threshold from `optimal_threshold.json` |
| `version_update.md` | This file |

---

## How to Retrain

```bash
cd Hackathon-Final1
python scripts/retrain_cross_station.py
```

This regenerates all model artefacts in `app/models/` (weights, scaler, feature list, station stats, optimal threshold, eval metrics). Restart the backend to pick up the new model.

---

## How to Evaluate

```bash
python scripts/evaluate.py              # full report with threshold sweep
python scripts/evaluate.py --json       # machine-readable JSON output
python scripts/evaluate.py --show-baseline   # include persistence baseline
```

The evaluation script now always reports both the default (0.50) and optimal-threshold metrics side by side.

---

## Compatibility Notes

- The model weights file (`cross_station_model.pth`) is **not backward-compatible** with the old 7-feature architecture. You must retrain after updating.
- The backend will fail fast with a clear error if old weights are loaded with the new service code (PyTorch `load_state_dict` strict mode).
- The frontend heuristic engine (`frontend/lib/aquaguard-engine.ts`) is unchanged — it continues to serve as a deterministic fallback when the backend is unavailable.
