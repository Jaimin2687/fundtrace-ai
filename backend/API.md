# FundTrace AI - API Documentation

## Overview

The FundTrace AI backend provides REST and WebSocket APIs for real-time fraud detection, transaction network analysis, and ML model management.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: Configure via `NEXT_PUBLIC_API_BASE_URL`

## Authentication

Most endpoints require API key authentication via the `X-API-Key` header:

```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/v1/graph/stats
```

**Exceptions** (no auth required):
- `GET /` - Health check
- `GET /health` - Legacy health check
- `WebSocket /api/v1/stream/alerts` - Real-time alerts

## Endpoints

### Health Check

#### `GET /`

Returns service status.

**Response:**
```json
{
  "status": "ok",
  "service": "FundTrace AI"
}
```

---

## Graph API (`/api/v1/graph`)

### Get Focus Subgraph

#### `GET /api/v1/graph/focus`

Get transaction subgraph focused on a specific transaction.

**Query Parameters:**
- `txId` (required): Transaction ID to focus on
- `depth` (optional): Traversal depth (1-4, default: 2)

**Headers:**
- `X-API-Key`: API key (required)

**Response:**
```json
{
  "nodes": [
    {
      "txId": "12345",
      "aml_label": "fraud",
      "risk_score": 0.85,
      "time_step": 42,
      "x": null,
      "y": null
    }
  ],
  "edges": [
    {
      "source": "12345",
      "target": "67890",
      "is_suspicious": true,
      "pattern": "Layering"
    }
  ]
}
```

**Example:**
```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:8000/api/v1/graph/focus?txId=12345&depth=3"
```

---

### Get Fraud Clusters

#### `GET /api/v1/graph/fraud-clusters`

Get fraud transaction clusters (up to 50 fraud transactions and neighbors).

**Headers:**
- `X-API-Key`: API key (required)

**Response:**
```json
{
  "nodes": [...],
  "edges": [...]
}
```

**Example:**
```bash
curl -H "X-API-Key: your-key" \
  http://localhost:8000/api/v1/graph/fraud-clusters
```

---

### Get Evidence Package

#### `GET /api/v1/graph/evidence/{txId}`

Generate comprehensive evidence package for a transaction chain.

**Path Parameters:**
- `txId`: Transaction ID

**Headers:**
- `X-API-Key`: API key (required)

**Response:**
```json
{
  "txId": "12345",
  "chain": ["12345", "67890", "11111"],
  "risk_scores": [0.85, 0.92, 0.78],
  "patterns": ["Layering", "Round-tripping", "Structuring"],
  "total_amount": 125000.50,
  "generated_at": "2026-05-07T10:30:00Z",
  "narrative": "Transaction 12345 initiated a Round-tripping chain through 3 accounts totaling $125,000.50. Risk score: 0.92."
}
```

**Example:**
```bash
curl -H "X-API-Key: your-key" \
  http://localhost:8000/api/v1/graph/evidence/12345
```

---

### Get Graph Statistics

#### `GET /api/v1/graph/stats`

Get graph-wide statistics.

**Headers:**
- `X-API-Key`: API key (required)

**Response:**
```json
{
  "total_nodes": 46564,
  "fraud_nodes": 4545,
  "legit_nodes": 42019,
  "unknown_nodes": 0,
  "total_edges": 234355
}
```

**Example:**
```bash
curl -H "X-API-Key: your-key" \
  http://localhost:8000/api/v1/graph/stats
```

---

## Stream API (`/api/v1/stream`)

### WebSocket: Real-time Alerts

#### `WebSocket /api/v1/stream/alerts`

Connect to receive real-time fraud alerts.

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/stream/alerts');

ws.onmessage = (event) => {
  const alert = JSON.parse(event.data);
  console.log('Alert:', alert);
};
```

**Alert Format:**
```json
{
  "txId": "12345",
  "risk_score": 0.87,
  "aml_label": "fraud",
  "pattern": "Layering",
  "timestamp": "2026-05-07T10:30:00Z",
  "amount": 50000.00,
  "source": "elliptic"
}
```

**Sources:**
- `elliptic`: From Elliptic dataset scoring
- `paysim`: From PaySim fraud alerts

---

### Get Model Status

#### `GET /api/v1/stream/model-status`

Get ML model status and statistics.

**Headers:**
- `X-API-Key`: API key (required)

**Response:**
```json
{
  "last_trained": "2026-05-07T08:00:00Z",
  "model_file_exists": true,
  "total_scored": 15234
}
```

**Example:**
```bash
curl -H "X-API-Key: your-key" \
  http://localhost:8000/api/v1/stream/model-status
```

---

## Ingest API (`/api/v1/ingest`)

### Ingest Bank Transactions (HTTP)

#### `POST /api/v1/ingest/transactions`

Ingest bank transactions over HTTP. Requires `KAFKA_ENABLED=true`.

**Headers:**
- `X-API-Key`: API key (required)

**Body:**
```json
{
  "transactions": [
    {
      "tx_id": "TX-1001",
      "source_id": "ACC-001",
      "target_id": "ACC-002",
      "amount": 15000.0,
      "currency": "INR",
      "timestamp": "2026-05-21T06:05:00Z",
      "is_structuring_flag": false
    }
  ]
}
```

**Response:**
```json
{
  "accepted": 1,
  "stored": 1,
  "failed": 0
}
```

### Ingest Status

#### `GET /api/v1/ingest/status`

Returns ingest counters and Kafka status.

---

## Bank API Ingest (`/api/v1/ingest/bank`)

### Bank API Status

#### `GET /api/v1/ingest/bank/status`

Returns bank API ingest telemetry. Requires `BANK_API_ENABLED=true`.

### Fetch Bank Batch

#### `POST /api/v1/ingest/bank/fetch`

Triggers a single pull from the configured bank API and streams each transaction
directly to the alert queue (no Neo4j persistence). Requires `BANK_API_ENABLED=true`.

## Export API (`/api/v1/export`)

### Generate FIU-IND Draft

#### `POST /api/v1/export/fiu-ind`

Generate a watermarked FIU-IND draft PDF for a transaction cluster.

**Headers:**
- `X-API-Key`: API key (required)

**Body:**
```json
{
  "cluster_id": "12345"
}
```

**Response:**
- `application/pdf` file stream with `Content-Disposition: attachment`

**Example:**
```bash
curl -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"cluster_id":"12345"}' \
  http://localhost:8000/api/v1/export/fiu-ind --output fiu-ind-12345.pdf
```

---

## Data Models

### AlertEvent

```typescript
{
  txId: string;
  risk_score: number;
  aml_label?: string;
  pattern: string;
  timestamp: string;
  amount?: number;
  from_account?: string;
  to_account?: string;
  source?: string;
}
```

### GraphNode

```typescript
{
  txId: string;
  aml_label: string;
  risk_score: number;
  time_step?: number;
  amount?: number;
  pattern?: string;
  x?: number;
  y?: number;
}
```

### GraphEdge

```typescript
{
  source: string;
  target: string;
  is_suspicious?: boolean;
  pattern?: string;
}
```

### EvidencePackage

```typescript
{
  txId: string;
  chain: string[];
  risk_scores: number[];
  patterns: string[];
  total_amount: number;
  generated_at: string;
  narrative: string;
}
```

---

## Error Responses

### 401 Unauthorized

```json
{
  "detail": "Invalid or missing API key"
}
```

### 404 Not Found

```json
{
  "detail": "Transaction 12345 not found"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Database error: connection failed"
}
```

---

## Running the Backend

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update:

```bash
cp .env.example .env
```

Required variables:
- `NEO4J_URI`: Neo4j connection URI
- `NEO4J_USER`: Neo4j username
- `NEO4J_PASSWORD`: Neo4j password
- `API_KEY`: API key for authentication
- `CORS_ORIGINS`: Allowed CORS origins (JSON array)

### 3. Ingest Data

```bash
python data/ingest.py
```

### 4. Train Model

```bash
python backend/worker/ml_worker.py --train
```

### 5. Start Server

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The server will automatically:
- Initialize Neo4j connection
- Start ML worker for transaction scoring
- Start PaySim alert streamer
- Start WebSocket alert broadcaster

---

## Background Workers

The backend runs three background tasks:

1. **Alert Broadcaster**: Reads from alert queue and broadcasts to WebSocket clients
2. **Transaction Scoring Worker**: Scores unscored transactions every 5 seconds
3. **PaySim Alert Streamer**: Streams PaySim fraud alerts every 3 seconds

All workers share a common alert queue and run concurrently using asyncio.

---

## Development

### Interactive API Docs

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Testing WebSocket

```bash
# Using websocat
websocat ws://localhost:8000/api/v1/stream/alerts

# Using wscat
wscat -c ws://localhost:8000/api/v1/stream/alerts
```

---

## Architecture

```
┌─────────────────┐
│   Frontend      │
│   (Next.js)     │
└────────┬────────┘
         │
         │ HTTP/WebSocket
         │
┌────────▼────────┐
│   FastAPI       │
│   Backend       │
├─────────────────┤
│ • Graph API     │
│ • Stream API    │
│ • ML Worker     │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼──────┐
│ Neo4j │ │ XGBoost │
│  DB   │ │  Model  │
└───────┘ └─────────┘
```
