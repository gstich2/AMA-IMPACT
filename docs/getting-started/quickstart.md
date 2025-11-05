# Quick Start Guide

Get AMA-IMPACT up and running in under 10 minutes.

## Prerequisites

- **Python 3.12+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/))

## Step 1: Clone Repository

```bash
git clone https://github.com/gstich2/AMA-IMPACT.git
cd AMA-IMPACT
```

## Step 2: Backend Setup

### Create Virtual Environment

```bash
python -m venv .venv

# Activate (Linux/Mac)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate
```

### Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Setup Database & Fixtures

```bash
python scripts/setup_dev_environment.py
```

This script will:
- ✅ Initialize database tables
- ✅ Create admin, HR, PM, manager users
- ✅ Load contracts (ASSESS)
- ✅ Load departments
- ✅ Create sample beneficiaries
- ✅ Create visa applications
- ✅ Create case groups
- ✅ Create sample todos

### Start Backend Server

```bash
uvicorn app.main:app --reload --port 8000
```

**Server running at:** `http://localhost:8000`

**API Documentation:** `http://localhost:8000/docs`

## Step 3: Frontend Setup

### Install Dependencies

```bash
cd ../frontend
npm install
```

### Configure Environment

Create `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### Start Frontend

```bash
npm run dev
```

**Frontend running at:** `http://localhost:3000`

## Step 4: Login

### Default Users

The setup script creates these test users:

| Role | Email | Password |
|------|-------|----------|
| **Admin** | admin@ama-impact.com | adminpass123 |
| **HR** | hr@ama-impact.com | securepass123 |
| **PM** | pm@ama-impact.com | securepass123 |
| **Manager** | techlead@ama-impact.com | securepass123 |
| **Beneficiary** | priya.sharma@ama-impact.com | securepass123 |

### Login via API

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@ama-impact.com&password=adminpass123"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Step 5: Explore the API

### Interactive Documentation

Visit `http://localhost:8000/docs` for Swagger UI

### Example API Calls

**Get current user:**
```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**List beneficiaries:**
```bash
curl -X GET "http://localhost:8000/api/v1/beneficiaries" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Get my todos:**
```bash
curl -X GET "http://localhost:8000/api/v1/todos/my-todos" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Project Structure

```
AMA-IMPACT/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Config, database, security
│   │   ├── models/       # SQLAlchemy models
│   │   └── schemas/      # Pydantic schemas
│   ├── scripts/
│   │   └── fixtures/     # Database seed data
│   ├── devel.db          # SQLite database
│   └── requirements.txt
│
├── frontend/
│   ├── app/              # Next.js app router
│   ├── components/       # React components
│   └── package.json
│
└── docs/                 # This documentation
```

## What's Included

The setup script creates sample data:

### Contracts & Departments
- **ASSESS Contract** with 3 departments:
  - Technical & Scientific Management (TSM)
  - Technical Numerical Analysis (TNA)
  - IT & Data Systems (ITDS)

### Users
- 1 Admin, 1 HR, 1 PM, 3 Managers
- 6 Beneficiary employees (Luis, Priya, Wei, Elena, Carlos, Yuki)

### Visa Applications
- Luis: EB2-NIW I-140 (Approved)
- Priya: H1B Extension (In Progress)
- Wei: TN Status (Active)
- Elena: EB2-NIW I-140 (In Progress)

### Case Groups
- Luis: "EB2-NIW to Green Card Pathway"
- Priya: "H1B Extension 2025"
- Elena: "EB2-NIW Pathway"

### Todos
- 7 sample todos with various priorities and statuses
- Assigned to different users
- Linked to visa applications and case groups

## Common Tasks

### Reset Database

```bash
cd backend
rm devel.db
python scripts/setup_dev_environment.py
```

### Run Backend Tests

```bash
cd backend
pytest
```

### View Database

```bash
cd backend
sqlite3 devel.db
```

```sql
-- List all users
SELECT email, role FROM users;

-- List all beneficiaries
SELECT first_name, last_name, current_visa_type FROM beneficiaries;

-- List all todos
SELECT title, status, priority, due_date FROM todos;
```

## Troubleshooting

### Port Already in Use

**Backend:**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn app.main:app --reload --port 8001
```

**Frontend:**
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or use different port
npm run dev -- -p 3001
```

### Database Locked

```bash
# Stop all servers
pkill -f uvicorn

# Remove database lock
rm backend/devel.db-shm backend/devel.db-wal

# Restart
cd backend
uvicorn app.main:app --reload --port 8000
```

### Module Not Found

```bash
# Ensure virtual environment is activated
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Reinstall dependencies
cd backend
pip install -r requirements.txt
```

## Next Steps

- [Explore API Documentation](../api/overview.md)
- [Understanding Data Models](../architecture/data-models.md)
- [Development Guide](../development/setup.md)
- [Read the PRD](../product/prd.md)

## Need Help?

- **API Issues**: Check `http://localhost:8000/docs`
- **Database Issues**: See [Database Guide](../development/database.md)
- **Contact**: dev-team@ama-inc.com
