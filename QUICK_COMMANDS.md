# Quick Development Commands

**Essential commands for daily development**

## Start Development Session

```bash
# 1. Activate Python environment
source .venv/bin/activate

# 2. Start backend (Terminal 1)
cd backend && uvicorn app.main:app --reload --port 8000

# 3. Start frontend (Terminal 2) 
cd frontend && npm run dev
```

## Package Installation

```bash
# Python packages (with venv activated)
cd backend
pip install package_name
pip freeze > requirements.txt

# Node packages
cd frontend  
npm install package_name
npm install  # Install all from package.json
```

## Common Issues

```bash
# Missing tailwindcss-animate
cd frontend && npm install tailwindcss-animate

# Reset database
cd backend && rm ama_impact.db && python scripts/setup_dev_environment.py

# Kill conflicting processes
pkill -f "uvicorn.*8000" && pkill -f "next dev"

# Verify venv activation
echo $VIRTUAL_ENV  # Should show .venv path
```

## URLs
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs  
- **Frontend**: http://localhost:3000

## Test Credentials
- **HR**: hr@ama-impact.com / HR123!
- **PM**: pm@ama-impact.com / PM123!
- **Admin**: admin@ama-impact.com / Admin123!