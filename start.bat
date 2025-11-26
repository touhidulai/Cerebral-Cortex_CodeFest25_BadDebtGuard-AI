@echo off
echo ================================
echo BadDebtGuard AI - Quick Start
echo ================================
echo.

echo Starting Backend Server...
start cmd /k "cd backend && python -m app.main"

timeout /t 3 /nobreak > nul

echo Starting Frontend Development Server...
start cmd /k "cd frontend && npm run dev"

echo.
echo ================================
echo Both servers are starting!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo ================================
