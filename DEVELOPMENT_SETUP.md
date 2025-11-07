# Development Setup Guide

This guide covers setting up the AMA-IMPACT system for local development without Docker.

## Prerequisites

### System Requirements
- **Python 3.12+** (recommended: 3.12.x)
- **Node.js 18+** (recommended: 18.x or 20.x)
- **npm** (comes with Node.js)
- **Git**

### Operating System
- **Linux/macOS**: Primary development environments
- **Windows**: Supported via WSL2 (Windows Subsystem for Linux)

## Python Backend Setup

### 1. Create Virtual Environment

```bash
# Navigate to project root
cd AMA-IMPACT

# Create Python virtual environment
python -m venv .venv

# Alternative: Use python3 if python command not available
python3 -m venv .venv
```

### 2. Activate Virtual Environment

```bash
# Linux/macOS
source .venv/bin/activate

# Windows (if not using WSL2)
.venv\Scripts\activate

# Verify activation - should show (.venv) prefix in terminal
```

### 3. Install Python Dependencies

```bash
# Navigate to backend directory
cd backend

# Upgrade pip to latest version
pip install --upgrade pip

# Install all backend dependencies
pip install -r requirements.txt
```

### 4. Backend Dependencies (from requirements.txt)

**Core Framework:**
- `fastapi==0.104.1` - Modern web framework
- `uvicorn[standard]==0.24.0` - ASGI server
- `python-multipart==0.0.6` - Form data handling

**Database:**
- `sqlalchemy==2.0.23` - ORM
- `alembic==1.12.1` - Database migrations

**Authentication & Security:**
- `python-jose[cryptography]==3.3.0` - JWT tokens
- `passlib[bcrypt]==1.7.4` - Password hashing
- `bcrypt==4.1.1` - Encryption

**Validation:**
- `pydantic==2.5.0` - Data validation
- `pydantic-settings==2.1.0` - Settings management
- `email-validator==2.1.0` - Email validation

**Utilities:**
- `python-dotenv==1.0.0` - Environment variables
- `apscheduler==3.10.4` - Background tasks
- `jinja2==3.1.2` - Email templates
- `slowapi==0.1.9` - Rate limiting
- `python-dateutil==2.8.2` - Date utilities

**Development & Testing:**
- `pytest==7.4.3` - Testing framework
- `pytest-asyncio==0.21.1` - Async testing
- `httpx==0.25.2` - HTTP client for testing

**Production:**
- `gunicorn==21.2.0` - WSGI server

**Documentation:**
- `mkdocs==1.5.3` - Documentation generator
- `mkdocs-material==9.5.3` - Material theme

### 5. Setup Database

```bash
# Create database with sample data
python scripts/setup_dev_environment.py

# Alternative: Manual setup
python scripts/init_database.py
```

### 6. Run Backend Development Server

```bash
# Make sure you're in backend/ directory and venv is activated
uvicorn app.main:app --reload --port 8000

# Server will be available at:
# - API: http://localhost:8000
# - Swagger Docs: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
```

## Frontend Setup

### 1. Install Node.js Dependencies

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install all dependencies from package.json
npm install
```

### 2. Frontend Dependencies (from package.json)

**Core Framework:**
- `next@16.0.1` - React framework
- `react@19.2.0` - React library
- `react-dom@19.2.0` - React DOM renderer
- `typescript@^5` - TypeScript support

**UI Components:**
- `@radix-ui/react-*` - Accessible UI primitives
- `lucide-react@^0.552.0` - Icon library
- `tailwindcss@^4` - Utility-first CSS
- `tailwindcss-animate@^1.0.7` - Animation utilities
- `class-variance-authority@^0.7.1` - Component variants
- `clsx@^2.1.1` - Conditional classes
- `tailwind-merge@^3.3.1` - Tailwind class merging

**Data & State Management:**
- `@tanstack/react-query@^5.90.7` - Server state management
- `axios@^1.13.2` - HTTP client
- `zustand` (if needed) - Client state management

**Forms & Validation:**
- `react-hook-form@^7.66.0` - Form handling
- `@hookform/resolvers@^5.2.2` - Form validation resolvers
- `zod@^4.1.12` - Schema validation

**Charts & Data Visualization:**
- `recharts@^3.3.0` - Chart library
- `date-fns@^4.1.0` - Date utilities

**Development:**
- `@types/node@^20` - Node.js types
- `@types/react@^19` - React types
- `@types/react-dom@^19` - React DOM types
- `eslint@^9` - Code linting
- `eslint-config-next@16.0.1` - Next.js ESLint config

### 3. Run Frontend Development Server

```bash
# Make sure you're in frontend/ directory
npm run dev

# Server will be available at:
# http://localhost:3000
```

## Development Workflow

### Starting Development Session

```bash
# 1. Navigate to project root
cd /path/to/AMA-IMPACT

# 2. Activate Python virtual environment
source .venv/bin/activate

# 3. Start backend (Terminal 1)
cd backend
uvicorn app.main:app --reload --port 8000

# 4. Start frontend (Terminal 2 - new terminal)
cd frontend
npm run dev
```

### Environment Variables

#### Backend (.env)
Create `backend/.env` from `backend/.env.example`:

```bash
# Database
DATABASE_URL=sqlite:///./ama_impact.db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
FRONTEND_URL=http://localhost:3000

# Email (optional for development)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@ama-impact.com
```

#### Frontend (.env.local)
Create `frontend/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Common Issues & Solutions

### Python Virtual Environment

**Issue:** `pip: command not found` after activating venv
```bash
# Solution: Ensure venv is properly activated
source .venv/bin/activate
which pip  # Should show path within .venv
```

**Issue:** Permission denied when creating venv
```bash
# Solution: Check Python installation and permissions
python3 -m venv .venv --clear
```

### Frontend Dependencies

**Issue:** `Module not found: Can't resolve 'tailwindcss-animate'`
```bash
# Solution: Install missing dependency
cd frontend
npm install tailwindcss-animate
```

**Issue:** Node version compatibility
```bash
# Solution: Use Node Version Manager (nvm)
nvm install 18
nvm use 18
npm install
```

### Database Issues

**Issue:** Database not found
```bash
# Solution: Reinitialize database
cd backend
python scripts/setup_dev_environment.py
```

**Issue:** Migration errors
```bash
# Solution: Reset database (development only)
rm ama_impact.db
alembic upgrade head
python scripts/setup_dev_environment.py
```

## Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests (when implemented)
```bash
cd frontend
npm test
```

## Production Deployment Differences

For production deployment, you would typically:

1. **Use PostgreSQL** instead of SQLite
2. **Set production environment variables**
3. **Use production ASGI server** (gunicorn + uvicorn)
4. **Build optimized frontend** (`npm run build`)
5. **Use reverse proxy** (nginx)
6. **Enable HTTPS/SSL certificates**

This guide focuses on development setup with SQLite and development servers.

## Troubleshooting

### Check System Requirements
```bash
# Python version
python --version  # Should be 3.12+

# Node version
node --version   # Should be 18+

# npm version
npm --version

# Check if virtual environment is active
echo $VIRTUAL_ENV  # Should show path to .venv
```

### Verify Installations
```bash
# Backend dependencies
cd backend
pip list | grep fastapi

# Frontend dependencies  
cd frontend
npm list --depth=0
```

### Port Conflicts
```bash
# Kill process using port 8000
pkill -f "uvicorn.*8000"

# Kill process using port 3000
pkill -f "next dev"
```

---

**Note:** Always ensure your virtual environment is activated before running any Python commands or installing packages. This keeps dependencies isolated and prevents conflicts with system Python packages.