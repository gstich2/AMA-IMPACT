# AMA-IMPACT
## Immigration Visa Management System

**Version 2.0** - Complete case management with todo tracking and hierarchical organization

A comprehensive FastAPI + Next.js application for tracking and managing foreign national employee visa and green card applications across multiple company contracts.

## ✨ What's New in v2.0

- 🗂️ **Case Groups**: Organize related visa applications into immigration pathways
- ✅ **Todo System**: Task tracking with computed metrics (overdue status, completion time)
- � **Role-Based User Creation**: Enhanced security with permission controls
- 📚 **Complete Documentation**: MkDocs site with comprehensive guides
- 🔧 **Modular Fixtures**: Improved database seeding system

## �🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- Git

### Backend Setup (FastAPI)

```bash
# Clone repository
git clone https://github.com/gstich2/AMA-IMPACT.git
cd AMA-IMPACT

# Create virtual environment
python -m venv .venv

# Activate virtual environment (Linux/Mac)
source .venv/bin/activate
# On Windows: .venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Setup database with sample data
python scripts/setup_dev_environment.py

# Run development server
uvicorn app.main:app --reload --port 8000
```

Backend available at: `http://localhost:8000`  
API Documentation: `http://localhost:8000/docs`

### Frontend Setup (Next.js)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will be available at: `http://localhost:3000`

## 📁 Project Structure

```
AMA-IMPACT/
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Config, security, dependencies
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── crud/           # Database operations
│   │   ├── services/       # Business logic
│   │   └── main.py         # Application entry point
│   ├── alembic/            # Database migrations
│   ├── tests/              # Backend tests
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment variables template
├── frontend/               # Next.js application
│   ├── src/
│   │   ├── app/           # Next.js 14 App Router
│   │   ├── components/    # React components
│   │   ├── lib/           # Utilities and API client
│   │   ├── hooks/         # Custom React hooks
│   │   └── types/         # TypeScript types
│   ├── public/            # Static assets
│   └── package.json       # Node dependencies
├── docs/                  # Documentation
├── PRD.md                 # Product Requirements Document
└── README.md              # This file
```

## 🔑 Key Features

### Core Functionality
- **Role-Based Access Control**: 5 user roles (ADMIN, HR, PM, MANAGER, BENEFICIARY)
- **Hierarchical Visibility**: Users see data based on organizational structure
- **Visa Tracking**: H-1B, L-1, O-1, TN, EB-1A/B, EB-2, PERM, OPT, EAD, Green Card
- **Case Groups**: Organize related visa applications (e.g., H1B → Green Card pathway)
- **Beneficiary System**: Separation of users from foreign nationals

### Task Management
- **Todo System** with hierarchical linking to visa apps, case groups, beneficiaries
- **Computed Metrics**: 
  - `is_overdue` - Dynamic overdue calculation
  - `days_overdue` - Time past due date
  - `days_to_complete` - Completion duration
  - `completed_on_time` - On-time performance tracking
- **Dashboard Views**: Personal and team todos with filtering
- **Role-Based Visibility**: See tasks based on assignment and hierarchy

### Administration
- **User Creation Control**: Role-based permissions for creating users
- **Audit Trail**: Complete history of all data modifications
- **Automated Notifications**: Email alerts for visa expirations (planned)
- **Analytics Dashboard**: Expiration timelines, status breakdowns, reports
- **Export Reports**: CSV export for compliance and reporting

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy 2.0** - ORM for database operations
- **SQLite** (WAL mode) - Lightweight database
- **Alembic** - Database migrations
- **JWT** - Token-based authentication
- **APScheduler** - Background task scheduling
- **Pydantic v2** - Data validation

### Frontend
- **Next.js 14** - React framework (App Router)
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first styling
- **shadcn/ui** - Component library
- **React Query** - Server state management
- **Zustand** - Client state management
- **React Hook Form** - Form handling

## 📊 User Roles

| Role | Access Level | Permissions | User Creation Rights |
|------|-------------|-------------|---------------------|
| **ADMIN** | System-wide | Full access to all data and settings | Can create any role |
| **HR** | Multi-contract | Manage visa applications, view all beneficiaries | Can create BENEFICIARY users only |
| **PM** | Contract-wide | View all data + advanced metrics | Can create BENEFICIARY users only |
| **MANAGER** | Team-level | View/edit direct and indirect reports | Can create BENEFICIARY users only |
| **BENEFICIARY** | Self-only | View own visa cases and todos | Cannot create users |

## 🔐 Security Features

- Bcrypt password hashing
- JWT access tokens (15 min expiry) + refresh tokens (7 days)
- Rate limiting on authentication endpoints
- Row-level security (contract-based isolation)
- Comprehensive audit logging
- HTTPS enforcement in production

## 📧 Notification System

- **Daily background job** checks expiration dates
- **Escalation logic**:
  - 90/60/30 days: Employee only
  - 14/7 days: Employee + Manager + HR
  - Overdue: All + Program Manager
- **Configurable preferences** per user
- Email templates with Jinja2

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📦 Deployment

### Production Setup
1. Set environment variables (copy `.env.example` to `.env`)
2. Run database migrations: `alembic upgrade head`
3. Start backend with Gunicorn: `gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker`
4. Build frontend: `npm run build`
5. Start frontend: `npm start`

### Systemd Service (Optional)
See `docs/deployment.md` for systemd service configuration.

## 📝 Environment Variables

### Backend (.env)
```bash
# Database
DATABASE_URL=sqlite:///./ama_impact.db

# Security
SECRET_KEY=your-secret-key-here-generate-with-openssl
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@ama-impact.com

# CORS
FRONTEND_URL=http://localhost:3000
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🗺️ Roadmap

### ✅ Phase 1: MVP (Completed - v1.0)
- ✅ Authentication & authorization
- ✅ User & contract management
- ✅ Visa application CRUD
- ✅ Beneficiary system
- ✅ Audit trail

### ✅ Phase 2: Core Features (Completed - v2.0)
- ✅ Case Groups for immigration pathways
- ✅ Todo system with computed metrics
- ✅ Hierarchical task visibility
- ✅ Role-based user creation
- ✅ Modular fixture system
- ✅ Complete documentation (MkDocs)

### 🚧 Phase 3: Enhancements (In Progress)
- [ ] Frontend implementation (Next.js)
- [ ] Email notification system
- [ ] Advanced analytics dashboard
- [ ] In-app notifications
- [ ] User settings management

### 📋 Phase 4: Future
- [ ] Multi-contract user assignment
- [ ] Microsoft SSO integration
- [ ] Document upload and management
- [ ] Workflow approvals
- [ ] Mobile app (React Native)
- [ ] USCIS case status API integration

## 📖 Documentation

Complete documentation available in the `docs/` directory:

- **[Quick Start](docs/getting-started/quickstart.md)** - Get running in 10 minutes
- **[Data Models](docs/architecture/data-models.md)** - Complete database schema with CaseGroup and Todo
- **[API Reference](docs/api/overview.md)** - All endpoints with examples
- **[Development Guide](docs/development/setup.md)** - Setup, fixtures, testing, workflow
- **[Changelog](docs/changelog.md)** - Version history and migration guide
- **[PRD](PRD.md)** - Product requirements document
- **API Interactive Docs** - Available at `/docs` when backend is running

### Documentation Site

To view the full documentation site:

```bash
# Install MkDocs
pip install mkdocs-material mkdocs-awesome-pages-plugin

# Serve documentation
mkdocs serve

# View at http://localhost:8001
```

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and test thoroughly
3. Commit with clear messages: `git commit -m "Add feature X"`
4. Push and create a pull request

## 📄 License

Internal use only - Proprietary

## 🐛 Issues & Support

For bugs and feature requests, please create an issue in the GitHub repository.

---

**Built with ❤️ for AMA Immigration Compliance**
