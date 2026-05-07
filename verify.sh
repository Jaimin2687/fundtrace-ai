#!/bin/bash
# Verification script for FundTrace AI

echo "=========================================="
echo "FundTrace AI - System Verification"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check functions
check_pass() {
    echo -e "${GREEN}✓${NC} $1"
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# 1. Check Python
echo "1. Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    check_pass "Python installed: $PYTHON_VERSION"
else
    check_fail "Python not found"
fi
echo ""

# 2. Check Node.js
echo "2. Checking Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    check_pass "Node.js installed: $NODE_VERSION"
else
    check_fail "Node.js not found"
fi
echo ""

# 3. Check Neo4j
echo "3. Checking Neo4j..."
if command -v neo4j &> /dev/null; then
    NEO4J_STATUS=$(neo4j status 2>&1)
    if echo "$NEO4J_STATUS" | grep -q "running"; then
        check_pass "Neo4j is running"
    else
        check_warn "Neo4j is not running (run: neo4j start)"
    fi
else
    check_warn "Neo4j command not found (may be running in Docker)"
fi
echo ""

# 4. Check environment files
echo "4. Checking environment files..."
if [ -f ".env" ]; then
    check_pass ".env exists"
else
    check_fail ".env not found"
fi

if [ -f "frontend/.env.local" ]; then
    check_pass "frontend/.env.local exists"
else
    check_fail "frontend/.env.local not found"
fi
echo ""

# 5. Check data files
echo "5. Checking data files..."
if [ -f "data/elliptic_txs_classes.csv" ]; then
    check_pass "Elliptic data files exist"
else
    check_warn "Elliptic data files not found"
fi

if [ -f "data/paysim.csv" ]; then
    check_pass "PaySim data file exists"
else
    check_warn "PaySim data file not found"
fi
echo ""

# 6. Check ML model
echo "6. Checking ML model..."
if [ -f "data/fraud_model.json" ]; then
    MODEL_SIZE=$(ls -lh data/fraud_model.json | awk '{print $5}')
    check_pass "ML model exists (size: $MODEL_SIZE)"
else
    check_warn "ML model not found (run: python backend/worker/ml_worker.py --train)"
fi
echo ""

# 7. Check Python dependencies
echo "7. Checking Python dependencies..."
if python3 -c "import fastapi" 2>/dev/null; then
    check_pass "fastapi installed"
else
    check_fail "fastapi not installed"
fi

if python3 -c "import neo4j" 2>/dev/null; then
    check_pass "neo4j driver installed"
else
    check_fail "neo4j driver not installed"
fi

if python3 -c "import xgboost" 2>/dev/null; then
    check_pass "xgboost installed"
else
    check_fail "xgboost not installed"
fi
echo ""

# 8. Check frontend dependencies
echo "8. Checking frontend dependencies..."
if [ -d "frontend/node_modules" ]; then
    check_pass "Frontend dependencies installed"
else
    check_warn "Frontend dependencies not installed (run: cd frontend && npm install)"
fi
echo ""

# 9. Check backend health (if running)
echo "9. Checking backend health..."
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    HEALTH=$(curl -s http://localhost:8000/)
    if echo "$HEALTH" | grep -q "ok"; then
        check_pass "Backend is running and healthy"
    else
        check_warn "Backend is running but health check failed"
    fi
else
    check_warn "Backend is not running (run: uvicorn backend.main:app --reload --port 8000)"
fi
echo ""

# 10. Check frontend health (if running)
echo "10. Checking frontend health..."
if curl -s http://localhost:3000/ > /dev/null 2>&1; then
    check_pass "Frontend is running"
else
    check_warn "Frontend is not running (run: cd frontend && npm run dev)"
fi
echo ""

# Summary
echo "=========================================="
echo "Verification Complete"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. If Neo4j is not running: neo4j start"
echo "  2. If data not ingested: python data/ingest.py"
echo "  3. If model not trained: python backend/worker/ml_worker.py --train"
echo "  4. If backend not running: uvicorn backend.main:app --reload --port 8000"
echo "  5. If frontend not running: cd frontend && npm run dev"
echo ""
echo "Then open: http://localhost:3000/dashboard"
echo ""
