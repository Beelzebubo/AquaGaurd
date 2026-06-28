#!/usr/bin/env python3
"""Retrain flood model on all station data with relative (cross-station) features.

Creates:
  app/models/cross_station_model.pth      — PyTorch model weights
  app/models/cross_station_scaler.pkl      — StandardScaler
  app/models/cross_station_features.pkl   — feature list
  app/models/station_stats.json            — per-station flow statistics
  app/models/optimal_threshold.json        — best probability cutoff ( maximal F1 )
"""
import json
import os
import warnings

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import StandardScaler
import joblib


# ── Helpers ──────────────────────────────────────────────────────────────


def load_station(name, weather_csv, flow_csv, date_col, flow_col, eco_threshold):
    w = pd.read_csv(weather_csv)
    w["Dates"] = pd.to_datetime(
        w["YEAR"].astype(str) + "-" + w["DOY"].astype(str), format="%Y-%j"
    )
    f = pd.read_csv(flow_csv)
    f["Dates"] = pd.to_datetime(f[date_col])

    df = pd.merge(w, f, on="Dates", how="inner")
    rename_map = {"PRECTOTCORR": "Rainfall", "T2M": "Temperature", "RH2M": "Humidity"}
    if flow_col in df.columns:
        rename_map[flow_col] = "Waterflow"
    df = df.rename(columns=rename_map)
    df["Station"] = name
    df["ecoThreshold"] = eco_threshold
    df = df.sort_values("Dates").reset_index(drop=True)

    flow = df["Waterflow"].values
    stats = {
        "mean": float(np.mean(flow)),
        "std": float(np.std(flow, ddof=1)),
        "p95": float(np.percentile(flow, 95)),
        "p50": float(np.percentile(flow, 50)),
        "min": float(np.min(flow)),
        "max": float(np.max(flow)),
        "ecoThreshold": eco_threshold,
    }
    return df, stats


# ── 1. Load data ────────────────────────────────────────────────────────

print("Loading station data ...")
df_m, stats_m = load_station(
    "melamchi",
    "Datasets/melamchi_weather.csv",
    "Datasets/melamchi_waterflow.csv",
    "Dates",
    "Values",
    12,
)
df_c, stats_c = load_station(
    "chisapani",
    "Datasets/chisepani_weather.csv",
    "Datasets/chisapani_ratedischarge.csv",
    "datetime",
    "discharge_cms",
    280,
)
print(f"  Melamchi:  {len(df_m)} rows  mean={stats_m['mean']:.1f}  P95={stats_m['p95']:.1f}")
print(f"  Chisapani: {len(df_c)} rows  mean={stats_c['mean']:.1f}  P95={stats_c['p95']:.1f}")

# ── 2. Rolling flow & lag features ─────────────────────────────────────
print("Computing rolling flows, lag features and relative features ...")
for df in (df_m, df_c):
    df["rollingFlow"] = df["Waterflow"].rolling(7, min_periods=1).mean()
    df["rain_3d"] = df["Rainfall"].rolling(3, min_periods=1).mean()
    df["rain_7d"] = df["Rainfall"].rolling(7, min_periods=1).mean()
    df["temp_3d"] = df["Temperature"].rolling(3, min_periods=1).mean()
    df["flow_change"] = df["Waterflow"].pct_change().fillna(0)
    p90 = df["Waterflow"].quantile(0.90)
    above = (df["Waterflow"] > p90).astype(int)
    df["days_above_p90"] = above.groupby(
        (above != above.shift()).cumsum()
    ).cumcount() + 1
    df.loc[above == 0, "days_above_p90"] = 0

for df, s in [(df_m, stats_m), (df_c, stats_c)]:
    safe_std = max(s["std"], 1e-6)
    safe_eco = max(s["ecoThreshold"], 1e-6)
    safe_p95 = max(s["p95"], 1e-6)
    df["flow_zscore"] = (df["Waterflow"] - s["mean"]) / safe_std
    df["flow_ratio_eco"] = df["Waterflow"] / safe_eco
    df["flow_ratio_p95"] = df["Waterflow"] / safe_p95
    df["flow_spike_ratio"] = df["Waterflow"] / df["rollingFlow"].replace(0, np.nan)
    df["flow_spike_ratio"] = df["flow_spike_ratio"].replace([np.inf, -np.inf], np.nan).fillna(1.0)
    df["flow_change"] = df["flow_change"].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    df["floodLabel"] = (df["Waterflow"] > s["p95"]).astype(int)

# ── 3. Combine & sort chronologically ────────────────────────────────────
df_all = pd.concat([df_m, df_c], ignore_index=True)
df_all = df_all.sort_values("Dates").reset_index(drop=True)

feature_cols = [
    "Temperature",
    "Rainfall",
    "Humidity",
    "flow_zscore",
    "flow_ratio_eco",
    "flow_ratio_p95",
    "flow_spike_ratio",
    "rain_3d",
    "rain_7d",
    "temp_3d",
    "flow_change",
    "days_above_p90",
]
label_col = "floodLabel"

df_all[feature_cols] = df_all[feature_cols].replace([np.inf, -np.inf], np.nan)
df_all = df_all.dropna(subset=feature_cols + [label_col]).reset_index(drop=True)
n_m = (df_all["Station"] == "melamchi").sum()
n_c = (df_all["Station"] == "chisapani").sum()
n_f = df_all["floodLabel"].sum()
print(f"  Combined: {len(df_all)} rows  ({n_m} melamchi / {n_c} chisapani)")
print(f"  Flood events: {n_f} / {len(df_all)} ({n_f/len(df_all)*100:.1f}%)")

# ── 4. Chronological 80/20 split ────────────────────────────────────────
X = df_all[feature_cols].values
y = df_all[label_col].values.astype(np.float32)

split_idx = int(0.8 * len(df_all))
X_train, X_val = X[:split_idx], X[split_idx:]
y_train, y_val = y[:split_idx], y[split_idx:]

scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_val_s = scaler.transform(X_val)

print(f"  Train: {len(X_train)}  Validation: {len(X_val)}")

# ── 5. Build model ──────────────────────────────────────────────────────


class FloodModel(nn.Module):
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


model = FloodModel(input_size=len(feature_cols))

n_neg = (y_train == 0).sum()
n_pos = (y_train == 1).sum()
pos_weight = torch.tensor(n_neg / n_pos, dtype=torch.float32)
criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
optimizer = optim.Adam(model.parameters(), lr=0.001)

X_train_t = torch.tensor(X_train_s, dtype=torch.float32)
y_train_t = torch.tensor(y_train, dtype=torch.float32).reshape(-1, 1)
X_val_t = torch.tensor(X_val_s, dtype=torch.float32)
y_val_t = torch.tensor(y_val, dtype=torch.float32).reshape(-1, 1)

# ── 6. Training loop ────────────────────────────────────────────────────
epochs = 300
print(f"\nTraining for {epochs} epochs ...")
for epoch in range(epochs):
    model.train()
    optimizer.zero_grad()
    train_logits = model(X_train_t)
    loss = criterion(train_logits, y_train_t)
    loss.backward()
    optimizer.step()

    if (epoch + 1) % 50 == 0:
        model.eval()
        with torch.no_grad():
            val_logits = model(X_val_t)
            val_loss = criterion(val_logits, y_val_t)
        train_acc = (
            (torch.sigmoid(train_logits) >= 0.5)
            .int()
            .eq(y_train_t.int())
            .sum()
            .item()
            / len(y_train_t)
        )
        val_acc = (
            (torch.sigmoid(val_logits) >= 0.5)
            .int()
            .eq(y_val_t.int())
            .sum()
            .item()
            / len(y_val_t)
        )
        print(
            f"  Epoch [{epoch+1:>3}/{epochs}]  "
            f"Train Loss: {loss.item():.4f} ({train_acc:.3f})  "
            f"Val Loss: {val_loss.item():.4f} ({val_acc:.3f})"
        )

# ── 7. Final evaluation & threshold sweep ───────────────────────────────
model.eval()
with torch.no_grad():
    val_probs = torch.sigmoid(model(X_val_t)).numpy().flatten()

# Default 0.5 threshold metrics
val_preds = (val_probs >= 0.5).astype(int)
tn = ((y_val == 0) & (val_preds == 0)).sum()
fp = ((y_val == 0) & (val_preds == 1)).sum()
fn = ((y_val == 1) & (val_preds == 0)).sum()
tp = ((y_val == 1) & (val_preds == 1)).sum()
total = len(y_val)

accuracy = (tp + tn) / total
precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
f1 = (
    2 * precision * recall / (precision + recall)
    if (precision + recall) > 0
    else 0.0
)

print(f"\n{'='*52}")
print(f"  CROSS-STATION MODEL — FINAL EVALUATION (threshold=0.50)")
print(f"{'='*52}")
print(f"  Confusion Matrix:")
print(f"                    Pred: No Flood    Pred: Flood")
print(f"    Actual No Flood     {tn:>5}             {fp:<5}")
print(f"    Actual Flood        {fn:>5}             {tp:<5}")
print(f"  Total: {total}  |  Accuracy: {accuracy:.4f}  |  Precision: {precision:.4f}")
print(f"  Recall: {recall:.4f}  |  F1: {f1:.4f}")

# Threshold sweep — find cutoff that maximises F1
print(f"\n  Threshold sweep (maximising F1):")
best_f1, best_th = 0.0, 0.5
for th in np.arange(0.15, 0.75, 0.01):
    preds_th = (val_probs >= th).astype(int)
    tp_t = ((y_val == 1) & (preds_th == 1)).sum()
    fp_t = ((y_val == 0) & (preds_th == 1)).sum()
    fn_t = ((y_val == 1) & (preds_th == 0)).sum()
    prec_t = tp_t / (tp_t + fp_t) if (tp_t + fp_t) > 0 else 1.0
    rec_t = tp_t / (tp_t + fn_t) if (tp_t + fn_t) > 0 else 0.0
    f1_t = (
        2 * prec_t * rec_t / (prec_t + rec_t)
        if (prec_t + rec_t) > 0
        else 0.0
    )
    if f1_t > best_f1:
        best_f1, best_th = f1_t, float(th)

# Re-evaluate at optimal threshold
opt_preds = (val_probs >= best_th).astype(int)
opt_tn = ((y_val == 0) & (opt_preds == 0)).sum()
opt_fp = ((y_val == 0) & (opt_preds == 1)).sum()
opt_fn = ((y_val == 1) & (opt_preds == 0)).sum()
opt_tp = ((y_val == 1) & (opt_preds == 1)).sum()
opt_acc = (opt_tp + opt_tn) / total
opt_prec = opt_tp / (opt_tp + opt_fp) if (opt_tp + opt_fp) > 0 else 1.0
opt_rec = opt_tp / (opt_tp + opt_fn) if (opt_tp + opt_fn) > 0 else 0.0
opt_f1 = (
    2 * opt_prec * opt_rec / (opt_prec + opt_rec)
    if (opt_prec + opt_rec) > 0
    else 0.0
)

print(f"\n  ── Optimal threshold: {best_th:.2f} ──")
print(f"  Confusion Matrix @ {best_th:.2f}:")
print(f"                    Pred: No Flood    Pred: Flood")
print(f"    Actual No Flood     {opt_tn:>5}             {opt_fp:<5}")
print(f"    Actual Flood        {opt_fn:>5}             {opt_tp:<5}")
print(f"  Accuracy: {opt_acc:.4f}  |  Precision: {opt_prec:.4f}")
print(f"  Recall: {opt_rec:.4f}  |  F1: {opt_f1:.4f}")

# ── 8. Save artefacts ───────────────────────────────────────────────────
os.makedirs("app/models", exist_ok=True)
torch.save(model.state_dict(), "app/models/cross_station_model.pth")
joblib.dump(scaler, "app/models/cross_station_scaler.pkl")
joblib.dump(feature_cols, "app/models/cross_station_features.pkl")

station_stats = {"melamchi": stats_m, "chisapani": stats_c}
with open("app/models/station_stats.json", "w") as f:
    json.dump(station_stats, f, indent=2)

threshold_data = {"optimal_threshold": best_th}
with open("app/models/optimal_threshold.json", "w") as f:
    json.dump(threshold_data, f, indent=2)

metrics = {
    "timestamp": pd.Timestamp.now().isoformat(),
    "dataset": "Melamchi + Chisapani combined (1979-2026)",
    "train_samples": int(len(X_train)),
    "val_samples": int(total),
    "val_flood_count": int(y_val.sum()),
    "features": feature_cols,
    "confusion_matrix_default": {
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
    },
    "confusion_matrix_optimal": {
        "tn": int(opt_tn), "fp": int(opt_fp),
        "fn": int(opt_fn), "tp": int(opt_tp),
    },
    "accuracy_default": round(float(accuracy), 4),
    "precision_default": round(float(precision), 4),
    "recall_default": round(float(recall), 4),
    "f1_default": round(float(f1), 4),
    "optimal_threshold": round(best_th, 4),
    "accuracy_optimal": round(float(opt_acc), 4),
    "precision_optimal": round(float(opt_prec), 4),
    "recall_optimal": round(float(opt_rec), 4),
    "f1_optimal": round(float(opt_f1), 4),
}
with open("app/models/eval_metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)

print(f"\n  Saved artefacts:")
print(f"    - app/models/cross_station_model.pth")
print(f"    - app/models/cross_station_scaler.pkl")
print(f"    - app/models/cross_station_features.pkl")
print(f"    - app/models/station_stats.json")
print(f"    - app/models/optimal_threshold.json")
print(f"    - app/models/eval_metrics.json")

# ── 9. Per-station breakdown ────────────────────────────────────────────
print(f"\n  Per-station breakdown (full dataset @ optimal threshold {best_th:.2f}):")
for st in sorted(df_all["Station"].unique()):
    mask = df_all["Station"] == st
    if mask.sum() == 0:
        continue
    Xst = scaler.transform(df_all.loc[mask, feature_cols].values)
    yst = df_all.loc[mask, "floodLabel"].values
    with torch.no_grad():
        pst = torch.sigmoid(model(torch.tensor(Xst, dtype=torch.float32))).numpy().flatten()
    ypst = (pst >= best_th).astype(int)
    tn2 = ((yst == 0) & (ypst == 0)).sum()
    fp2 = ((yst == 0) & (ypst == 1)).sum()
    fn2 = ((yst == 1) & (ypst == 0)).sum()
    tp2 = ((yst == 1) & (ypst == 1)).sum()
    n2 = len(yst)
    a2 = (tp2 + tn2) / n2
    r2 = tp2 / (tp2 + fn2) if (tp2 + fn2) > 0 else 0
    p2 = tp2 / (tp2 + fp2) if (tp2 + fp2) > 0 else 1
    f12 = 2 * p2 * r2 / (p2 + r2) if (p2 + r2) > 0 else 0
    print(
        f"    {st:12s}  n={n2:>5}  acc={a2:.4f}  prec={p2:.4f}  "
        f"rec={r2:.4f}  f1={f12:.4f}  TN={tn2} FP={fp2} FN={fn2} TP={tp2}"
    )
print("  Done.")
