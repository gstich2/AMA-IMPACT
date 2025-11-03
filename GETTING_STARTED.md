# 🚀 Getting Started with AMA-IMPACT

## Project Overview

**AMA-IMPACT** is a full-stack immigration visa management system built with:
- **Backend:** FastAPI + SQLAlchemy + SQLite
- **Frontend:** Next.js 14 + TypeScript + Tailwind CSS
- **Authentication:** JWT tokens with bcrypt password hashing
- **Database:** SQLite with WAL mode (Write-Ahead Logging)

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/))
- **npm** or **yarn** (comes with Node.js)

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

### 5. Configure Environment Variables

```bash
cp .env.example .env
```

**Edit `.env` and update the following:**

```bash
# Generate a secure SECRET_KEY:
openssl rand -hex 32

# Update .env with generated key:
SECRET_KEY=your-generated-key-here

# Email configuration (optional for MVP):
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 6. Initialize Database

```bash
alembic upgrade head
```

This creates the SQLite database with all tables.

### 7. Start Backend Server

**Option A - Using the startup script:**
```bash
./start.sh
```

**Option B - Manual start:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 8. Verify Backend is Running

Open your browser and visit:
- **API Root:** http://localhost:8000
- **API Docs (Swagger):** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

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

### Create Your First Admin User

Use the API documentation at http://localhost:8000/docs:

1. Navigate to **POST /api/v1/auth/register**
2. Click "Try it out"
3. Enter the following JSON:

```json
{
  "email": "admin@ama-impact.com",
  "password": "SecurePassword123!",
  "full_name": "System Administrator",
  "role": "admin",
  "phone": "+1-555-0100"
}
```

4. Click "Execute"

### Login and Get JWT Token

1. Navigate to **POST /api/v1/auth/login**
2. Enter credentials:
   - **username:** `admin@ama-impact.com`
   - **password:** `SecurePassword123!`
3. Copy the `access_token` from the response
4. Click the **Authorize** button at the top
5. Enter: `Bearer <your-access-token>`
6. Now you can test all protected endpoints!

---

## 📊 Database Schema

The database includes the following tables:

- **users** - User accounts with roles and authentication
- **contracts** - Company contracts (ASSESS, RESESS, etc.)
- **visa_applications** - Visa/green card tracking records
- **visa_types** - Visa type definitions (H-1B, L-1, etc.)
- **audit_logs** - Complete audit trail
- **notifications** - In-app notifications
- **email_logs** - Email delivery tracking
- **user_settings** - User preferences and alert thresholds

---

## 🔐 User Roles

| Role | Access Level | Permissions |
|------|-------------|-------------|
| **admin** | System-wide | Full access to all contracts, users, and settings |
| **hr** | Multi-contract | View/edit assigned contracts, generate reports |
| **program_manager** | Contract-wide | View/edit entire contract, receive critical alerts |
| **tech_lead** | Team-level | View/edit direct and indirect reports |
| **staff** | Self-only | View own visa status, receive personal alerts |

---

## 📝 Common Tasks

### Create a New Contract

**API Endpoint:** `POST /api/v1/contracts`

```json
{
  "name": "ASSESS Program",
  "code": "ASSESS-2025",
  "start_date": "2025-01-01",
  "status": "active"
}
```

### Create a Visa Application

**API Endpoint:** `POST /api/v1/visa-applications`

```json
{
  "user_id": "<user_uuid>",
  "visa_type_id": "<visa_type_uuid>",
  "visa_type": "H1B",
  "status": "in_progress",
  "priority": "high",
  "filing_date": "2025-01-15",
  "expiration_date": "2028-01-15"
}
```

### View Dashboard Data

**API Endpoint:** `GET /api/v1/reports/dashboard`

This returns role-filtered statistics for the current user.

---

## 🐛 Troubleshooting

### Backend Won't Start

**Error:** `ModuleNotFoundError: No module named 'app'`

**Solution:** Make sure you're running from the `backend/` directory:
```bash
cd backend
uvicorn app.main:app --reload
```

### Database Error

**Error:** `alembic.util.exc.CommandError: Target database is not up to date.`

**Solution:** Run migrations:
```bash
cd backend
alembic upgrade head
```

### Frontend Can't Connect to Backend

**Error:** `fetch failed` or `CORS error`

**Solution:**
1. Verify backend is running at http://localhost:8000
2. Check `.env.local` has correct API URL
3. Ensure CORS is configured in `backend/app/core/config.py`

### Virtual Environment Issues

**Error:** `command not found: uvicorn`

**Solution:** Activate the virtual environment:
```bash
source ../.venv/bin/activate  # Linux/Mac
# or
..\.venv\Scripts\activate  # Windows
```

---

## 📚 Next Steps

1. **Read the PRD:** Review `PRD.md` for complete feature specifications
2. **Explore API Docs:** http://localhost:8000/docs for all endpoints
3. **Check Models:** Review `backend/app/models/` for data structures
4. **Review Schemas:** See `backend/app/schemas/` for API contracts

---

## 🔧 Development Workflow

### Making Database Changes

1. Update models in `backend/app/models/`
2. Generate migration:
   ```bash
   alembic revision --autogenerate -m "Description of change"
   ```
3. Review migration in `backend/alembic/versions/`
4. Apply migration:
   ```bash
   alembic upgrade head
   ```

### Adding a New API Endpoint

1. Create/update router in `backend/app/api/v1/`
2. Add Pydantic schemas in `backend/app/schemas/`
3. Implement CRUD operations in `backend/app/crud/` (if needed)
4. Register router in `backend/app/main.py`

### Frontend Development

1. Create components in `frontend/components/`
2. Add pages in `frontend/app/`
3. Use Tailwind CSS for styling
4. Connect to API using `fetch` or `axios`

---

## 📦 Project Structure

```
AMA-IMPACT/
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── api/v1/            # API routes (auth, users, contracts, visas)
│   │   ├── core/              # Config, database, security
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic validation schemas
│   │   ├── crud/              # Database operations (future)
│   │   ├── services/          # Business logic (future)
│   │   └── main.py            # FastAPI app initialization
│   ├── alembic/               # Database migrations
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example           # Environment template
│   └── start.sh               # Startup script
├── frontend/                  # Next.js application
│   ├── app/                   # Next.js 14 App Router pages
│   ├── components/            # React components (to be added)
│   ├── lib/                   # Utilities and API client (to be added)
│   ├── package.json           # Node dependencies
│   └── .env.local             # Frontend environment variables
├── PRD.md                     # Product Requirements Document
├── README.md                  # Project overview
├── GETTING_STARTED.md         # This file
└── .gitignore                 # Git ignore rules
```

---

## 🚀 Production Deployment

### Backend

1. **Set production environment variables:**
   ```bash
   DEBUG=False
   DATABASE_URL=sqlite:///./ama_impact.db  # or PostgreSQL for scale
   ```

2. **Run with Gunicorn:**
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

3. **Set up Nginx reverse proxy:**
   ```nginx
   location / {
       proxy_pass http://localhost:8000;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
   }
   ```

### Frontend

1. **Build production bundle:**
   ```bash
   npm run build
   ```

2. **Start production server:**
   ```bash
   npm start
   ```

3. **Or deploy to Vercel:**
   ```bash
   vercel --prod
   ```

---

## 📧 Support

For issues or questions:
1. Check the **Troubleshooting** section above
2. Review API documentation at http://localhost:8000/docs
3. Create an issue in the GitHub repository

---

**Happy Coding! 🎉**
