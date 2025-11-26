@echo off
REM Loan Assessment API - Quick Start Script (Windows)
REM This script sets up and starts the FastAPI backend

echo ======================================================
echo 🚀 Loan Assessment API - Backend Setup
echo ======================================================

REM Check Python version
echo.
echo 📌 Checking Python version...
python --version

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo.
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo.
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Check if .env exists
if not exist ".env" (
    echo.
    echo ⚠️  No .env file found. Creating from .env.example...
    copy .env.example .env
    echo ❗ IMPORTANT: Edit .env file and add your HuggingFace token!
    echo    Get token from: https://huggingface.co/settings/tokens
    echo.
    pause
)

REM Create temp directory
echo.
echo 📁 Creating temporary upload directory...
if not exist "temp_uploads" mkdir temp_uploads

REM Test imports
echo.
echo 🧪 Testing imports...
python -c "from extractor import extract_text; print('✓ extractor.py')"
python -c "from llm_analyzer import analyze_loan_risk; print('✓ llm_analyzer.py')"

REM Start server
echo.
echo ======================================================
echo ✅ Setup complete! Starting server...
echo ======================================================
echo.
echo 🌐 Backend will be available at: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo 📊 Health Check: http://localhost:8000/api/health
echo.
echo Press Ctrl+C to stop the server
echo.

python main.py
