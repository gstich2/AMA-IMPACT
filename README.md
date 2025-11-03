# AMA-IMPACT
## Immigration Visa Management System

A comprehensive FastAPI + Next.js application for tracking and managing foreign national employee visa and green card applications across multiple company contracts.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### Backend Setup (FastAPI)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
alembic upgrade head

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`
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

- **Role-Based Access Control**: 5 user roles (Admin, HR, Program Manager, Tech Lead, Staff)
- **Hierarchical Visibility**: Users see only their contract data and reports
- **Visa Tracking**: Support for H-1B, L-1, O-1, TN, EB-1A/B, EB-2, PERM, OPT, EAD, Green Card
- **Automated Notifications**: Email alerts for visa expirations (90/60/30/14/7 days)
- **Analytics Dashboard**: Expiration timelines, status breakdowns, contract reports
- **Audit Trail**: Complete history of all data modifications
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

| Role | Access Level | Permissions |
|------|-------------|-------------|
| **Admin** | System-wide | Full access to all contracts, users, and settings |
| **HR** | Multi-contract | View/edit assigned contracts, generate reports |
| **Program Manager** | Contract-wide | View/edit entire contract, receive critical alerts |
| **Tech Lead** | Team-level | View/edit direct and indirect reports |
| **Staff** | Self-only | View own visa status, receive personal alerts |

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

### Phase 1: MVP (Current)
- ✅ Authentication & authorization
- ✅ User & contract management
- ✅ Visa application CRUD
- ✅ Basic dashboard
- ✅ Email notifications

### Phase 2: Core Features
- [ ] Hierarchical reporting
- [ ] Advanced analytics
- [ ] In-app notifications
- [ ] Audit log viewer
- [ ] User settings

### Phase 3: Enhancements
- [ ] Multi-contract user assignment
- [ ] Microsoft SSO integration
- [ ] Document uploads
- [ ] Workflow approvals
- [ ] Mobile app

## 📖 Documentation

- **[PRD.md](PRD.md)** - Complete product requirements
- **API Docs** - Available at `/docs` when backend is running
- **User Guide** - See `docs/user-guide.md`
- **Deployment Guide** - See `docs/deployment.md`

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
