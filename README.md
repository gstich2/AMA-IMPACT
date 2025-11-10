# AMA-IMPACT
## Immigration Visa Management System

**Version 3.0** - Production-Ready Backend with Advanced Analytics

A comprehensive FastAPI application for tracking and managing foreign national employee visa and green card applications with enterprise-grade features including notifications, audit logging, and advanced reporting.

## ✨ What's New in v3.0

- 🔔 **Notifications System**: Automated visa expiration alerts and system notifications
- 📋 **Audit Logging**: Complete compliance trail for all system changes
- 📊 **Advanced Reports**: Executive dashboards, analytics, and compliance reporting
- 🔐 **Enhanced Security**: Comprehensive role-based access control and monitoring
- 🚀 **Production Ready**: 100+ API endpoints with full documentation# Immigration Visa Management System

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
├── backend/                     # FastAPI application (Production Ready)
│   ├── app/
│   │   ├── api/v1/             # API routes (14 modules, 100+ endpoints)
│   │   │   ├── auth.py         # Authentication & JWT management
│   │   │   ├── users.py        # User management with RBAC
│   │   │   ├── beneficiaries.py # Foreign nationals tracking
│   │   │   ├── visa_applications.py # Core visa case management
│   │   │   ├── todos.py        # Task tracking with metrics
│   │   │   ├── dashboard.py    # Analytics and summaries
│   │   │   ├── notifications.py # Alert and messaging system
│   │   │   ├── audit_logs.py   # Compliance and audit trails
│   │   │   ├── reports.py      # Advanced analytics and reporting
│   │   │   └── ...             # Additional modules
│   │   ├── core/               # Application foundation
│   │   │   ├── config.py       # Environment configuration
│   │   │   ├── database.py     # SQLAlchemy setup
│   │   │   └── security.py     # JWT and authentication
│   │   ├── models/             # SQLAlchemy database models
│   │   │   ├── user.py         # User accounts and roles
│   │   │   ├── beneficiary.py  # Foreign nationals
│   │   │   ├── visa.py         # Visa applications and types
│   │   │   ├── notification.py # Notifications and email logs
│   │   │   ├── audit.py        # Audit trail tracking
│   │   │   └── ...             # Additional models
│   │   ├── schemas/            # Pydantic validation schemas
│   │   ├── services/           # Business logic services
│   │   │   ├── rbac_service.py # Role-based access control
│   │   │   ├── notification_service.py # Alert management
│   │   │   ├── audit_service.py # Compliance tracking
│   │   │   └── reports_service.py # Analytics engine
│   │   └── main.py             # Application entry point
│   ├── scripts/                # Database utilities
│   │   ├── fixtures/           # Sample data generators
│   │   └── init_database.py    # Database setup
│   ├── alembic/                # Database migrations
│   ├── tests/                  # Backend tests
│   ├── requirements.txt        # Python dependencies
│   └── .env.example            # Environment variables template
├── frontend/                   # Next.js application (Planned)
├── docs/                       # Documentation
├── PRD.md                      # Product Requirements Document  
└── README.md                   # This file
```

## 🔑 Key Features

### Core Functionality
- **Role-Based Access Control**: 5 user roles (ADMIN, HR, PM, MANAGER, BENEFICIARY)
- **Hierarchical Visibility**: Users see data based on organizational structure  
- **Department Management**: Full CRUD for organizational units with tree hierarchy
- **Visa Tracking**: H-1B, L-1, O-1, TN, EB-1A/B, EB-2, PERM, OPT, EAD, Green Card
- **Case Groups**: Organize related visa applications (e.g., H1B → Green Card pathway)
  - PM approval workflow with status transitions (DRAFT → PENDING_PM_APPROVAL → APPROVED/REJECTED)
  - Timeline endpoint combines audit logs, milestones, and todos for complete case history
  - Automatic HR and law firm assignment on approval
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

### Notifications & Alerts
- **Automated Monitoring**: Visa expiration detection (30, 60, 90 days ahead)
- **System Notifications**: In-app alerts for status changes and deadlines
- **Bulk Messaging**: Role-based announcements and communications
- **Email Integration**: Configurable email alerts and notifications
- **Overdue Detection**: Automatic alerts for overdue tasks and expired visas

### Audit & Compliance
- **Complete Audit Trail**: Every system change tracked with user, timestamp, and details
- **Security Monitoring**: Failed login attempts and suspicious activity detection
- **Compliance Reports**: Automated generation of audit reports for regulations
- **Access Logging**: Track who accessed what data and when
- **Data Retention**: Configurable cleanup of old audit records

### Analytics & Reporting
- **Executive Dashboards**: Real-time KPIs and performance metrics
- **Visa Analytics**: Processing time analysis, expiration forecasting, status trends
- **User Activity Reports**: Engagement patterns and system usage analytics
- **Export Capabilities**: Multiple formats (JSON, CSV, Excel, PDF)
- **Custom Reports**: Flexible reporting with role-based data access

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework with automatic API documentation
- **SQLAlchemy** - Object-relational mapping with PostgreSQL/SQLite support
- **Alembic** - Database schema migrations and version control
- **Pydantic** - Data validation and serialization with type safety
- **JWT Authentication** - Secure token-based authentication with refresh tokens
- **bcrypt** - Password hashing with salt for security
- **Python 3.8+** - Modern Python features and type hints

### Database & Storage  
- **PostgreSQL** - Production database (recommended)
- **SQLite** - Development database (default)
- **Redis** - Session storage and caching (optional)
- **File Storage** - Local filesystem for document uploads

### Authentication & Security
- **JWT (JSON Web Tokens)** - Stateless authentication
- **Role-Based Access Control** - Hierarchical permission system
- **Password Security** - bcrypt hashing with configurable rounds
- **CORS** - Cross-origin resource sharing configuration
- **Rate Limiting** - Protection against brute force attacks

### Development & Deployment
- **Uvicorn** - ASGI server for FastAPI
- **pytest** - Testing framework with fixtures
- **Black** - Code formatting
- **isort** - Import sorting
- **mypy** - Static type checking
- **Docker** - Containerization (optional)

### API Features
- **OpenAPI/Swagger** - Interactive API documentation
- **ReDoc** - Alternative API documentation
- **Automatic Validation** - Request/response validation via Pydantic
- **Error Handling** - Consistent error responses
- **Pagination** - Efficient large dataset handling
- **Advanced Filtering** - Multi-parameter search and sorting

### Frontend (Planned)
- **Next.js** - React framework with App Router
- **TypeScript** - Type-safe JavaScript development
- **Tailwind CSS** - Modern utility-first CSS framework
- **shadcn/ui** - Accessible component library
- **React Query** - Server state management and caching
- **Zustand** - Lightweight client state management
- **React Hook Form** - Efficient form validation and handling

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

### Backend Tests (Ready)
```bash
cd backend
pytest tests/                    # Run all backend tests
pytest tests/test_auth.py       # Test authentication
pytest tests/test_rbac.py       # Test role-based access control
pytest tests/test_notifications.py  # Test notification system
pytest tests/test_audit.py      # Test audit logging
```

### Frontend Tests (Planned)
```bash
cd frontend
npm test                        # Run Jest/React Testing Library tests
npm run test:e2e               # Run Playwright end-to-end tests
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
- ✅ Basic audit trail

### ✅ Phase 2: Core Features (Completed - v2.0)  
- ✅ Case Groups for immigration pathways
- ✅ Todo system with computed metrics
- ✅ Hierarchical task visibility
- ✅ Role-based user creation
- ✅ Enhanced filtering and search
- ✅ Dashboard with expiring visas

### ✅ Phase 3: Enterprise Features (Completed - v3.0)
- ✅ Complete notifications system with automated alerts
- ✅ Comprehensive audit logging and compliance reporting
- ✅ Advanced analytics and executive dashboards
- ✅ Role-based data scoping and security enhancements
- ✅ Production-ready API with 100+ endpoints

### 🚧 Phase 4: Frontend & Integration (In Progress)
- [ ] Frontend implementation (Next.js)
- [ ] Email delivery system integration
- [ ] Mobile-responsive design
- [ ] Real-time notifications
- [ ] Advanced user settings management

### 📋 Phase 5: Future Enhancements
- [ ] Multi-contract user assignment
- [ ] Microsoft SSO integration  
- [ ] Document upload and management
- [ ] Workflow approvals and routing
- [ ] Mobile app (React Native)
- [ ] USCIS case status API integration
- [ ] Advanced analytics with ML predictions

## 📖 API Documentation

### Interactive API Documentation
- **Swagger UI**: `http://localhost:8000/docs` - Interactive API testing and documentation
- **ReDoc**: `http://localhost:8000/redoc` - Clean, detailed API reference
- **Health Check**: `http://localhost:8000/health` - System status endpoint

### Complete API Reference
- **[API_REFERENCE.md](API_REFERENCE.md)** - Complete endpoint documentation with examples
- **100+ Endpoints** across 14 API modules
- **Role-based filtering** - Automatic data scoping based on user permissions  
- **Advanced search** - Multi-parameter filtering and pagination
- **Consistent responses** - Standardized JSON format with error handling

### Key API Features
- **Authentication**: JWT tokens with refresh capability
- **RBAC Integration**: Endpoints automatically filter data based on user role
- **Audit Logging**: All actions tracked with comprehensive audit trail
- **Notifications**: Automated alerts and manual messaging system
- **Reports**: Dynamic report generation with multiple export formats
- **Data Validation**: Pydantic schemas ensure data integrity

### Documentation Files
- **[PRD.md](PRD.md)** - Product requirements and specifications
- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Setup and installation guide
- **[DATA_MODEL.md](DATA_MODEL.md)** - Database schema and relationships
- **[CREDENTIALS.md](CREDENTIALS.md)** - Default users and authentication guide

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
