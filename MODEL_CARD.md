# Model Card — PeakFlow Cross-Station Flood Model

## Model Overview

| Property               | Value                                                       |
| ---------------------- | ----------------------------------------------------------- |
| **Model type**         | Feed-forward neural network                                 |
| **Architecture**       | `Linear(7→64) → ReLU → Linear(64→64) → ReLU → Linear(64→1)` |
| **Parameters**         | ~4,737                                                      |
| **Training framework** | PyTorch 2.x                                                 |
| **Inputs**             | 7 features (see below)                                      |
| **Output**             | Flood probability (logit → sigmoid)                         |

---

## Input Features

| #   | Feature          | Description                         | Units    | Preprocessing         |
| --- | ---------------- | ----------------------------------- | -------- | --------------------- |
| 1   | `T2M`            | Temperature at 2m                   | °C       | Z-score (per-dataset) |
| 2   | `PRECTOTCORR`    | Corrected precipitation             | mm/day   | Z-score (per-dataset) |
| 3   | `RH2M`           | Relative humidity at 2m             | %        | Z-score (per-dataset) |
| 4   | `flow_zscore`    | (flow - station_mean) / station_std | unitless | Station-normalised    |
| 5   | `flow_ratio_eco` | flow / eco_threshold                | unitless | Station-normalised    |
| 6   | `flow_ratio_p95` | flow / station_95th_percentile      | unitless | Station-normalised    |
| 7   | `flow_spike`     | flow / 7-day rolling_mean           | unitless | Station-normalised    |

The last 4 features are **river-agnostic** — they normalise each station's
flow by its own historical statistics, so the model learns flood _patterns_
rather than memorising absolute discharge values. This is why the same
model works on both Melamchi (mean flow 0.5 m³/s) and Chisapani
(mean flow 1,300 m³/s).

---

## Training

| Property           | Value                               |
| ------------------ | ----------------------------------- |
| **Data**           | Melamchi + Chisapani (1979–2024)    |
| **Samples**        | 26,297 train / 6,575 validation     |
| **Split**          | Chronological 80/20 (past → future) |
| **Loss**           | BCEWithLogitsLoss                   |
| **Optimiser**      | Adam, lr=0.001                      |
| **Epochs**         | 300                                 |
| **Batch**          | Full-batch gradient descent         |
| **Normalisation**  | StandardScaler per feature          |
| **Regularisation** | None (small model, large data)      |

### Why chronological split?

Time-series models must be evaluated on **future data** — a random shuffle
would let the model peek at future patterns, inflating accuracy. We train
on the oldest 80% of dates and test on the most recent 20%.

---

## Intended Use

- **Primary:** Early-warning support for hydropower operators and basin
  authorities in Nepal.
- **Secondary:** Hydropower potential estimation, compliance monitoring,
  and ESG scoring.
- **Users:** Plant operators, DHM officials, infrastructure planners.

## Not Intended For

- ❌ **Official flood warnings** — this is a research tool, not a certified
  early-warning system.
- ❌ **Real-time life-safety decisions** — always consult DHM bulletins
  and local authorities.
- ❌ **Basins outside Nepal** — the model has been validated only on Nepal
  river regimes.

---

## Failure Modes & Mitigations

| Failure Mode                                  | Risk   | Mitigation                                            |
| --------------------------------------------- | ------ | ----------------------------------------------------- |
| Unseen extreme events (beyond training range) | Medium | Model output saturates; threshold recalibration helps |
| Station without historical data               | Medium | Fallback to eco-threshold-based estimated stats       |
| Climate non-stationarity (changing monsoon)   | Medium | Periodic retraining with new data                     |
| Sensor / gauge failure → bad discharge input  | Low    | Rolling-flow anomaly detection flags outliers         |
| Missing weather data (NASA POWER outage)      | Low    | Falls back to user-provided values or climatology     |

---

## Bias & Fairness

- The model was trained on **two stations** (Melamchi and Chisapani) and
  estimated for 8 others. Predictions for the 8 estimated stations may
  have higher uncertainty.
- Low-flow stations (eco_threshold >> natural flow, e.g. Melamchi) may
  behave differently from high-flow stations.

---

## License

MIT — see [`LICENSE`](./LICENSE).
