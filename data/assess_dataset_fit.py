#!/usr/bin/env python3
"""
Assess Elliptic vs PaySim dataset-domain fit and emit a JSON report.
"""

import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent
if str(DATA_DIR) not in sys.path:
    sys.path.append(str(DATA_DIR))

from path_utils import resolve_dataset_path  # noqa: E402


def assess_elliptic() -> dict:
    classes_path = resolve_dataset_path("elliptic_txs_classes.csv")
    features_path = resolve_dataset_path("elliptic_txs_features.csv")

    if classes_path is None or features_path is None:
        return {"status": "missing", "details": "Elliptic CSV files not found"}

    classes_df = pd.read_csv(classes_path)
    features_df = pd.read_csv(features_path, header=None)

    label_counts = classes_df["class"].astype(str).value_counts().to_dict()
    feature_dim = features_df.shape[1] - 2
    time_step_min = int(features_df.iloc[:, 1].min())
    time_step_max = int(features_df.iloc[:, 1].max())

    return {
        "status": "available",
        "transactions": len(classes_df),
        "label_counts": label_counts,
        "feature_dim": feature_dim,
        "time_step_range": [time_step_min, time_step_max],
    }


def assess_paysim() -> dict:
    paysim_path = resolve_dataset_path("paysim.csv")
    if paysim_path is None:
        return {"status": "missing", "details": "paysim.csv not found"}

    total = 0
    fraud = 0
    amount_sum = 0.0
    amount_min = float("inf")
    amount_max = 0.0
    type_counts: Counter = Counter()

    for chunk in pd.read_csv(
        paysim_path,
        usecols=["step", "type", "amount", "isFraud"],
        chunksize=200_000,
    ):
        total += len(chunk)
        fraud += int(chunk["isFraud"].sum())
        amount_sum += float(chunk["amount"].sum())
        amount_min = min(amount_min, float(chunk["amount"].min()))
        amount_max = max(amount_max, float(chunk["amount"].max()))
        type_counts.update(chunk["type"].value_counts().to_dict())

    mean_amount = (amount_sum / total) if total else 0.0
    fraud_rate = (fraud / total) if total else 0.0

    return {
        "status": "available",
        "transactions": total,
        "fraud_count": fraud,
        "fraud_rate": fraud_rate,
        "amount_stats": {
            "min": amount_min if total else None,
            "max": amount_max if total else None,
            "mean": mean_amount,
        },
        "type_distribution": dict(type_counts),
        "feature_dim": 7,
    }


def assess_fit(elliptic: dict, paysim: dict) -> dict:
    notes = []

    if elliptic.get("status") == "available" and paysim.get("status") == "available":
        if elliptic.get("feature_dim") != paysim.get("feature_dim"):
            notes.append("Feature dimensions mismatch; requires adapter or separate model.")
        if "unknown" in elliptic.get("label_counts", {}):
            notes.append("Elliptic has unlabeled transactions; training excludes unknown labels.")
        notes.append("Elliptic is crypto transaction graph; PaySim is mobile money ledger.")
    elif paysim.get("status") == "missing":
        notes.append("PaySim dataset missing; cannot evaluate cross-domain fit.")
    elif elliptic.get("status") == "missing":
        notes.append("Elliptic dataset missing; cannot evaluate base model fit.")

    return {"notes": notes}


def main() -> None:
    elliptic = assess_elliptic()
    paysim = assess_paysim()
    fit = assess_fit(elliptic, paysim)

    report = {
        "elliptic": elliptic,
        "paysim": paysim,
        "fit_summary": fit,
    }

    output_path = DATA_DIR / "dataset_fit_report.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)

    print("\n" + "=" * 60)
    print("DATASET DOMAIN FIT REPORT")
    print("=" * 60)
    print(json.dumps(report, indent=2))
    print(f"\n✓ Saved report to {output_path}")


if __name__ == "__main__":
    main()
