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

# Load environment variables from .env file
load_dotenv()


# Module-level model cache
_MODEL_CACHE: Optional[xgb.XGBClassifier] = None
_PAYSIM_DATA: Optional[pd.DataFrame] = None


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


async def run_worker(neo4j_driver: Driver, alert_queue: asyncio.Queue):
    """
    Continuous worker loop that scores transactions and generates alerts.
    
    Every 5 seconds:
    - Queries Neo4j for 10 random Transaction nodes with risk_score == 0.0
    - Generates mock feature vectors (165 random floats)
    - Scores transactions using the trained model
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
            
            # Query Neo4j for unscored transactions
            with neo4j_driver.session() as session:
                result = session.run("""
                    MATCH (t:Transaction)
                    WHERE t.risk_score = 0.0
                    RETURN t.txId AS txId, t.aml_label AS aml_label
                    ORDER BY rand()
                    LIMIT 10
                """)
                transactions = [dict(record) for record in result]
            
            if not transactions:
                print(f"[Worker #{iteration}] No unscored transactions found")
                await asyncio.sleep(5)
                continue
            
            print(f"[Worker #{iteration}] Processing {len(transactions)} transactions...")
            
            alerts_generated = 0
            
            for tx in transactions:
                tx_id = tx['txId']
                aml_label = tx['aml_label']
                
                # Generate mock feature vector (165 random floats)
                # In production, these would be real transaction features
                features_dict = {f'f{i}': random.uniform(0, 1) for i in range(1, 166)}
                
                # Score the transaction
                risk_score = score_transaction(features_dict)
                
                # Update risk_score in Neo4j
                with neo4j_driver.session() as session:
                    session.run("""
                        MATCH (t:Transaction {txId: $txId})
                        SET t.risk_score = $risk_score
                    """, txId=tx_id, risk_score=risk_score)
                
                # Generate alert if high risk
                if risk_score > 0.75:
                    pattern = get_pattern(risk_score)
                    alert = {
                        'txId': tx_id,
                        'risk_score': round(risk_score, 4),
                        'aml_label': aml_label,
                        'pattern': pattern,
                        'timestamp': datetime.now(timezone.utc).isoformat(),
                        'source': 'elliptic'
                    }
                    
                    await alert_queue.put(alert)
                    alerts_generated += 1
                    
                    print(f"  🚨 ALERT: txId={tx_id}, risk={risk_score:.3f}, pattern={pattern}")
            
            print(f"[Worker #{iteration}] Scored {len(transactions)} txs, generated {alerts_generated} alerts")
            
        except Exception as e:
            print(f"[Worker #{iteration}] Error: {str(e)}")
        
        await asyncio.sleep(5)


async def stream_paysim_alerts(alert_queue: asyncio.Queue):
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
            print("   Run data/ingest.py first to generate paysim_alerts.csv")
            return
        
        _PAYSIM_DATA = pd.read_csv(paysim_path)
        print(f"📂 Loaded {len(_PAYSIM_DATA)} PaySim fraud alerts")
    
    iteration = 0
    while True:
        try:
            iteration += 1
            
            # Pick a random fraud transaction
            row = _PAYSIM_DATA.sample(n=1).iloc[0]
            
            # Create alert dict
            alert = {
                'txId': row['nameOrig'],  # Use origin account as txId
                'amount': float(row['amount']),
                'from_account': row['nameOrig'],
                'to_account': row['nameDest'],
                'pattern': row['pattern_label'],
                'risk_score': round(0.85 + random.uniform(0, 0.14), 4),  # 0.85-0.99
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
    if len(sys.argv) > 1 and sys.argv[1] == '--train':
        train_xgboost_model()
    else:
        # Run worker loops
        asyncio.run(main_worker_loop())
