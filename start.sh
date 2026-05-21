#!/bin/bash

# FundTrace AI - Quick Start Script
# This script helps you get the entire pipeline running

set -e  # Exit on error

echo "=========================================="
echo "FundTrace AI - Quick Start"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "   Please copy .env.example to .env and configure it:"
    echo "   cp .env.example .env"
    echo ""
    exit 1
fi

echo "✓ Found .env file"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Determine model source (auto | elliptic | paysim)
MODEL_SOURCE=$(grep -E "^MODEL_SOURCE=" .env | tail -n1 | cut -d= -f2-)
if [ -z "$MODEL_SOURCE" ]; then
    MODEL_SOURCE="auto"
fi

if [ "$MODEL_SOURCE" = "auto" ]; then
    if [ -f "data/paysim_model.json" ]; then
        MODEL_SOURCE="paysim"
    else
        MODEL_SOURCE="elliptic"
    fi
fi

export MODEL_SOURCE

# Check if data files exist
if [ "$MODEL_SOURCE" = "paysim" ]; then
    if [ ! -f "data/paysim.csv" ]; then
        echo "❌ PaySim dataset not found in data/ directory!"
        echo "   Please ensure the following file exists:"
        echo "   - data/paysim.csv"
        echo ""
        exit 1
    fi
else
    if [ ! -f "data/elliptic_txs_classes.csv" ]; then
        echo "❌ Elliptic data files not found in data/ directory!"
        echo "   Please ensure the following files exist:"
        echo "   - data/elliptic_txs_classes.csv"
        echo "   - data/elliptic_txs_edgelist.csv"
        echo "   - data/elliptic_txs_features.csv"
        echo ""
        exit 1
    fi
fi

echo "✓ Data files found"
echo ""

# Check if data has been ingested
if [ "$MODEL_SOURCE" = "elliptic" ]; then
    if [ ! -f "data/elliptic_ml_ready.csv" ]; then
        echo "📊 Running data ingestion..."
        echo "   This will:"
        echo "   - Load Elliptic data to Neo4j"
        echo "   - Label PaySim patterns"
        echo "   - Build ML-ready feature matrix"
        echo ""
        python data/ingest.py
        echo ""
        echo "✓ Data ingestion complete"
        echo ""
    else
        echo "✓ Data already ingested (elliptic_ml_ready.csv exists)"
        echo ""
    fi
fi

if [ "$MODEL_SOURCE" = "paysim" ]; then
    echo "📊 Running PaySim data ingestion..."
    echo "   This will:"
    echo "   - Load PaySim data to Neo4j"
    echo "   - Label PaySim patterns"
    echo ""
    python data/ingest.py
    echo ""
    echo "✓ PaySim ingestion complete"
    echo ""
fi

# Check if model has been trained
if [ "$MODEL_SOURCE" = "paysim" ]; then
    if [ ! -f "data/paysim_ml_ready.csv" ]; then
        echo "📊 Preparing PaySim dataset..."
        python data/prepare_paysim.py
        echo "✓ PaySim dataset ready"
        echo ""
    fi

    if [ ! -f "data/paysim_model.json" ]; then
        echo "🤖 Training PaySim XGBoost model..."
        echo "   This may take a few minutes..."
        echo ""
        python backend/worker/ml_worker.py --train-paysim
        echo ""
        echo "✓ PaySim model training complete"
        echo ""
    else
        echo "✓ PaySim model already trained (paysim_model.json exists)"
        echo ""
    fi
else
    if [ ! -f "data/fraud_model.json" ]; then
        echo "🤖 Training XGBoost model..."
        echo "   This may take a few minutes..."
        echo ""
        python backend/worker/ml_worker.py --train
        echo ""
        echo "✓ Model training complete"
        echo ""
    else
        echo "✓ Model already trained (fraud_model.json exists)"
        echo ""
    fi
fi

# Start the backend
echo "=========================================="
echo "🚀 Starting FundTrace AI Backend"
echo "=========================================="
echo ""
echo "The backend will start with:"
echo "  • FastAPI server on http://localhost:8000"
echo "  • Transaction scoring worker (every 5s)"
echo "  • PaySim alert streamer (every 3s)"
echo "  • WebSocket alert broadcaster"
echo ""
echo "API Documentation:"
echo "  • Swagger UI: http://localhost:8000/docs"
echo "  • ReDoc: http://localhost:8000/redoc"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "=========================================="
echo ""

# Start uvicorn
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
