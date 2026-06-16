# PeakFlow Analytics — Data Sources

## Melamchi River

| File                              | Source                 | Rows   | Date Range       | Columns                                         |
| --------------------------------- | ---------------------- | ------ | ---------------- | ----------------------------------------------- |
| `Datasets/melamchi_waterflow.csv` | Melamchi station gauge | 31,413 | 1940-01 to ~2025 | Dates, Values (m³/s)                            |
| `Datasets/melamchi_weather.csv`   | NASA POWER (grid)      | 16,436 | 1981-01 to ~2025 | YEAR, DOY, T2M (°C), PRECTOTCORR (mm), RH2M (%) |

**Processing notes:**

- Merged on `Dates` column (constructed in weather data as YEAR + DOY).
- Rows with -999 (NASA fill) in weather data are dropped.
- `floodOccurrence` label: 1 when Waterflow > 95th percentile.

## Chisapani River (Karnali)

| File                                                | Source                  | Rows   | Date Range               | Columns                        |
| --------------------------------------------------- | ----------------------- | ------ | ------------------------ | ------------------------------ |
| `chisapani_yearly_csv/chisapani_master_cleaned.csv` | Chisapani station gauge | 17,167 | 1979-01-02 to 2025-12-31 | datetime, discharge_cms (m³/s) |

## Hydropower Generalization

Seasonal flow estimates for all 10 monitoring stations are derived from:

- **Melamchi & Chisapani** — actual historical seasonal means computed from the 47-year daily discharge CSVs (melamchi\_waterflow.csv, chisapani\_ratedischarge.csv).
- **Other 8 stations** — estimated using the station's `ecoThreshold` × seasonal multipliers derived from Chisapani's natural river flow pattern (winter: 1.15×, spring: 1.0×, monsoon: 5.0×, autumn: 2.0×).

The hydropower page also fetches live NASA POWER weather (rainfall, temperature, humidity) for any station's coordinates to provide a real-time comparison against the historical seasonal baselines.

## License / Attribution

- **Melamchi waterflow**: Nepal Department of Hydrology and Meteorology (DHM) station data.
- **Chisapani discharge**: Karnali River station gauge, DHM / GWS data.
- **Weather data**: NASA POWER (Prediction Of Worldwide Energy Resources) — meteorological reanalysis. _Does not provide direct river discharge._
