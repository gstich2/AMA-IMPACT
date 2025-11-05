# Changelog

All notable changes to the AMA-IMPACT project.

## [2.0.0] - 2025-11-05

### 🎉 Major Features Added

#### Case Groups
- **CaseGroup Model**: Organize related visa applications into immigration pathways
- Support for H1B extension, green card pathways, TN to H1B transitions, etc.
- Hierarchical organization: Beneficiary → CaseGroup → VisaApplication
- Status tracking: PLANNING, ACTIVE, COMPLETED, CANCELLED
- Priority levels and target completion dates

#### Todo System
- **Todo Model**: Comprehensive task tracking with hierarchical relationships
- Link todos to visa applications, case groups, or beneficiaries
- **Computed Metrics** (calculated dynamically):
  - `is_overdue`: Whether task is past due
  - `days_overdue`: Days past the due date
  - `days_to_complete`: Duration from creation to completion
  - `completed_on_time`: Whether completed before deadline
- **Auto-population**: Hierarchy automatically filled from visa app → case group → beneficiary
- **Role-based visibility**:
  - BENEFICIARY: Own todos only
  - MANAGER: Own + subordinates' todos (recursive hierarchy)
  - PM/HR/ADMIN: All todos
- Dashboard endpoints: `/my-todos`, `/team-todos`, `/stats`
- Filter by status, priority, completion
- 7 sample todos in development fixtures

#### User Creation Permissions
- **Role-based user creation control**:
  - ADMIN: Can create any role (ADMIN, HR, PM, MANAGER, BENEFICIARY)
  - HR/PM/MANAGER: Can only create BENEFICIARY users
  - BENEFICIARY: Cannot create users
- Enhanced security and access control

### 📚 Documentation Overhaul

#### MkDocs Setup
- **Complete documentation site** with Material theme
- Organized structure:
  - Getting Started (Quick Start, Installation, Configuration)
  - Product (Overview, PRD, User Roles, Use Cases)
  - Architecture (Data Models, Database Schema, Security)
  - API Reference (All endpoints with examples)
  - Development (Setup, Database, Fixtures, Testing)
  - Deployment (Production setup, Environment, Monitoring)

#### Updated Documentation
- **DATA_MODEL.md**: Complete v3.0 with CaseGroup and Todo models
- **API Documentation**: Comprehensive endpoint docs with examples
- **Quick Start Guide**: Get running in under 10 minutes
- **Development Guide**: Complete setup and workflow documentation

### 🔧 Backend Improvements

#### Fixture System
- **Modular fixture architecture**:
  - `seed_users.py` - System users with roles
  - `seed_contracts.py` - Contract data
  - `seed_departments.py` - Department hierarchy
  - `seed_beneficiaries.py` - Sample beneficiaries
  - `seed_visa_applications.py` - Visa petitions
  - `seed_case_groups.py` - Case group pathways
  - `seed_dependents.py` - Family members
  - `seed_law_firms.py` - Law firm data
  - `seed_development_data.py` - Todos and additional data
- **setup_dev_environment.py**: Single command to initialize complete database
- Representative sample data for realistic testing

#### API Enhancements
- **Todo API** (`/api/v1/todos`):
  - `POST /` - Create todo with auto-population
  - `GET /my-todos` - Personal todos with filters
  - `GET /team-todos` - Team/hierarchy todos
  - `GET /stats` - Dashboard statistics
  - `GET /beneficiary/{id}` - Todos for beneficiary
  - `GET /visa-application/{id}` - Todos for visa app
  - `GET /case-group/{id}` - Todos for case group
  - `PATCH /{id}` - Update todo (auto-set completed_at)
  - `DELETE /{id}` - Delete todo
- **CaseGroup API** (`/api/v1/case-groups`):
  - Full CRUD operations
  - Hierarchy management
  - Visa application associations
- All endpoints return enriched responses with computed metrics

#### Database Schema
- Added `case_groups` table with relationships
- Added `todos` table with denormalized hierarchy
- Multiple indexes for performance:
  - `todo_assigned_status_idx`
  - `todo_assigned_priority_idx`
  - `todo_beneficiary_status_idx`
  - `todo_due_date_status_idx`
  - `case_group_beneficiary_idx`
  - `case_group_status_idx`

### 🎨 Design Decisions

#### Computed Metrics vs Stored Status
- **Why**: Always accurate, no stale data
- Overdue status calculated dynamically: `due_date < now AND status NOT IN (COMPLETED, CANCELLED)`
- Enables flexible reporting without background jobs
- Timezone-aware datetime comparisons (UTC)

#### Denormalized Todo Hierarchy
- **Why**: Performance and query simplicity
- Store `beneficiary_id`, `case_group_id`, `visa_application_id` on Todo
- Fast filtering: "all todos for a beneficiary" without joins
- Auto-populated from parent relationships

#### CaseGroup as Optional Parent
- **Why**: Flexibility
- Visa applications can exist standalone or in groups
- Not all cases are multi-step pathways
- Organizes related applications for better management

### 📝 Sample Data Included

#### Users
- 1 Admin, 1 HR, 1 PM, 3 Managers
- 6 Beneficiaries (Luis, Priya, Wei, Elena, Carlos, Yuki)

#### Visa Applications
- Luis: EB2-NIW I-140 (Approved)
- Priya: H1B Extension (In Progress)
- Wei: TN Status (Active)
- Elena: EB2-NIW I-140 (In Progress)

#### Case Groups
- Luis: "EB2-NIW to Green Card Pathway"
- Priya: "H1B Extension 2025"
- Elena: "EB2-NIW Pathway"

#### Todos
- 7 sample todos with various priorities
- Linked to visa applications and case groups
- Demonstrates overdue tracking and metrics

---

## [1.0.0] - 2025-11-04

### Initial Release

#### Core Features
- **User Management**: Authentication, roles, hierarchy
- **Beneficiary System**: Separation from User accounts
- **Visa Application Tracking**: Full lifecycle management
- **Contract & Department Management**: Organizational structure
- **Dependent Tracking**: Family member visa management
- **Law Firm Integration**: Attorney and firm management
- **Audit Logging**: Complete change tracking
- **Email Notifications**: Expiration alerts (planned)

#### Authentication & Security
- JWT-based authentication
- OAuth2 password flow
- Role-based access control (5 roles)
- Password reset functionality
- Rate limiting

#### API Endpoints
- `/api/v1/auth/*` - Authentication
- `/api/v1/users/*` - User management
- `/api/v1/beneficiaries/*` - Beneficiary management
- `/api/v1/visa-applications/*` - Visa tracking
- `/api/v1/contracts/*` - Contract management
- `/api/v1/departments/*` - Department management

#### Database Models
- User, Beneficiary, VisaApplication, Contract, Department
- Dependent, LawFirm, VisaType
- AuditLog, Notification, UserSettings, EmailLog
- ApplicationMilestone, RFETracking

#### Documentation
- Initial PRD (Product Requirements Document)
- Basic data model documentation
- README with setup instructions

---

## Version Comparison

| Feature | v1.0.0 | v2.0.0 |
|---------|--------|--------|
| **Visa Applications** | ✅ | ✅ |
| **Case Groups** | ❌ | ✅ |
| **Todo System** | ❌ | ✅ |
| **Computed Metrics** | ❌ | ✅ |
| **Fixture System** | Basic | ✅ Modular |
| **Documentation** | Basic | ✅ Complete |
| **User Creation Control** | ❌ | ✅ Role-based |
| **MkDocs Site** | ❌ | ✅ |
| **API Docs** | Swagger only | ✅ + Examples |

---

## Upcoming Features (v3.0.0)

### Planned
- [ ] Email notification system
- [ ] Frontend implementation (Next.js)
- [ ] Advanced reporting and analytics
- [ ] Document upload and management
- [ ] Workflow approvals
- [ ] Multi-contract assignment for users
- [ ] Cost tracking and budgeting
- [ ] Immigration attorney collaboration module
- [ ] SMS notifications (Twilio)
- [ ] Microsoft SSO integration

### Under Consideration
- [ ] Mobile app (React Native)
- [ ] Workflow automation
- [ ] AI-powered case recommendations
- [ ] Integration with USCIS case status API
- [ ] Calendar integration for deadlines
- [ ] Slack/Teams notifications

---

## Migration Guide

### From v1.0.0 to v2.0.0

#### Database Migration

**Option 1: Fresh Install (Recommended for Development)**
```bash
# Backup existing data
cp backend/devel.db backend/devel.db.backup

# Delete and recreate
rm backend/devel.db
python backend/scripts/setup_dev_environment.py
```

**Option 2: Add New Tables (Production)**
```sql
-- Add case_groups table
CREATE TABLE case_groups (
    id TEXT PRIMARY KEY,
    beneficiary_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    case_type TEXT NOT NULL,
    status TEXT NOT NULL,
    priority TEXT NOT NULL,
    start_date DATE,
    target_completion_date DATE,
    actual_completion_date DATE,
    responsible_party_id TEXT,
    notes TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    FOREIGN KEY (beneficiary_id) REFERENCES beneficiaries (id),
    FOREIGN KEY (responsible_party_id) REFERENCES users (id)
);

-- Add todos table
CREATE TABLE todos (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    assigned_to_user_id TEXT NOT NULL,
    created_by_user_id TEXT NOT NULL,
    visa_application_id TEXT,
    case_group_id TEXT,
    beneficiary_id TEXT,
    status TEXT NOT NULL,
    priority TEXT NOT NULL,
    due_date DATE,
    completed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    FOREIGN KEY (assigned_to_user_id) REFERENCES users (id),
    FOREIGN KEY (created_by_user_id) REFERENCES users (id),
    FOREIGN KEY (visa_application_id) REFERENCES visa_applications (id),
    FOREIGN KEY (case_group_id) REFERENCES case_groups (id),
    FOREIGN KEY (beneficiary_id) REFERENCES beneficiaries (id)
);

-- Add indexes
CREATE INDEX idx_todo_assigned_status ON todos(assigned_to_user_id, status);
CREATE INDEX idx_todo_assigned_priority ON todos(assigned_to_user_id, priority);
CREATE INDEX idx_todo_beneficiary_status ON todos(beneficiary_id, status) WHERE beneficiary_id IS NOT NULL;
CREATE INDEX idx_todo_due_date_status ON todos(due_date, status) WHERE due_date IS NOT NULL;
CREATE INDEX idx_case_group_beneficiary ON case_groups(beneficiary_id);
CREATE INDEX idx_case_group_status ON case_groups(status);
```

#### API Changes

**No Breaking Changes** - All v1.0.0 endpoints remain functional.

**New Endpoints:**
- `POST /api/v1/case-groups` - Create case group
- `GET /api/v1/case-groups` - List case groups
- `POST /api/v1/todos` - Create todo
- `GET /api/v1/todos/my-todos` - Get personal todos
- And more... (see API documentation)

#### Code Updates

**User Creation**:
```python
# v1.0.0 - No restrictions
POST /api/v1/users
{
    "role": "ADMIN"  # Any role could create any role
}

# v2.0.0 - Role-based restrictions
POST /api/v1/users
{
    "role": "ADMIN"  # Only ADMIN can create ADMIN users
    # HR/PM/MANAGER can only create BENEFICIARY users
}
```

---

## Contributors

- Engineering Team @ AMA Inc.
- Special thanks to all contributors

---

**For detailed changes, see the [commit history](https://github.com/gstich2/AMA-IMPACT/commits/main)**
