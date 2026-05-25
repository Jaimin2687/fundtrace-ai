<div align="center">

<br />

```
██████╗  ██╗   ██╗  ███╗   ██╗  ██████╗   ████████╗  ██████╗   █████╗   ██████╗  ███████╗
██╔═══╝  ██║   ██║  ████╗  ██║  ██╔══██╗  ╚══██╔══╝  ██╔══██╗  ██╔══██╗  ██╔════╝  ██╔════╝
█████╗   ██║   ██║  ██╔██╗ ██║  ██║  ██║     ██║     ██████╔╝  ███████║  ██║      █████╗  
██╔══╝   ██║   ██║  ██║╚██╗██║  ██║  ██║     ██║     ██╔══██╗  ██╔══██║  ██║      ██╔══╝  
██║      ╚██████╔╝  ██║ ╚████║  ██████╔╝     ██║     ██║  ██║  ██║  ██║  ╚██████╗  ███████╗
╚═╝       ╚═════╝   ╚═╝  ╚═══╝  ╚═════╝      ╚═╝     ╚═╝  ╚═╝  ╚═╝  ╚═╝   ╚═════╝  ╚══════╝
```

**Real-time AML fraud detection with graph analytics, ML scoring, and compliant reporting.**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.x-008CC1?style=flat-square&logo=neo4j)](https://neo4j.com/)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.1-3E6C9B?style=flat-square)](https://xgboost.readthedocs.io/)
[![Next.js](https://img.shields.io/badge/Next.js-16-black?style=flat-square&logo=next.js)](https://nextjs.org/)
[![ReportLab](https://img.shields.io/badge/ReportLab-4.2-37474F?style=flat-square)](https://www.reportlab.com/)

</div>

---

## Problem being solved
Financial crime teams need to **detect suspicious transaction chains fast**, explain them clearly, and export regulatory-ready evidence. FundTrace AI combines **graph analysis** (multi-hop networks), **ML risk scoring**, and **real‑time alerting** to surface AML patterns like structuring, layering, and round‑tripping with a single end‑to‑end workflow.

## What’s inside
- **Graph intelligence**: multi-hop chain tracing, fraud clusters, and evidence generation backed by Neo4j.
- **ML scoring**: PaySim‑trained XGBoost model that scores transactions in real time.
- **Streaming alerts**: WebSocket push to the dashboard and terminal.
- **Compliance export**: FIU‑IND styled PDF reports (ReportLab).
- **Ingestion options**: CSV (PaySim), Kafka/HTTP stream, optional Bank API polling (in‑memory scoring).

## Architecture
See [`ARCHITECTURE_DIAGRAM.md`](ARCHITECTURE_DIAGRAM.md) for the full system map and design choices.

---

## How to run locally

### 1. Prerequisites
- Python 3.9+
- Node.js 18+
- Neo4j 5.x running on `bolt://localhost:7687`

### 2. Configure environment
```bash
cp .env.example .env
```
Edit `.env` (minimum):
```env
NEO4J_PASSWORD=your-neo4j-password
API_KEY=your-local-api-key
MODEL_SOURCE=paysim
```
Frontend config (edit existing file):
```bash
frontend/.env.local
```
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_API_KEY=your-local-api-key
```

### 3. Get data (PaySim)
Download **PaySim** and place the file here:
```
data/paysim.csv
```

### 4. Run backend pipeline
```bash
./run.sh
```
This will install Python deps, ingest PaySim to Neo4j, prepare the ML dataset, train the PaySim model, and start the FastAPI server.

### 5. Start frontend
```bash
cd frontend
npm install
npm run dev
```

Open:
- **Dashboard**: http://localhost:3000/dashboard  
- **API docs**: http://localhost:8000/docs

---

## Libraries / dependencies

### Backend (Python)
| Category | Libraries |
|---|---|
| API | FastAPI, Uvicorn |
| Graph | Neo4j Driver |
| ML | XGBoost, scikit‑learn, NumPy, Pandas |
| Streaming | websockets |
| PDF | ReportLab |
| Ingestion | kafka-python, httpx |

### Frontend (Node)
| Category | Libraries |
|---|---|
| Framework | Next.js, React |
| Graph UI | react-force-graph-2d/3d, three |
| Motion | framer-motion |
| UI | Tailwind CSS, shadcn/ui, Radix |
| Auth | Clerk |

---

## Sample dataset / synthetic data

### PaySim (recommended)
- **Dataset**: [PaySim Synthetic Financial Dataset](https://www.kaggle.com/ntnu-testimon/paysim1)  
- **Place file**: `data/paysim.csv`  
- Optional limit for faster dev:
  ```env
  PAYSIM_MAX_TX=150000
  ```

### Synthetic graph data (optional)
Generate a small AML graph directly into Neo4j:
```bash
python generate_data.py --reset --accounts 160 --transactions 520
```

---

## Key API endpoints
| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Health check |
| `/api/v1/graph/focus` | GET | Transaction subgraph (depth 1–5) |
| `/api/v1/graph/fraud-clusters` | GET | Fraud clusters |
| `/api/v1/graph/evidence/{txId}` | GET | Evidence package |
| `/api/v1/graph/stats` | GET | Graph statistics |
| `/api/v1/export/fiu-ind` | POST | FIU‑IND PDF export |
| `/api/v1/stream/alerts` | WebSocket | Real‑time alerts |
| `/api/v1/ingest/transactions` | POST | Kafka/HTTP ingest |
| `/api/v1/ingest/bank/fetch` | POST | Bank API fetch (in‑memory) |

> Most REST endpoints require `X-API-Key` header (set in `.env` and frontend env).

---

## Known limitations
- **PaySim is synthetic**; signals may not generalize to production traffic.
- **Graph view is trimmed** to ~300 nodes to keep the UI responsive.
- **Bank API ingest does not persist** to Neo4j (privacy‑first, no long‑term graph evidence).
- **Model is tabular XGBoost only** (no temporal or sequence modeling).
- **Kafka/Bank API flows require external services** and are disabled by default.

---

## Project structure (high level)
```
fundtrace-ai/
├── data/                    # PaySim + prepared datasets
├── backend/                 # FastAPI + ML worker + Neo4j client
├── frontend/                # Next.js UI
├── run.sh                   # Automated backend pipeline
├── start.sh                 # Run backend + frontend together
└── requirements.txt         # Python deps
```

---

## License
MIT
