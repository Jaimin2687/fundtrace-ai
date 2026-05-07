# FundTrace AI

Real-time fraud detection and transaction network analysis using graph databases and machine learning.

## 🚀 Quick Start

```bash
# 1. Setup environment
cp .env.example .env
# Edit .env with your Neo4j credentials and API key

# 2. Run the automated setup
./start.sh
```

The script will:
- Create virtual environment
- Install dependencies
- Ingest data to Neo4j
- Train XGBoost model
- Start the backend server

**Manual Setup:**

```bash
# Install dependencies
pip install -r requirements.txt

# Ingest data
python data/ingest.py

# Train model
python backend/worker/ml_worker.py --train

# Start backend
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

## 📋 Overview

FundTrace AI is a comprehensive fraud detection system that combines:
- **Graph Database**: Neo4j for transaction network analysis
- **Machine Learning**: XGBoost for fraud prediction
- **Real-time API**: FastAPI with WebSocket streaming
- **Data Pipeline**: Automated ingestion and feature engineering

## 🏗️ Architecture

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

## 📊 Data Pipeline

### 1. Data Ingestion (`data/ingest.py`)

**Elliptic Dataset → Neo4j**
- Loads 46,564 Bitcoin transactions
- Creates Transaction nodes with properties: txId, aml_label, time_step, risk_score
- Creates 234,355 SENT_TO relationships
- Uses batch loading (500 records/batch) for performance

**PaySim Pattern Labeling**
- Processes mobile money fraud dataset
- Applies 4 fraud pattern rules:
  - Structuring (amount < 200k)
  - Dormant Account Activated
  - Layering - Cash Out
  - Suspicious Transfer
- Outputs labeled fraud alerts to `data/paysim_alerts.csv`

**Feature Matrix Builder**
- Processes 167 feature columns
- Merges with fraud labels
- Outputs ML-ready data to `data/elliptic_ml_ready.csv`

### 2. ML Pipeline (`backend/worker/ml_worker.py`)

**Model Training**
- XGBoost classifier with class imbalance handling (scale_pos_weight=9)
- 80/20 train/test split (stratified)
- Saves model to `data/fraud_model.json`
- Prints classification report and confusion matrix

**Real-time Scoring**
- Continuous worker loop (every 5 seconds)
- Scores unscored transactions from Neo4j
- Generates alerts for high-risk transactions (>0.75)
- Updates risk_score in database

**Alert Streaming**
- PaySim alert streamer (every 3 seconds)
- Broadcasts alerts via WebSocket
- Shared alert queue for all workers

## 🔌 API Endpoints

### Graph API (`/api/v1/graph`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/focus` | GET | Get transaction subgraph (depth 1-4) |
| `/fraud-clusters` | GET | Get fraud transaction clusters |
| `/evidence/{txId}` | GET | Generate evidence package |
| `/stats` | GET | Get graph statistics |

### Stream API (`/api/v1/stream`)

| Endpoint | Type | Description |
|----------|------|-------------|
| `/alerts` | WebSocket | Real-time fraud alerts |
| `/model-status` | GET | ML model status |

### Authentication

Most endpoints require API key via `X-API-Key` header:

```bash
curl -H "X-API-Key: your-key" http://localhost:8000/api/v1/graph/stats
```

**See full API documentation**: `backend/API.md`

## 📁 Project Structure

```
fundtrace-ai/
├── data/
│   ├── ingest.py                    # Data ingestion pipeline
│   ├── elliptic_txs_*.csv          # Elliptic Bitcoin dataset
│   ├── paysim.csv                  # PaySim mobile money dataset
│   ├── paysim_alerts.csv           # Generated fraud alerts
│   ├── elliptic_ml_ready.csv       # ML-ready features
│   └── fraud_model.json            # Trained XGBoost model
│
├── backend/
│   ├── main.py                     # FastAPI application
│   ├── core/
│   │   ├── config.py               # Configuration management
│   │   └── security.py             # CORS & authentication
│   ├── db/
│   │   └── neo4j_client.py         # Neo4j driver (singleton)
│   ├── api/v1/
│   │   ├── schemas.py              # Pydantic models
│   │   ├── graph.py                # Graph endpoints
│   │   └── stream.py               # Streaming endpoints
│   └── worker/
│       └── ml_worker.py            # ML training & workers
│
├── frontend/                        # Next.js frontend
├── .env.example                    # Environment template
├── requirements.txt                # Python dependencies
├── start.sh                        # Quick start script
└── README.md                       # This file
```

## 🔧 Configuration

### Environment Variables

```bash
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
NEO4J_ENCRYPTION=false

# API Configuration
API_KEY=your-api-key
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]

# Optional
FRONTEND_ORIGIN=http://localhost:3000
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_WS_BASE_URL=ws://localhost:8000
```

## 🎯 Features

### Implemented ✅

**Backend + Data Layer**
- ✅ FastAPI with async/await throughout
- ✅ Neo4j integration with singleton driver
- ✅ Graph API endpoints (focus, clusters, evidence, stats)
- ✅ WebSocket streaming for real-time alerts
- ✅ API key authentication
- ✅ CORS configuration
- ✅ Background worker management

**ML Pipeline**
- ✅ XGBoost fraud detection model
- ✅ Class imbalance handling (scale_pos_weight)
- ✅ Continuous transaction scoring
- ✅ Real-time alert generation
- ✅ Model caching for performance

**Data Pipeline**
- ✅ Elliptic dataset ingestion (46k+ transactions)
- ✅ PaySim pattern labeling (4 fraud patterns)
- ✅ Feature engineering (165 features)
- ✅ Batch loading with UNWIND (500 records/batch)
- ✅ Progress indicators and error handling

**Frontend + Visualization**
- ✅ Live threat stream panel
- ✅ Fraud node highlighting
- ✅ Interactive graph visualization
- ✅ Model status monitoring

### Production Roadmap 🚧

**1. Data Ingestion & Integration**
- [ ] Change Data Capture (Debezium) from CBS RDBMS
- [ ] Kafka/Redpanda event streaming
- [ ] Stream processing (Flink/Kafka Streams)
- [ ] Nightly reconciliation ETL (Airflow/PySpark)

**2. Enterprise Graph Infrastructure**
- [ ] Neo4j Enterprise Causal Cluster
- [ ] Graph partitioning/sharding
- [ ] Neo4j GDS (Louvain/PageRank) analytics

**3. ML Ops & AI Pipeline**
- [ ] Feature store (Feast/Hopsworks)
- [ ] Model registry + serving (MLflow + Triton)
- [ ] Shadow mode deployment
- [ ] Feedback loop from investigators

**4. Backend Microservices**
- [ ] Separate ingestion/scoring/query services
- [ ] Async worker queue (Celery + Redis)
- [ ] Rate limiting and caching

**5. Security & Compliance**
- [ ] SAML 2.0 / OIDC (Azure AD/Okta)
- [ ] RBAC by analyst tier
- [ ] Immutable audit logs
- [ ] PII encryption + dynamic masking

**6. Frontend Enhancement**
- [ ] Custom WebGL rendering (Three.js/deck.gl)
- [ ] Graph summarization and clustering
- [ ] State management (Redux/Zustand)

**7. Infrastructure & DevOps**
- [ ] Kubernetes deployment (EKS/AKS/GKE)
- [ ] Terraform IaC
- [ ] CI/CD pipeline with SAST
- [ ] APM/monitoring (Datadog/Prometheus)

## 📚 Documentation

- **API Documentation**: `backend/API.md`
- **Implementation Summary**: `IMPLEMENTATION_SUMMARY.md`
- **Interactive API Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Testing

```bash
# Health check
curl http://localhost:8000/

# Graph stats (requires API key)
curl -H "X-API-Key: your-key" http://localhost:8000/api/v1/graph/stats

# WebSocket alerts
wscat -c ws://localhost:8000/api/v1/stream/alerts
```

## 📊 Datasets

### Elliptic Bitcoin Dataset
- **Nodes**: 46,564 Bitcoin transactions
- **Edges**: 234,355 directed payment flows
- **Features**: 166 features (local + aggregate)
- **Labels**: Fraud (4,545), Legit (42,019), Unknown

### PaySim Mobile Money Dataset
- **Transactions**: 6.3M mobile money transfers
- **Fraud**: 8,213 fraudulent transactions
- **Patterns**: Structuring, Layering, Dormant Accounts

## 🤝 Contributing

This is an MVP implementation. For production deployment, refer to the roadmap above.

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Elliptic Bitcoin Dataset
- PaySim Mobile Money Simulator
- Neo4j Graph Database
- XGBoost Machine Learning Library
