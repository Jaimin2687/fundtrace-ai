#!/usr/bin/env bash
export PYTHONUNBUFFERED=1

echo "=========================================="
echo "FundTrace AI - Starting"
echo "=========================================="
echo ""
echo "🔍 Environment check:"
echo "  PORT          = ${PORT:-NOT SET}"
echo "  MODEL_SOURCE  = ${MODEL_SOURCE:-NOT SET}"
echo "  NEO4J_URI     = ${NEO4J_URI:+SET (hidden)}"
echo "  NEO4J_USER    = ${NEO4J_USER:+SET (hidden)}"
echo "  NEO4J_PASSWORD= ${NEO4J_PASSWORD:+SET (hidden)}"
echo "  API_KEY       = ${API_KEY:+SET (hidden)}"
echo "  KAFKA_ENABLED = ${KAFKA_ENABLED:-NOT SET}"
echo "  BANK_API_ENABLED = ${BANK_API_ENABLED:-NOT SET}"
echo "  CORS_ORIGINS  = ${CORS_ORIGINS:-NOT SET}"
echo ""

# Validate required vars
MISSING=""
[ -z "$PORT" ]           && MISSING="$MISSING PORT"
[ -z "$NEO4J_URI" ]      && MISSING="$MISSING NEO4J_URI"
[ -z "$NEO4J_USER" ]     && MISSING="$MISSING NEO4J_USER"
[ -z "$NEO4J_PASSWORD" ] && MISSING="$MISSING NEO4J_PASSWORD"
[ -z "$API_KEY" ]        && MISSING="$MISSING API_KEY"

if [ -n "$MISSING" ]; then
  echo "❌ MISSING required environment variables:$MISSING"
  echo "   Set them in Render Dashboard → Environment"
  exit 1
fi

echo "🩺 Running pre-flight diagnostics..."
python - <<'PYEOF'
import sys, os

print(f"  Python: {sys.version}")
print(f"  CWD: {os.getcwd()}")

# Check data directory
data_files = os.listdir("data") if os.path.exists("data") else []
print(f"  data/ files: {data_files}")

# Check model files
for f in ["data/paysim_model.json", "data/fraud_model.json"]:
    exists = os.path.exists(f)
    print(f"  {f}: {'✓ EXISTS' if exists else '✗ MISSING'}")

# Check config loads
try:
    from backend.core.config import get_settings
    settings = get_settings()
    print(f"  Config: ✓ OK (MODEL_SOURCE={settings.MODEL_SOURCE}, CORS={settings.CORS_ORIGINS})")
except Exception as e:
    print(f"  Config: ✗ FAILED — {e}")
    sys.exit(1)

# Check model registry
try:
    from backend.core.model_registry import get_model_info, model_exists
    model_info = get_model_info()
    exists = model_exists(model_info)
    print(f"  Model:  {'✓' if exists else '✗'} source={model_info.source}, path={model_info.path}, exists={exists}")
    if not exists:
        sys.exit(1)
except Exception as e:
    print(f"  Model:  ✗ FAILED — {e}")
    sys.exit(1)

# Check Neo4j connection
try:
    from backend.db.neo4j_client import get_driver
    driver = get_driver()
    with driver.session() as session:
        result = session.run("RETURN 1 AS ok")
        record = result.single()
        print(f"  Neo4j:  ✓ Connected (ping={record['ok']})")
    driver.close()
except Exception as e:
    print(f"  Neo4j:  ✗ FAILED — {e}")
    sys.exit(1)

print("")
print("✅ All pre-flight checks passed!")
PYEOF

CLEAN_PORT="${PORT//[^0-9]/}"
echo ""
echo "🚀 Starting uvicorn on port $CLEAN_PORT..."
echo ""

exec uvicorn backend.main:app \
  --host 0.0.0.0 \
  --port "$CLEAN_PORT" \
  --log-level info
