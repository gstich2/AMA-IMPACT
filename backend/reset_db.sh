#!/bin/bash

# AMA-IMPACT Database Reset and Seed Script
# This script resets the database and creates initial admin user + sample data

echo "🔄 AMA-IMPACT Database Reset & Seed"
echo "======================================"
echo ""

# Navigate to backend directory
cd "$(dirname "$0")"

# Activate virtual environment
if [ ! -d "../.venv" ]; then
    echo "❌ Virtual environment not found! Run setup first."
    exit 1
fi

source ../.venv/bin/activate

# Confirm reset
read -p "⚠️  This will DELETE all data and reset the database. Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Aborted."
    exit 1
fi

echo ""
echo "🗑️  Step 1: Removing old database..."
rm -f ama_impact.db ama_impact.db-shm ama_impact.db-wal
echo "✅ Old database removed"

echo ""
echo "🔧 Step 2: Resetting Alembic..."
rm -rf alembic/versions/*.py
echo "✅ Alembic versions cleared"

echo ""
echo "📝 Step 3: Creating fresh migration..."
alembic revision --autogenerate -m "Initial migration - fresh start"
echo "✅ Migration created"

echo ""
echo "📦 Step 4: Applying migration..."
alembic upgrade head
echo "✅ Database schema created"

echo ""
echo "🌱 Step 5: Seeding database with initial data..."
python seed.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Database reset and seeded successfully!"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📋 DEFAULT USER CREDENTIALS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "👨‍💼 ADMIN (Full System Access)"
    echo "   Email:    admin@ama-impact.com"
    echo "   Password: Admin123!"
    echo ""
    echo "👔 HR (Multi-Contract Access)"
    echo "   Email:    hr@ama-impact.com"
    echo "   Password: HR123!"
    echo ""
    echo "📊 PROGRAM MANAGER (Contract-Wide)"
    echo "   Email:    pm@ama-impact.com"
    echo "   Password: PM123!"
    echo ""
    echo "👨‍💻 TECH LEAD (Team-Level)"
    echo "   Email:    techlead@ama-impact.com"
    echo "   Password: Tech123!"
    echo ""
    echo "👤 STAFF (Self-Only)"
    echo "   Email:    staff@ama-impact.com"
    echo "   Password: Staff123!"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📦 SAMPLE DATA CREATED:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "   • 2 Contracts (ASSESS-2025, RESESS-2025)"
    echo "   • 12 Visa Types (H1B, L1, O1, TN, EB-1A/B, etc.)"
    echo "   • 5 Users with role hierarchy"
    echo ""
    echo "🚀 Start the server with: ./start.sh"
    echo "📚 API Docs: http://localhost:8000/docs"
    echo ""
else
    echo ""
    echo "❌ Database seeding failed. Check errors above."
    exit 1
fi
