#!/bin/bash
# Start the Generic Ordering Service Enhanced
# This starts both the backend API and frontend dev server

echo "========================================="
echo "  OmniAssist AI - Universal Service Platform"
echo "========================================="

# Start backend
echo ""
echo "Starting backend API on http://localhost:8000..."
cd "$(dirname "$0")"
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait for backend to be ready
sleep 2

# Start frontend
echo "Starting frontend on http://localhost:3000..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "========================================="
echo "  Backend:  http://localhost:8000/api/health"
echo "  Frontend: http://localhost:3000"
echo "========================================="
echo ""
echo "Login credentials:"
echo "  Admin:   admin / Admin@123!"
echo "  Manager: manager1 / Manager@123!"
echo "  User:    john_doe / User@1234!"
echo ""
echo "Press Ctrl+C to stop all services"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
