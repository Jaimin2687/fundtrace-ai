"""
ML Worker for FundTrace AI
Trains XGBoost fraud detection model, scores transactions, and streams alerts
"""

import os
import asyncio
import random
from datetime import datetime, timezone
from typing import Dict, Optional

import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from neo4j import Driver
from dotenv import load_dotenv

from backend.core.model_registry import get_model_info

# Load environment variables from .env file
load_dotenv()


# Module-level model cache
_MODEL_CACHE: Optional[xgb.XGBClassifier] = None
_PAYSIM_MODEL_CACHE: Optional[xgb.XGBClassifier] = None
_PAYSIM_DATA: Optional[pd.DataFrame] = None

PAYSIM_FEATURE_COLUMNS = [
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


def train_xgboost_model():
    """
    Train XGBoost fraud detection model on Elliptic dataset.
    
    Loads data/elliptic_ml_ready.csv, trains with 80/20 split,
    saves model to data/fraud_model.json, and prints evaluation metrics.
    """
    print("\n" + "="*60)
    print("TRAINING XGBOOST FRAUD DETECTION MODEL")
    print("="*60)
    
    # Load ML-ready data
    print("\n📂 Loading data/elliptic_ml_ready.csv...")
    df = pd.read_csv('data/elliptic_ml_ready.csv')
    print(f"  Loaded {len(df)} rows")
    
    # Separate features and labels
    feature_cols = [f'f{i}' for i in range(1, 166)]
    X = df[feature_cols].values
    y = df['label'].values
    
    print(f"\n📊 Dataset info:")
    print(f"  Features: {X.shape[1]} columns")
    print(f"  Samples: {X.shape[0]}")
    print(f"  Fraud: {(y == 1).sum():,} ({(y == 1).sum() / len(y) * 100:.1f}%)")
    print(f"  Legit: {(y == 0).sum():,} ({(y == 0).sum() / len(y) * 100:.1f}%)")
    
    # Train/test split (80/20, stratified)
    print("\n🔀 Splitting data (80/20, stratified)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"  Train: {len(X_train)} samples")
    print(f"  Test: {len(X_test)} samples")
    
    # Train XGBoost with scale_pos_weight=9 for class imbalance
    print("\n🤖 Training XGBoost classifier...")
    print("  Parameters: scale_pos_weight=9 (handles ~1:9 fraud:legit ratio)")
    
    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=9,  # Handles class imbalance
        eval_metric='logloss',
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train, verbose=False)
    print("  ✓ Training complete")
    
    # Save model
    model_path = 'data/fraud_model.json'
    model.save_model(model_path)
    print(f"\n💾 Model saved to {model_path}")
    
    # Evaluate on test set
    print("\n📈 EVALUATION ON TEST SET:")
    y_pred = model.predict(X_test)
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Legit', 'Fraud']))
    
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"                Predicted")
    print(f"                Legit  Fraud")
    print(f"Actual Legit    {cm[0][0]:5d}  {cm[0][1]:5d}")
    print(f"       Fraud    {cm[1][0]:5d}  {cm[1][1]:5d}")
    
    print("\n✅ Model training complete!")


def train_paysim_model():
    """
    Train XGBoost fraud detection model on PaySim dataset.

    Loads data/paysim_ml_ready.csv, trains with 80/20 split,
    saves model to data/paysim_model.json, and prints evaluation metrics.
    """
    print("\n" + "=" * 60)
    print("TRAINING PAYSIM XGBOOST MODEL")
    print("=" * 60)

    print("\n📂 Loading data/paysim_ml_ready.csv...")
    df = pd.read_csv('data/paysim_ml_ready.csv')
    print(f"  Loaded {len(df)} rows")

    feature_cols = [
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

    X = df[feature_cols].values
    y = df["label"].values

    print("\n📊 Dataset info:")
    print(f"  Features: {X.shape[1]} columns")
    print(f"  Samples: {X.shape[0]}")
    print(f"  Fraud: {(y == 1).sum():,} ({(y == 1).sum() / len(y) * 100:.1f}%)")
    print(f"  Legit: {(y == 0).sum():,} ({(y == 0).sum() / len(y) * 100:.1f}%)")

    print("\n🔀 Splitting data (80/20, stratified)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"  Train: {len(X_train)} samples")
    print(f"  Test: {len(X_test)} samples")

    pos_weight = (y_train == 0).sum() / max((y_train == 1).sum(), 1)
    print("\n🤖 Training XGBoost classifier...")
    print(f"  Parameters: scale_pos_weight={pos_weight:.2f}")

    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=pos_weight,
        eval_metric="logloss",
        random_state=42,
        n_jobs=-1,
    )

    model.fit(X_train, y_train, verbose=False)
    print("  ✓ Training complete")

    model_path = "data/paysim_model.json"
    model.save_model(model_path)
    print(f"\n💾 Model saved to {model_path}")

    print("\n📈 EVALUATION ON TEST SET:")
    y_pred = model.predict(X_test)

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Legit", "Fraud"]))

    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print("                Predicted")
    print("                Legit  Fraud")
    print(f"Actual Legit    {cm[0][0]:5d}  {cm[0][1]:5d}")
    print(f"       Fraud    {cm[1][0]:5d}  {cm[1][1]:5d}")

    print("\n✅ PaySim model training complete!")


def score_transaction(features_dict: Dict[str, float]) -> float:
    """
    Score a transaction using the trained fraud detection model.
    
    Args:
        features_dict: Dictionary with keys f1..f165 containing feature values
        
    Returns:
        Risk score between 0.0 and 1.0
    """
    global _MODEL_CACHE
    
    # Load model if not cached
    if _MODEL_CACHE is None:
        model_path = 'data/fraud_model.json'
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}. Run train_xgboost_model() first.")
        
        _MODEL_CACHE = xgb.XGBClassifier()
        _MODEL_CACHE.load_model(model_path)
    
    # Prepare feature vector (f1..f165)
    feature_cols = [f'f{i}' for i in range(1, 166)]
    features = np.array([[features_dict.get(col, 0.0) for col in feature_cols]])
    
    # Get probability of fraud (class 1)
    risk_score = float(_MODEL_CACHE.predict_proba(features)[0, 1])
    
    return risk_score


def _load_paysim_model(model_path: str) -> xgb.XGBClassifier:
    global _PAYSIM_MODEL_CACHE
    if _PAYSIM_MODEL_CACHE is None:
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}. Run train_paysim_model() first.")
        _PAYSIM_MODEL_CACHE = xgb.XGBClassifier()
        _PAYSIM_MODEL_CACHE.load_model(model_path)
    return _PAYSIM_MODEL_CACHE


def _build_paysim_feature_vector(row: pd.Series) -> np.ndarray:
    type_value = row["type"]
    features = [
        float(row["step"]),
        float(row["amount"]),
        float(row["oldbalanceOrg"]),
        float(row["newbalanceOrig"]),
        float(row["oldbalanceDest"]),
        float(row["newbalanceDest"]),
        float(row.get("isFlaggedFraud", 0.0)),
        1.0 if type_value == "CASH_OUT" else 0.0,
        1.0 if type_value == "TRANSFER" else 0.0,
        1.0 if type_value == "PAYMENT" else 0.0,
        1.0 if type_value == "CASH_IN" else 0.0,
        1.0 if type_value == "DEBIT" else 0.0,
    ]
    return np.array(features, dtype=float)


def _build_paysim_vector_from_props(props: Dict[str, float]) -> np.ndarray:
    type_value = props.get("type") or props.get("tx_type") or props.get("type_value")
    return np.array(
        [
            float(props.get("step", 0.0)),
            float(props.get("amount", 0.0)),
            float(props.get("oldbalanceOrg", 0.0)),
            float(props.get("newbalanceOrig", 0.0)),
            float(props.get("oldbalanceDest", 0.0)),
            float(props.get("newbalanceDest", 0.0)),
            float(props.get("isFlaggedFraud", 0.0)),
            float(props.get("type_CASH_OUT", 1.0 if type_value == "CASH_OUT" else 0.0)),
            float(props.get("type_TRANSFER", 1.0 if type_value == "TRANSFER" else 0.0)),
            float(props.get("type_PAYMENT", 1.0 if type_value == "PAYMENT" else 0.0)),
            float(props.get("type_CASH_IN", 1.0 if type_value == "CASH_IN" else 0.0)),
            float(props.get("type_DEBIT", 1.0 if type_value == "DEBIT" else 0.0)),
        ],
        dtype=float,
    )


def _build_elliptic_features(props: Dict[str, float]) -> Dict[str, float]:
    return {f"f{i}": float(props.get(f"f{i}", 0.0)) for i in range(1, 166)}


async def run_worker(neo4j_driver: Driver, alert_queue: asyncio.Queue):
    """
    Continuous worker loop that scores transactions and generates alerts.
    
    Every 5 seconds:
    - Queries Neo4j for 10 random Transaction nodes with risk_score == 0.0
    - Scores transactions using real feature properties stored on the node
    - Updates risk_score in Neo4j
    - Puts high-risk alerts (>0.75) on the alert queue
    
    Args:
        neo4j_driver: Neo4j driver instance
        alert_queue: Async queue for alerts
    """
    print("\n" + "="*60)
    print("STARTING TRANSACTION SCORING WORKER")
    print("="*60)
    print("  Interval: 5 seconds")
    print("  Batch size: 10 transactions")
    print("  Alert threshold: risk_score > 0.75")
    print()
    
    model_info = get_model_info()
    if model_info.source == "paysim":
        model = _load_paysim_model(model_info.path)
        def score_props(props: Dict[str, float]) -> float:
            features = _build_paysim_vector_from_props(props)
            return float(model.predict_proba(features.reshape(1, -1))[0, 1])
    else:
        def score_props(props: Dict[str, float]) -> float:
            return score_transaction(_build_elliptic_features(props))

    # Pattern assignment based on risk score ranges
    def get_pattern(risk_score: float) -> str:
        if risk_score >= 0.90:
            return "Round-tripping"
        elif risk_score >= 0.85:
            return "Layering"
        elif risk_score >= 0.80:
            return "Structuring"
        else:
            return "Dormant Account Activated"
    
    iteration = 0
    while True:
        try:
            iteration += 1
            
            # Query Neo4j for transactions that haven't been processed by this worker.
            # PaySim ingest already sets risk_score at ingest time, so we look for
            # transactions that don't have the 'scored_by_worker' flag yet.
            with neo4j_driver.session() as session:
                result = session.run(
                    """
                    MATCH (t:Transaction)
                    WHERE t.scored_by_worker IS NULL
                    RETURN t AS tx
                    ORDER BY rand()
                    LIMIT 10
                    """
                )
                transactions = [record["tx"] for record in result]
            
            if not transactions:
                if iteration <= 3 or iteration % 60 == 0:
                    print(f"[Worker #{iteration}] All transactions already processed")
                await asyncio.sleep(5)
                continue
            
            print(f"[Worker #{iteration}] Processing {len(transactions)} transactions...")
            
            alerts_generated = 0
            batch_updates = []  # Collect updates for batch write
            
            for tx in transactions:
                props = dict(tx)
                tx_id = props.get("txId") or props.get("tx_id")
                if not tx_id:
                    continue

                aml_label = props.get("aml_label")

                # Score the transaction using real feature properties
                try:
                    risk_score = score_props(props)
                except Exception as exc:
                    print(f"[Worker #{iteration}] Failed to score {tx_id}: {exc}")
                    continue
                
                resolved_label = "fraud" if risk_score > 0.75 else (aml_label or "legit")
                batch_updates.append({
                    "txId": str(tx_id),
                    "risk_score": risk_score,
                    "aml_label": resolved_label,
                })

                # Generate alert if high risk
                if risk_score > 0.75:
                    pattern = get_pattern(risk_score)
                    amount = props.get("amount")
                    alert = {
                        "txId": str(tx_id),
                        "risk_score": round(risk_score, 4),
                        "aml_label": aml_label or "fraud",
                        "pattern": pattern,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "amount": float(amount) if amount is not None else None,
                        "source": model_info.source,
                    }
                    
                    await alert_queue.put(alert)
                    alerts_generated += 1
                    
                    print(f"  🚨 ALERT: txId={tx_id}, risk={risk_score:.3f}, pattern={pattern}")
            
            # Batch update Neo4j in a single query
            if batch_updates:
                with neo4j_driver.session() as session:
                    session.run(
                        """
                        UNWIND $updates AS u
                        MATCH (t:Transaction)
                        WHERE t.txId = u.txId OR t.tx_id = u.txId
                        SET t.risk_score = u.risk_score,
                            t.aml_label = u.aml_label,
                            t.scored_by_worker = true
                        """,
                        updates=batch_updates,
                    )

            print(f"[Worker #{iteration}] Scored {len(transactions)} txs, generated {alerts_generated} alerts")
            
        except Exception as e:
            print(f"[Worker #{iteration}] Error: {str(e)}")
        
        await asyncio.sleep(5)


async def stream_paysim_alerts(alert_queue: asyncio.Queue, use_model: bool = False):
    """
    Stream PaySim fraud alerts to the alert queue.
    
    Every 3 seconds:
    - Picks a random row from data/paysim_alerts.csv
    - Creates an alert dict with transaction details
    - Puts alert on the queue
    
    Args:
        alert_queue: Async queue for alerts
    """
    global _PAYSIM_DATA
    
    print("\n" + "="*60)
    print("STARTING PAYSIM ALERT STREAMER")
    print("="*60)
    print("  Interval: 3 seconds")
    print("  Source: data/paysim_alerts.csv")
    print()
    
    # Load PaySim alerts once
    if _PAYSIM_DATA is None:
        paysim_path = 'data/paysim_alerts.csv'
        if not os.path.exists(paysim_path):
            print(f"❌ PaySim alerts not found at {paysim_path}")
            print("   Run data/prepare_paysim.py first to generate paysim_alerts.csv")
            return

        _PAYSIM_DATA = pd.read_csv(paysim_path)
        print(f"📂 Loaded {len(_PAYSIM_DATA)} PaySim fraud alerts")

    model_info = None
    model = None
    if use_model:
        model_info = get_model_info()
        if model_info.source != "paysim":
            print("⚠ PaySim model requested but MODEL_SOURCE is not paysim. Streaming with mock scores.")
            use_model = False
        else:
            model = _load_paysim_model(model_info.path)
            print(f"🤖 Using PaySim model at {model_info.path} for risk scoring")
    
    iteration = 0
    while True:
        try:
            iteration += 1
            
            # Pick a random fraud transaction
            row = _PAYSIM_DATA.sample(n=1).iloc[0]
            
            # Create alert dict
            if use_model and model is not None:
                features = _build_paysim_feature_vector(row)
                risk_score = float(model.predict_proba(features.reshape(1, -1))[0, 1])
            else:
                risk_score = 0.85 + random.uniform(0, 0.14)

            tx_id = row.get("txId")
            if not tx_id:
                tx_id = f"{row['nameOrig']}_{row['nameDest']}_{row['step']}_{row.name}"
            alert = {
                'txId': str(tx_id),
                'amount': float(row['amount']),
                'from_account': row['nameOrig'],
                'to_account': row['nameDest'],
                'pattern': row['pattern_label'],
                'risk_score': round(risk_score, 4),
                'source': 'paysim',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            await alert_queue.put(alert)
            
            print(f"[PaySim #{iteration}] Alert: {alert['from_account']} → {alert['to_account']}, "
                  f"${alert['amount']:,.2f}, pattern={alert['pattern']}, risk={alert['risk_score']:.3f}")
            
        except Exception as e:
            print(f"[PaySim #{iteration}] Error: {str(e)}")
        
        await asyncio.sleep(3)


async def main_worker_loop():
    """
    Main entry point for running both worker loops concurrently.
    
    Starts:
    - Transaction scoring worker (every 5 seconds)
    - PaySim alert streamer (every 3 seconds)
    
    Both workers share an alert queue.
    """
    # Get Neo4j credentials from environment
    neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
    neo4j_password = os.getenv('NEO4J_PASSWORD')
    
    if not neo4j_password:
        raise ValueError("NEO4J_PASSWORD environment variable not set")
    
    # Create Neo4j driver
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    
    # Create shared alert queue
    alert_queue = asyncio.Queue()
    
    print("\n" + "="*60)
    print("FUNDTRACE AI - ML WORKER")
    print("="*60)
    print(f"Neo4j: {neo4j_uri}")
    print(f"Alert queue: shared between workers")
    print()
    
    try:
        # Run both workers concurrently
        await asyncio.gather(
            run_worker(driver, alert_queue),
            stream_paysim_alerts(alert_queue)
        )
    finally:
        driver.close()


if __name__ == "__main__":
    import sys
    
    # Check if training mode
    if len(sys.argv) > 1:
        if sys.argv[1] == '--train':
            train_xgboost_model()
        elif sys.argv[1] == '--train-paysim':
            train_paysim_model()
        else:
            print("Usage:")
            print("  python backend/worker/ml_worker.py --train")
            print("  python backend/worker/ml_worker.py --train-paysim")
            print("  python backend/worker/ml_worker.py")
            sys.exit(1)
    else:
        asyncio.run(main_worker_loop())
