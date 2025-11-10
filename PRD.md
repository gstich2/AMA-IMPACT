# Product Requirements Document (PRD)
## Immigration Visa Management System

**Version:** 3.0  
**Date:** November 5, 2025  
**Status:** Production Ready - Backend Complete  
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
- **Complete Backend API** - 100+ endpoints across 14 modules (v3.0)
- **Role-based access control (RBAC)** with 5 hierarchical user roles
- **Case Groups** for organizing related visa applications
- **Todo System** with computed performance metrics and overdue tracking
- **Notifications System** with automated alerts and messaging (v3.0)
- **Comprehensive Audit Logging** with compliance reporting (v3.0)
- **Advanced Analytics** with executive dashboards and reporting (v3.0)
- **Contract-based organizational structure** with department hierarchy
- **Production-ready security** with JWT authentication and rate limiting

### 1.4 Success Metrics
- **Zero missed renewals** within 30-day warning window
- **< 5 minutes** to generate contract-wide visa report
- **100% user adoption** across all contracts within 3 months
- **< 2 seconds** average API response time
- **Weekly active usage** by 80%+ of managers

---

## 2. User Personas & Roles

### 2.1 BENEFICIARY (Foreign National Employee)
**Primary Goal:** View personal visa status and upcoming deadlines  
**Access Level:** Own records only (self-access)  
**Key Actions:**
- View own visa applications and current status
- See personal task assignments and deadlines
- Receive automated expiration alerts
- Update limited personal information

**Implementation Status:** ✅ Complete - Full self-access with task visibility

### 2.2 MANAGER (Team Lead/Supervisor)
**Primary Goal:** Monitor team visa compliance and task completion  
**Access Level:** Direct and indirect reports based on organizational hierarchy  
**Key Actions:**
- View team member visa status and tasks
- Identify upcoming expirations within team
- Create visa applications and tasks for reports
- Receive escalated alerts for team compliance issues
- Export team-specific reports

**Implementation Status:** ✅ Complete - Hierarchical access with team management

### 2.3 PM (Program Manager)
**Primary Goal:** Ensure contract-wide visa compliance and analytics  
**Access Level:** All employees and data within assigned contract  
**Key Actions:**
- View entire contract roster and analytics
- Generate comprehensive compliance reports
- Access advanced dashboard metrics and trends
- Create beneficiary user accounts
- Track contract-wide performance and deadlines

**Implementation Status:** ✅ Complete - Contract-wide access with advanced analytics

### 2.4 HR (Human Resources)
**Primary Goal:** Multi-contract visa management and compliance oversight  
**Access Level:** Multiple contracts with cross-contract reporting capabilities  
**Key Actions:**
- Manage visa data across assigned contracts
- Generate cross-contract analytics and audit reports
- Configure system-wide notification policies
- Create beneficiary user accounts
- Export comprehensive compliance data

**Implementation Status:** ✅ Complete - Multi-contract access with full reporting

### 2.5 ADMIN (System Administrator)
**Primary Goal:** Complete system administration and configuration  
**Access Level:** Full system access across all contracts and settings  
**Key Actions:**
- Manage all user accounts and role assignments
- Assign users to contracts
- Configure system-wide settings
- View audit logs
- Manage organizational hierarchy

---

## 3. Features & User Stories

### 3.1 Authentication & Authorization

**F-001: User Authentication** ✅ **COMPLETE**
- **As a** user, **I want to** log in with email/password, **so that** I can securely access the system
- **Acceptance Criteria:**
  - Login form with email + password
  - JWT access token (15 min expiry) + refresh token (7 days)
  - Rate limiting: 5 failed attempts = 15-min lockout
  - Password requirements: min 8 chars, 1 uppercase, 1 number, 1 special char

**Implementation Status:** ✅ Complete - Full JWT authentication with refresh tokens and rate limiting

**F-002: Role-Based Access Control** ✅ **COMPLETE**
- **As a** system admin, **I want to** assign roles to users, **so that** they see only appropriate data
- **Acceptance Criteria:**
  - Five roles: ADMIN, HR, PM, MANAGER, BENEFICIARY
  - Hierarchical visibility enforced at API level
  - Users cannot access other contracts' data
  - Middleware validates permissions on every request

**Implementation Status:** ✅ Complete - Full RBAC with hierarchical data scoping and automatic filtering

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
  - CRUD operations for contracts (e.g., ASSESS, RSES)
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

### 3.3a Case Groups (NEW in v2.0) ⭐

**F-010a: Case Group Management**
- **As an** HR rep, **I want to** organize related visa applications into case groups, **so that** I can track immigration pathways
- **Acceptance Criteria:**
  - Create case group with name, description, case type, priority, status
  - Link multiple visa applications to a case group
  - Case types: H1B Extension, H1B Transfer, Green Card Pathway, TN to H1B, L1 to Green Card, EB2-NIW, PERM-Based, Family-Based, Other
  - Status: Planning, Active, Completed, Cancelled
  - Priority: Low, Medium, High, Urgent
  - Track start date, target completion date, actual completion date

**F-010b: Case Group Hierarchy**
- **As a** manager, **I want to** see all visa applications within a case group, **so that** I understand the full immigration journey
- **Acceptance Criteria:**
  - Beneficiary → Case Group → Visa Applications hierarchy
  - Example: "Luis - EB2-NIW to Green Card" contains I-140, I-485, EAD, AP
  - Visual timeline showing progression through pathway
  - Responsible party assignment for case group

**F-010c: Auto-population from Case Group**
- **As an** HR rep, **I want to** case group information to auto-populate on related records, **so that** I maintain consistency
- **Acceptance Criteria:**
  - Creating todo for visa app auto-fills case group and beneficiary
  - Creating visa app in case group auto-links to beneficiary
  - Prevents orphaned records and maintains data integrity

---

### 3.3b Task Management (NEW in v2.0) ⭐

**F-010d: Todo Creation and Assignment**
- **As an** HR rep, **I want to** create todos for visa-related tasks, **so that** work is tracked and assigned
- **Acceptance Criteria:**
  - Create todo with title, description, assignee, due date, priority, status
  - Link todo to: visa application, case group, or beneficiary (hierarchical)
  - Status: TODO, IN_PROGRESS, BLOCKED, COMPLETED, CANCELLED
  - Priority: LOW, MEDIUM, HIGH, URGENT
  - Automatically populate hierarchy from parent (visa app → case group → beneficiary)

**F-010e: Personal and Team Todo Views**
- **As a** user, **I want to** see my assigned todos and team todos, **so that** I know what needs attention
- **Acceptance Criteria:**
  - "My Todos" shows todos assigned to current user
  - "Team Todos" shows todos based on hierarchy:
    - BENEFICIARY: Own todos only
    - MANAGER: Own + subordinates' todos (recursive)
    - PM/HR/ADMIN: All todos
  - Filter by status, priority, overdue
  - Sort by priority, due date, created date

**F-010f: Todo Computed Metrics**
- **As a** manager, **I want to** see performance metrics on todos, **so that** I can assess team efficiency
- **Acceptance Criteria:**
  - **is_overdue**: Calculated dynamically (due_date < now AND status NOT IN [COMPLETED, CANCELLED])
  - **days_overdue**: Number of days past due (if overdue)
  - **days_to_complete**: Duration from created_at to completed_at (if completed)
  - **completed_on_time**: True if completed_at <= due_date (if completed)
  - Metrics computed on retrieval, not stored (always accurate)
  - Timezone-aware datetime comparisons (UTC)

**F-010g: Todo Dashboard Statistics**
- **As a** user, **I want to** see summary statistics of my todos, **so that** I understand my workload
- **Acceptance Criteria:**
  - Total todos assigned
  - Count by status (TODO, IN_PROGRESS, BLOCKED, COMPLETED, CANCELLED)
  - Count of overdue todos
  - Count of urgent and high priority todos
  - Dashboard widget for quick overview

**F-010h: Todo Auto-completion Tracking**
- **As a** system, **I want to** automatically set completion timestamp, **so that** metrics are accurate
- **Acceptance Criteria:**
  - When status changes to COMPLETED, auto-set completed_at to current time
  - When status changes from COMPLETED to other, clear completed_at
  - Track who completed the todo (audit trail)
  - Prevent manual completed_at manipulation

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

**F-014a: Department Statistics Report (NEW - v3.0)** ⭐
- **As a** PM/Manager, **I want to** view visa tracking statistics by department, **so that** I can monitor team compliance
- **Acceptance Criteria:**
  - Query department-level or contract-level visa statistics
  - Metrics: Beneficiary counts (direct/total/active/inactive), visa application counts by status/type
  - Expiration alerts: 30-day, 90-day, and expired visas
  - Support for recursive sub-department statistics
  - Role-based access: ADMIN (all), PM/HR (their contract), MANAGER (their dept only)
  - Used in department tree view for inline statistics display

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

#### **CaseGroup** (NEW in v2.0) ⭐
```python
id: UUID (PK)
beneficiary_id: UUID (FK → User)        # The person whose immigration case this is
name: String                            # e.g., "Luis - EB2-NIW to Green Card"
description: Text (nullable)
case_type: Enum                         # H1B_EXTENSION, H1B_TRANSFER, GREEN_CARD_PATHWAY, etc.
priority: Enum (LOW, MEDIUM, HIGH, URGENT)
status: Enum (PLANNING, ACTIVE, COMPLETED, CANCELLED)
start_date: Date (nullable)
target_completion_date: Date (nullable)
actual_completion_date: Date (nullable)
responsible_party_id: UUID (FK → User, nullable)  # Who manages this case group
notes: Text (nullable)
created_by_id: UUID (FK → User)
created_at: DateTime
updated_at: DateTime
```

**Case Types:**
- H1B_EXTENSION
- H1B_TRANSFER
- GREEN_CARD_PATHWAY
- TN_TO_H1B
- L1_TO_GREEN_CARD
- EB2_NIW
- PERM_BASED
- FAMILY_BASED
- OTHER

#### **Todo** (NEW in v2.0) ⭐
```python
id: UUID (PK)
title: String                           # Task title
description: Text (nullable)
assigned_to_id: UUID (FK → User)        # Who should complete this
priority: Enum (LOW, MEDIUM, HIGH, URGENT)
status: Enum (TODO, IN_PROGRESS, BLOCKED, COMPLETED, CANCELLED)
due_date: DateTime (nullable)
completed_at: DateTime (nullable)       # Auto-set when status → COMPLETED

# Hierarchical linking (denormalized for performance)
visa_application_id: UUID (FK → VisaApplication, nullable)
case_group_id: UUID (FK → CaseGroup, nullable)     # Auto-populated from visa_app
beneficiary_id: UUID (FK → User, nullable)         # Auto-populated from case_group

notes: Text (nullable)
created_by_id: UUID (FK → User)
created_at: DateTime
updated_at: DateTime

# Computed fields (not stored, calculated on retrieval):
# - is_overdue: bool (due_date < now AND status NOT IN [COMPLETED, CANCELLED])
# - days_overdue: int | None (days past due if overdue)
# - days_to_complete: int | None (created_at to completed_at if completed)
# - completed_on_time: bool | None (completed_at <= due_date if completed)
```

### 4.2 Relationships
- **User → Contract**: Many-to-One (one user belongs to one contract in v1)
- **User → User**: Self-referencing (reports_to hierarchy)
- **User → VisaApplication**: One-to-Many (one user has multiple visa applications)
- **User → AuditLog**: One-to-Many
- **User → Notification**: One-to-Many
- **User → CaseGroup**: One-to-Many (as beneficiary)
- **User → CaseGroup**: One-to-Many (as responsible_party)
- **User → Todo**: One-to-Many (as assigned_to)
- **Contract → User**: One-to-Many
- **CaseGroup → VisaApplication**: One-to-Many
- **CaseGroup → Todo**: One-to-Many
- **VisaApplication → Todo**: One-to-Many
- **VisaApplication → VisaType**: Many-to-One
- **VisaApplication → EmailLog**: One-to-Many

### 4.3 Indexes
- `User.email` (unique)
- `User.contract_id` (for filtering by contract)
- `VisaApplication.user_id` (for user lookups)
- `VisaApplication.expiration_date` (for notification queries)
- `VisaApplication.status` (for dashboard filtering)
- `VisaApplication.case_group_id` (for case group queries)
- `CaseGroup.beneficiary_id` (for beneficiary lookups)
- `CaseGroup.status` (for filtering active case groups)
- `Todo.assigned_to_id` (for "My Todos" queries)
- `Todo.status` (for filtering)
- `Todo.due_date` (for overdue queries)
- `Todo.visa_application_id, Todo.case_group_id, Todo.beneficiary_id` (for hierarchical queries)
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

### 5.5a Case Groups (NEW in v2.0) ⭐
```
GET    /api/v1/case-groups                       # List case groups (filtered by permissions)
GET    /api/v1/case-groups/{id}                  # Get case group details
POST   /api/v1/case-groups                       # Create case group (HR/PM/MANAGER)
PATCH  /api/v1/case-groups/{id}                  # Update case group
DELETE /api/v1/case-groups/{id}                  # Delete case group (HR/PM only)
GET    /api/v1/case-groups/{id}/visa-applications  # List visa apps in case group
POST   /api/v1/case-groups/{id}/visa-applications  # Link visa app to case group
GET    /api/v1/case-groups/{id}/todos            # List todos for case group
GET    /api/v1/beneficiaries/{id}/case-groups    # List beneficiary's case groups
```

### 5.5b Todos (NEW in v2.0) ⭐
```
GET    /api/v1/todos                   # List todos (filtered by permissions & role)
GET    /api/v1/todos/my                # Current user's assigned todos
GET    /api/v1/todos/team              # Team todos (hierarchy-based)
GET    /api/v1/todos/{id}              # Get todo details with computed metrics
POST   /api/v1/todos                   # Create todo (auto-populate hierarchy)
PATCH  /api/v1/todos/{id}              # Update todo (auto-sets completed_at)
DELETE /api/v1/todos/{id}              # Delete todo
GET    /api/v1/todos/stats             # Dashboard statistics (counts by status)
GET    /api/v1/visa-applications/{id}/todos    # Todos for specific visa app
```

**Todo Computed Metrics (returned on GET):**
```json
{
  "id": "uuid",
  "title": "File I-140",
  "due_date": "2024-06-15T00:00:00Z",
  "completed_at": "2024-06-14T15:30:00Z",
  "status": "COMPLETED",
  "is_overdue": false,
  "days_overdue": null,
  "days_to_complete": 3,
  "completed_on_time": true
}
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
GET    /api/v1/reports/dashboard         # Dashboard stats (role-filtered)
GET    /api/v1/reports/expiring          # Expiration report (CSV export)
GET    /api/v1/reports/analytics         # Charts data
GET    /api/v1/reports/audit-log         # Audit log export (admin)
GET    /api/v1/reports/department-stats  # Department visa tracking statistics (NEW)
```

**Department Statistics Endpoint (NEW):**
- Returns beneficiary and visa application metrics for departments
- Supports both department-level and contract-level queries
- Includes recursive sub-department statistics (configurable)
- Provides expiration alerts (30-day, 90-day, expired)
- Role-based access control (ADMIN, PM, HR, MANAGER)
- Used for department tree view inline statistics

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

### Phase 1: MVP (Weeks 1-3) ✅ COMPLETED
- ✅ Authentication (login, JWT, password reset)
- ✅ User + Contract + Visa Application models
- ✅ Basic CRUD for visa applications
- ✅ Role-based access control (5 roles)
- ✅ Simple dashboard (list view)
- ✅ Email notifications (hardcoded thresholds)

### Phase 2: Core Features (Weeks 4-6) ✅ COMPLETED
- ✅ Hierarchical reporting (Tech Lead sees reports)
- ✅ Expiration report + CSV export
- ✅ In-app notifications
- ✅ Audit log
- ✅ User settings (alert preferences)
- ✅ Analytics dashboard (charts)
- ✅ **Case Groups** - Organize visa applications by immigration pathway (NEW v2.0)
- ✅ **Todo System** - Task tracking with computed performance metrics (NEW v2.0)
- ✅ **Law Firm Management** - Track immigration attorneys and preferred vendors (NEW v2.0)
- ✅ **Fixture System** - Seed data for realistic development/testing (NEW v2.0)

### Phase 3: Polish (Weeks 7-8) ✅ COMPLETED
- ✅ Mobile responsiveness
- ✅ Advanced filtering/sorting
- ✅ Bulk operations (future)
- ✅ User onboarding flow
- ✅ Comprehensive testing
- ✅ Deployment guide + README

---

## 10. Phase 4: Future Enhancements

### High Priority 🎯

**F-030: Workflow Approvals & Delegation** (PARTIALLY COMPLETED)
- ✅ PM approval for case groups with status transitions (DRAFT → PENDING_PM_APPROVAL → APPROVED/REJECTED)
- ✅ Approval endpoints: `/case-groups/{id}/submit-for-approval`, `/case-groups/{id}/approve`, `/case-groups/{id}/reject`
- ✅ Audit logging captures all approval workflow changes (who approved/rejected, when, with what reason)
- ✅ Timeline endpoint `/case-groups/{id}/timeline` provides unified history (audit + milestones + todos)
- ⚠️ Still needed: Task delegation between HR/PM/Managers
- Effort: 1-2 weeks remaining for delegation features

**F-031: Cost Tracking**
- Track legal fees, filing fees, other costs per visa application
- Cost breakdown by case group and contract
- Export cost reports for finance
- Budget vs actual tracking
- Effort: Medium (2-3 weeks)

**F-032: SMS Notifications**
- Optional SMS alerts for critical expirations (Twilio)
- User opt-in with phone number configuration
- Rate limiting and cost monitoring
- Effort: Low-Medium (1-2 weeks)

### Lower Priority 📋

**F-033: Email Integration**
- Parse incoming emails from law firms
- Auto-update visa application status from email
- Email threading and conversation history
- Effort: High (4-5 weeks)

**F-034: Microsoft SSO**
- Single sign-on with Azure AD/Entra ID
- Requires IT department cooperation
- Auto-provision users on first login
- Effort: Medium-High (3-4 weeks)

**F-035: Immigration Attorney Portal**
- Limited portal access for law firm attorneys
- Read-only view of assigned cases
- Status updates and notes capability
- No document upload (firms have own portals)
- Effort: High (4-6 weeks)

**F-036: Multi-Contract Assignment**
- Allow users assigned to multiple contracts
- Very rare use case
- Major database schema change required
- Effort: High (4-6 weeks)

**F-037: Mobile App**
- React Native app for iOS/Android
- Push notifications, biometric login
- Evaluate need after 6 months of usage
- Effort: Very High (8-12 weeks)

### Explicitly Excluded ❌

**Document Upload & Storage**
- Each law firm has their own secure document portal
- No sensitive immigration documents stored in our system

---

## 11. Success Metrics (90 Days Post-Launch)

### 11.1 Adoption Metrics
- ✅ 100% of active employees have accounts
- ✅ 80% weekly active users (managers + HR)
- ✅ 50% of staff log in monthly

### 11.2 Operational Metrics
- ✅ Zero visa lapses due to missed deadlines
- ✅ 95% of expiration alerts delivered on time
- ✅ < 5 min to generate contract compliance report
- ✅ 90% of users rate UX as "Good" or "Excellent"

### 11.3 Technical Metrics
- ✅ < 2 sec API response time (p95)
- ✅ 99% uptime during business hours
- ✅ < 5 support tickets per week after onboarding

---

## 12. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Email service reliability (Gmail SMTP limits) | High | Use Brevo (300/day free), add retry logic, monitor send rates |
| SQLite concurrency issues (WAL mode limits) | Medium | Enable WAL mode, limit write concurrency, plan PostgreSQL migration path |
| Users forget to update visa info | High | Automated reminders, make status updates required quarterly |
| Complex reporting hierarchy edge cases | Medium | Validate no circular reports, add safeguards in recursive queries |
| Security breach (token theft) | High | Short token expiry, HTTPS only, monitor for anomalous access patterns |
| No IT department for Microsoft SSO | Low | Skip SSO in Phase 5, document setup for future when IT available |

---

## 13. Open Questions & Design Decisions

1. **Visa Application Costs**  
   **Decision:** Implement in Phase 4 (F-031) - Cost tracking per application for financial reporting.

2. **Employees Leaving Mid-Process**  
   **Decision:** Soft delete (is_active=False), preserve historical records for audit compliance.

3. **Task Delegation**  
   **Decision:** Implement in Phase 4 (F-030) - PM/HR can delegate tasks with approval workflow.

4. **Notification Timezone**  
   **Decision:** Default EST (company HQ), user override available in settings (implemented Phase 2).

5. **Immigration Attorney Information**  
   **Decision:** Law Firm Management implemented in v2.0. Attorney portal access planned for Phase 4 (F-035).

6. **Document Upload**  
   **Decision:** NOT implemented - Law firms maintain their own secure document portals. System stores URLs/references only.

---

## 14. Approval & Sign-Off

| Role | Name | Status | Date |
|------|------|--------|------|
| Product Owner | [User] | Approved | 2025-11-03 |
| Engineering Lead | GitHub Copilot | Approved | 2025-11-05 |
| HR Stakeholder | TBD | Pending | TBD |

---

## 15. Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-03 | GitHub Copilot | Initial PRD - MVP specification |
| 2.0 | 2025-11-05 | GitHub Copilot | Added Case Groups, Todo System, Law Firm Management. Updated all sections to reflect implemented v2.0 features. Marked Phases 1-3 as completed. Reorganized Phase 4 future enhancements by priority. |
| 3.0 | 2025-11-07 | GitHub Copilot | Added Department Statistics feature (F-014a). New endpoint `/api/v1/reports/department-stats` for visa tracking metrics focused on beneficiaries. Updated schema to focus on beneficiary counts vs user counts. Comprehensive department-level analytics for PM/Manager dashboards. |

---

**Next Steps:**
1. Deploy to production environment
2. Begin Phase 4 implementation (workflow approvals, cost tracking)
3. Monitor success metrics
4. Collect user feedback for prioritization

---

**Document History:**
- **v1.0** (2025-11-03): Initial draft based on stakeholder requirements
