import argparse
import os
import time
from datetime import datetime, timezone

import pandas as pd
import requests
import xgboost as xgb

from backend.core.config import get_settings
from backend.db.neo4j_client import Neo4jClient

FEATURE_QUERY = """
MATCH (a:Account)
CALL (a) {
    OPTIONAL MATCH (a)-[t:TRANSACTION]->()
    RETURN count(t) AS out_count,
           coalesce(sum(t.amount), 0) AS out_amount,
           coalesce(avg(t.amount), 0) AS out_avg,
           sum(CASE WHEN t.is_structuring THEN 1 ELSE 0 END) AS out_structuring
}
CALL (a) {
    OPTIONAL MATCH ()-[t:TRANSACTION]->(a)
    RETURN count(t) AS in_count,
           coalesce(sum(t.amount), 0) AS in_amount,
           coalesce(avg(t.amount), 0) AS in_avg,
           sum(CASE WHEN t.is_structuring THEN 1 ELSE 0 END) AS in_structuring
}
RETURN a.account_id AS account_id,
       a.account_type AS account_type,
       coalesce(a.kyc_risk_baseline, 0) AS kyc_risk_baseline,
       coalesce(a.total_volume, 0) AS total_volume,
    coalesce(a.is_fraud, a.aml_label, a.fraud_label, null) AS aml_label,
       out_count, out_amount, out_avg, out_structuring,
       in_count, in_amount, in_avg, in_structuring
"""

FOCUS_QUERY = """
MATCH (start:Account {account_id: $cluster_id})
CALL (start) {
    MATCH (start)-[:TRANSACTION*1..3]-(n:Account)
    WITH start, collect(DISTINCT n) AS neighbors
    RETURN neighbors + [start] AS nodes
}
WITH nodes[0..$node_limit] AS limited_nodes
UNWIND limited_nodes AS node
WITH collect(DISTINCT node) AS nodes
MATCH (a:Account)-[t:TRANSACTION]->(b:Account)
WHERE a IN nodes AND b IN nodes
RETURN nodes, collect(DISTINCT t) AS rels
"""


def _fetch_features(driver) -> pd.DataFrame:
    with driver.session() as session:
        records = session.run(FEATURE_QUERY).data()
    if not records:
        return pd.DataFrame()
    return pd.DataFrame(records)


def _prepare_features(frame: pd.DataFrame) -> pd.DataFrame:
    numeric_cols = [
        "kyc_risk_baseline",
        "total_volume",
        "out_count",
        "out_amount",
        "out_avg",
        "out_structuring",
        "in_count",
        "in_amount",
        "in_avg",
        "in_structuring",
    ]
    for col in numeric_cols:
        frame[col] = frame[col].fillna(0).astype(float)

    frame["out_in_ratio"] = (frame["out_amount"] + 1) / (frame["in_amount"] + 1)
    frame["out_structuring_rate"] = frame["out_structuring"] / frame["out_count"].clip(lower=1)
    frame["in_structuring_rate"] = frame["in_structuring"] / frame["in_count"].clip(lower=1)
    frame["flow_balance"] = (
        (frame["out_amount"] - frame["in_amount"]).abs()
        / (frame["out_amount"] + frame["in_amount"] + 1)
    )

    ratio_cols = [
        "out_in_ratio",
        "out_structuring_rate",
        "in_structuring_rate",
        "flow_balance",
    ]

    types = pd.get_dummies(frame["account_type"].fillna("Unknown"), prefix="type")
    features = pd.concat([frame[numeric_cols + ratio_cols], types], axis=1)
    return features.fillna(0.0)


def _coerce_label(value) -> int | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return int(value != 0)
    text = str(value).strip().lower()
    if text in {"true", "t", "yes", "y", "fraud", "aml", "1"}:
        return 1
    if text in {"false", "f", "no", "n", "clear", "0"}:
        return 0
    return None


def _build_labels(frame: pd.DataFrame) -> pd.Series:
    if "aml_label" in frame.columns:
        coerced = frame["aml_label"].map(_coerce_label)
        if coerced.notna().any():
            return coerced.fillna(0).astype(int)

    out_structuring_rate = frame["out_structuring"] / frame["out_count"].clip(lower=1)
    flow_balance = (
        (frame["out_amount"] - frame["in_amount"]).abs()
        / (frame["out_amount"] + frame["in_amount"] + 1)
    )
    vol_cutoff = frame["total_volume"].quantile(0.90)
    out_cutoff = frame["out_amount"].quantile(0.90)

    labels = (
        ((out_structuring_rate > 0.35) & (frame["out_count"] >= 6))
        | ((frame["in_count"] >= 5) & (frame["out_count"] >= 5) & (flow_balance < 0.25))
        | (frame["total_volume"] >= vol_cutoff)
        | (frame["out_amount"] >= out_cutoff)
    ).astype(int)

    if labels.sum() == 0 and len(frame.index) > 0:
        top_count = max(1, int(len(frame.index) * 0.05))
        top_index = frame["total_volume"].nlargest(top_count).index
        labels.loc[top_index] = 1

    return labels


def _train_model(frame: pd.DataFrame):
    features = _prepare_features(frame)
    labels = _build_labels(frame)

    if labels.nunique() < 2:
        return None, features

    pos_weight = (labels == 0).sum() / max((labels == 1).sum(), 1)
    model = xgb.XGBClassifier(
        n_estimators=250,
        max_depth=5,
        learning_rate=0.08,
        subsample=0.9,
        colsample_bytree=0.9,
        reg_lambda=1.0,
        scale_pos_weight=pos_weight,
        eval_metric="logloss",
        random_state=42,
        n_jobs=2,
    )
    model.fit(features, labels)
    return model, features


def _normalize(series: pd.Series) -> pd.Series:
    min_val = float(series.min())
    max_val = float(series.max())
    if max_val - min_val < 1e-9:
        return pd.Series(0.0, index=series.index)
    return (series - min_val) / (max_val - min_val)


def _heuristic_score(frame: pd.DataFrame) -> pd.Series:
    out_structuring_rate = frame["out_structuring"] / frame["out_count"].clip(lower=1)
    flow_balance = (
        (frame["out_amount"] - frame["in_amount"]).abs()
        / (frame["out_amount"] + frame["in_amount"] + 1)
    )

    score = (
        0.35 * _normalize(frame["kyc_risk_baseline"])
        + 0.25 * _normalize(out_structuring_rate)
        + 0.20 * _normalize(frame["total_volume"])
        + 0.10 * _normalize(frame["out_amount"])
        + 0.10 * _normalize(flow_balance)
    )
    return score * 100


def _score(model, features: pd.DataFrame, frame: pd.DataFrame) -> pd.Series:
    if model is None:
        return _heuristic_score(frame)
    probabilities = model.predict_proba(features)[:, 1]
    return pd.Series(probabilities * 100)


def _fetch_focus(driver, account_id: str, node_limit: int = 150) -> tuple[list, list]:
    with driver.session() as session:
        result = session.run(
            FOCUS_QUERY, cluster_id=account_id, node_limit=node_limit
        ).single()
        if result is None:
            return [], []
        nodes = result["nodes"] or []
        rels = result["rels"] or []

    node_out = [
        {
            "account_id": str(node.get("account_id")),
            "account_type": str(node.get("account_type")),
            "kyc_risk_baseline": float(node.get("kyc_risk_baseline", 0.0)),
            "total_volume": float(node.get("total_volume", 0.0)),
        }
        for node in nodes
    ]
    edge_out = [
        {
            "tx_id": str(rel.get("tx_id")),
            "source_id": str(rel.get("source_id")),
            "target_id": str(rel.get("target_id")),
            "amount": float(rel.get("amount", 0.0)),
            "timestamp": str(rel.get("timestamp")),
            "is_structuring": bool(rel.get("is_structuring", False)),
        }
        for rel in rels
    ]
    return node_out, edge_out


def _build_narrative(row: pd.Series) -> tuple[str, str]:
    structuring_ratio = 0.0
    if row["out_count"]:
        structuring_ratio = row["out_structuring"] / max(row["out_count"], 1)

    if structuring_ratio > 0.35 and row["out_count"] >= 6:
        threat_type = "Structured Smurfing"
        narrative = (
            f"Account {row['account_id']} initiated repeated small transfers across "
            f"{int(row['out_count'])} outbound hops with {structuring_ratio:.0%} structuring flags."
        )
    elif row["in_count"] >= 5 and row["out_count"] >= 5:
        threat_type = "Rapid Layering"
        narrative = (
            f"Account {row['account_id']} shows symmetric in/out flow with "
            f"{int(row['in_count'])} inbound and {int(row['out_count'])} outbound transfers."
        )
    else:
        threat_type = "Anomalous Volume"
        narrative = (
            f"Account {row['account_id']} deviates from peer volume baselines with "
            f"{row['total_volume']:.2f} total movement."
        )

    return threat_type, narrative


def _post_alert(api_base: str, api_key: str, payload: dict) -> None:
    url = f"{api_base}/api/v1/stream/ingest"
    response = requests.post(
        url,
        json=payload,
        headers={"x-api-key": api_key},
        timeout=10,
    )
    response.raise_for_status()


def _post_status(api_base: str, api_key: str, payload: dict) -> None:
    url = f"{api_base}/api/v1/stream/status"
    response = requests.post(
        url,
        json=payload,
        headers={"x-api-key": api_key},
        timeout=10,
    )
    response.raise_for_status()


def run_once(driver, api_base: str, api_key: str) -> int:
    frame = _fetch_features(driver)
    if frame.empty:
        return 0

    model, features = _train_model(frame)
    frame["risk_score"] = _score(model, features, frame)

    percentile = float(os.getenv("ML_ALERT_PERCENTILE", "95"))
    cutoff = frame["risk_score"].quantile(percentile / 100.0)
    max_alerts = int(os.getenv("ML_MAX_ALERTS", "25"))

    candidates = frame[frame["risk_score"] >= cutoff].nlargest(max_alerts, "risk_score")

    alerts_sent = 0
    for _, row in candidates.iterrows():
        nodes, edges = _fetch_focus(driver, row["account_id"])
        threat_type, narrative = _build_narrative(row)

        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cluster_id": row["account_id"],
            "risk_score": round(float(row["risk_score"]), 2),
            "threat_type": threat_type,
            "narrative": narrative,
            "nodes": nodes,
            "edges": edges,
        }
        _post_alert(api_base, api_key, payload)
        alerts_sent += 1

    status_payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "alerts_sent": alerts_sent,
        "model_version": "xgboost-v1",
        "run_mode": os.getenv("ML_RUN_MODE", "heuristic-supervised"),
    }
    _post_status(api_base, api_key, status_payload)
    return alerts_sent


def main() -> None:
    parser = argparse.ArgumentParser(description="FundTrace ML alert worker")
    parser.add_argument("--once", action="store_true", help="Run one cycle and exit")
    parser.add_argument("--interval", type=int, default=30, help="Seconds between runs")
    args = parser.parse_args()

    settings = get_settings()
    api_base = settings.NEXT_PUBLIC_API_BASE_URL or "http://localhost:8000"

    client = Neo4jClient(settings)
    client.connect()

    try:
        while True:
            sent = run_once(client.driver, api_base, settings.API_KEY)
            print(f"[ml-worker] alerts_sent={sent}")
            if args.once:
                break
            time.sleep(args.interval)
    finally:
        client.close()


if __name__ == "__main__":
    main()
