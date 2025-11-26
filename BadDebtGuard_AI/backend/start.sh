#!/bin/bash

# Loan Assessment API - Quick Start Script
# This script sets up and starts the FastAPI backend

echo "======================================================"
echo "🚀 Loan Assessment API - Backend Setup"
echo "======================================================"

# Check Python version
echo ""
echo "📌 Checking Python version..."
python3 --version || python --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv || python -m venv venv
fi

# Activate virtual environment
echo ""
echo "🔧 Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "❗ IMPORTANT: Edit .env file and add your HuggingFace token!"
    echo "   Get token from: https://huggingface.co/settings/tokens"
    echo ""
    read -p "Press Enter when you've added your token to continue..."
fi

# Create temp directory
echo ""
echo "📁 Creating temporary upload directory..."
mkdir -p temp_uploads

# Test imports
echo ""
echo "🧪 Testing imports..."
python -c "from extractor import extract_text; print('✓ extractor.py')"
python -c "from llm_analyzer import analyze_loan_risk; print('✓ llm_analyzer.py')"

# Start server
echo ""
echo "======================================================"
echo "✅ Setup complete! Starting server..."
echo "======================================================"
echo ""
echo "🌐 Backend will be available at: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "📊 Health Check: http://localhost:8000/api/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python main.py
