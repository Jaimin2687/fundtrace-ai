# FundTrace AI

Real-time fraud detection and transaction network analysis using graph databases, machine learning, and interactive visualization. Detects money laundering patterns including structuring, layering, round-tripping, and dormant account activation.

## 🚀 Quick Start

```bash
# 1. Start Neo4j (ensure running on bolt://localhost:7687)
neo4j start

# 2. Ingest data to Neo4j and prepare ML features
python data/ingest.py

# 3. Train XGBoost fraud detection model
python backend/worker/ml_worker.py --train

# 4. Start backend (in one terminal)
uvicorn backend.main:app --reload --port 8000

# 5. Start frontend (in another terminal)
cd frontend && npm install && npm run dev
```

Open http://localhost:3000/dashboard to view the live fraud detection dashboard.

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
| `/api/v1/graph/seed-demo` | POST | Seed demo data for testing |
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
- **Demo Mode**: 4-step walkthrough for presentations
- **Real-time Updates**: WebSocket connection for live alerts

## 🔧 Configuration

### Backend (`.env`)
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
API_KEY=fraudtrace-dev-key-2026
CORS_ORIGINS=["http://localhost:3000"]
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

## 🧪 Testing

```bash
# Test backend health
curl http://localhost:8000/

# Test API with authentication
curl -H "X-API-Key: fraudtrace-dev-key-2026" \
  http://localhost:8000/api/v1/graph/stats

# Test WebSocket
wscat -c ws://localhost:8000/api/v1/stream/alerts

# Seed demo data (if Neo4j is empty)
curl -X POST -H "X-API-Key: fraudtrace-dev-key-2026" \
  http://localhost:8000/api/v1/graph/seed-demo
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
- Use "Seed Demo Data" button in dashboard

## 🎉 Demo Walkthrough

1. **Dashboard** (http://localhost:3000/dashboard)
   - Click "Seed Demo Data" to populate graph
   - Watch live alerts stream in left panel
   - Click alert → View transaction network
   - Click node → View evidence package

2. **Network** (http://localhost:3000/network)
   - Search transaction by ID
   - Adjust depth (1-4)
   - Click "Fraud Clusters" to view fraud network

3. **Demo** (http://localhost:3000/demo)
   - Click "Run Full Demo" for automated walkthrough
   - Perfect for presentations to judges/stakeholders

## 🙏 Credits

- **Elliptic Dataset**: Elliptic Data Set (Kaggle)
- **PaySim Dataset**: NTNU PaySim Synthetic Financial Dataset (Kaggle)
- **Technologies**: Neo4j, XGBoost, FastAPI, Next.js, React Force Graph

## 📄 License

MIT License - See LICENSE file for details

---

**Built for real-time fraud detection in financial networks** 🕵️‍♂️
