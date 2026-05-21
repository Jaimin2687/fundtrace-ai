#!/usr/bin/env python3
"""
Label PaySim patterns, generate alerts, and build an ML-ready dataset.
"""

import argparse
import os
import sys
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent
if str(DATA_DIR) not in sys.path:
    sys.path.append(str(DATA_DIR))

from path_utils import require_dataset_path  # noqa: E402


PAYSIM_TYPE_CATEGORIES = ["CASH_OUT", "TRANSFER", "PAYMENT", "CASH_IN", "DEBIT"]


def assign_pattern(row: pd.Series) -> str | None:
    if row["amount"] < 200000 and row["type"] == "TRANSFER":
        return "Structuring"
    if row["oldbalanceDest"] == 0 and row["type"] == "TRANSFER":
        return "Dormant Account Activated"
    if row["type"] == "CASH_OUT" and row["isFraud"] == 1:
        return "Layering - Cash Out"
    if row["isFraud"] == 1:
        return "Suspicious Transfer"
    return None


def label_paysim_patterns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["pattern_label"] = df.apply(assign_pattern, axis=1)
    return df


def build_ml_ready_dataset(df: pd.DataFrame, seed: int, sample_size: int | None) -> pd.DataFrame:
    fraud_df = df[df["isFraud"] == 1].copy()
    legit_df = df[df["isFraud"] == 0].copy()

    if fraud_df.empty or legit_df.empty:
        raise ValueError("PaySim dataset must include both fraud and legit rows.")

    legit_sample = legit_df.sample(n=len(fraud_df), random_state=seed)
    balanced_df = pd.concat([fraud_df, legit_sample], ignore_index=True).sample(frac=1.0, random_state=seed)

    if sample_size and sample_size < len(balanced_df):
        balanced_df = balanced_df.sample(n=sample_size, random_state=seed)

    if "txId" not in balanced_df.columns:
        balanced_df["txId"] = (
            balanced_df["nameOrig"].astype(str)
            + "_"
            + balanced_df["nameDest"].astype(str)
            + "_"
            + balanced_df["step"].astype(str)
            + "_"
            + balanced_df.index.astype(str)
        )

    for category in PAYSIM_TYPE_CATEGORIES:
        balanced_df[f"type_{category}"] = (balanced_df["type"] == category).astype(int)

    ml_cols = [
        "txId",
        "label",
        "step",
        "amount",
        "oldbalanceOrg",
        "newbalanceOrig",
        "oldbalanceDest",
        "newbalanceDest",
        "isFlaggedFraud",
        *[f"type_{category}" for category in PAYSIM_TYPE_CATEGORIES],
    ]

    balanced_df["label"] = balanced_df["isFraud"].astype(int)
    return balanced_df[ml_cols]


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare PaySim alerts and ML-ready dataset.")
    parser.add_argument("--sample-size", type=int, default=None)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("PAYSIM DATA PREPARATION")
    print("=" * 60)

    paysim_path = require_dataset_path("paysim.csv")
    print(f"\n📂 Reading {paysim_path}...")
    max_tx_raw = os.getenv("PAYSIM_MAX_TX")
    max_tx = 0
    if max_tx_raw:
        try:
            max_tx = int(max_tx_raw.strip())
        except ValueError:
            max_tx = 0
    if max_tx > 0:
        max_tx = min(max_tx, 190000)
        df = pd.read_csv(paysim_path, nrows=max_tx)
    else:
        df = pd.read_csv(paysim_path)
    print(f"  Total rows: {len(df):,}")

    print("\n🏷️  Applying pattern labels...")
    labeled_df = label_paysim_patterns(df)
    labeled_df = labeled_df.copy().reset_index(drop=True)
    labeled_df["txId"] = (
        labeled_df["nameOrig"].astype(str)
        + "_"
        + labeled_df["nameDest"].astype(str)
        + "_"
        + labeled_df["step"].astype(str)
        + "_"
        + labeled_df.index.astype(str)
    )
    fraud_df = labeled_df[labeled_df["isFraud"] == 1].copy()

    alerts_path = DATA_DIR / "paysim_alerts.csv"
    fraud_df.to_csv(alerts_path, index=False)
    print(f"\n💾 Saved fraud alerts to {alerts_path}")

    print("\n📊 ALERT SUMMARY:")
    print(f"  Fraud rows: {len(fraud_df):,}")
    pattern_counts = fraud_df["pattern_label"].value_counts()
    for pattern, count in pattern_counts.items():
        print(f"    {pattern}: {count:,}")

    print("\n🧪 Building ML-ready dataset (balanced)...")
    ml_ready_df = build_ml_ready_dataset(labeled_df, seed=args.seed, sample_size=args.sample_size)
    ml_path = DATA_DIR / "paysim_ml_ready.csv"
    ml_ready_df.to_csv(ml_path, index=False)
    print(f"💾 Saved ML-ready dataset to {ml_path}")

    class_counts = ml_ready_df["label"].value_counts().sort_index()
    print("\n📊 ML DATASET SUMMARY:")
    print(f"  Legit (0): {class_counts.get(0, 0):,}")
    print(f"  Fraud (1): {class_counts.get(1, 0):,}")
    print(f"  Total: {len(ml_ready_df):,}")

    print("\n✅ PaySim preparation complete!")


if __name__ == "__main__":
    main()
