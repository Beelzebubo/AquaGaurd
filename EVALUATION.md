# Evaluation — Accuracy Criteria

## How accuracy is measured

The model is a **binary classifier** that predicts whether river discharge
will exceed the station's historical 95th percentile (the "flood" class).
Performance is measured on a **chronological hold-out set** (the most
recent 20% of the combined Melamchi + Chisapani record).

| Split          | Start | End   | Samples | Flood % |
| -------------- | ----- | ----- | ------- | ------- |
| **Train**      | 1981  | ~2015 | 26,297  | ~6%     |
| **Validation** | ~2015 | 2024  | 6,575   | ~6%     |

A **time-based split** is essential for time-series forecasting: training
on the past and testing on the future prevents the model from "cheating"
by learning from data that hasn't happened yet.

---

## Metrics

#### Aggregate Performance & Class Imbalance Analysis

When evaluating a flood prediction model, high overall accuracy can be deeply misleading. Because flood events are rare (representing only ~6% of our historical dataset), a naive baseline model that blindly predicts "No Flood" every single day would automatically achieve an accuracy of roughly 94%.

Therefore, our evaluation prioritizes metrics that strictly account for severe class imbalance, specifically the **F1-Score** and **ROC-AUC**, rather than relying on raw accuracy.

| Metric | Value | Meaning & Relevance to Class Imbalance |
| --- | --- | --- |
| **ROC-AUC** | **0.9997** | The Area Under the ROC Curve proves near-perfect ranking ability, demonstrating that the model cleanly separates flood signals from normal variance regardless of class distribution. |
| **F1 Score** | **0.868** | The harmonic mean of precision and recall. Because it ignores True Negatives, this score confirms robust performance specifically on the rare "Flood" class. |
| **Precision** | **99.35%** | Out of all predicted floods, 99.35% were actual events—minimizing costly false alarms for infrastructure operators. |
| **Recall** | **77.02%** | The model successfully captures ~3 out of 4 actual flood events. The remaining 23% constitute false negatives, which we address below via threshold tuning. |
| **Overall Accuracy** | **98.59%** | Included for baseline completeness, but outshone by the class-specific metrics above. |

---

## What Recall means for flood risk

Recall (77.02%) is our most operationally critical metric because it dictates safety margins. In a real-world deployment, false negatives (missed floods) present a significantly higher risk than false positives (false alarms).

Because our core architecture outputs continuous probabilities (logits passed through a sigmoid function), we can directly manipulate this trade-off by adjusting the operational decision threshold:

* **Operational Safety Mode (Threshold = 0.3):** Drops precision slightly to ~97% but pushes **Recall up to ~85%**. This is the recommended configuration for early-warning support, prioritizing community safety and proactive plant drawdown.
* **Standard Balanced Mode (Threshold = 0.5):** The default configuration yielding a balanced **F1 of 0.868**.
* **Conservative Infrastructure Mode (Threshold = 0.7):** Maximizes precision to ~100%, eliminating false alarms at the cost of capturing fewer floods (Recall ~65%).

---

## Per-Station Performance (from training run)

These metrics come from the random 80/20 split used during training
(not the chronological split above — included for comparison).

| Station       | Accuracy   | Precision  | Recall     | F1        |
| ------------- | ---------- | ---------- | ---------- | --------- |
| **Melamchi**  | 99.82%     | 99.25%     | 97.08%     | 0.982     |
| **Chisapani** | 99.58%     | 98.33%     | 93.19%     | 0.957     |
| **Combined**  | **99.63%** | **98.72%** | **93.92%** | **0.963** |

---

## How the label ("flood") is defined

- **Flood threshold** = 95th percentile of the station's full discharge
  record.
- This is a **statistical definition** of flood risk, not a physical
  flood-zone delineation.
- A prediction of "flood" means discharge is expected to exceed historical
  high-flow conditions for that specific station.

---

## Reproducibility

To reproduce the evaluation results:

```bash
# 1. Set up environment
bash setup.sh

# 2. Run evaluation (loads saved model, runs on chronological split)
python scripts/evaluate.py

# 3. Alternatively, train from scratch + evaluate
python scripts/retrain_cross_station.py
python scripts/evaluate.py

# The script saves metrics to:
#   app/models/eval_metrics.json
```

The evaluation script runs the same data-loading, preprocessing, split,
and model-inference pipeline described above. No randomness beyond numpy's
default seed.
