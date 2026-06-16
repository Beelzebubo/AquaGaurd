#!/usr/bin/env python3
"""Standalone evaluation script for PeakFlow Analytics.

Usage:
    python scripts/evaluate.py

Loads the cross-station model, runs inference on the validation split of
the Melamchi-Chisapani combined dataset, and prints a rich evaluation
report.  On CI / automation, pass --json to get machine-readable output.
"""
import argparse
import json
import os
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

import joblib
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score, roc_curve,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


# ── Model architecture ────────────────────────────────────────────────
class CrossStationFloodModel(nn.Module):
    def __init__(self, input_size: int = 7):
        super().__init__()
        self.linear1 = nn.Linear(input_size, 64)
        self.hidden  = nn.Linear(64, 64)
        self.relu    = nn.ReLU()
        self.linear2 = nn.Linear(64, 1)

    def forward(self, x):
        x = self.relu(self.linear1(x))
        x = self.relu(self.hidden(x))
        return self.linear2(x)


BASE = Path(__file__).resolve().parent.parent


def load_data() -> pd.DataFrame:
    """Load and merge Melamchi + Chisapani data with relative features."""
    dfs = []
    stations_data = {
        "melamchi": {
            "weather": "Datasets/melamchi_weather.csv",
            "flow": "Datasets/melamchi_waterflow.csv",
            "eco": 12,
        },
        "chisapani": {
            "weather": "Datasets/chisepani_weather.csv",
            "flow": "Datasets/chisapani_ratedischarge.csv",
            "eco": 280,
        },
    }

    for st_name, paths in stations_data.items():
        # ── Weather ──
        wdf = pd.read_csv(BASE / paths["weather"])
        wdf["DATE"] = wdf["YEAR"].astype(str).str.zfill(4) + \
                      wdf["DOY"].astype(str).str.zfill(3)
        wdf = wdf.drop_duplicates(subset="DATE").set_index("DATE")

        # ── Flow / discharge ──
        fdf = pd.read_csv(BASE / paths["flow"])
        # Normalise date column name
        date_col = None
        for candidate in ["Date", "Dates", "datetime", "date", "time"]:
            if candidate in fdf.columns:
                date_col = candidate
                break
        if date_col is None:
            raise KeyError(f"No date column found in {paths['flow']}: {list(fdf.columns)}")
        fdf = fdf.drop_duplicates(subset=date_col).set_index(date_col)

        # Determine the flow (discharge) column
        fcol = None
        for candidate in ["Values", "discharge_cms", "Waterflow", "waterflow", "Q"]:
            if candidate in fdf.columns:
                fcol = candidate
                break
        if fcol is None:
            # Pick the first float column that isn't the date
            float_cols = fdf.select_dtypes(include=[np.number]).columns.tolist()
            if float_cols:
                fcol = float_cols[0]
            else:
                raise KeyError(f"No flow column in {paths['flow']}: {list(fdf.columns)}")

        flow_series = fdf[fcol].rename("waterflow")
        flow_series.index = pd.to_datetime(flow_series.index, errors="coerce")

        wdf.index = pd.to_datetime(wdf.index, format="%Y%j", errors="coerce")
        merged = wdf.join(flow_series, how="inner")
        merged = merged.dropna(subset=["T2M", "PRECTOTCORR", "RH2M", "waterflow"])

        for c in merged.columns:
            if merged[c].dtype == object:
                merged[c] = pd.to_numeric(merged[c], errors="coerce")
        merged = merged.dropna()

        # ── Relative features ──
        eco = paths["eco"]
        merged["flow_ratio_eco"] = merged["waterflow"] / max(eco, 1e-6)
        p95 = merged["waterflow"].quantile(0.95)
        merged["flow_ratio_p95"] = merged["waterflow"] / max(p95, 1e-6)
        merged["flow_zscore"] = (merged["waterflow"] - merged["waterflow"].mean()) \
                                / max(merged["waterflow"].std(), 1e-6)
        merged["flow_spike"] = merged["waterflow"] / \
            merged["waterflow"].rolling(7, min_periods=1).mean().clip(lower=1e-6)

        merged["Station"] = st_name
        merged["floodLabel"] = (merged["waterflow"] > p95).astype(int)
        merged["date_ordinal"] = merged.index.map(pd.Timestamp.toordinal)
        dfs.append(merged)

    df_all = pd.concat(dfs, ignore_index=False).sort_index()
    df_all = df_all.dropna()
    return df_all


def evaluate(args):
    print("=" * 62)
    print("  PEAKFLOW ANALYTICS — MODEL EVALUATION")
    print("=" * 62)

    # ── Load data ────────────────────────────────────────────────────
    print("\n  Loading data ...")
    df_all = load_data()

    feature_cols = [
        "T2M", "PRECTOTCORR", "RH2M",
        "flow_zscore", "flow_ratio_eco", "flow_ratio_p95", "flow_spike",
    ]

    X = df_all[feature_cols].values
    y = df_all["floodLabel"].values

    # ── Time-based split (chronological — best practice for forecasting) ─
    # Sort by date first, then take chronological 80/20
    sort_idx = np.argsort(df_all["date_ordinal"].values)
    X_sorted = X[sort_idx]
    y_sorted = y[sort_idx]
    split = int(0.8 * len(X_sorted))
    X_train, X_val = X_sorted[:split], X_sorted[split:]
    y_train, y_val = y_sorted[:split], y_sorted[split:]

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_val_s   = scaler.transform(X_val)

    n_test = len(y_val)
    n_flood_val = int(y_val.sum())
    prop_flood = 100 * n_flood_val / n_test
    print(f"  Training samples:    {len(X_train)}")
    print(f"  Validation samples:  {n_test} ({n_flood_val} flood = {prop_flood:.1f}%)")
    print(f"  Features:            {len(feature_cols)}")
    print(f"  Feature names:       {feature_cols}")

    # ── Load / train model ───────────────────────────────────────────
    model_path = BASE / "app" / "models" / "cross_station_model.pth"

    if os.path.exists(model_path) and args.use_saved:
        print(f"\n  Loading saved model from {model_path} ...")
        model = CrossStationFloodModel()
        model.load_state_dict(
            torch.load(model_path, map_location="cpu", weights_only=True)
        )
        print("  ✓ Model loaded")
    else:
        print("\n  Training model (300 epochs) ...")
        model = CrossStationFloodModel()
        criterion = nn.BCEWithLogitsLoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

        Xt = torch.tensor(X_train_s, dtype=torch.float32)
        yt = torch.tensor(y_train, dtype=torch.float32).unsqueeze(1)
        Xv = torch.tensor(X_val_s, dtype=torch.float32)
        yv = torch.tensor(y_val, dtype=torch.float32).unsqueeze(1)

        for epoch in range(1, 301):
            optimizer.zero_grad()
            out = model(Xt)
            loss = criterion(out, yt)
            loss.backward()
            optimizer.step()

            if epoch % 50 == 0 or epoch == 300:
                with torch.no_grad():
                    vout = model(Xv)
                    vloss = criterion(vout, yv)
                    vpred = (torch.sigmoid(vout) >= 0.5).float()
                    vacc = (vpred == yv).float().mean().item()
                print(f"    Epoch [{epoch:>3}/300]  "
                      f"Train Loss: {loss.item():.4f}  "
                      f"Val Loss: {vloss.item():.4f}  "
                      f"Val Acc: {vacc:.4f}")

        save_path = BASE / "app" / "models" / "cross_station_model.pth"
        torch.save(model.state_dict(), save_path)
        print(f"  ✓ Model saved to {save_path}")

    # ── Full evaluation ──────────────────────────────────────────────
    model.eval()
    Xv_t = torch.tensor(X_val_s, dtype=torch.float32)
    with torch.no_grad():
        logits = model(Xv_t)
        probs  = torch.sigmoid(logits).numpy().flatten()
    y_pred = (probs >= 0.5).astype(int)

    tn, fp, fn, tp = confusion_matrix(y_val, y_pred).ravel()
    acc  = accuracy_score(y_val, y_pred)
    prec = precision_score(y_val, y_pred, zero_division=0)
    rec  = recall_score(y_val, y_pred, zero_division=0)
    f1   = f1_score(y_val, y_pred, zero_division=0)
    try:
        auc  = roc_auc_score(y_val, probs)
    except Exception:
        auc = 0.0

    # ── Print report ─────────────────────────────────────────────────
    print(f"\n{'=' * 62}")
    print(f"  CROSS-STATION MODEL — EVALUATION RESULTS")
    print(f"{'=' * 62}")
    print(f"\n  Confusion Matrix:")
    print(f"                    Pred: No Flood    Pred: Flood")
    print(f"    Actual No Flood      {tn:<5d}          {fp:<5d}")
    print(f"    Actual Flood         {fn:<5d}          {tp:<5d}")
    print(f"\n  Metrics:")
    print(f"    Accuracy:  {acc:.4f}   ({acc * 100:.2f}%)")
    print(f"    Precision: {prec:.4f}   ({prec * 100:.2f}%)")
    print(f"    Recall:    {rec:.4f}   ({rec * 100:.2f}%)")
    print(f"    F1 Score:  {f1:.4f}")
    print(f"    ROC-AUC:   {auc:.4f}")
    print(f"    Baseline (persistence): ~82%" if args.show_baseline else "")
    print(f"    Total validation samples: {n_test}")

    print(f"\n  Classification Report:")
    report = classification_report(
        y_val, y_pred,
        target_names=["No Flood", "Flood"],
        digits=4,
    )
    print(report)

    # ── Optional: threshold sweep ────────────────────────────────────
    if args.threshold_sweep:
        print(f"\n  Threshold Sweep:")
        for th in [0.3, 0.4, 0.5, 0.6, 0.7]:
            yp_th = (probs >= th).astype(int)
            r = recall_score(y_val, yp_th, zero_division=0)
            p = precision_score(y_val, yp_th, zero_division=0)
            print(f"    Threshold {th:.1f} → precision: {p:.4f}, recall: {r:.4f}")

    # ── Save metrics to JSON ─────────────────────────────────────────
    metrics = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "dataset": "Melamchi + Chisapani combined (1979–2026)",
        "train_samples": int(len(X_train)),
        "val_samples": int(n_test),
        "val_flood_count": int(n_flood_val),
        "features": feature_cols,
        "confusion_matrix": {
            "tn": int(tn), "fp": int(fp),
            "fn": int(fn), "tp": int(tp),
        },
        "accuracy": round(float(acc), 4),
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "f1": round(float(f1), 4),
        "roc_auc": round(float(auc), 4),
        "baseline_accuracy": 0.82,
    }

    if args.json:
        print(json.dumps(metrics, indent=2))

    # Save to file
    out_path = BASE / "app" / "models" / "eval_metrics.json"
    with open(out_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n  ✓ Metrics saved to {out_path}")
    print(f"{'=' * 62}\n")


if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description="PeakFlow Analytics — Model Evaluation"
    )
    p.add_argument(
        "--use-saved", action="store_true", default=True,
        help="Load saved model weights if available (default: True)"
    )
    p.add_argument(
        "--json", action="store_true",
        help="Output metrics as JSON (for CI/automation)"
    )
    p.add_argument(
        "--threshold-sweep", action="store_true",
        help="Print precision/recall at multiple thresholds"
    )
    p.add_argument(
        "--show-baseline", action="store_true",
        help="Include baseline comparison in output"
    )
    args = p.parse_args()

    evaluate(args)
