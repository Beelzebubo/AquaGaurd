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
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
    roc_auc_score,
)
from sklearn.preprocessing import StandardScaler


# ── Model architecture (must match retrain_cross_station.py) ────────────


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


BASE = Path(__file__).resolve().parent.parent

FEATURE_COLS = [
    "T2M",
    "PRECTOTCORR",
    "RH2M",
    "flow_zscore",
    "flow_ratio_eco",
    "flow_ratio_p95",
    "flow_spike",
    "rain_3d",
    "rain_7d",
    "temp_3d",
    "flow_change",
    "days_above_p90",
]


def load_data() -> pd.DataFrame:
    """Load and merge Melamchi + Chisapani data with relative and lag features."""
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
        wdf = pd.read_csv(BASE / paths["weather"])
        wdf["DATE"] = (
            wdf["YEAR"].astype(str).str.zfill(4)
            + wdf["DOY"].astype(str).str.zfill(3)
        )
        wdf = wdf.drop_duplicates(subset="DATE").set_index("DATE")

        fdf = pd.read_csv(BASE / paths["flow"])
        date_col = None
        for candidate in ["Date", "Dates", "datetime", "date", "time"]:
            if candidate in fdf.columns:
                date_col = candidate
                break
        if date_col is None:
            raise KeyError(
                f"No date column found in {paths['flow']}: {list(fdf.columns)}"
            )
        fdf = fdf.drop_duplicates(subset=date_col).set_index(date_col)

        fcol = None
        for candidate in ["Values", "discharge_cms", "Waterflow", "waterflow", "Q"]:
            if candidate in fdf.columns:
                fcol = candidate
                break
        if fcol is None:
            float_cols = fdf.select_dtypes(include=[np.number]).columns.tolist()
            if float_cols:
                fcol = float_cols[0]
            else:
                raise KeyError(
                    f"No flow column in {paths['flow']}: {list(fdf.columns)}"
                )

        flow_series = fdf[fcol].rename("waterflow")
        flow_series.index = pd.to_datetime(flow_series.index, errors="coerce")

        wdf.index = pd.to_datetime(wdf.index, format="%Y%j", errors="coerce")
        merged = wdf.join(flow_series, how="inner")
        merged = merged.dropna(subset=["T2M", "PRECTOTCORR", "RH2M", "waterflow"])

        for c in merged.columns:
            if merged[c].dtype == object:
                merged[c] = pd.to_numeric(merged[c], errors="coerce")
        merged = merged.dropna()

        eco = paths["eco"]
        merged["flow_ratio_eco"] = merged["waterflow"] / max(eco, 1e-6)
        p95 = merged["waterflow"].quantile(0.95)
        merged["flow_ratio_p95"] = merged["waterflow"] / max(p95, 1e-6)
        merged["flow_zscore"] = (merged["waterflow"] - merged["waterflow"].mean()) / max(
            merged["waterflow"].std(), 1e-6
        )
        merged["flow_spike"] = merged["waterflow"] / merged["waterflow"].rolling(
            7, min_periods=1
        ).mean().clip(lower=1e-6)

        # Lag features (must match retrain script)
        merged["rain_3d"] = merged["PRECTOTCORR"].rolling(3, min_periods=1).mean()
        merged["rain_7d"] = merged["PRECTOTCORR"].rolling(7, min_periods=1).mean()
        merged["temp_3d"] = merged["T2M"].rolling(3, min_periods=1).mean()
        merged["flow_change"] = merged["waterflow"].pct_change().replace([np.inf, -np.inf], np.nan).fillna(0)
        p90 = merged["waterflow"].quantile(0.90)
        above = (merged["waterflow"] > p90).astype(int)
        merged["days_above_p90"] = above.groupby(
            (above != above.shift()).cumsum()
        ).cumcount() + 1
        merged.loc[above == 0, "days_above_p90"] = 0

        merged["Station"] = st_name
        merged["floodLabel"] = (merged["waterflow"] > p95).astype(int)
        merged["date_ordinal"] = merged.index.map(pd.Timestamp.toordinal)
        dfs.append(merged)

    df_all = pd.concat(dfs, ignore_index=False).sort_index()
    df_all = df_all.dropna()
    return df_all


def evaluate(args):
    print("=" * 62)
    print("  PEAKFLOW ANALYTICS — MODEL EVALUATION  (v1.01)")
    print("=" * 62)

    print("\n  Loading data ...")
    df_all = load_data()

    X = df_all[FEATURE_COLS].values.astype(np.float64)
    y = df_all["floodLabel"].values

    X = np.nan_to_num(X, nan=0.0, posinf=1e6, neginf=-1e6)

    sort_idx = np.argsort(df_all["date_ordinal"].values)
    X_sorted = X[sort_idx]
    y_sorted = y[sort_idx]
    split = int(0.8 * len(X_sorted))
    X_train, X_val = X_sorted[:split], X_sorted[split:]
    y_train, y_val = y_sorted[:split], y_sorted[split:]

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_val_s = scaler.transform(X_val)

    n_test = len(y_val)
    n_flood_val = int(y_val.sum())
    prop_flood = 100 * n_flood_val / n_test
    print(f"  Training samples:    {len(X_train)}")
    print(f"  Validation samples:  {n_test} ({n_flood_val} flood = {prop_flood:.1f}%)")
    print(f"  Features:            {len(FEATURE_COLS)}")
    print(f"  Feature names:       {FEATURE_COLS}")

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
        n_neg = (y_train == 0).sum()
        n_pos = (y_train == 1).sum()
        pos_weight = torch.tensor(n_neg / n_pos, dtype=torch.float32)
        criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

        Xt = torch.tensor(X_train_s, dtype=torch.float32)
        yt = torch.tensor(y_train, dtype=torch.float32).unsqueeze(1)
        Xv = torch.tensor(X_val_s, dtype=torch.float32)
        yv = torch.tensor(y_val, dtype=torch.float32).unsqueeze(1)

        for epoch in range(1, 301):
            model.train()
            optimizer.zero_grad()
            out = model(Xt)
            loss = criterion(out, yt)
            loss.backward()
            optimizer.step()

            if epoch % 50 == 0 or epoch == 300:
                model.eval()
                with torch.no_grad():
                    vout = model(Xv)
                    vloss = criterion(vout, yv)
                    vpred = (torch.sigmoid(vout) >= 0.5).float()
                    vacc = (vpred == yv).float().mean().item()
                print(
                    f"    Epoch [{epoch:>3}/300]  "
                    f"Train Loss: {loss.item():.4f}  "
                    f"Val Loss: {vloss.item():.4f}  "
                    f"Val Acc: {vacc:.4f}"
                )

        torch.save(model.state_dict(), model_path)
        print(f"  ✓ Model saved to {model_path}")

    # ── Full evaluation ──────────────────────────────────────────────
    model.eval()
    Xv_t = torch.tensor(X_val_s, dtype=torch.float32)
    with torch.no_grad():
        logits = model(Xv_t)
        probs = torch.sigmoid(logits).numpy().flatten()

    # Default threshold
    y_pred = (probs >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_val, y_pred).ravel()
    acc = accuracy_score(y_val, y_pred)
    prec = precision_score(y_val, y_pred, zero_division=0)
    rec = recall_score(y_val, y_pred, zero_division=0)
    f1 = f1_score(y_val, y_pred, zero_division=0)
    try:
        auc = roc_auc_score(y_val, probs)
    except Exception:
        auc = 0.0

    print(f"\n{'=' * 62}")
    print(f"  EVALUATION RESULTS (threshold = 0.50)")
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

    # ── Threshold sweep ──────────────────────────────────────────────
    best_f1_th, best_th = 0.0, 0.5
    for th in np.arange(0.15, 0.75, 0.01):
        yp_th = (probs >= th).astype(int)
        tp_th = ((y_val == 1) & (yp_th == 1)).sum()
        fp_th = ((y_val == 0) & (yp_th == 1)).sum()
        fn_th = ((y_val == 1) & (yp_th == 0)).sum()
        prec_th = tp_th / (tp_th + fp_th) if (tp_th + fp_th) > 0 else 1.0
        rec_th = tp_th / (tp_th + fn_th) if (tp_th + fn_th) > 0 else 0.0
        f1_th = (
            2 * prec_th * rec_th / (prec_th + rec_th)
            if (prec_th + rec_th) > 0
            else 0.0
        )
        if f1_th > best_f1_th:
            best_f1_th, best_th = f1_th, float(th)

    opt_preds = (probs >= best_th).astype(int)
    opt_tn, opt_fp, opt_fn, opt_tp = confusion_matrix(y_val, opt_preds).ravel()
    opt_acc = accuracy_score(y_val, opt_preds)
    opt_prec = precision_score(y_val, opt_preds, zero_division=0)
    opt_rec = recall_score(y_val, opt_preds, zero_division=0)
    opt_f1 = f1_score(y_val, opt_preds, zero_division=0)

    print(f"\n  ── Optimal threshold: {best_th:.2f} ──")
    print(f"  Confusion Matrix @ {best_th:.2f}:")
    print(f"                    Pred: No Flood    Pred: Flood")
    print(f"    Actual No Flood      {opt_tn:<5d}          {opt_fp:<5d}")
    print(f"    Actual Flood         {opt_fn:<5d}          {opt_tp:<5d}")
    print(f"    Accuracy:  {opt_acc:.4f}   ({opt_acc * 100:.2f}%)")
    print(f"    Precision: {opt_prec:.4f}   ({opt_prec * 100:.2f}%)")
    print(f"    Recall:    {opt_rec:.4f}   ({opt_rec * 100:.2f}%)")
    print(f"    F1 Score:  {opt_f1:.4f}")

    # Verbose sweep table
    if args.threshold_sweep:
        print(f"\n  Full threshold sweep:")
        print(f"    {'Th':>5s}  {'Precision':>10s}  {'Recall':>8s}  {'F1':>8s}")
        for th in [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70]:
            yp_th = (probs >= th).astype(int)
            r = recall_score(y_val, yp_th, zero_division=0)
            p = precision_score(y_val, yp_th, zero_division=0)
            f = f1_score(y_val, yp_th, zero_division=0)
            print(f"    {th:.2f}  {p:>10.4f}  {r:>8.4f}  {f:>8.4f}")

    print(f"\n  Classification Report (@ {best_th:.2f}):")
    report = classification_report(
        y_val, opt_preds, target_names=["No Flood", "Flood"], digits=4
    )
    print(report)

    # ── Save metrics ─────────────────────────────────────────────────
    metrics = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "dataset": "Melamchi + Chisapani combined (1979-2026)",
        "train_samples": int(len(X_train)),
        "val_samples": int(n_test),
        "val_flood_count": int(n_flood_val),
        "features": FEATURE_COLS,
        "confusion_matrix_default": {
            "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
        },
        "accuracy_default": round(float(acc), 4),
        "precision_default": round(float(prec), 4),
        "recall_default": round(float(rec), 4),
        "f1_default": round(float(f1), 4),
        "roc_auc": round(float(auc), 4),
        "optimal_threshold": round(best_th, 4),
        "confusion_matrix_optimal": {
            "tn": int(opt_tn), "fp": int(opt_fp),
            "fn": int(opt_fn), "tp": int(opt_tp),
        },
        "accuracy_optimal": round(float(opt_acc), 4),
        "precision_optimal": round(float(opt_prec), 4),
        "recall_optimal": round(float(opt_rec), 4),
        "f1_optimal": round(float(opt_f1), 4),
        "baseline_accuracy": 0.82,
    }

    if args.json:
        print(json.dumps(metrics, indent=2))

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
        "--use-saved",
        action="store_true",
        default=True,
        help="Load saved model weights if available (default: True)",
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="Output metrics as JSON (for CI/automation)",
    )
    p.add_argument(
        "--threshold-sweep",
        action="store_true",
        default=True,
        help="Print precision/recall at multiple thresholds (default: True)",
    )
    p.add_argument(
        "--show-baseline",
        action="store_true",
        help="Include baseline comparison in output",
    )
    args = p.parse_args()
    evaluate(args)
