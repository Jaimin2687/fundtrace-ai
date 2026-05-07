# FundTrace AI - Pre-Demo Checklist

## ✅ Before the Demo

### 1. Environment Setup

- [ ] **Neo4j is running**
  ```bash
  neo4j status
  # Should show: Neo4j is running
  ```
  
- [ ] **Environment files exist**
  - [ ] `.env` exists in project root
  - [ ] `frontend/.env.local` exists
  - [ ] API keys match in both files

- [ ] **Dependencies installed**
  ```bash
  # Backend
  pip list | grep fastapi
  pip list | grep neo4j
  pip list | grep xgboost
  
  # Frontend
  cd frontend && npm list react-force-graph-2d
  ```

---

### 2. Data & Model

- [ ] **Data ingested to Neo4j**
  ```bash
  # Check if transactions exist
  cypher-shell -u neo4j -p password \
    "MATCH (t:Transaction) RETURN count(t) AS total"
  # Should return: 46,564 (or at least > 0)
  ```

- [ ] **ML model trained**
  ```bash
  ls -lh data/fraud_model.json
  # Should exist and be ~1-5MB
  ```

- [ ] **Demo data seeded (optional)**
  ```bash
  curl -X POST -H "X-API-Key: fraudtrace-dev-key-2026" \
    http://localhost:8000/api/v1/graph/seed-demo
  # Or use "Seed Demo Data" button in dashboard
  ```

---

### 3. Backend Health

- [ ] **Backend starts without errors**
  ```bash
  uvicorn backend.main:app --reload --port 8000
  ```
  
  Expected output:
  ```
  ✓ Step 1: Neo4j driver initialized
  ✓ Step 2: ML model found at data/fraud_model.json
  ✓ Step 3a: Alert broadcaster started
  ✓ Step 3b: Transaction scoring worker started
  ✓ Step 3c: PaySim alert streamer started
  ✅ FundTrace AI running at http://localhost:8000
  ```

- [ ] **Health check works**
  ```bash
  curl http://localhost:8000/
  # Should return: {"status":"ok","service":"FundTrace AI"}
  ```

- [ ] **API authentication works**
  ```bash
  curl -H "X-API-Key: fraudtrace-dev-key-2026" \
    http://localhost:8000/api/v1/graph/stats
  # Should return graph statistics JSON
  ```

- [ ] **WebSocket connection works**
  ```bash
  wscat -c ws://localhost:8000/api/v1/stream/alerts
  # Should connect and stream alerts
  ```

---

### 4. Frontend Health

- [ ] **Frontend starts without errors**
  ```bash
  cd frontend && npm run dev
  ```
  
  Expected output:
  ```
  ▲ Next.js 16.2.4
  - Local:   http://localhost:3000
  ✓ Ready in X.Xs
  ```

- [ ] **Dashboard loads**
  - Open http://localhost:3000/dashboard
  - Should see "FundTrace AI" title
  - Should see stats row (even if zeros)
  - Should see green "Connected" dot in left panel

- [ ] **Network page loads**
  - Open http://localhost:3000/network
  - Should see search bar and controls
  - Should see empty graph (or demo data if seeded)

- [ ] **Demo page loads**
  - Open http://localhost:3000/demo
  - Should see 4 step cards
  - Should see "Run Full Demo" button

---

### 5. Integration Tests

- [ ] **Alert streaming works**
  - Dashboard → Left panel shows "Connected" (green dot)
  - Wait 5-10 seconds
  - Alerts should appear in left panel
  - Click an alert → Graph should load in center

- [ ] **Graph interaction works**
  - Click a node in graph
  - Evidence panel should slide in from right
  - Should show transaction details

- [ ] **Search works**
  - Network page → Enter transaction ID
  - Click "Search"
  - Graph should load

- [ ] **Fraud clusters work**
  - Dashboard → Click "Load Fraud Clusters"
  - Graph should show fraud network
  - Red nodes should be visible

- [ ] **Demo walkthrough works**
  - Demo page → Click "Run Full Demo"
  - Should auto-play through 4 steps
  - Graph and evidence should update

---

### 6. Performance Check

- [ ] **Backend response time < 1s**
  ```bash
  time curl -H "X-API-Key: fraudtrace-dev-key-2026" \
    http://localhost:8000/api/v1/graph/stats
  # Should complete in < 1 second
  ```

- [ ] **Graph renders smoothly**
  - Load fraud clusters
  - Graph should render without lag
  - Nodes should be interactive

- [ ] **WebSocket latency < 100ms**
  - Alerts should appear immediately
  - No noticeable delay

---

### 7. Browser Compatibility

- [ ] **Chrome/Edge** - Primary browser
- [ ] **Firefox** - Backup browser
- [ ] **Safari** - If on Mac

Test in at least one browser:
- Dashboard loads
- Graph renders
- WebSocket connects
- Evidence panel works

---

### 8. Demo Scenarios

Prepare these scenarios for judges:

#### Scenario 1: Real-time Monitoring
1. Open dashboard
2. Show live alerts streaming
3. Click an alert
4. Show graph visualization
5. Click a node
6. Show evidence package

#### Scenario 2: Investigation
1. Open network page
2. Search for a fraud transaction
3. Show subgraph
4. Explain patterns
5. Download evidence

#### Scenario 3: Automated Demo
1. Open demo page
2. Click "Run Full Demo"
3. Explain each step as it runs
4. Show final evidence package

---

### 9. Backup Plans

- [ ] **If Neo4j is empty**
  - Use "Seed Demo Data" button
  - Shows 3 fraud patterns immediately

- [ ] **If WebSocket fails**
  - Use "Load Fraud Clusters" button
  - Show static graph visualization

- [ ] **If backend crashes**
  - Have screenshots ready
  - Have video recording as backup

- [ ] **If frontend crashes**
  - Use API docs at http://localhost:8000/docs
  - Show curl commands

---

### 10. Presentation Prep

- [ ] **Screen resolution set to 1920x1080**
- [ ] **Browser zoom at 100%**
- [ ] **Close unnecessary tabs**
- [ ] **Disable notifications**
- [ ] **Full screen browser (F11)**
- [ ] **Terminal ready with commands**
- [ ] **Backup browser open**

---

## 🚨 Common Issues & Fixes

### Issue: "Neo4j connection failed"
**Fix:**
```bash
neo4j start
# Or
docker run -p 7687:7687 -p 7474:7474 -e NEO4J_AUTH=neo4j/password neo4j:5
```

### Issue: "WebSocket disconnected"
**Fix:**
- Check backend is running
- Verify CORS_ORIGINS includes http://localhost:3000
- Restart backend

### Issue: "No alerts appearing"
**Fix:**
- Check ML worker logs in backend terminal
- Verify model exists: `ls data/fraud_model.json`
- Use "Seed Demo Data" button

### Issue: "Graph not rendering"
**Fix:**
- Check browser console for errors
- Try different browser
- Reload page (Ctrl+R)

### Issue: "API returns 401"
**Fix:**
- Verify API keys match in `.env` and `frontend/.env.local`
- Restart both backend and frontend

---

## 📊 Expected Metrics

When everything is working:

- **Neo4j**: 46,564+ transactions, 234,355+ edges
- **Backend**: 3 workers running, alerts every 3-5 seconds
- **Frontend**: Green "Connected" dot, alerts streaming
- **Response time**: < 1 second for API calls
- **Graph**: Renders in < 2 seconds

---

## 🎯 Demo Script

### Opening (30 seconds)
"FundTrace AI is a real-time fraud detection system that combines graph databases, machine learning, and interactive visualization to detect money laundering patterns in financial networks."

### Live Demo (2 minutes)
1. **Show Dashboard** - "Here's our live monitoring dashboard"
2. **Point to alerts** - "Alerts are streaming in real-time via WebSocket"
3. **Click alert** - "When we click an alert, we see the transaction network"
4. **Click node** - "Clicking a node shows the evidence package"
5. **Show patterns** - "We detect 4 fraud patterns: structuring, layering, round-tripping, and dormant accounts"

### Technical Deep Dive (1 minute)
1. **Show Network page** - "Investigators can search any transaction"
2. **Search demo transaction** - "Here's a confirmed fraud case"
3. **Show evidence** - "The system generates comprehensive evidence packages"
4. **Download JSON** - "Evidence can be exported for compliance"

### Closing (30 seconds)
"FundTrace AI processes 46,000+ transactions, detects fraud in real-time, and provides actionable evidence for investigators. Built with Neo4j, XGBoost, FastAPI, and Next.js."

---

## ✅ Final Checklist

Before starting the demo:

- [ ] Backend running (green checkmarks in terminal)
- [ ] Frontend running (no errors in terminal)
- [ ] Dashboard open in browser
- [ ] WebSocket connected (green dot)
- [ ] Alerts streaming
- [ ] Graph loads when clicking alert
- [ ] Evidence panel works
- [ ] Demo page tested
- [ ] Backup browser ready
- [ ] Screen recording started (optional)

---

## 🎉 You're Ready!

If all checkboxes are checked, you're ready to demo FundTrace AI!

**Good luck!** 🚀
