#!/usr/bin/env python3
"""
Evaluate the XGBoost fraud detection model.
Supports synthetic evaluation and PaySim compatibility evaluation.
"""

import argparse
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)
from dotenv import load_dotenv

# Load environment
load_dotenv()

DATA_DIR = Path(__file__).resolve().parent / "data"
if str(DATA_DIR) not in sys.path:
    sys.path.append(str(DATA_DIR))

from path_utils import require_dataset_path  # noqa: E402
from paysim_adapter import build_paysim_feature_matrix  # noqa: E402

PAYSIM_FEATURE_COLS = [
    "step",
    "amount",
    "oldbalanceOrg",
    "newbalanceOrig",
    "oldbalanceDest",
    "newbalanceDest",
    "isFlaggedFraud",
    "type_CASH_OUT",
    "type_TRANSFER",
    "type_PAYMENT",
    "type_CASH_IN",
    "type_DEBIT",
]


def load_model(model_path: str) -> xgb.XGBClassifier:
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Model not found at {model_path}. Train first with backend/worker/ml_worker.py --train"
        )
    model = xgb.XGBClassifier()
    model.load_model(model_path)
    return model


def build_synthetic_test_set(seed: int, samples: int, feature_dim: int) -> tuple[np.ndarray, np.ndarray]:
    np.random.seed(seed)
    n_legit = int(samples * 0.9)
    n_fraud = samples - n_legit

    X_legit = np.random.normal(0.5, 0.2, (n_legit, feature_dim))
    X_legit = np.clip(X_legit, 0, 1)
    X_fraud = np.random.normal(0.6, 0.25, (n_fraud, feature_dim))
    X_fraud = np.clip(X_fraud, 0, 1)

    X_test = np.vstack([X_legit, X_fraud])
    y_test = np.hstack([np.zeros(n_legit), np.ones(n_fraud)])

    idx = np.random.permutation(len(X_test))
    return X_test[idx], y_test[idx]


def build_paysim_test_set(paysim_path: str, sample_size: int | None, seed: int) -> tuple[np.ndarray, np.ndarray]:
    df = pd.read_csv(
        paysim_path,
        usecols=[
            "step",
            "type",
            "amount",
            "oldbalanceOrg",
            "newbalanceOrig",
            "oldbalanceDest",
            "newbalanceDest",
            "isFraud",
            "isFlaggedFraud",
        ],
    )

    if sample_size and sample_size < len(df):
        df = df.sample(n=sample_size, random_state=seed)

    y_test = df["isFraud"].astype(int).to_numpy()
    X_test = build_paysim_feature_matrix(df)
    return X_test, y_test


def build_paysim_ml_ready_set(paysim_ml_ready_path: str, sample_size: int | None, seed: int) -> tuple[np.ndarray, np.ndarray]:
    df = pd.read_csv(paysim_ml_ready_path)

    if sample_size and sample_size < len(df):
        df = df.sample(n=sample_size, random_state=seed)

    missing = [col for col in PAYSIM_FEATURE_COLS if col not in df.columns]
    if missing:
        raise ValueError(f"PaySim ML-ready dataset missing columns: {', '.join(missing)}")

    X_test = df[PAYSIM_FEATURE_COLS].astype(float).to_numpy()
    y_test = df["label"].astype(int).to_numpy()
    return X_test, y_test


def resolve_model_path(dataset: str, model_path: str) -> str:
    if dataset != "paysim":
        return model_path

    default_path = Path("data/fraud_model.json")
    if model_path != str(default_path):
        return model_path

    paysim_model = Path("data/paysim_model.json")
    if paysim_model.exists():
        print(f"\nℹ️  Using PaySim model at {paysim_model}")
        return str(paysim_model)

    print("\n⚠️  PaySim model not found. Using Elliptic model for cross-domain evaluation.")
    return model_path


def resolve_paysim_source(model_path: str, requested: str | None) -> str:
    if requested:
        return requested
    if model_path.endswith("paysim_model.json"):
        return "ml-ready"
    return "full"


def print_metrics(y_test: np.ndarray, y_pred: np.ndarray, y_pred_proba: np.ndarray | None) -> dict:
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    roc_auc = None
    if y_pred_proba is not None and len(np.unique(y_test)) > 1:
        roc_auc = roc_auc_score(y_test, y_pred_proba)

    print("\n📊 Performance Metrics:")
    print(f"   Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"   Precision: {precision:.4f} ({precision*100:.2f}%)")
    print(f"   Recall:    {recall:.4f} ({recall*100:.2f}%)")
    print(f"   F1-Score:  {f1:.4f}")
    if roc_auc is not None:
        print(f"   ROC-AUC:   {roc_auc:.4f}")

    cm = confusion_matrix(y_test, y_pred)
    print("\n🔍 Confusion Matrix:")
    print("                Predicted")
    print("                Legit  Fraud")
    print(f"   Actual Legit    {cm[0][0]:5d}  {cm[0][1]:5d}")
    print(f"          Fraud    {cm[1][0]:5d}  {cm[1][1]:5d}")

    print("\n📋 Detailed Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["Legit", "Fraud"], digits=4))

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc_auc": roc_auc,
        "confusion_matrix": cm,
    }


def evaluate_model(
    dataset: str,
    model_path: str,
    sample_size: int | None,
    seed: int,
    paysim_source: str | None,
) -> dict:
    print("\n" + "=" * 70)
    print("FRAUD DETECTION MODEL EVALUATION")
    print("=" * 70)

    resolved_model_path = resolve_model_path(dataset, model_path)
    print(f"\n📂 Loading model from {resolved_model_path}...")
    model = load_model(resolved_model_path)
    print("   ✓ Model loaded successfully")

    if dataset == "synthetic":
        print("\n📊 Generating synthetic test data...")
        X_test, y_test = build_synthetic_test_set(seed=seed, samples=sample_size or 1000, feature_dim=165)
        print(f"   Synthetic test set: {len(X_test)} samples")
    elif dataset == "paysim":
        paysim_source = resolve_paysim_source(resolved_model_path, paysim_source)
        if paysim_source == "ml-ready":
            paysim_ml_ready_path = require_dataset_path("paysim_ml_ready.csv")
            print("\n📊 Loading PaySim ML-ready data (balanced)...")
            X_test, y_test = build_paysim_ml_ready_set(str(paysim_ml_ready_path), sample_size, seed)
        else:
            paysim_path = require_dataset_path("paysim.csv")
            print("\n📊 Loading PaySim data (compatibility adapter)...")
            X_test, y_test = build_paysim_test_set(str(paysim_path), sample_size, seed)
        print(f"   PaySim test set: {len(X_test)} samples (source: {paysim_source})")
    else:
        raise ValueError("Unsupported dataset. Use 'synthetic' or 'paysim'.")

    print(f"   - Legit: {(y_test == 0).sum()} ({(y_test == 0).sum() / len(y_test) * 100:.1f}%)")
    print(f"   - Fraud: {(y_test == 1).sum()} ({(y_test == 1).sum() / len(y_test) * 100:.1f}%)")
    print(f"   - Features per sample: {X_test.shape[1]}")

    print("\n🤖 Running model predictions...")
    y_pred = model.predict(X_test)
    y_pred_proba = None
    if hasattr(model, "predict_proba"):
        y_pred_proba = model.predict_proba(X_test)[:, 1]

    print("\n📈 MODEL EVALUATION RESULTS:")
    print("=" * 70)
    metrics = print_metrics(y_test, y_pred, y_pred_proba)

    print("\n🎯 Top 10 Most Important Features:")
    feature_importance = model.feature_importances_
    top_features = np.argsort(feature_importance)[-10:][::-1]
    for rank, feature_idx in enumerate(top_features, 1):
        feature_name = f"f{feature_idx + 1}"
        importance = feature_importance[feature_idx]
        print(f"   {rank:2d}. {feature_name}: {importance:.4f}")

    print("\n" + "=" * 70)
    print("✅ Model evaluation complete!")
    print("=" * 70 + "\n")
    return metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate fraud detection model.")
    parser.add_argument("--dataset", choices=["synthetic", "paysim"], default="synthetic")
    parser.add_argument("--model-path", default="data/fraud_model.json")
    parser.add_argument("--sample-size", type=int, default=None)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--paysim-source", choices=["full", "ml-ready"], default=None)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    evaluate_model(
        dataset=args.dataset,
        model_path=args.model_path,
        sample_size=args.sample_size,
        seed=args.seed,
        paysim_source=args.paysim_source,
    )
