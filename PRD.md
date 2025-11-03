# Product Requirements Document (PRD)
## Immigration Visa Management System

**Version:** 1.0  
**Date:** November 3, 2025  
**Status:** Draft  
**Owner:** Engineering Team

---

## 1. Executive Summary

### 1.1 Purpose
Build an internal web application to track and manage foreign national employee visa and green card applications across multiple company contracts. The system will provide hierarchical access control, automated expiration alerts, and reporting capabilities for HR and management.

### 1.2 Problem Statement
Currently, visa tracking is managed through spreadsheets, leading to:
- Missed renewal deadlines
- Lack of visibility for managers on team member visa status
- Manual effort to generate compliance reports
- No automated alerting system
- Inconsistent data across contracts

### 1.3 Solution Overview
A FastAPI backend + Next.js frontend application with:
- Role-based access control (RBAC) with hierarchical visibility
- Automated email notifications for expiration dates
- Contract-based organizational structure
- Comprehensive visa lifecycle tracking
- Analytics and reporting dashboard

### 1.4 Success Metrics
- **Zero missed renewals** within 30-day warning window
- **< 5 minutes** to generate contract-wide visa report
- **100% user adoption** across all contracts within 3 months
- **< 2 seconds** average API response time
- **Weekly active usage** by 80%+ of managers

---

## 2. User Personas & Roles

### 2.1 Staff (Employee)
**Primary Goal:** View personal visa status and upcoming deadlines  
**Access Level:** Own records only (read-only)  
**Key Actions:**
- View own visa applications and status
- See upcoming expiration dates
- Receive email alerts for renewals
- Update limited fields (e.g., current address, emergency contact)

### 2.2 Technical Lead (Tech Lead)
**Primary Goal:** Monitor team visa compliance and prevent lapses  
**Access Level:** Direct and indirect reports within contract  
**Key Actions:**
- View team member visa status
- Identify upcoming expirations
- Add/edit visa records for reports
- Receive escalation alerts for overdue renewals
- Export team reports

### 2.3 Program Manager (PM) / Deputy PM
**Primary Goal:** Ensure contract-wide visa compliance  
**Access Level:** All employees within assigned contract  
**Key Actions:**
- View entire contract roster
- Generate compliance reports
- Receive critical escalation alerts
- Approve visa-related actions (optional workflow)
- Track visa costs and timelines (future)

### 2.4 HR Representative
**Primary Goal:** Manage visa data and generate cross-contract reports  
**Access Level:** Assigned contracts (one or more)  
**Key Actions:**
- Create/edit/archive employee visa records
- Manage visa types and statuses
- Generate analytics and reports
- Configure notification schedules
- Export data for audits (CSV)

### 2.5 System Administrator
**Primary Goal:** System configuration and user management  
**Access Level:** All contracts and system settings  
**Key Actions:**
- Manage user accounts and roles
- Assign users to contracts
- Configure system-wide settings
- View audit logs
- Manage organizational hierarchy

---

## 3. Features & User Stories

### 3.1 Authentication & Authorization

**F-001: User Authentication**
- **As a** user, **I want to** log in with email/password, **so that** I can securely access the system
- **Acceptance Criteria:**
  - Login form with email + password
  - JWT access token (15 min expiry) + refresh token (7 days)
  - Rate limiting: 5 failed attempts = 15-min lockout
  - Password requirements: min 8 chars, 1 uppercase, 1 number, 1 special char

**F-002: Role-Based Access Control**
- **As a** system admin, **I want to** assign roles to users, **so that** they see only appropriate data
- **Acceptance Criteria:**
  - Five roles: Admin, HR, Program Manager, Tech Lead, Staff
  - Hierarchical visibility enforced at API level
  - Users cannot access other contracts' data
  - Middleware validates permissions on every request

**F-003: Password Reset**
- **As a** user, **I want to** reset my forgotten password, **so that** I can regain access
- **Acceptance Criteria:**
  - "Forgot Password" link sends secure email token (1-hour expiry)
  - User sets new password via token link
  - Old tokens invalidated after use

---

### 3.2 Organizational Structure

**F-004: Contract Management**
- **As an** admin, **I want to** create and manage contracts, **so that** users can be organized by project
- **Acceptance Criteria:**
  - CRUD operations for contracts (e.g., ASSESS, RESESS)
  - Each contract has: name, code, start date, end date, status (active/archived)
  - Archived contracts are read-only

**F-005: User-Contract Assignment**
- **As an** admin, **I want to** assign users to contracts, **so that** access is properly scoped
- **Acceptance Criteria:**
  - Users assigned to exactly one contract (v1 limitation)
  - Future-proof: database schema supports many-to-many (user_contracts table)
  - Contract assignment required before user can access system

**F-006: Reporting Hierarchy**
- **As an** admin, **I want to** define who reports to whom, **so that** managers see their team's data
- **Acceptance Criteria:**
  - Each user has optional `reports_to` field (user_id)
  - Tech Leads see direct + indirect reports (recursive query)
  - PMs see all contract users regardless of hierarchy
  - Circular reporting relationships prevented (validation)

---

### 3.3 Visa Application Tracking

**F-007: Visa Application CRUD**
- **As an** HR rep, **I want to** create visa applications for employees, **so that** status can be tracked
- **Acceptance Criteria:**
  - Fields: employee (FK), visa type, status, priority, filing date, approval date, expiration date, I-94 expiration, notes
  - Visa types: H-1B, L-1, O-1, TN, EB-1A, EB-1B, EB-2, EB-2 NIW, PERM, OPT, EAD, Green Card
  - Statuses: Draft, Submitted, In Progress, Approved, Denied, Expired, Renewed
  - Priority: Low, Medium, High, Critical
  - Audit log captures all changes (who, what, when)

**F-008: Visa Type Definitions**
- **As an** admin, **I want to** manage visa type metadata, **so that** dropdown options are standardized
- **Acceptance Criteria:**
  - Pre-populated visa types with descriptions
  - Admin can add custom types (e.g., "J-1 Waiver")
  - Each type has default renewal lead time (e.g., H-1B = 180 days)

**F-009: Status Workflow**
- **As a** manager, **I want to** update visa application status, **so that** progress is visible
- **Acceptance Criteria:**
  - Status transitions logged with timestamp + user
  - Optional: workflow rules (e.g., Draft → Submitted requires approval)
  - Comments field for status change notes

**F-010: Multiple Visa Applications per User**
- **As an** HR rep, **I want to** track multiple visa applications for one employee, **so that** history is preserved
- **Acceptance Criteria:**
  - One-to-many relationship: user → visa applications
  - Mark applications as "active" or "historical"
  - Timeline view shows all applications chronologically

---

### 3.4 Notifications & Alerts

**F-011: Email Notifications**
- **As an** employee, **I want to** receive email alerts before my visa expires, **so that** I don't miss deadlines
- **Acceptance Criteria:**
  - Automated daily job checks expiration dates
  - Default thresholds: 90, 60, 30, 14, 7 days before expiration
  - Email template includes: employee name, visa type, expiration date, action needed
  - Escalation rules:
    - 90/60/30 days: Employee only
    - 14/7 days: Employee + Tech Lead + HR
    - Overdue: All + PM

**F-012: Configurable Alert Preferences**
- **As a** user, **I want to** customize my alert settings, **so that** I receive relevant notifications
- **Acceptance Criteria:**
  - User settings: enable/disable email alerts, custom thresholds (e.g., 45 days)
  - HR can override user preferences for critical alerts
  - Global settings for system-wide defaults

**F-013: In-App Notifications**
- **As a** user, **I want to** see alerts when I log in, **so that** I'm aware of urgent items
- **Acceptance Criteria:**
  - Bell icon shows unread notification count
  - Notification center lists recent alerts (last 30 days)
  - Mark as read/dismiss functionality

---

### 3.5 Reporting & Analytics

**F-014: Dashboard Overview**
- **As a** manager, **I want to** see a dashboard of team visa status, **so that** I can quickly assess risks
- **Acceptance Criteria:**
  - Summary cards: Total employees, Active visas, Expiring <30 days, Expired
  - Visual timeline: Gantt chart or calendar view of expirations
  - Filter by: visa type, status, employee, date range
  - Role-specific data (staff see own, leads see team, PM sees contract)

**F-015: Expiration Report**
- **As an** HR rep, **I want to** generate a report of upcoming expirations, **so that** I can plan renewals
- **Acceptance Criteria:**
  - Filters: contract, date range (e.g., next 90 days), visa type, status
  - Table view: Employee, Visa Type, Expiration Date, Days Remaining, Manager, Status
  - Export to CSV
  - Save report templates for recurring use

**F-016: Audit Log**
- **As an** admin, **I want to** view all data changes, **so that** I can ensure compliance
- **Acceptance Criteria:**
  - Log table: timestamp, user, action (create/update/delete), resource (visa application), old value, new value
  - Searchable and filterable (by user, date, resource)
  - Export to CSV for audits

**F-017: Analytics Dashboard**
- **As a** PM, **I want to** see visa statistics for my contract, **so that** I can report to leadership
- **Acceptance Criteria:**
  - Charts: Visa types distribution (pie chart), Status breakdown (bar chart), Expiration timeline (line chart)
  - Metrics: Avg processing time, Renewal success rate, Overdue count
  - Comparison across contracts (admin/HR only)

---

### 3.6 User Management

**F-018: User Profile**
- **As a** user, **I want to** update my profile information, **so that** contact details are current
- **Acceptance Criteria:**
  - Editable fields: Name, Email (requires verification), Phone, Emergency Contact
  - Non-editable by user: Role, Contract, Reports To
  - Profile photo upload (optional, future)

**F-019: Admin User Management**
- **As an** admin, **I want to** manage all user accounts, **so that** access is controlled
- **Acceptance Criteria:**
  - CRUD operations for users
  - Assign role, contract, reporting manager
  - Deactivate (soft delete) users who leave company
  - Reactivate deactivated users
  - Bulk import via CSV (future)

---

## 4. Data Model

### 4.1 Core Entities

#### **User**
```python
id: UUID (PK)
email: String (unique, indexed)
hashed_password: String
full_name: String
phone: String (optional)
role: Enum (admin, hr, program_manager, tech_lead, staff)
contract_id: UUID (FK → Contract)
reports_to_id: UUID (FK → User, nullable)
is_active: Boolean (default True)
last_login: DateTime (nullable)
created_at: DateTime
updated_at: DateTime
```

#### **Contract**
```python
id: UUID (PK)
name: String (e.g., "ASSESS")
code: String (unique, e.g., "ASSESS-2024")
start_date: Date
end_date: Date (nullable)
status: Enum (active, archived)
created_at: DateTime
updated_at: DateTime
```

#### **VisaApplication**
```python
id: UUID (PK)
user_id: UUID (FK → User)
visa_type: Enum (H1B, L1, O1, TN, EB1A, EB1B, EB2, EB2NIW, PERM, OPT, EAD, GreenCard)
status: Enum (draft, submitted, in_progress, approved, denied, expired, renewed)
priority: Enum (low, medium, high, critical)
filing_date: Date (nullable)
approval_date: Date (nullable)
expiration_date: Date (nullable)
i94_expiration_date: Date (nullable)
is_active: Boolean (default True)  # Only one active visa per type per user
notes: Text (nullable)
created_by: UUID (FK → User)
created_at: DateTime
updated_at: DateTime
```

#### **VisaType**
```python
id: UUID (PK)
code: String (unique, e.g., "H1B")
name: String (e.g., "H-1B Specialty Occupation")
description: Text
default_renewal_lead_days: Integer (e.g., 180)
is_active: Boolean (default True)
created_at: DateTime
```

#### **AuditLog**
```python
id: UUID (PK)
user_id: UUID (FK → User)
action: Enum (create, update, delete, login, logout)
resource_type: String (e.g., "VisaApplication")
resource_id: UUID
old_value: JSON (nullable)
new_value: JSON (nullable)
ip_address: String
created_at: DateTime
```

#### **Notification**
```python
id: UUID (PK)
user_id: UUID (FK → User)
type: Enum (visa_expiring, status_changed, overdue, system)
title: String
message: Text
link: String (nullable, e.g., "/visa/123")
is_read: Boolean (default False)
created_at: DateTime
```

#### **EmailLog**
```python
id: UUID (PK)
recipient_email: String
subject: String
body: Text
status: Enum (queued, sent, failed)
error_message: Text (nullable)
visa_application_id: UUID (FK → VisaApplication, nullable)
sent_at: DateTime (nullable)
created_at: DateTime
```

#### **UserSettings**
```python
id: UUID (PK)
user_id: UUID (FK → User, unique)
email_notifications_enabled: Boolean (default True)
alert_thresholds: JSON (e.g., {"visa_expiry": [90, 60, 30, 14, 7]})
timezone: String (default "UTC")
created_at: DateTime
updated_at: DateTime
```

### 4.2 Relationships
- **User → Contract**: Many-to-One (one user belongs to one contract in v1)
- **User → User**: Self-referencing (reports_to hierarchy)
- **User → VisaApplication**: One-to-Many (one user has multiple visa applications)
- **User → AuditLog**: One-to-Many
- **User → Notification**: One-to-Many
- **Contract → User**: One-to-Many
- **VisaApplication → VisaType**: Many-to-One
- **VisaApplication → EmailLog**: One-to-Many

### 4.3 Indexes
- `User.email` (unique)
- `User.contract_id` (for filtering by contract)
- `VisaApplication.user_id` (for user lookups)
- `VisaApplication.expiration_date` (for notification queries)
- `VisaApplication.status` (for dashboard filtering)
- `AuditLog.user_id, AuditLog.created_at` (for audit queries)
- `Notification.user_id, Notification.is_read` (for unread count)

---

## 5. API Design (High-Level)

### 5.1 Authentication Endpoints
```
POST   /api/v1/auth/register           # Admin-only: Create user
POST   /api/v1/auth/login              # Email/password → JWT tokens
POST   /api/v1/auth/refresh            # Refresh access token
POST   /api/v1/auth/logout             # Invalidate refresh token
POST   /api/v1/auth/forgot-password    # Send reset email
POST   /api/v1/auth/reset-password     # Reset with token
```

### 5.2 User Management
```
GET    /api/v1/users                   # List users (filtered by role/contract)
GET    /api/v1/users/{id}              # Get user details
POST   /api/v1/users                   # Create user (admin/HR)
PATCH  /api/v1/users/{id}              # Update user
DELETE /api/v1/users/{id}              # Deactivate user (soft delete)
GET    /api/v1/users/me                # Current user profile
PATCH  /api/v1/users/me                # Update own profile
GET    /api/v1/users/{id}/reports      # Get direct reports
```

### 5.3 Contract Management
```
GET    /api/v1/contracts               # List contracts
GET    /api/v1/contracts/{id}          # Get contract details
POST   /api/v1/contracts               # Create contract (admin)
PATCH  /api/v1/contracts/{id}          # Update contract
DELETE /api/v1/contracts/{id}          # Archive contract
GET    /api/v1/contracts/{id}/users    # List users in contract
```

### 5.4 Visa Applications
```
GET    /api/v1/visa-applications                      # List (filtered by permissions)
GET    /api/v1/visa-applications/{id}                 # Get details
POST   /api/v1/visa-applications                      # Create
PATCH  /api/v1/visa-applications/{id}                 # Update
DELETE /api/v1/visa-applications/{id}                 # Delete (admin only)
GET    /api/v1/visa-applications/{id}/history         # Audit trail
POST   /api/v1/visa-applications/{id}/status          # Update status
GET    /api/v1/visa-applications/expiring             # List expiring soon
GET    /api/v1/users/{user_id}/visa-applications      # User's visa history
```

### 5.5 Visa Types
```
GET    /api/v1/visa-types              # List visa types
GET    /api/v1/visa-types/{id}         # Get details
POST   /api/v1/visa-types              # Create (admin)
PATCH  /api/v1/visa-types/{id}         # Update
DELETE /api/v1/visa-types/{id}         # Deactivate
```

### 5.6 Notifications
```
GET    /api/v1/notifications           # Current user's notifications
PATCH  /api/v1/notifications/{id}/read # Mark as read
DELETE /api/v1/notifications/{id}      # Dismiss
GET    /api/v1/notifications/unread-count  # Badge count
```

### 5.7 Reports & Analytics
```
GET    /api/v1/reports/dashboard       # Dashboard stats (role-filtered)
GET    /api/v1/reports/expiring        # Expiration report (CSV export)
GET    /api/v1/reports/analytics       # Charts data
GET    /api/v1/reports/audit-log       # Audit log export (admin)
```

### 5.8 Settings
```
GET    /api/v1/settings                # Current user settings
PATCH  /api/v1/settings                # Update preferences
```

### 5.9 Response Formats

**Success (200/201):**
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful"
}
```

**Error (4xx/5xx):**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Email already exists",
    "details": { "field": "email" }
  }
}
```

**List with Pagination:**
```json
{
  "success": true,
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 156,
    "pages": 8
  }
}
```

---

## 6. Security Requirements

### 6.1 Authentication
- ✅ Passwords hashed with bcrypt (cost factor 12)
- ✅ JWT tokens with short expiry (15 min access, 7 day refresh)
- ✅ Refresh token rotation on use
- ✅ Rate limiting: 5 login attempts per 15 min per IP
- ✅ HTTPS only in production (HTTP → HTTPS redirect)

### 6.2 Authorization
- ✅ Every API endpoint validates user role + contract access
- ✅ Row-level security: users cannot access other contracts' data
- ✅ Hierarchical checks: Tech Leads query `reports_to` chain
- ✅ Admin actions logged to audit trail

### 6.3 Data Protection
- ✅ No SSN, passport numbers, or PII stored (v1 scope)
- ✅ SQLite in WAL mode with proper file permissions (600)
- ✅ Environment variables for secrets (.env file, gitignored)
- ✅ SQL injection prevention (SQLAlchemy ORM + parameterized queries)

### 6.4 Audit & Compliance
- ✅ All data modifications logged (who, what, when)
- ✅ Login/logout events tracked
- ✅ Soft deletes (preserve data for compliance)
- ✅ Audit log immutable (append-only, no updates/deletes)

### 6.5 Frontend Security
- ✅ CSRF protection (SameSite cookies)
- ✅ XSS prevention (React auto-escaping, CSP headers)
- ✅ Secure cookie flags (HttpOnly, Secure)
- ✅ Input validation on client + server

---

## 7. Non-Functional Requirements

### 7.1 Performance
- API response time < 2 seconds (95th percentile)
- Dashboard loads in < 3 seconds
- Notification job runs daily at 8 AM (configurable)
- Support 100 concurrent users (sufficient for single-server)

### 7.2 Scalability
- SQLite sufficient for < 10,000 records
- Database schema supports future PostgreSQL migration
- Stateless API design (horizontal scaling possible)

### 7.3 Reliability
- 99% uptime during business hours (9 AM - 6 PM EST)
- Daily automated database backups (cron job)
- Email retry logic (3 attempts with exponential backoff)

### 7.4 Usability
- Mobile-responsive design (Tailwind breakpoints)
- Accessible (WCAG 2.1 AA compliance)
- Intuitive navigation (max 3 clicks to any feature)
- Inline help tooltips for complex fields

### 7.5 Maintainability
- Code coverage > 70% (unit + integration tests)
- API documentation (auto-generated from FastAPI)
- Deployment guide for new environments
- Database migrations via Alembic

---

## 8. Technical Stack

### 8.1 Backend
- **Framework:** FastAPI 0.104+
- **ORM:** SQLAlchemy 2.0+
- **Database:** SQLite (WAL mode)
- **Migrations:** Alembic
- **Auth:** python-jose (JWT), passlib (bcrypt)
- **Validation:** Pydantic v2
- **Scheduler:** APScheduler
- **Email:** smtplib + Jinja2 templates (Gmail SMTP or Brevo)
- **Rate Limiting:** slowapi
- **Server:** Uvicorn + Gunicorn (production)

### 8.2 Frontend
- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS + shadcn/ui
- **State Management:** Zustand (local), React Query (server state)
- **Forms:** React Hook Form + Zod validation
- **Charts:** Recharts or Chart.js
- **Icons:** Lucide React
- **Date Handling:** date-fns

### 8.3 DevOps
- **Environment:** Python venv (no Docker)
- **Process Manager:** Systemd service
- **Reverse Proxy:** Nginx (optional)
- **Backups:** Cron job → rsync to network drive
- **Logs:** Python logging + file rotation

---

## 9. Implementation Phases

### Phase 1: MVP (Weeks 1-3)
- ✅ Authentication (login, JWT, password reset)
- ✅ User + Contract + Visa Application models
- ✅ Basic CRUD for visa applications
- ✅ Role-based access control (5 roles)
- ✅ Simple dashboard (list view)
- ✅ Email notifications (hardcoded thresholds)

### Phase 2: Core Features (Weeks 4-6)
- ✅ Hierarchical reporting (Tech Lead sees reports)
- ✅ Expiration report + CSV export
- ✅ In-app notifications
- ✅ Audit log
- ✅ User settings (alert preferences)
- ✅ Analytics dashboard (charts)

### Phase 3: Polish (Weeks 7-8)
- ✅ Mobile responsiveness
- ✅ Advanced filtering/sorting
- ✅ Bulk operations (future)
- ✅ User onboarding flow
- ✅ Comprehensive testing
- ✅ Deployment guide + README

### Phase 4: Future Enhancements (Post-Launch)
- Multi-contract assignment for users
- Microsoft SSO integration
- Document upload + storage
- Workflow approvals (PM approval for visa requests)
- Cost tracking per application
- Immigration attorney collaboration module
- SMS notifications (Twilio)
- Mobile app (React Native)

---

## 10. Success Metrics (90 Days Post-Launch)

### 10.1 Adoption Metrics
- ✅ 100% of active employees have accounts
- ✅ 80% weekly active users (managers + HR)
- ✅ 50% of staff log in monthly

### 10.2 Operational Metrics
- ✅ Zero visa lapses due to missed deadlines
- ✅ 95% of expiration alerts delivered on time
- ✅ < 5 min to generate contract compliance report
- ✅ 90% of users rate UX as "Good" or "Excellent"

### 10.3 Technical Metrics
- ✅ < 2 sec API response time (p95)
- ✅ 99% uptime during business hours
- ✅ < 5 support tickets per week after onboarding

---

## 11. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Email service reliability (Gmail SMTP limits) | High | Use Brevo (300/day free), add retry logic, monitor send rates |
| SQLite concurrency issues (WAL mode limits) | Medium | Enable WAL mode, limit write concurrency, plan PostgreSQL migration path |
| Users forget to update visa info | High | Automated reminders, make status updates required quarterly |
| Complex reporting hierarchy edge cases | Medium | Validate no circular reports, add safeguards in recursive queries |
| Security breach (token theft) | High | Short token expiry, HTTPS only, monitor for anomalous access patterns |
| No IT department for Microsoft SSO | Low | Skip SSO in v1, document setup for future when IT available |

---

## 12. Open Questions

1. **Q:** Should we track visa application costs?  
   **A:** Not in v1. Add in Phase 4 if needed.

2. **Q:** How to handle employees who leave the company mid-visa-process?  
   **A:** Soft delete user (is_active=False), keep historical records for audit.

3. **Q:** Can PMs delegate tasks to others (e.g., "HR, please renew this")?  
   **A:** Not in v1. Consider workflow module in Phase 4.

4. **Q:** What timezone for notification scheduling?  
   **A:** Default to EST (company HQ), allow user override in settings (Phase 2).

5. **Q:** Should system track immigration attorney contact info?  
   **A:** Not in v1 (no attorney collaboration). Add in Phase 4 if needed.

---

## 13. Approval & Sign-Off

| Role | Name | Status | Date |
|------|------|--------|------|
| Product Owner | [User] | Pending | 2025-11-03 |
| Engineering Lead | GitHub Copilot | Pending | 2025-11-03 |
| HR Stakeholder | TBD | Pending | TBD |

---

**Next Steps:**
1. Review and approve this PRD
2. Set up development environment (backend + frontend scaffolding)
3. Begin Phase 1 implementation (MVP)
4. Schedule weekly demos for stakeholder feedback

---

**Document History:**
- **v1.0** (2025-11-03): Initial draft based on stakeholder requirements
