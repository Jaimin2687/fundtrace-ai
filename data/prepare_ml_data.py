"""
Quick script to build ML-ready feature matrix from Elliptic data
"""

import sys
from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent
if str(DATA_DIR) not in sys.path:
    sys.path.append(str(DATA_DIR))

from path_utils import require_dataset_path  # noqa: E402

print("\n" + "="*60)
print("BUILDING FEATURE MATRIX FOR ML")
print("="*60)

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

print("\n✅ Feature matrix ready for ML training!")
