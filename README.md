# FundTrace AI

Real-time fraud detection and transaction network analysis using graph databases, machine learning, and interactive visualization. Detects money laundering patterns including structuring, layering, round-tripping, and dormant account activation.

## 🚀 Quick Start

```bash
# 1. Start Neo4j (ensure running on bolt://localhost:7687)
neo4j start

# 2. Ingest data to Neo4j and prepare ML features
python3 data/ingest.py

# 3. Train XGBoost fraud detection model
python3 backend/worker/ml_worker.py --train

# 4. Start backend (in one terminal)
source .venv/bin/activate
uvicorn backend.main:app --reload --port 8000

# 5. Start frontend (in another terminal)
cd frontend && npm install && npm run dev
```

Open http://localhost:3000/sign-in to authenticate, then access the dashboard at /dashboard.

## 📊 Architecture

```
┌─────────────┐
│  Next.js    │  Real-time dashboard with WebSocket alerts
│  Frontend   │  Interactive graph visualization
└──────┬──────┘
       │ HTTP/WebSocket
┌──────▼──────┐
│   FastAPI   │  REST API + WebSocket streaming
│   Backend   │  ML worker for transaction scoring
└──────┬──────┘
       │
  ┌────┴────┐
  │         │
┌─▼──┐  ┌──▼────┐
│Neo4j│  │XGBoost│  Graph database + ML model
└─────┘  └───────┘
```

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/api/v1/graph/focus` | GET | Get transaction subgraph (depth 1-4) |
| `/api/v1/graph/fraud-clusters` | GET | Get fraud transaction clusters |
| `/api/v1/graph/evidence/{txId}` | GET | Generate evidence package |
| `/api/v1/graph/stats` | GET | Get graph statistics |
| `/api/v1/export/fiu-ind` | POST | Generate FIU-IND draft PDF |
| `/api/v1/stream/alerts` | WebSocket | Real-time fraud alerts |
| `/api/v1/stream/model-status` | GET | ML model status |

**Authentication:** All endpoints (except `/` and WebSocket) require `X-API-Key` header.

**Interactive Docs:** http://localhost:8000/docs

## 📁 Project Structure

```
fundtrace-ai/
├── data/
│   ├── ingest.py              # Data ingestion pipeline
│   └── *.csv                  # Elliptic & PaySim datasets
├── backend/
│   ├── main.py                # FastAPI application
│   ├── worker/ml_worker.py    # ML training & scoring
│   ├── api/v1/                # API endpoints
│   ├── core/                  # Configuration
│   └── db/                    # Neo4j client
├── frontend/
│   ├── src/app/               # Next.js pages
│   └── src/components/        # React components
├── .env                       # Backend configuration
├── frontend/.env.local        # Frontend configuration
└── requirements.txt           # Python dependencies
```

## 🎯 Features

### Data Pipeline
- **Elliptic Dataset**: 46,564 Bitcoin transactions with fraud labels
- **PaySim Dataset**: 6.3M mobile money transactions with fraud patterns
- **Batch Loading**: UNWIND batching (500 records/batch) for performance
- **Pattern Detection**: 4 fraud patterns (Structuring, Layering, Dormant, Round-tripping)

### ML Pipeline
- **XGBoost Classifier**: 80/20 train/test split with class imbalance handling
- **Real-time Scoring**: Continuous worker scores transactions every 5 seconds
- **Alert Generation**: High-risk transactions (>0.75) trigger alerts
- **Model Caching**: Singleton pattern for performance

### Frontend
- **Dashboard**: Live alert stream, interactive graph, evidence viewer
- **Network Visualization**: Search by transaction ID, configurable depth
- **Real-time Updates**: WebSocket connection for live alerts

## 🔧 Configuration

### Backend (`.env`)
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
API_KEY=fraudtrace-dev-key-2026
CORS_ORIGINS=["http://localhost:3000"]
MODEL_SOURCE=paysim
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_replace_me
CLERK_SECRET_KEY=sk_test_replace_me
PAYSIM_MAX_TX=150000
RESET_NEO4J=false
KAFKA_ENABLED=false
KAFKA_BROKERS=localhost:9092
KAFKA_TOPIC=cbs.transactions.raw
KAFKA_GROUP_ID=fundtrace-ingest
KAFKA_SECURITY_PROTOCOL=PLAINTEXT
KAFKA_SASL_MECHANISM=
KAFKA_USERNAME=
KAFKA_PASSWORD=
KAFKA_BATCH_SIZE=200
KAFKA_POLL_TIMEOUT_MS=1000
BANK_API_ENABLED=false
BANK_API_BASE_URL=
BANK_API_ENDPOINT=/transactions/batch
BANK_API_AUTH_HEADER=Authorization
BANK_API_AUTH_TOKEN=
BANK_API_POLL_INTERVAL_SEC=15
BANK_API_TIMEOUT_SEC=10
BANK_API_VERIFY_SSL=true
```

### Frontend (`frontend/.env.local`)
```env
NEXT_PUBLIC_API_KEY=fraudtrace-dev-key-2026
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_WS_BASE_URL=ws://localhost:8000
```

## 📊 Datasets

### Elliptic Bitcoin Dataset
- **Source**: [Elliptic Data Set](https://www.kaggle.com/ellipticco/elliptic-data-set)
- **Nodes**: 46,564 Bitcoin transactions
- **Edges**: 234,355 directed payment flows
- **Features**: 166 features (local + aggregate)
- **Labels**: Fraud (4,545), Legit (42,019), Unknown

### PaySim Mobile Money Dataset
- **Source**: [PaySim Synthetic Financial Dataset](https://www.kaggle.com/ntnu-testimon/paysim1)
- **Transactions**: 6.3M mobile money transfers
- **Fraud**: 8,213 fraudulent transactions
- **Patterns**: Structuring, Layering, Cash Out, Dormant Accounts

### Dataset Placement (Required)
- Place Elliptic files in `data/` as:
  - `elliptic_txs_classes.csv`
  - `elliptic_txs_edgelist.csv`
  - `elliptic_txs_features.csv`
- Place PaySim file in `data/` as:
  - `paysim.csv`

### Dataset Download & Preparation

#### Elliptic Bitcoin Dataset
```bash
# Download from Kaggle (requires account)
cd data/

# Option 1: Using Kaggle CLI
kaggle datasets download -d ellipticco/elliptic-data-set
unzip elliptic-data-set.zip

# Option 2: Manual download from https://www.kaggle.com/ellipticco/elliptic-data-set
# Extract these 3 files to data/:
#   - elliptic_txs_classes.csv (46,564 rows, fraud labels)
#   - elliptic_txs_edgelist.csv (234,355 rows, transaction edges)
#   - elliptic_txs_features.csv (46,564 rows, 166 features each)
```

#### PaySim Mobile Money Dataset
```bash
# Download from Kaggle
cd data/
kaggle datasets download -d ntnu-testimon/paysim1
unzip paysim1.zip

# Extract paysim.csv to data/
# File: 6.3M transactions with fraud patterns
```


## 🔄 Data Pipeline & ML Flow

### Step 1: Data Ingestion (`python3 data/ingest.py`)

**Inputs:**
- `elliptic_txs_classes.csv` - Transaction fraud labels
- `elliptic_txs_edgelist.csv` - Payment flow edges
- `elliptic_txs_features.csv` - Feature vectors
- `paysim.csv` (optional) - Additional transactions

**Processing:**
1. Load CSV files into pandas DataFrames
2. Create Neo4j nodes for each transaction:
   ```cypher
   CREATE (t:Transaction {
     txId: "123",
     aml_label: "fraud|normal|unknown",
     risk_score: 0.75,
     time_step: 42,
     amount: 50000
   })
   ```
3. Create edges (SENT_TO) for payment relationships with batching (500 records/batch)
4. Generate ML training CSV at `data/fraud_features.csv`

**Output:**
- Neo4j graph populated with transactions and edges
- `data/fraud_features.csv` - Flattened features for ML training

### Step 2: Model Training (`python3 backend/worker/ml_worker.py --train`)

**Inputs:**
- `data/fraud_features.csv` from Step 1

**Processing:**
1. Load features and labels (80/20 train/test split)
2. Handle class imbalance with weight scaling
3. Train XGBoost classifier with parameters:
   - max_depth: 6
   - learning_rate: 0.1
   - n_estimators: 100
   - scale_pos_weight: 10 (fraud cost weight)
4. Evaluate on test set (precision, recall, F1)
5. Save model to `data/fraud_model.json`

**Output:**
- `data/fraud_model.json` - Serialized XGBoost model
- Model metrics logged to console

### Step 3: Real-Time Scoring (Backend Running)

**Trigger:** ML worker runs continuously (every 5 seconds)

**Processing:**
1. Load model from `data/fraud_model.json`
2. Query new transactions from Neo4j
3. Score each transaction with features:
   - Local features (degree, amount, time)
   - Aggregated features (network density, clustering)
4. Update `risk_score` on Transaction nodes
5. Alert if risk_score > 0.75 (configurable threshold)

**Output:**
- Alert payloads sent via WebSocket to frontend
- Updated risk scores stored in Neo4j

### Step 4: Frontend Visualization (Dashboard)

**WebSocket Streaming:**
- Real-time alerts appear in Live Threat Feed (left panel)
- User clicks alert → Fetch subgraph from `/api/v1/graph/focus`
- Graph displays nodes colored by risk, edges by pattern

**Evidence Generation:**
- User clicks node → Fetch evidence from `/api/v1/graph/evidence/{txId}`
- Entity Intelligence Panel shows narrative + metrics
- "Generate FIU-IND Draft" exports watermarked PDF

### Data Flow Diagram

```
┌─────────────────┐
│ Kaggle/CSV      │
│ Datasets        │
└────────┬────────┘
         │
    ┌────▼────────────────┐
    │ data/ingest.py       │
    │ (Load + Transform)   │
    └────┬────────────────┘
         │
    ┌────▼──────────────────────┐
    │ Neo4j Graph Database       │
    │ (46K+ transactions)        │
    └────┬──────────────────────┘
         │
    ┌────▼─────────────────────────────┐
    │ data/fraud_features.csv           │
    │ (Flattened + Aggregated Features) │
    └────┬─────────────────────────────┘
         │
    ┌────▼──────────────────┐
    │ ml_worker.py --train   │
    │ (XGBoost Training)    │
    └────┬──────────────────┘
         │
    ┌────▼──────────────────────┐
    │ data/fraud_model.json      │
    │ (Trained Model)           │
    └────┬──────────────────────┘
         │
    ┌────▼──────────────────────────┐
    │ ml_worker.py (Continuous)      │
    │ (Score + Alert Every 5 Sec)   │
    └────┬──────────────────────────┘
         │
    ┌────▼──────────────────────┐
    │ FastAPI WebSocket          │
    │ (Stream Alerts)           │
    └────┬──────────────────────┘
         │
    ┌────▼──────────────────────┐
    │ Next.js Frontend           │
    │ (Visualize + Export)      │
    └───────────────────────────┘
```

### Configuration Variables

```env
# .env
STREAM_MOCK_MODE=false           # Use real ML model (true = synthetic alerts)
NEO4J_URI=bolt://localhost:7687  # Neo4j connection
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
API_KEY=fraudtrace-dev-key-2026
FRAUD_THRESHOLD=0.75             # Alert if risk_score > this
```

### Model Training Workflow (Detailed)

```bash
# 1. Check datasets are present
ls -la data/elliptic_txs_*.csv data/paysim.csv 2>/dev/null || echo "Missing datasets"

# 2. Run ingestion
source .venv/bin/activate
python3 data/ingest.py
# → Logs: "Ingested 46,564 transactions", "Created fraud_features.csv"

# 3. Verify Neo4j has data
curl -u neo4j:password http://localhost:7474/db/neo4j/browser/
# Or in Cypher: MATCH (t:Transaction) RETURN count(t);

# 4. Train model
python3 backend/worker/ml_worker.py --train
# → Logs: "Training XGBoost...", "Test Accuracy: 0.95", "Model saved to data/fraud_model.json"

# 5. Verify model was created
ls -la data/fraud_model.json

# 6. Start backend (which runs real-time scoring)
uvicorn backend.main:app --reload --port 8000
# → Logs: "ML Worker initialized", "Scoring enabled"
```

## 🧪 Testing

```bash
# Test backend health
curl http://localhost:8000/

# Test API with authentication
curl -H "X-API-Key: fraudtrace-dev-key-2026" \
  http://localhost:8000/api/v1/graph/stats

# Test WebSocket
wscat -c ws://localhost:8000/api/v1/stream/alerts

```

## 📚 Documentation

- **Quick Start**: `QUICK_START.md` - Get running in 5 minutes
- **Integration Guide**: `INTEGRATION_GUIDE.md` - Complete setup walkthrough
- **Implementation Summary**: `IMPLEMENTATION_SUMMARY.md` - Technical details
- **Frontend Guide**: `FRONTEND_IMPLEMENTATION.md` - Frontend architecture
- **API Reference**: `backend/API.md` - Detailed API documentation

## 🐛 Troubleshooting

### Neo4j Connection Failed
```bash
# Start Neo4j
neo4j start

# Or use Docker
docker run -p 7687:7687 -p 7474:7474 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5
```

### WebSocket Disconnected
- Ensure backend is running on port 8000
- Check `NEXT_PUBLIC_WS_BASE_URL` in `frontend/.env.local`
- Verify CORS_ORIGINS includes frontend URL

### No Alerts Appearing
- Check ML worker is running (logs in backend terminal)
- Verify transactions exist: `MATCH (t:Transaction) RETURN count(t)`
 - Ensure Neo4j contains transactions to score

## 🙏 Credits

- **Elliptic Dataset**: Elliptic Data Set (Kaggle)
- **PaySim Dataset**: NTNU PaySim Synthetic Financial Dataset (Kaggle)
- **Technologies**: Neo4j, XGBoost, FastAPI, Next.js, React Force Graph

## 📄 License

MIT License - See LICENSE file for details

---

**Built for real-time fraud detection in financial networks** 🕵️‍♂️
