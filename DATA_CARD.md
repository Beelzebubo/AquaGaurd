# Data Card

## Overview

This project uses two types of data: **historical river discharge** (from
station gauge records) and **historical weather / climate** data (from
NASA POWER reanalysis). The combination is used to train a cross-station
flood-risk model.

---

## Datasets

### 1. Melamchi River — Weather (`Datasets/melamchi_weather.csv`)

| Field         | Description              | Units  |
| ------------- | ------------------------ | ------ |
| `YEAR`        | Calendar year            |        |
| `DOY`         | Day of year              | 1–366  |
| `RH2M`        | Relative humidity at 2 m | %      |
| `PRECTOTCORR` | Corrected precipitation  | mm/day |
| `T2M`         | Temperature at 2 m       | °C     |

- **Source:** NASA POWER reanalysis (point extracted for Melamchi gauge
  coordinates)
- **Date range:** 1981-01-01 – 2024-12-31
- **Rows:** 16,437
- **Missing values:** None (reanalysis interpolates)

### 2. Melamchi River — Discharge (`Datasets/melamchi_waterflow.csv`)

| Field    | Description       | Units |
| -------- | ----------------- | ----- |
| `Dates`  | Timestamp (daily) |       |
| `Values` | River discharge   | m³/s  |

- **Source:** Nepal Department of Hydrology and Meteorology (DHM) gauge
- **Date range:** 1940-01-01 – 2024-12-31
- **Rows:** 31,414
- **Missing values:** sporadic gaps before 1981
- **Note:** Only the 1981–2024 overlap with weather data is used for
  training (~16,400 rows).

### 3. Chisapani (Karnali) — Weather (`Datasets/chisepani_weather.csv`)

Identical schema to `melamchi_weather.csv`.

- **Source:** NASA POWER reanalysis
- **Date range:** 1981-01-01 – 2024-12-31
- **Rows:** 16,437

### 4. Chisapani (Karnali) — Discharge (`Datasets/chisapani_ratedischarge.csv`)

| Field           | Description     | Units |
| --------------- | --------------- | ----- |
| `datetime`      | Date            |       |
| `discharge_cms` | River discharge | m³/s  |

- **Source:** Nepal DHM gauge (Karnali River at Chisapani)
- **Date range:** 1979-01-02 – 2026-01-01
- **Rows:** 17,168
- **Note:** This is the longest continuous record in the repository
  (~47 years).

### 5. Chisapani — Cleaned Master (`chisapani_yearly_csv/` directory)

Pre-computed yearly aggregated CSVs for trend analysis.

- **Source:** Aggregated from the daily discharge CSV

---

## Combined Training Dataset

| Property           | Value                                                                                        |
| ------------------ | -------------------------------------------------------------------------------------------- |
| Stations           | Melamchi + Chisapani                                                                         |
| Rows (after merge) | ~32,860                                                                                      |
| Date range         | 1981 – 2024                                                                                  |
| Features           | 7 (Temperature, Rainfall, Humidity, flow_zscore, flow_ratio_eco, flow_ratio_p95, flow_spike) |
| Target             | `floodLabel` (1 if discharge > station 95th percentile, else 0)                              |
| Split              | Chronological 80/20 (train on past, test on future)                                          |

---

## Live Data (NASA POWER)

The `fetch_nasa_weather.py` script and the `/predict` endpoint with
`live_weather: true` fetch real-time data from:

- **NASA POWER API** — `https://power.larc.nasa.gov/api/temporal/daily/point`
- **Parameters:** PRECTOTCORR, T2M, RH2M
- **Coordinates:** Per-station lat/lng from `app/data/stations.py`
- **License:** Open, free. No API key required.

---

## Known Limitations

- Only two stations have CSV data for training (Melamchi, Chisapani).
- The other 8 stations use estimated flow statistics based on eco-threshold
  relationships.
- Weather data is reanalysis (model-hindcast), not direct sensor readings.
- Discharge records may have undocumented gaps or rating-curve changes.
