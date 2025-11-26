#!/bin/bash

echo "================================"
echo "BadDebtGuard AI - Quick Start"
echo "================================"
echo ""

echo "Starting Backend Server..."
cd backend
python -m app.main &
BACKEND_PID=$!

cd ..
sleep 3

echo "Starting Frontend Development Server..."
cd frontend
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "================================"
echo "Both servers are running!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "================================"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
