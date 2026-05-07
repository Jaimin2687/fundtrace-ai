#!/bin/bash
# Starts backend and frontend together

echo "=========================================="
echo "Starting FundTrace AI..."
echo "=========================================="
echo ""

# Start backend in background
echo "Starting backend on http://localhost:8000..."
uvicorn backend.main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend in background
echo "Starting frontend on http://localhost:3000..."
cd frontend && npm run dev &
FRONTEND_PID=$!

echo ""
echo "=========================================="
echo "FundTrace AI is running!"
echo "=========================================="
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:3000/dashboard"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both services"
echo "=========================================="
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
