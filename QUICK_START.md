# FundTrace AI - Quick Start Guide

## ⚡ 5-Minute Setup

### 1. Prerequisites
```bash
# Check versions
python3 --version  # Need 3.9+
node --version     # Need 18+
neo4j status       # Should be running
```

### 2. Configure
```bash
# Backend
cp .env.example .env
# Edit .env: Set NEO4J_PASSWORD and API_KEY

# Frontend
# Uses root .env values via next.config.ts
```

### 3. Run Automated Setup
```bash
./start.sh
```

This script will:
- ✅ Create virtual environment
- ✅ Install Python dependencies
- ✅ Ingest data to Neo4j
- ✅ Train ML model
- ✅ Start backend server

### 4. Start Frontend (New Terminal)
```bash
cd frontend
npm install
npm run dev
```

### 5. Access Application
- **Sign-in**: http://localhost:3000/sign-in
- **Dashboard**: http://localhost:3000/dashboard
- **Network**: http://localhost:3000/network
- **API Docs**: http://localhost:8000/docs

---

## 🎯 Manual Setup (If Automated Fails)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
cd frontend && npm install && cd ..
```

### Step 2: Ingest Data
```bash
python data/ingest.py
```

### Step 3: Train Model
```bash
python backend/worker/ml_worker.py --train
```

### Step 4: Start Backend
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 5: Start Frontend (New Terminal)
```bash
cd frontend
npm run dev
```

---

## ✅ Verify Installation

### Test Backend
```bash
curl http://localhost:8000/
# Should return: {"status":"ok","service":"FundTrace AI"}
```

### Test API
```bash
curl -H "X-API-Key: your-key" http://localhost:8000/api/v1/graph/stats
# Should return graph statistics
```

### Test WebSocket
```bash
wscat -c ws://localhost:8000/api/v1/stream/alerts
# Should stream alerts
```

### Test Frontend
Open http://localhost:3000/dashboard
- Should see live alerts (green dot = connected)
- Click alert → Graph loads
- Click node → Evidence panel appears

---

## 🐛 Common Issues

### "Neo4j connection failed"
```bash
# Start Neo4j
neo4j start

# Or use Docker
docker run -p 7687:7687 -p 7474:7474 neo4j:5
```

### "Invalid API key"
Check that `API_KEY` in `.env` matches `NEXT_PUBLIC_API_KEY` in `frontend/.env.local`

### "WebSocket disconnected"
1. Ensure backend is running on port 8000
2. Check `NEXT_PUBLIC_WS_BASE_URL=ws://localhost:8000`

### "Graph not rendering"
```bash
cd frontend
npm install react-force-graph-2d
npm run dev
```

---

## 📁 Project Structure

```
fundtrace-ai/
├── data/
│   ├── ingest.py              # Run first
│   └── *.csv                  # Data files
├── backend/
│   ├── main.py                # FastAPI app
│   ├── worker/ml_worker.py    # ML training
│   └── api/v1/                # API endpoints
├── frontend/
│   ├── src/app/               # Pages
│   └── src/components/        # Components
├── .env                       # Backend + frontend config
└── start.sh                   # Automated setup
```

---

## 🎨 Pages Overview

### Dashboard (`/dashboard`)
- **Left**: Live alert stream (WebSocket)
- **Center**: Interactive graph
- **Right**: Evidence panel (slide-in)
- **Top**: Stats and controls

### Network (`/network`)
- Search by transaction ID
- Configurable depth (1-4)
- Load fraud clusters
- Full-screen graph with legend

---

## 🔑 Environment Variables

### Backend (`.env`)
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
API_KEY=your-secret-key
CORS_ORIGINS=["http://localhost:3000"]
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_replace_me
CLERK_SECRET_KEY=sk_test_replace_me
```

### Frontend (inherited via `.env`)
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_WS_BASE_URL=ws://localhost:8000
NEXT_PUBLIC_API_KEY=your-secret-key
```

---

## 📊 Data Pipeline

```
1. CSV Files → data/ingest.py → Neo4j + ML CSV
2. ML CSV → ml_worker.py --train → Model
3. Model + Neo4j → Backend → WebSocket → Frontend
```

---

## 🚀 Production Deployment

### Backend
```bash
# Build
pip install -r requirements.txt

# Run with gunicorn
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend
```bash
cd frontend
npm run build
npm start
```

### Docker (Optional)
```bash
# Backend
docker build -t fundtrace-backend .
docker run -p 8000:8000 fundtrace-backend

# Frontend
docker build -t fundtrace-frontend ./frontend
docker run -p 3000:3000 fundtrace-frontend
```

---

## 📚 Documentation

- **Full Integration Guide**: `INTEGRATION_GUIDE.md`
- **Implementation Summary**: `IMPLEMENTATION_SUMMARY.md`
- **Frontend Details**: `frontend/FRONTEND_README.md`
- **API Documentation**: `backend/API.md`
- **Interactive API Docs**: http://localhost:8000/docs

---

## 🎯 Success Checklist

- [ ] Backend starts without errors
- [ ] Frontend loads at localhost:3000
- [ ] WebSocket shows "Connected" (green dot)
- [ ] Alerts appear in dashboard
- [ ] Clicking alert loads graph
- [ ] Clicking node shows evidence
- [ ] Search works in network page

---

## 🆘 Need Help?

1. Check logs in terminal
2. Check browser console (F12)
3. Review `INTEGRATION_GUIDE.md`
4. Verify environment variables
5. Ensure all services running

---

## 🎉 You're Ready!

System is working when you see:
- ✅ Backend: "Application startup complete"
- ✅ Frontend: "Ready in X.Xs"
- ✅ Dashboard: Green "Connected" dot
- ✅ Alerts: Streaming in left panel

**Happy fraud hunting!** 🕵️‍♂️
