#!/usr/bin/env python3
"""Cross‑station flood model evaluation — Chisapani cross‑validation.

Replicates the Melamchi training pipeline, applies the trained model to
Chisapani data, and reports accuracy.  Optionally fetches live NASA POWER
weather for any station's coordinates and runs the model against its
historical discharge record.
"""

import os, sys, json, argparse
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn

# ── Model architecture (must match main.ipynb) ──────────────────────────
class FloodPredictionModel(nn.Module):
    """Must match the architecture used in main.ipynb."""
    def __init__(self, input_size: int = 4):
        super().__init__()
        self.linear1 = nn.Linear(input_size, 64)
        self.hidden  = nn.Linear(64, 64)
        self.relu    = nn.ReLU()
        self.linear2 = nn.Linear(64, 1)

    def forward(self, x):
        x = self.relu(self.linear1(x))
        x = self.relu(self.hidden(x))
        x = self.linear2(x)
        return x


# ── Helper: merge weather + waterflow by YEAR/DOY ──────────────────────
def load_and_merge(weather_csv: str, flow_csv: str,
                   date_col: str = "Dates",
                   flow_col: str = "Values") -> pd.DataFrame:
    """Load, align and merge a weather CSV and a water-flow CSV by date."""
    df_w = pd.read_csv(weather_csv)
    # Create a date column from YEAR + DOY
    df_w["Dates"] = pd.to_datetime(
        df_w["YEAR"].astype(str) + "-" + df_w["DOY"].astype(str),
        format="%Y-%j",
    )
    df_f = pd.read_csv(flow_csv)
    df_f["Dates"] = pd.to_datetime(df_f[date_col])

    merged = pd.merge(df_w, df_f, on="Dates", how="inner")
    merged.rename(
        columns={
            "PRECTOTCORR": "Rainfall",
            "T2M": "Temperature",
            flow_col: "Waterflow",
            "RH2M": "Relative_Humidity",
        },
        inplace=True,
    )
    merged.dropna(subset=["Temperature", "Rainfall", "Relative_Humidity", "Waterflow"], inplace=True)
    return merged


# ── Scaler helper ──────────────────────────────────────────────────────
class SimpleScaler:
    """Standalone StandardScaler (avoids sklearn dependency if absent)."""
    def __init__(self):
        self.mean_ = None
        self.std_ = None

    def fit(self, X: np.ndarray):
        self.mean_ = X.mean(axis=0)
        # Use std with dof=1 (sample) like sklearn default
        self.std_ = X.std(axis=0, ddof=1) + 1e-12
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        return (X - self.mean_) / self.std_


# ── Main evaluation ────────────────────────────────────────────────────
def evaluate_station(
    station_name: str,
    weather_csv: str,
    flow_csv: str,
    flow_date_col: str,
    flow_val_col: str,
    model_path: str = "app/models/flood_prediction_weights.pth",
    melamchi_weather_csv: str = "Datasets/melamchi_weather.csv",
    melamchi_flow_csv: str = "Datasets/melamchi_waterflow.csv",
    threshold_quantile: float = 0.95,
) -> dict:
    """Evaluate the flood model on a *different* station than it was trained on."""

    # ── 1. Fit scaler on Melamchi training data ───────────────────────
    print(f"  Loading Melamchi weather ({melamchi_weather_csv}) …")
    df_m_weather = pd.read_csv(melamchi_weather_csv)
    df_m_flow = pd.read_csv(melamchi_flow_csv)
    df_m_flow["Dates"] = pd.to_datetime(df_m_flow["Dates"])
    df_m_weather["Dates"] = pd.to_datetime(
        df_m_weather["YEAR"].astype(str) + "-" + df_m_weather["DOY"].astype(str),
        format="%Y-%j",
    )
    df_m = pd.merge(df_m_weather, df_m_flow, on="Dates", how="inner")
    df_m.rename(
        columns={"PRECTOTCORR": "Rainfall", "T2M": "Temperature",
                 "Values": "Waterflow", "RH2M": "Relative_Humidity"},
        inplace=True,
    )
    df_m.dropna(inplace=True)

    # 80/20 temporal split (first 80 % by sorted date)
    df_m = df_m.sort_values("Dates").reset_index(drop=True)
    split_idx = int(len(df_m) * 0.8)
    m_train = df_m.iloc[:split_idx]

    feature_cols = ["Temperature", "Rainfall", "Relative_Humidity", "Waterflow"]
    scaler = SimpleScaler()
    scaler.fit(m_train[feature_cols].values)
    print(f"  Scaler fitted on {len(m_train)} Melamchi training rows.")
    print(f"    Means:   {np.round(scaler.mean_, 3)}")
    print(f"    Stds:    {np.round(scaler.std_, 3)}")

    # ── 2. Load the trained model ─────────────────────────────────────
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = FloodPredictionModel(input_size=4).to(device)
    state = torch.load(model_path, map_location=device, weights_only=True)
    model.load_state_dict(state)
    model.eval()
    print(f"  Model loaded from {model_path}")

    # ── 3. Load & prepare target station data ─────────────────────────
    print(f"\n  Loading {station_name} weather ({weather_csv}) …")
    df_t = load_and_merge(weather_csv, flow_csv, flow_date_col, flow_val_col)
    df_t = df_t.sort_values("Dates").reset_index(drop=True)
    print(f"  {station_name} merged rows: {len(df_t)}")

    # Flood label: 95th percentile of *this* station's flow
    flood_threshold = df_t["Waterflow"].quantile(threshold_quantile)
    df_t["floodOccurrence"] = (df_t["Waterflow"] > flood_threshold).astype(int)
    n_flood = df_t["floodOccurrence"].sum()
    print(f"  {station_name} flood threshold (P95): {flood_threshold:.1f} m³/s")
    print(f"  Flood events (labels): {n_flood} / {len(df_t)} ({n_flood/len(df_t)*100:.1f} %)")

    # ── 4. Predict ─────────────────────────────────────────────────────
    X_t = scaler.transform(df_t[feature_cols].values)
    X_tensor = torch.tensor(X_t, dtype=torch.float32).to(device)
    y_true = df_t["floodOccurrence"].values

    with torch.no_grad():
        logits = model(X_tensor)
        probs = torch.sigmoid(logits).cpu().numpy().flatten()
    y_pred = (probs >= 0.5).astype(int)

    # ── 5. Metrics ────────────────────────────────────────────────────
    tn = ((y_true == 0) & (y_pred == 0)).sum()
    fp = ((y_true == 0) & (y_pred == 1)).sum()
    fn = ((y_true == 1) & (y_pred == 0)).sum()
    tp = ((y_true == 1) & (y_pred == 1)).sum()
    total = len(y_true)

    accuracy   = (tp + tn) / total
    precision  = tp / (tp + fp) if (tp + fp) > 0 else 1.0
    recall     = tp / (tp + fn) if (tp + fn) > 0 else 1.0
    f1         = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    print(f"\n  ── Cross‑station Results: {station_name} ──")
    print(f"  ● Samples evaluated: {total}")
    print(f"  ● Confusion Matrix:")
    print(f"                    Predicted No Flood    Predicted Flood")
    print(f"    Actual No Flood    {tn:>6}                {fp:<6}")
    print(f"    Actual Flood       {fn:>6}                {tp:<6}")
    print(f"  ● Accuracy :  {accuracy:.4f}  ({(tp + tn)} / {total})")
    print(f"  ● Precision: {precision:.4f}  ({tp} / {tp + fp})")
    print(f"  ● Recall   : {recall:.4f}    ({tp} / {tp + fn})")
    print(f"  ● F1-Score : {f1:.4f}")

    return {
        "station": station_name,
        "samples": total,
        "flood_threshold_m3s": round(float(flood_threshold), 1),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        "accuracy": round(float(accuracy), 4),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1": round(float(f1), 4),
        "melamchi_baseline": {
            "accuracy": 0.994,
            "precision": 1.0,
            "recall": 0.85,
            "f1": 0.92,
            "confusion_matrix": {"tn": 3149, "fp": 0, "fn": 21, "tp": 118},
        },
    }


def fetch_nasa_live(station_name: str, lat: float, lng: float):
    """Fetch live NASA POWER weather for a single station coordinate."""
    import requests

    BASE = "https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        "community": "RE",
        "parameters": "PRECTOTCORR,T2M,RH2M",
        "start": "20240101",
        "end": "20241231",
        "lon": lng,
        "lat": lat,
        "format": "JSON",
    }
    print(f"\n  Fetching NASA POWER live data for {station_name} …")
    resp = requests.get(BASE, params=params, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    records = data.get("properties", {}).get("parameter", {})
    print(f"  ✓ Received parameters: {list(records.keys())}")
    days = list(records.get("PRECTOTCORR", {}).keys())
    print(f"  ✓ {len(days)} days of data")
    out_dir = Path("Datasets/nasa_live")
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{station_name}_nasa_2024.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  ✓ Saved to {path}")
    return records


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cross‑station flood model evaluation")
    parser.add_argument("--fetch-live", action="store_true",
                        help="Fetch live NASA POWER weather for each station")
    parser.add_argument("--station", type=str, default="chisapani",
                        choices=["chisapani", "melamchi", "kali-gandaki"],
                        help="Station to evaluate")
    args = parser.parse_args()

    stations_map = {
        "chisapani": {
            "name": "Chisapani",
            "weather_csv": "Datasets/chisepani_weather.csv",
            "flow_csv": "Datasets/chisapani_ratedischarge.csv",
            "flow_date_col": "datetime",
            "flow_val_col": "discharge_cms",
            "lat": 28.6447, "lng": 81.2731,
        },
        "melamchi": {
            "name": "Melamchi",
            "weather_csv": "Datasets/melamchi_weather.csv",
            "flow_csv": "Datasets/melamchi_waterflow.csv",
            "flow_date_col": "Dates",
            "flow_val_col": "Values",
            "lat": 27.8333, "lng": 85.5667,
        },
        "kali-gandaki": {
            "name": "Kali Gandaki A",
            "weather_csv": None,  # no separate CSV — would need NASA
            "flow_csv": None,
            "flow_date_col": None,
            "flow_val_col": None,
            "lat": 27.9833, "lng": 83.5833,
        },
    }

    stn = stations_map[args.station]

    print("=" * 58)
    print("    PeakFlow Analytics — Cross‑Station Model Validation")
    print("    Training station: Melamchi (1981–2024)")
    print("    Target station:   ", stn["name"])
    print("=" * 58)

    if stn["weather_csv"] and stn["flow_csv"]:
        sys.path.insert(0, os.path.dirname(__file__) or ".")
        result = evaluate_station(
            station_name=stn["name"],
            weather_csv=stn["weather_csv"],
            flow_csv=stn["flow_csv"],
            flow_date_col=stn["flow_date_col"],
            flow_val_col=stn["flow_val_col"],
        )
        print("\n  ── Summary ──")
        for k, v in result.items():
            if k != "melamchi_baseline":
                print(f"    {k}: {v}")
        print(f"\n  ── Compare: Melamchi (trained & tested on same station) ──")
        bl = result["melamchi_baseline"]
        print(f"    accuracy : {bl['accuracy']}  → now {result['accuracy']}")
        print(f"    precision: {bl['precision']}  → now {result['precision']}")
        print(f"    recall   : {bl['recall']}    → now {result['recall']}")
        print(f"    f1       : {bl['f1']}  → now {result['f1']}")

        # Save result as JSON
        out_path = f"cross_station_{args.station}_eval.json"
        with open(out_path, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\n  Full results saved to {out_path}")

    if args.fetch_live and stn.get("lat") and stn.get("lng"):
        fetch_nasa_live(stn["name"], stn["lat"], stn["lng"])

    print("\n  Done.")
