# 🚀 Getting Started with AMA-IMPACT

> **⚠️ This file contains condensed setup instructions. For comprehensive documentation, see:**
> - **[Full Documentation](docs/)** - Complete guides and API reference
> - **[Quick Start Guide](docs/getting-started/quickstart.md)** - Detailed 10-minute setup
> - **[Development Guide](docs/development/setup.md)** - Development workflow and testing

## Project Overview

**AMA-IMPACT v2.0** is a full-stack immigration visa management system with:
- **Backend:** FastAPI + SQLAlchemy + SQLite (WAL mode)
- **Frontend:** Next.js 14 + TypeScript + Tailwind CSS
- **Key Features:** Case Groups, Todo System, Hierarchical Departments, Role-Based Access

## 📋 Prerequisites

- **Python 3.12+**
- **Node.js 18+**
- **Git**

---

## 🛠️ Backend Setup (FastAPI)

### 1. Navigate to Backend Directory

```bash
cd backend
```

### 2. Create Virtual Environment

```bash
python -m venv ../.venv
```

### 3. Activate Virtual Environment

**Linux/Mac:**
```bash
source ../.venv/bin/activate
```

**Windows:**
```cmd
..\.venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Setup Database with Fixtures

```bash
python scripts/setup_dev_environment.py
```

This creates the database with:
- 2 contracts (ASSESS, RSES)
- 11 departments (9 ASSESS + 2 RSES)
- 6 test users (see [CREDENTIALS.md](CREDENTIALS.md))
- Sample visa applications, case groups, and todos

### 6. Start Backend Server

```bash
uvicorn app.main:app --reload --port 8000
```

### 7. Verify Backend is Running

- **API Docs (Swagger):** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

**Test Login:**
- Use credentials from [CREDENTIALS.md](CREDENTIALS.md)
- Default admin: `admin@ama-impact.com` / `Admin123!`

---

## 🎨 Frontend Setup (Next.js)

### 1. Navigate to Frontend Directory

```bash
cd frontend
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Configure Environment Variables

Create `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4. Start Development Server

```bash
npm run dev
```

### 5. Verify Frontend is Running

Open your browser and visit: http://localhost:3000

---

## 🧪 Testing the Application

The fixture system creates test users automatically. See [CREDENTIALS.md](CREDENTIALS.md) for login details.

**Quick Test:**
1. Go to http://localhost:8000/docs
2. Click **Authorize**
3. Login with admin credentials: `admin@ama-impact.com` / `Admin123!`
4. Test any endpoint

---

## 📊 Key Features in v2.0

- **Case Groups** - Organize related visa applications (e.g., H1B → Green Card pathway)
- **Todo System** - Task tracking with computed metrics (overdue, completion time)
- **Departments API** - Full CRUD for organizational structure
- **Hierarchical Visibility** - Users see data based on role and organizational structure
- **Role-Based User Creation** - Controlled permissions for creating new users

**For complete feature list, see [README.md](README.md) or [PRD.md](PRD.md)**

---

## 🔐 User Roles

| Role | Access Level | Can Create Users |
|------|-------------|------------------|
| **ADMIN** | System-wide | Any role |
| **HR** | Multi-contract | BENEFICIARY only |
| **PM** | Contract-wide | BENEFICIARY only |
| **MANAGER** | Team-level | BENEFICIARY only |
| **BENEFICIARY** | Self-only | Cannot create users |

See [CREDENTIALS.md](CREDENTIALS.md) for test user accounts.

---

## 🐛 Troubleshooting

### Backend Won't Start
**Error:** `ModuleNotFoundError: No module named 'app'`  
**Solution:** Ensure you're in the `backend/` directory and virtual environment is activated

### Database Error
**Solution:** Re-run setup script: `python scripts/setup_dev_environment.py`

### Virtual Environment Issues
**Error:** `command not found: uvicorn`  
**Solution:** Activate virtual environment: `source ../.venv/bin/activate`

**For more troubleshooting, see [Development Guide](docs/development/setup.md)**

---

## 📚 Documentation

- **[README.md](README.md)** - Project overview and features
- **[PRD.md](PRD.md)** - Product requirements and specifications
- **[CREDENTIALS.md](CREDENTIALS.md)** - Test user accounts
- **[docs/](docs/)** - Complete documentation site
  - [Quick Start](docs/getting-started/quickstart.md) - Detailed setup guide
  - [Development Guide](docs/development/setup.md) - Development workflow
  - [API Reference](docs/api/overview.md) - Complete API documentation
  - [Data Models](docs/architecture/data-models.md) - Database schema

---

## � Common Development Tasks

**See [Development Guide](docs/development/setup.md) for:**
- Adding database migrations
- Creating new API endpoints
- Running tests
- Code standards and conventions

---

**Happy Coding! 🎉**
