from typing import Dict, List

import numpy as np
import pandas as pd


PAYSIM_TYPE_CATEGORIES: List[str] = [
    "CASH_OUT",
    "TRANSFER",
    "PAYMENT",
    "CASH_IN",
    "DEBIT",
]

PAYSIM_NUMERIC_COLUMNS: List[str] = [
    "step",
    "amount",
    "oldbalanceOrg",
    "newbalanceOrig",
    "oldbalanceDest",
    "newbalanceDest",
    "isFlaggedFraud",
]


def paysim_feature_mapping() -> Dict[str, int]:
    mapping = {
        "step": 0,
        "amount": 1,
        "oldbalanceOrg": 2,
        "newbalanceOrig": 3,
        "oldbalanceDest": 4,
        "newbalanceDest": 5,
        "isFlaggedFraud": 6,
    }
    for idx, category in enumerate(PAYSIM_TYPE_CATEGORIES):
        mapping[f"type_{category}"] = 7 + idx
    return mapping


def _min_max_scale(series: pd.Series) -> np.ndarray:
    values = series.astype(float).to_numpy()
    min_val = float(np.nanmin(values))
    max_val = float(np.nanmax(values))
    if max_val == min_val:
        return np.zeros_like(values, dtype=float)
    return (values - min_val) / (max_val - min_val)


def build_paysim_feature_matrix(df: pd.DataFrame, feature_dim: int = 165) -> np.ndarray:
    mapping = paysim_feature_mapping()
    features = np.zeros((len(df), feature_dim), dtype=float)

    for column in PAYSIM_NUMERIC_COLUMNS:
        if column not in df.columns:
            raise ValueError(f"Missing required PaySim column: {column}")
        idx = mapping[column]
        features[:, idx] = _min_max_scale(df[column])

    if "type" not in df.columns:
        raise ValueError("Missing required PaySim column: type")

    for idx, category in enumerate(PAYSIM_TYPE_CATEGORIES):
        col_name = f"type_{category}"
        mapped_idx = mapping[col_name]
        features[:, mapped_idx] = (df["type"] == category).astype(float).to_numpy()

    return features


def paysim_feature_coverage(feature_dim: int = 165) -> Dict[str, object]:
    mapping = paysim_feature_mapping()
    mapped_indices = sorted(set(mapping.values()))
    return {
        "feature_dim": feature_dim,
        "mapped_count": len(mapped_indices),
        "coverage_ratio": len(mapped_indices) / feature_dim,
        "mapped_features": mapping,
    }
