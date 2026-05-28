#!/usr/bin/env bash
# Startup wrapper — prints env var presence and runs uvicorn with verbose logging

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
[ -z "$PORT" ]          && MISSING="$MISSING PORT"
[ -z "$NEO4J_URI" ]     && MISSING="$MISSING NEO4J_URI"
[ -z "$NEO4J_USER" ]    && MISSING="$MISSING NEO4J_USER"
[ -z "$NEO4J_PASSWORD" ] && MISSING="$MISSING NEO4J_PASSWORD"
[ -z "$API_KEY" ]       && MISSING="$MISSING API_KEY"

if [ -n "$MISSING" ]; then
  echo "❌ MISSING required environment variables:$MISSING"
  echo "   Please set them in the Render Dashboard → Environment"
  exit 1
fi

CLEAN_PORT="${PORT//[^0-9]/}"
echo "🚀 Starting uvicorn on port $CLEAN_PORT..."
echo ""

exec uvicorn backend.main:app \
  --host 0.0.0.0 \
  --port "$CLEAN_PORT" \
  --log-level info
