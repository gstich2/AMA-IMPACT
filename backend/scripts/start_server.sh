#!/bin/bash
# Start AMA-IMPACT Backend Server
# Automatically detects environment from .env file

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_DIR="$(dirname "$BACKEND_DIR")"

cd "$BACKEND_DIR"

# Check which environment file to use
if [ -f "$BACKEND_DIR/.env" ]; then
    ENV_FILE="$BACKEND_DIR/.env"
elif [ -f "$BACKEND_DIR/.env.development" ]; then
    ENV_FILE="$BACKEND_DIR/.env.development"
    echo "⚠️  No .env found, using .env.development"
else
    echo "❌ No environment file found!"
    echo "   Please create .env or copy from .env.development or .env.production.example"
    exit 1
fi

# Load environment
export $(grep -v '^#' "$ENV_FILE" | xargs)

# Activate virtual environment
if [ -f "$PROJECT_DIR/.venv/bin/activate" ]; then
    source "$PROJECT_DIR/.venv/bin/activate"
else
    echo "❌ Virtual environment not found at $PROJECT_DIR/.venv"
    exit 1
fi

# Determine mode based on DEBUG setting
if [ "$DEBUG" = "True" ] || [ "$DEBUG" = "true" ]; then
    MODE="DEVELOPMENT"
    RELOAD_FLAG="--reload"
else
    MODE="PRODUCTION"
    RELOAD_FLAG=""
fi

echo "🚀 Starting AMA-IMPACT Backend Server"
echo "   Mode: $MODE"
echo "   Database: $DB_NAME"
if [ -n "$RELOAD_FLAG" ]; then
    echo "   Auto-reload: enabled"
fi
echo "   API Docs: http://localhost:8000/docs"
echo ""

PYTHONPATH="$BACKEND_DIR" python -m uvicorn app.main:app $RELOAD_FLAG --host 0.0.0.0 --port 8000
