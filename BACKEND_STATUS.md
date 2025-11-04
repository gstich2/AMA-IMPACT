# Backend Status & Remaining Work

## ✅ Completed Backend Features

### Core Infrastructure
- [x] FastAPI application setup with Uvicorn
- [x] SQLAlchemy ORM with SQLite database
- [x] Alembic migrations (simplified for single-developer workflow)
- [x] JWT authentication with OAuth2 password flow
- [x] CORS middleware configuration
- [x] Rate limiting setup (slowapi)
- [x] API documentation (Swagger/ReDoc)
- [x] Database seed script with test users

### Database Models (8 models)
- [x] User - with roles, password management fields, invitation system
- [x] Contract - for organizing users by programs
- [x] VisaApplication - with case status tracking
- [x] VisaType - 12 pre-configured visa types
- [x] AuditLog - for tracking changes
- [x] Notification - for user alerts
- [x] EmailLog - for email tracking
- [x] UserSettings - for user preferences

### Authentication & User Management
- [x] User registration endpoint
- [x] Login with JWT tokens
- [x] Token refresh mechanism
- [x] Role-based access (5 roles: ADMIN, HR, PM, TECH_LEAD, STAFF)
- [x] User invitation system with secure tokens
- [x] Password reset flow with email tokens
- [x] Password change with rate limiting (2/24h)
- [x] Admin override for password limits
- [x] Forced password change on first login
- [x] Strong password validation

### Visa Management
- [x] Basic CRUD operations for visa applications
- [x] Case status tracking (UPCOMING, ACTIVE, FINALIZED)
- [x] Visa type management with 12 predefined types
- [x] Filtering by case status
- [x] Priority levels (LOW, MEDIUM, HIGH, URGENT)
- [x] Status tracking (DRAFT, SUBMITTED, IN_PROGRESS, APPROVED, DENIED, EXPIRED, RENEWED)

### Contract Management
- [x] Basic CRUD operations for contracts
- [x] Contract status tracking (ACTIVE, COMPLETED, CANCELLED)

---

## ⚠️ Backend Work Remaining

### 1. **Hierarchical Permission System** ⭐ HIGH PRIORITY
**Status**: Models support it, API enforcement needed

**What's Missing**:
- Permission middleware/dependencies for each role
- Filtering logic for data access:
  - **Staff**: Only their own visa applications
  - **Tech Lead**: Their direct reports + self
  - **Program Manager**: Everyone in their contract
  - **HR**: All assigned contracts
  - **Admin**: Everything

**Implementation Needed**:
```python
# Example needed in visa_applications.py
def get_accessible_visa_applications(user: User, db: Session):
    if user.role == UserRole.ADMIN:
        return db.query(VisaApplication).all()
    elif user.role == UserRole.HR:
        # Get all contracts assigned to this HR
        return visa apps for those contracts
    elif user.role == UserRole.PROGRAM_MANAGER:
        # Get all users in same contract
        return visa apps for contract users
    # etc...
```

**Files to Update**:
- `backend/app/api/v1/visa_applications.py` - Add filtering
- `backend/app/api/v1/users.py` - Add filtering
- `backend/app/api/v1/contracts.py` - Add filtering
- Create `backend/app/core/permissions.py` - Helper functions

---

### 2. **Email Notification System** ⭐ HIGH PRIORITY
**Status**: Models exist (EmailLog, Notification), no implementation

#### 2a. Email Service Integration
**What's Missing**:
- SMTP configuration in `.env`
- Email sending utility functions
- Email templates (HTML/text)

**Configuration Needed** (`.env`):
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@ama-impact.com
SMTP_FROM_NAME=AMA IMPACT
```

**Files to Create**:
- `backend/app/core/email.py` - Email sending functions
- `backend/app/templates/email/invitation.html` - User invitation template
- `backend/app/templates/email/password_reset.html` - Password reset template
- `backend/app/templates/email/visa_expiration.html` - Visa expiring template
- `backend/app/templates/email/visa_reminder.html` - General reminder template

#### 2b. Visa Expiration Warnings ⭐ YOUR QUESTION
**What's Missing**:
- Background job scheduler (APScheduler already in requirements.txt)
- Daily cron job to check approaching expirations
- Configurable warning thresholds (30, 60, 90 days)
- Email notifications for:
  - **H-1B Cap Alert**: When approaching the 6-year H-1B limit
  - **Visa Expiration**: When visa is about to expire
  - **I-94 Expiration**: When I-94 is about to expire
  - **Priority Deadline**: For high-priority cases

**Implementation Plan**:
```python
# backend/app/core/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler

async def check_visa_expirations():
    """Run daily to check for approaching expirations"""
    # Check visas expiring in 30, 60, 90 days
    # Send email alerts to user + their manager + HR
    
async def check_h1b_cap_limit():
    """Check if H-1B holders approaching 6-year limit"""
    # Query all H-1B visas
    # Calculate time on H-1B status
    # Alert if > 5 years 9 months (give 3 months warning)
```

**Warning Thresholds Needed**:
- H-1B 6-year limit: Alert at 5 years 9 months
- Visa expiration: 30, 60, 90 days before
- I-94 expiration: 30, 60 days before
- OPT/EAD: 60, 90 days before (critical for students)

**Files to Create**:
- `backend/app/core/scheduler.py` - APScheduler setup
- `backend/app/core/visa_alerts.py` - Expiration checking logic
- `backend/app/models/alert_settings.py` - Configurable thresholds (optional)

---

### 3. **Audit Logging** ⭐ MEDIUM PRIORITY
**Status**: Model exists, not being used

**What's Missing**:
- Middleware to automatically log changes
- Log creation on sensitive operations:
  - User creation/deletion/role changes
  - Visa status changes
  - Contract assignments
  - Password resets

**Files to Update**:
- Create `backend/app/core/audit.py` - Audit logging utilities
- Update all API endpoints to call audit logging

---

### 4. **API Enhancements**

#### 4a. User Management APIs
**Missing Endpoints**:
- `PATCH /api/v1/users/{user_id}` - Update user details
- `DELETE /api/v1/users/{user_id}` - Deactivate user (soft delete)
- `GET /api/v1/users/me/team` - Get user's team members
- `GET /api/v1/users/search?q=name` - Search users

#### 4b. Visa Application APIs
**Missing Endpoints**:
- `GET /api/v1/visa-applications/expiring?days=90` - Get expiring visas
- `GET /api/v1/visa-applications/user/{user_id}` - User's visa history
- `GET /api/v1/visa-applications/statistics` - Dashboard stats
- `POST /api/v1/visa-applications/{id}/documents` - Upload documents
- `GET /api/v1/visa-applications/{id}/timeline` - Status change history

#### 4c. Contract APIs
**Enhancements Needed**:
- `GET /api/v1/contracts/{id}/users` - List contract users
- `GET /api/v1/contracts/{id}/statistics` - Contract statistics
- `POST /api/v1/contracts/{id}/assign-hr` - Assign HR to contract

#### 4d. Dashboard/Reports APIs
**Missing Endpoints**:
- `GET /api/v1/dashboard/statistics` - Overall stats
- `GET /api/v1/reports/visa-by-type` - Visa type distribution
- `GET /api/v1/reports/expiring-visas` - Expiration report
- `GET /api/v1/reports/contract-summary` - Contract summary

---

### 5. **Notification System** ⭐ MEDIUM PRIORITY
**Status**: Model exists, API needed

**What's Missing**:
- Create notification on important events
- Mark notifications as read
- Get unread count
- Real-time notifications (WebSocket optional)

**Files to Create**:
- `backend/app/api/v1/notifications.py` - Notification endpoints
- Update relevant endpoints to create notifications

**Endpoints Needed**:
- `GET /api/v1/notifications` - List user's notifications
- `GET /api/v1/notifications/unread-count` - Get unread count
- `PATCH /api/v1/notifications/{id}/read` - Mark as read
- `POST /api/v1/notifications/mark-all-read` - Mark all read

---

### 6. **Document Management** (Optional but Recommended)
**Status**: Not started

**What's Needed**:
- File upload for visa documents (passport, I-797, etc.)
- Storage strategy (local filesystem or S3)
- Document types and metadata
- Access control for documents

**Files to Create**:
- `backend/app/models/document.py` - Document model
- `backend/app/api/v1/documents.py` - Upload/download endpoints
- `backend/app/core/storage.py` - File storage utilities

---

### 7. **Data Validation & Business Logic**

#### Missing Validations:
- **Visa Application Logic**:
  - Prevent overlapping visa dates
  - Validate I-94 date <= visa expiration date
  - H-1B cap validation (6-year limit)
  - Ensure renewal dates make sense

- **User Management Logic**:
  - Prevent deleting users with active visas
  - Ensure reporting structure doesn't create cycles
  - Validate contract assignment based on role

**Files to Update**:
- `backend/app/schemas/visa.py` - Add custom validators
- `backend/app/api/v1/visa_applications.py` - Add business logic checks

---

### 8. **Testing** (Recommended)
**Status**: No tests yet

**What's Needed**:
- Unit tests for business logic
- Integration tests for API endpoints
- Test fixtures and factories

**Files to Create**:
- `backend/tests/test_auth.py`
- `backend/tests/test_password_management.py`
- `backend/tests/test_visa_applications.py`
- `backend/tests/test_permissions.py`

---

## 🎯 Recommended Priority Order

### Phase 1: Critical for Basic Usage (1-2 days)
1. **Hierarchical Permissions** - Without this, everyone sees everything
2. **Email Service Setup** - For invitations and password resets
3. **Basic Notification System** - In-app alerts

### Phase 2: Visa Management Enhancement (2-3 days)
4. **Visa Expiration Monitoring** - Background jobs + email alerts
5. **H-1B Cap Limit Warnings** - Special alert for 6-year limit
6. **Enhanced Visa APIs** - Expiring visas, statistics, history
7. **Audit Logging** - Track who changed what

### Phase 3: Nice-to-Have Features (1-2 days)
8. **Document Management** - File uploads
9. **Dashboard APIs** - Reports and statistics
10. **Advanced Search** - Filter and search capabilities

---

## 📧 Email System Details (Your Question)

### Current Status
- ❌ No email sending configured
- ❌ No SMTP setup
- ❌ No email templates
- ✅ EmailLog model exists (ready to track sent emails)
- ✅ Password reset tokens being generated (but only logged to console)

### What We Need for Email Warnings

#### 1. SMTP Configuration
Add to `.env`:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
SMTP_FROM_EMAIL=noreply@ama-impact.com
```

#### 2. Email Templates
Create HTML templates for:
- User invitation
- Password reset
- Visa expiring in 90 days
- Visa expiring in 60 days
- Visa expiring in 30 days
- H-1B approaching 6-year limit
- Visa application approved/denied
- I-94 expiring soon

#### 3. Background Scheduler
Set up APScheduler to run daily:
```python
scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('cron', hour=9)  # Run at 9 AM daily
async def daily_visa_check():
    # Check for visas expiring in 30, 60, 90 days
    # Send email alerts
    # Log to EmailLog table
```

#### 4. H-1B Cap Alert Logic
```python
def check_h1b_cap_approaching(user_visa_history):
    """
    H-1B has 6-year maximum (with extensions possible for some)
    Alert when user has been on H-1B for > 5.75 years
    """
    h1b_visas = get_user_h1b_history(user)
    total_h1b_time = calculate_total_h1b_days(h1b_visas)
    
    if total_h1b_time > (365 * 5.75):  # 5 years 9 months
        send_alert_email(
            to=user.email,
            cc=[hr_manager.email, program_manager.email],
            subject="ACTION REQUIRED: H-1B Cap Approaching",
            template="h1b_cap_warning"
        )
```

### Recommended Email Alerts

| Alert Type | Threshold | Recipients | Priority |
|------------|-----------|------------|----------|
| H-1B Cap Warning | 5y 9m on H-1B | User, Manager, HR | URGENT |
| Visa Expiring | 30/60/90 days | User, Manager | HIGH |
| I-94 Expiring | 30/60 days | User, Manager | HIGH |
| OPT/EAD Expiring | 60/90 days | User, Manager | URGENT |
| Visa Approved | Immediate | User | MEDIUM |
| Password Reset | Immediate | User | LOW |
| New User Invitation | Immediate | User | LOW |

---

## 🚀 To Get Started on Email System

1. **Install email library** (already in requirements):
   ```bash
   pip install aiosmtplib  # for async email sending
   ```

2. **Create email utility**:
   ```bash
   touch backend/app/core/email.py
   ```

3. **Set up scheduler**:
   ```bash
   touch backend/app/core/scheduler.py
   touch backend/app/core/visa_alerts.py
   ```

4. **Create email templates folder**:
   ```bash
   mkdir -p backend/app/templates/email
   ```

5. **Add to app startup** in `main.py`:
   ```python
   from app.core.scheduler import start_scheduler
   
   @app.on_event("startup")
   async def startup_event():
       start_scheduler()
   ```

---

## Summary

**Backend is ~65% complete** for a production-ready application.

**Must-Have Before Frontend**:
1. ✅ Password management (DONE)
2. ✅ Visa case status (DONE)
3. ❌ Hierarchical permissions (CRITICAL)
4. ❌ Email service (CRITICAL for password resets)

**Can Add Later**:
- Visa expiration monitoring (but important!)
- Document management
- Advanced reporting
- Testing suite

The most important next steps are **permissions** and **email setup**. Without permissions, the app isn't secure. Without email, password resets don't work properly.
