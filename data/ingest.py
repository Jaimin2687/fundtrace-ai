"""
Data Ingestion Pipeline for FundTrace AI
Handles Elliptic dataset loading to Neo4j, PaySim pattern labeling, and ML feature preparation
"""

import os
import sys
from typing import Dict, List

import pandas as pd
from neo4j import GraphDatabase
from dotenv import load_dotenv

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
if DATA_DIR not in sys.path:
    sys.path.append(DATA_DIR)

from path_utils import require_dataset_path  # noqa: E402

# Load environment variables from .env file
load_dotenv()


class Neo4jLoader:
    """Handles connection and batch loading to Neo4j"""
    
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def create_index(self):
        """Create index on Transaction.txId for performance"""
        with self.driver.session() as session:
            session.run("CREATE INDEX IF NOT EXISTS FOR (t:Transaction) ON (t.txId)")
            print("✓ Created index on Transaction.txId")

    def clear_graph(self):
        """Remove all nodes and relationships in the database."""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        print("✓ Cleared existing Neo4j graph")
    
    def batch_create_transactions(self, transactions: List[Dict], batch_size: int = 500):
        """Create Transaction nodes using UNWIND batching"""
        with self.driver.session() as session:
            query = """
            UNWIND $batch AS tx
            CREATE (t:Transaction)
            SET t = tx
            """
            
            total = len(transactions)
            for i in range(0, total, batch_size):
                batch = transactions[i:i + batch_size]
                session.run(query, batch=batch)
                print(f"  Loaded {min(i + batch_size, total)}/{total} transactions", end='\r')
            print(f"\n✓ Created {total} Transaction nodes")
    
    def batch_create_relationships(
        self,
        edges: List[Dict],
        batch_size: int = 500,
        rel_type: str = "SENT_TO",
    ):
        """Create relationships using UNWIND batching"""
        if rel_type not in {"SENT_TO", "TRANSFERRED_TO"}:
            raise ValueError("rel_type must be SENT_TO or TRANSFERRED_TO")
        with self.driver.session() as session:
            query = f"""
            UNWIND $batch AS edge
            MATCH (t1:Transaction {{txId: edge.txId1}})
            MATCH (t2:Transaction {{txId: edge.txId2}})
            CREATE (t1)-[:{rel_type}]->(t2)
            """
            
            total = len(edges)
            for i in range(0, total, batch_size):
                batch = edges[i:i + batch_size]
                session.run(query, batch=batch)
                print(f"  Created {min(i + batch_size, total)}/{total} relationships", end='\r')
            print(f"\n✓ Created {total} {rel_type} relationships")


def _get_int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default


def _get_bool_env(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y"}


def _add_paysim_tx_id(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "txId" in df.columns:
        return df
    df["txId"] = (
        df["nameOrig"].astype(str)
        + "_"
        + df["nameDest"].astype(str)
        + "_"
        + df["step"].astype(str)
        + "_"
        + df.index.astype(str)
    )
    return df
    try:
        return int(raw)
    except ValueError:
        return default


def load_elliptic_to_neo4j(reset_graph: bool = False):
    """Task 1: Load Elliptic dataset into Neo4j"""
    print("\n" + "="*60)
    print("TASK 1: LOADING ELLIPTIC DATA TO NEO4J")
    print("="*60)
    
    # Get Neo4j credentials from environment
    neo4j_uri = os.getenv('NEO4J_URI')
    neo4j_user = os.getenv('NEO4J_USER')
    neo4j_password = os.getenv('NEO4J_PASSWORD')
    
    if not all([neo4j_uri, neo4j_user, neo4j_password]):
        raise ValueError("Missing Neo4j credentials. Set NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD")
    
    try:
        # Read data files
        print("\n📂 Reading Elliptic data files...")
        classes_path = require_dataset_path('elliptic_txs_classes.csv')
        edgelist_path = require_dataset_path('elliptic_txs_edgelist.csv')
        features_path = require_dataset_path('elliptic_txs_features.csv')
        classes_df = pd.read_csv(classes_path)
        edgelist_df = pd.read_csv(edgelist_path)
        features_df = pd.read_csv(features_path)
        
        print(f"  Classes: {len(classes_df)} rows")
        print(f"  Edges: {len(edgelist_df)} rows")
        print(f"  Features: {len(features_df)} rows")
        
        # Prepare transaction data
        print("\n🔧 Preparing transaction data...")
        
        # Merge classes with features (features has time_step in column 1)
        features_df.columns = ['txId', 'time_step'] + [f'f{i}' for i in range(1, len(features_df.columns) - 1)]
        feature_cols = [col for col in features_df.columns if col.startswith('f')]
        
        # Merge with classes
        tx_data = features_df[['txId', 'time_step', *feature_cols]].merge(
            classes_df, 
            left_on='txId', 
            right_on='txId', 
            how='left'
        )
        
        # Map class to aml_label
        def map_class(cls):
            if pd.isna(cls) or cls == 'unknown':
                return 'unknown'
            elif cls == '1':
                return 'fraud'
            elif cls == '2':
                return 'legit'
            else:
                return 'unknown'
        
        tx_data['aml_label'] = tx_data['class'].astype(str).apply(map_class)
        tx_data['risk_score'] = 0.0
        
        # Convert to list of dicts for Neo4j
        transactions = tx_data[['txId', 'aml_label', 'time_step', 'risk_score', *feature_cols]].to_dict('records')
        
        # Prepare edges
        edges = edgelist_df.to_dict('records')
        
        # Connect to Neo4j and load data
        print(f"\n🔌 Connecting to Neo4j at {neo4j_uri}...")
        loader = Neo4jLoader(neo4j_uri, neo4j_user, neo4j_password)
        
        try:
            if reset_graph:
                loader.clear_graph()
            # Create index
            loader.create_index()
            
            # Load transactions
            print(f"\n📥 Loading {len(transactions)} transactions (batch size: 500)...")
            loader.batch_create_transactions(transactions)
            
            # Load relationships
            print(f"\n🔗 Creating {len(edges)} relationships (batch size: 500)...")
            loader.batch_create_relationships(edges, rel_type="SENT_TO")
            
            print("\n✅ Elliptic data successfully loaded to Neo4j!")
            
        finally:
            loader.close()
    
    except Exception as e:
        print(f"\n❌ Error loading Elliptic data: {str(e)}")
        raise


def load_paysim_to_neo4j(reset_graph: bool = False):
    """Task: Load PaySim dataset into Neo4j as Transaction nodes."""
    print("\n" + "="*60)
    print("TASK 1: LOADING PAYSIM DATA TO NEO4J")
    print("="*60)

    neo4j_uri = os.getenv('NEO4J_URI')
    neo4j_user = os.getenv('NEO4J_USER')
    neo4j_password = os.getenv('NEO4J_PASSWORD')

    if not all([neo4j_uri, neo4j_user, neo4j_password]):
        raise ValueError("Missing Neo4j credentials. Set NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD")

    try:
        print("\n📂 Reading PaySim data file...")
        paysim_path = require_dataset_path('paysim.csv')

        max_tx = _get_int_env("PAYSIM_MAX_TX", 150000)
        if max_tx <= 0:
            df = pd.read_csv(paysim_path)
        else:
            max_tx = min(max_tx, 190000)
            df = pd.read_csv(paysim_path, nrows=max_tx)

        print(f"  Rows loaded: {len(df)}")

        print("\n🔧 Preparing transaction data...")
        df = df.copy().reset_index(drop=True)
        df = _add_paysim_tx_id(df)
        df["aml_label"] = df["isFraud"].apply(lambda value: "fraud" if int(value) == 1 else "legit")
        df["risk_score"] = df["isFraud"].apply(lambda value: 0.95 if int(value) == 1 else 0.05)
        df["time_step"] = df["step"].astype(int)
        df["tx_type"] = df["type"].astype(str)

        transactions = df[
            ["txId", "aml_label", "time_step", "risk_score", "amount", "tx_type", "nameOrig", "nameDest"]
        ].to_dict('records')

        print("\n🔗 Building transaction edges...")
        df_sorted = df.sort_values(["step", "nameOrig", "nameDest", "txId"], kind="mergesort")
        last_tx_by_account: Dict[str, str] = {}
        edges: List[Dict[str, str]] = []
        for row in df_sorted.itertuples(index=False):
            current_tx = row.txId
            origin = row.nameOrig
            dest = row.nameDest
            prev_origin_tx = last_tx_by_account.get(origin)
            prev_dest_tx = last_tx_by_account.get(dest)
            if prev_origin_tx and prev_origin_tx != current_tx:
                edges.append({"txId1": prev_origin_tx, "txId2": current_tx})
            if prev_dest_tx and prev_dest_tx not in {prev_origin_tx, current_tx}:
                edges.append({"txId1": prev_dest_tx, "txId2": current_tx})
            last_tx_by_account[origin] = current_tx
            last_tx_by_account[dest] = current_tx

        print(f"  Prepared {len(transactions)} transactions, {len(edges)} edges")

        print(f"\n🔌 Connecting to Neo4j at {neo4j_uri}...")
        loader = Neo4jLoader(neo4j_uri, neo4j_user, neo4j_password)

        try:
            if reset_graph:
                loader.clear_graph()
            loader.create_index()
            print(f"\n📥 Loading {len(transactions)} transactions (batch size: 500)...")
            loader.batch_create_transactions(transactions)

            print(f"\n🔗 Creating {len(edges)} relationships (batch size: 500)...")
            loader.batch_create_relationships(edges, rel_type="TRANSFERRED_TO")

            with loader.driver.session() as session:
                stats = session.run(
                    """
                    MATCH (t:Transaction)
                    OPTIONAL MATCH ()-[r:TRANSFERRED_TO]->()
                    RETURN count(t) AS total_nodes, count(r) AS total_edges
                    """
                ).single()
            total_nodes = int(stats["total_nodes"] or 0)
            total_edges = int(stats["total_edges"] or 0)
            if total_edges == 0:
                raise RuntimeError("PaySim ingestion created zero edges; verify data and retry.")
            print(f"✓ Verified graph: {total_nodes} nodes, {total_edges} edges")

            print("\n✅ PaySim data successfully loaded to Neo4j!")
        finally:
            loader.close()

    except Exception as e:
        print(f"\n❌ Error loading PaySim data: {str(e)}")
        raise


def label_paysim_patterns():
    """Task 2: Label PaySim patterns and save fraud alerts"""
    print("\n" + "="*60)
    print("TASK 2: LABELING PAYSIM PATTERNS")
    print("="*60)
    
    try:
        print("\n📂 Reading paysim.csv...")
        paysim_path = require_dataset_path('paysim.csv')
        max_tx = _get_int_env("PAYSIM_MAX_TX", 150000)
        if max_tx <= 0:
            df = pd.read_csv(paysim_path)
        else:
            max_tx = min(max_tx, 190000)
            df = pd.read_csv(paysim_path, nrows=max_tx)
        print(f"  Total rows: {len(df)}")
        
        # Apply pattern labeling rules
        print("\n🏷️  Applying pattern labels...")
        
        def assign_pattern(row):
            # Rule 1: Structuring
            if row['amount'] < 200000 and row['type'] == 'TRANSFER':
                return 'Structuring'
            # Rule 2: Dormant Account Activated
            elif row['oldbalanceDest'] == 0 and row['type'] == 'TRANSFER':
                return 'Dormant Account Activated'
            # Rule 3: Layering - Cash Out
            elif row['type'] == 'CASH_OUT' and row['isFraud'] == 1:
                return 'Layering - Cash Out'
            # Rule 4: Default for fraud
            elif row['isFraud'] == 1:
                return 'Suspicious Transfer'
            else:
                return None
        
        df = df.copy().reset_index(drop=True)
        df = _add_paysim_tx_id(df)
        df['pattern_label'] = df.apply(assign_pattern, axis=1)
        
        # Filter fraud rows only
        fraud_df = df[df['isFraud'] == 1].copy()
        
        # Save to CSV
        output_path = 'data/paysim_alerts.csv'
        fraud_df.to_csv(output_path, index=False)
        print(f"\n💾 Saved fraud alerts to {output_path}")
        
        # Print summary
        print("\n📊 SUMMARY:")
        print(f"  Total rows: {len(df):,}")
        print(f"  Fraud rows: {len(fraud_df):,}")
        print(f"\n  Pattern distribution:")
        pattern_counts = fraud_df['pattern_label'].value_counts()
        for pattern, count in pattern_counts.items():
            print(f"    {pattern}: {count:,}")
        
        print("\n✅ PaySim pattern labeling complete!")
    
    except Exception as e:
        print(f"\n❌ Error labeling PaySim patterns: {str(e)}")
        raise


def build_feature_matrix():
    """Task 3: Build ML-ready feature matrix from Elliptic data"""
    print("\n" + "="*60)
    print("TASK 3: BUILDING FEATURE MATRIX FOR ML")
    print("="*60)
    
    try:
        print("\n📂 Reading Elliptic data files...")
        features_path = require_dataset_path('elliptic_txs_features.csv')
        classes_path = require_dataset_path('elliptic_txs_classes.csv')
        features_df = pd.read_csv(features_path, header=None)
        classes_df = pd.read_csv(classes_path)
        
        print(f"  Features: {len(features_df)} rows, {len(features_df.columns)} columns")
        print(f"  Classes: {len(classes_df)} rows")
        
        # Rename columns: col0=txId, col1=time_step, col2-166=f1..f165
        print("\n🔧 Preparing feature matrix...")
        feature_cols = ['txId', 'time_step'] + [f'f{i}' for i in range(1, 166)]
        features_df.columns = feature_cols
        
        # Merge with classes
        merged_df = features_df.merge(classes_df, left_on='txId', right_on='txId', how='inner')
        
        print(f"  Merged: {len(merged_df)} rows")
        
        # Drop unknown rows (class is 'unknown' or not '1' or '2')
        merged_df = merged_df[merged_df['class'].isin(['1', '2'])].copy()
        
        print(f"  After dropping unknown: {len(merged_df)} rows")
        
        # Map class to binary label: 1=fraud (label=1), 2=legit (label=0)
        merged_df['label'] = merged_df['class'].apply(lambda x: 1 if x == '1' else 0)
        
        # Select final columns: txId, label, f1..f165
        final_cols = ['txId', 'label'] + [f'f{i}' for i in range(1, 166)]
        ml_ready_df = merged_df[final_cols]
        
        # Save to CSV
        output_path = 'data/elliptic_ml_ready.csv'
        ml_ready_df.to_csv(output_path, index=False)
        print(f"\n💾 Saved ML-ready data to {output_path}")
        
        # Print class distribution
        print("\n📊 CLASS DISTRIBUTION:")
        class_counts = ml_ready_df['label'].value_counts().sort_index()
        print(f"  Legit (0): {class_counts.get(0, 0):,}")
        print(f"  Fraud (1): {class_counts.get(1, 0):,}")
        print(f"  Total: {len(ml_ready_df):,}")
        
        print("\n✅ Feature matrix building complete!")
    
    except Exception as e:
        print(f"\n❌ Error building feature matrix: {str(e)}")
        raise


def main():
    """Main execution pipeline"""
    print("\n" + "="*60)
    print("FUNDTRACE AI - DATA INGESTION PIPELINE")
    print("="*60)
    
    try:
        model_source = os.getenv("MODEL_SOURCE", "auto").strip().lower()
        reset_graph = _get_bool_env("RESET_NEO4J", False)
        if model_source == "paysim":
            load_paysim_to_neo4j(reset_graph=reset_graph)
            label_paysim_patterns()
        else:
            load_elliptic_to_neo4j(reset_graph=reset_graph)
            label_paysim_patterns()
            build_feature_matrix()
        
        print("\n" + "="*60)
        print("🎉 ALL TASKS COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nOutputs:")
        print("  • Neo4j: Transaction nodes and relationships")
        print("  • data/paysim_alerts.csv: Labeled fraud patterns")
        if model_source != "paysim":
            print("  • data/elliptic_ml_ready.csv: ML-ready feature matrix")
        print()
        
    except Exception as e:
        print(f"\n💥 Pipeline failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
