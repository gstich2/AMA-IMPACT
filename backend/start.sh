#!/bin/bash

# AMA-IMPACT Backend Startup Script

echo "🚀 Starting AMA-IMPACT Backend..."

# Navigate to backend directory
cd "$(dirname "$0")"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found! Copying from .env.example..."
    cp .env.example .env
    echo "✅ .env file created. Please update it with your configuration."
    exit 1
fi

# Activate virtual environment
if [ ! -d "../.venv" ]; then
    echo "⚠️  Virtual environment not found! Creating one..."
    python -m venv ../.venv
    source ../.venv/bin/activate
    pip install -r requirements.txt
else
    source ../.venv/bin/activate
fi

# Run migrations
echo "📦 Running database migrations..."
alembic upgrade head

# Start the server
echo "🌐 Starting FastAPI server at http://localhost:8000"
echo "📚 API Documentation available at http://localhost:8000/docs"
echo ""
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
