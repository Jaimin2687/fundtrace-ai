#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "⚡ Upgrading pip, wheel and setuptools..."
pip install --upgrade pip wheel setuptools

echo "📦 Installing dependencies (using pre-built binaries)..."
pip install --prefer-binary -r requirements.txt

echo "🔍 Checking data files..."

if [ "$MODEL_SOURCE" = "paysim" ]; then
    if [ ! -f "data/paysim_model.json" ]; then
        echo "🤖 Training PaySim XGBoost model..."
        # Note: If paysim.csv is not committed to git due to size (493MB limit on GH without LFS),
        # You will need to either commit the paysim_model.json directly, or upload the csv using LFS!
        python data/prepare_paysim.py || echo "Warning: data/prepare_paysim.py failed. Make sure your data files exist."
        python backend/worker/ml_worker.py --train-paysim || echo "Warning: model training failed."
    else
        echo "✓ Model already trained (paysim_model.json exists)"
    fi
else
    if [ ! -f "data/fraud_model.json" ]; then
        echo "🤖 Training Elliptic XGBoost model..."
        python backend/worker/ml_worker.py --train || echo "Warning: model training failed."
    else
        echo "✓ Model already trained (fraud_model.json exists)"
    fi
fi
