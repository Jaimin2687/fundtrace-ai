#!/usr/bin/env python3
"""
Evaluate a Paysim-trained XGBoost model on the Paysim alerts CSV.
The script will:
- Load `data/paysim_model.json` (or the provided path)
- Inspect the model for expected feature count
- Load `data/paysim_alerts.csv`, extract numeric features, and label `isFraud`
- If feature counts mismatch, pad/truncate with warnings
- Compute accuracy, precision, recall, f1, roc-auc, confusion matrix
"""
import os
import sys
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, classification_report

MODEL_PATH = 'data/paysim_model.json'
DATA_PATH = 'data/paysim_alerts.csv'


def load_model(path):
    if not os.path.exists(path):
        print(f"ERROR: model file not found: {path}")
        sys.exit(2)
    model = xgb.XGBClassifier()
    model.load_model(path)
    return model


def get_model_expected_features(model):
    # Try sklearn attribute
    n = getattr(model, 'n_features_in_', None)
    if n is not None:
        return int(n)
    # Try booster info
    try:
        booster = model.get_booster()
        num = booster.num_features()
        return int(num)
    except Exception:
        return None


def load_paysim_data(path):
    if not os.path.exists(path):
        print(f"ERROR: data file not found: {path}")
        sys.exit(2)
    df = pd.read_csv(path)
    # Ensure label column exists
    if 'isFraud' not in df.columns:
        print("ERROR: 'isFraud' column not found in paysim CSV")
        sys.exit(2)
    # Extract numeric columns as features (exclude label)
    numeric = df.select_dtypes(include=[np.number]).copy()
    if 'isFraud' in numeric.columns:
        numeric = numeric.drop(columns=['isFraud'])
    X = numeric.values
    y = df['isFraud'].astype(int).values
    return X, y, numeric.columns.tolist()


def align_features(X, expected_n):
    if expected_n is None:
        return X, 'no_check'
    cur = X.shape[1]
    if cur == expected_n:
        return X, 'ok'
    elif cur < expected_n:
        # pad with zeros
        pad = np.zeros((X.shape[0], expected_n - cur), dtype=X.dtype)
        X2 = np.hstack([X, pad])
        return X2, f'padded from {cur} to {expected_n}'
    else:
        # truncate
        X2 = X[:, :expected_n]
        return X2, f'truncated from {cur} to {expected_n}'


def evaluate(model, X, y):
    y_pred = model.predict(X)
    try:
        y_proba = model.predict_proba(X)[:, 1]
    except Exception:
        y_proba = None
    acc = accuracy_score(y, y_pred)
    prec = precision_score(y, y_pred, zero_division=0)
    rec = recall_score(y, y_pred, zero_division=0)
    f1 = f1_score(y, y_pred, zero_division=0)
    roc = roc_auc_score(y, y_proba) if (y_proba is not None) else None
    cm = confusion_matrix(y, y_pred)
    return {
        'accuracy': acc,
        'precision': prec,
        'recall': rec,
        'f1': f1,
        'roc_auc': roc,
        'confusion_matrix': cm,
        'y_proba_exists': y_proba is not None,
        'y_pred': y_pred
    }


def main():
    print('\nInspecting model and Paysim data...')
    model = load_model(MODEL_PATH)
    expected = get_model_expected_features(model)
    print(f'  Model loaded: {MODEL_PATH}')
    print(f'  Expected feature count (from model): {expected}')

    X, y, feature_names = load_paysim_data(DATA_PATH)
    print(f'  Paysim data loaded: {DATA_PATH}')
    print(f'  Numeric feature columns found: {len(feature_names)} -> {feature_names}')
    print(f'  Samples: {len(y)}  Fraud: {(y==1).sum()} Legit: {(y==0).sum()}')

    X_aligned, note = align_features(X, expected)
    print(f'  Feature alignment: {note}')
    print(f'  Using feature matrix shape: {X_aligned.shape}')

    results = evaluate(model, X_aligned, y)

    print('\nEvaluation results:')
    print(f"  Accuracy: {results['accuracy']:.4f} ({results['accuracy']*100:.2f}%)")
    print(f"  Precision: {results['precision']:.4f}")
    print(f"  Recall: {results['recall']:.4f}")
    print(f"  F1: {results['f1']:.4f}")
    if results['roc_auc'] is not None:
        print(f"  ROC-AUC: {results['roc_auc']:.4f}")
    else:
        print('  ROC-AUC: n/a (no predict_proba)')

    cm = results['confusion_matrix']
    if cm.size == 4:
        print('\n  Confusion matrix:')
        print('                Predicted')
        print('                Legit  Fraud')
        print(f'  Actual Legit    {cm[0][0]:5d}  {cm[0][1]:5d}')
        print(f'         Fraud    {cm[1][0]:5d}  {cm[1][1]:5d}')

    print('\nClassification report:')
    print(classification_report(y, results['y_pred'], target_names=['Legit','Fraud'], digits=4))

    # Feature importance if available
    try:
        fi = model.feature_importances_
        top_idx = np.argsort(fi)[-10:][::-1]
        print('\nTop 10 feature importances:')
        for i, idx in enumerate(top_idx, 1):
            print(f"  {i}. f{idx+1} -> {fi[idx]:.4f}")
    except Exception:
        pass

if __name__ == '__main__':
    main()
