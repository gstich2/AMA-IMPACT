# VisaApplication → Petition Refactor - Complete Impact Analysis

## Executive Summary

This refactor affects **47+ backend files** and **6+ frontend files**. The scope includes:
- 8 Model files
- 6 API endpoint files  
- 3 Service files
- 2 Schema files
- 11 Seed script files
- 1 Main application file
- 6 Frontend files
- 10+ Related table references (todos, milestones, RFEs, notifications, audit logs)

**Estimated Effort**: 40-50 hours over 5-7 days

---

## 🗂️ Backend Files Requiring Changes

### Core Models (8 files)

#### 1. **backend/app/models/visa.py** → **backend/app/models/petition.py**
- **Action**: RENAME FILE + REFACTOR CLASS
- **Changes**:
  ```python
  class VisaApplication → class Petition
  __tablename__ = "visa_applications" → "petitions"
  
  # Remove redundant fields:
  - visa_type (Enum)
  - visa_type_id (FK)
  
  # Keep and clarify:
  petition_type → petition_type (Enum: I140, I485, I129, etc.)
  
  # Add new field:
  + dependent_id = Column(ForeignKey("dependents.id"), nullable=True)
  
  # Update all relationships:
  - beneficiary = back_populates="visa_applications" → "petitions"
  - case_group = back_populates="visa_applications" → "petitions"
  ```
- **Impact**: CASCADE to all related models
- **Risk**: **HIGH** - Central model

#### 2. **backend/app/models/case_group.py**
- **Action**: UPDATE ENUM + RELATIONSHIPS
- **Changes**:
  ```python
  # Rename enum:
  class CaseType → class PathwayType
  
  # Remove values:
  - PERM (this is a petition, not a pathway)
  - SINGLE (unclear purpose)
  
  # Add values:
  + EB2_PERM
  + EB3_PERM
  + H1B_EXTENSION
  + H1B_TRANSFER
  + L1A, L1B
  + FAMILY_BASED
  
  # Update model:
  case_type → pathway_type
  visa_applications → petitions (relationship)
  + milestones (relationship - NEW case-level milestones)
  ```
- **Impact**: ALL case group queries
- **Risk**: **HIGH**

#### 3. **backend/app/models/milestone.py**
- **Action**: ADD CASE GROUP SUPPORT
- **Changes**:
  ```python
  # Current:
  visa_application_id = FK (required)
  
  # New:
  + case_group_id = FK (nullable)
  petition_id = FK (nullable) # renamed from visa_application_id
  
  # Constraint: Either case_group_id OR petition_id must be set
  __table_args__ = (
      CheckConstraint(
          '(case_group_id IS NOT NULL AND petition_id IS NULL) OR '
          '(case_group_id IS NULL AND petition_id IS NOT NULL)'
      ),
  )
  
  # Update relationships:
  visa_application → petition
  + case_group (NEW)
  ```
- **Impact**: ALL milestone queries, pipeline system
- **Risk**: **MEDIUM-HIGH**

#### 4. **backend/app/models/todo.py**
- **Action**: RENAME FIELD
- **Changes**:
  ```python
  visa_application_id → petition_id
  visa_application (relationship) → petition
  ```
- **Impact**: Todo creation, filtering
- **Risk**: **LOW-MEDIUM**

#### 5. **backend/app/models/notification.py** (EmailLog)
- **Action**: RENAME FIELD
- **Changes**:
  ```python
  visa_application_id → petition_id
  visa_application (relationship) → petition
  ```
- **Impact**: Email tracking, notification queries
- **Risk**: **LOW**

#### 6. **backend/app/models/rfe.py** (RFETracking)
- **Action**: RENAME FIELD
- **Changes**:
  ```python
  visa_application_id → petition_id
  visa_application (relationship) → petition
  ```
- **Impact**: RFE tracking queries
- **Risk**: **LOW**

#### 7. **backend/app/models/beneficiary.py**
- **Action**: UPDATE RELATIONSHIP
- **Changes**:
  ```python
  visa_applications (relationship) → petitions
  ```
- **Impact**: Beneficiary queries with joins
- **Risk**: **LOW**

#### 8. **backend/app/models/user.py**
- **Action**: UPDATE RELATIONSHIP
- **Changes**:
  ```python
  created_visa_applications → created_petitions
  ```
- **Impact**: User audit queries
- **Risk**: **LOW**

#### 9. **backend/app/models/dependent.py**
- **Action**: ADD RELATIONSHIP
- **Changes**:
  ```python
  + petitions = relationship("Petition", back_populates="dependent")
  ```
- **Impact**: Dependent queries
- **Risk**: **LOW**

---

### API Endpoints (6 files)

#### 10. **backend/app/api/v1/visa_applications.py** → **backend/app/api/v1/petitions.py**
- **Action**: RENAME FILE + REFACTOR ALL ENDPOINTS
- **Changes**:
  - Update all routes: `/api/v1/visa-applications` → `/api/v1/petitions`
  - Update all model references: `VisaApplication` → `Petition`
  - Update schema references: `VisaApplication*` → `Petition*`
  - Update query filters
- **Impact**: **CRITICAL** - Main CRUD API
- **Risk**: **CRITICAL**

#### 11. **backend/app/api/v1/case_groups.py**
- **Action**: UPDATE MODEL REFERENCES
- **Changes**:
  - Lines 876-1033 (progress endpoint): Update to use `Petition`
  - All joins: `VisaApplication` → `Petition`
  - All filters: Update to use new `petition_type` enum
  - Progress calculation: Add case-level milestone support
- **Impact**: Case group endpoints, progress tracking
- **Risk**: **HIGH**

#### 12. **backend/app/api/v1/audit_logs.py**
- **Action**: UPDATE RESOURCE TYPE HANDLING
- **Changes**:
  - Update all `resource_type = "visa_application"` → `"petition"`
  - Update resource activity queries
  - Update filtering logic
  - **NO backward compatibility needed** (alpha stage, no production data)
- **Impact**: Audit trail queries, compliance reports
- **Risk**: **LOW** (clean break, no legacy data)

#### 13. **backend/app/api/v1/reports.py**
- **Action**: UPDATE ALL REPORT QUERIES
- **Changes**:
  - `generate_visa_status_report()`: Use `Petition` model
  - All queries: `VisaApplication` → `Petition`
  - Department stats: Update aggregation logic
  - Analytics: Update trend calculations
- **Impact**: **ALL REPORTS**
- **Risk**: **HIGH**

#### 14. **backend/app/api/v1/dashboard.py**
- **Action**: UPDATE DASHBOARD QUERIES
- **Changes**:
  ```python
  # Line 19: Update import
  from app.models.visa import VisaApplication → from app.models.petition import Petition
  
  # Lines 40-70: Update all queries
  db.query(VisaApplication) → db.query(Petition)
  ```
- **Impact**: Dashboard summary statistics
- **Risk**: **MEDIUM**

#### 15. **backend/app/api/v1/notifications.py**
- **Action**: UPDATE NOTIFICATION QUERIES (if exists)
- **Changes**: Update queries for visa expiration notifications
- **Impact**: Notification system
- **Risk**: **LOW-MEDIUM**

#### 16. **backend/app/main.py**
- **Action**: UPDATE ROUTER IMPORT
- **Changes**:
  ```python
  from app.api.v1 import visa_applications → petitions
  app.include_router(visa_applications.router → petitions.router)
  ```
- **Impact**: Application startup
- **Risk**: **LOW** (straightforward)

---

### Service Files (3 files)

#### 17. **backend/app/services/reports_service.py**
- **Action**: UPDATE ALL REPORT GENERATION LOGIC
- **Changes**:
  - Lines 483, 614-615, 627-628, 682-685: Update all `visa_application` references
  - All queries: `VisaApplication` → `Petition`
  - Update field names: `visa_type` → `petition_type`
  - Update department stats calculations
- **Impact**: **ALL REPORT GENERATION**
- **Risk**: **HIGH**

#### 18. **backend/app/services/rbac_service.py**
- **Action**: UPDATE RBAC FILTERING
- **Changes**:
  ```python
  # Line 165:
  def apply_visa_application_filters → def apply_petition_filters
  
  # Update all query filters
  ```
- **Impact**: Role-based access control for petitions
- **Risk**: **MEDIUM**

#### 19. **backend/app/services/audit_service.py** (if exists)
- **Action**: UPDATE RESOURCE TYPE
- **Changes**: Replace all `"visa_application"` → `"petition"`
- **Impact**: Audit log queries
- **Risk**: **LOW** (clean break)

---

### Schema Files (2 files)

#### 20. **backend/app/schemas/visa.py** → **backend/app/schemas/petition.py**
- **Action**: RENAME FILE + REFACTOR SCHEMAS
- **Changes**:
  ```python
  class VisaApplication* → class Petition*
  class VisaTypeEnum → class PetitionType
  
  # Update all field names
  visa_type → petition_type
  + dependent_id
  ```
- **Impact**: All API request/response validation
- **Risk**: **HIGH**

#### 21. **backend/app/schemas/case_group.py**
- **Action**: UPDATE NESTED SCHEMAS
- **Changes**:
  ```python
  # Update embedded visa application schemas to use Petition
  visa_applications: List[VisaApplication*] → petitions: List[Petition*]
  ```
- **Impact**: Case group API responses
- **Risk**: **MEDIUM**

---

### Configuration Files (1 file)

#### 22. **backend/app/config/visa_pipelines.py**
- **Action**: MAJOR RESTRUCTURE
- **Changes**:
  ```python
  # Current:
  VISA_PIPELINES = {
      VisaTypeEnum.EB2NIW: {...}
  }
  
  # New:
  CASE_GROUP_PIPELINES = {
      PathwayType.EB2_NIW: {...}
  }
  
  PETITION_PIPELINES = {
      PetitionType.I140: {...},
      PetitionType.I485: {...}
  }
  
  # NEW: YAML loader
  def load_company_overrides(company_slug):
      # Load from config/companies/{company_slug}.yaml
      pass
  ```
- **Impact**: **ENTIRE PIPELINE SYSTEM**
- **Risk**: **HIGH**

---

### Seed Scripts (11 files)

#### 23-33. **backend/scripts/fixtures/**
All seed scripts need updates:

1. **contracts/seed_assess_beneficiaries.py**
   - Update: `VisaApplication` → `Petition`
   - Add: Complete petition sets (I-140 + I-485 + EAD + AP)
   - Add: Dependent petitions
   - Lines: 206, 213, 220, 227, 528, 535, 668-696, 779-800, 1054, 1154-1175

2. **contracts/seed_assess_visa_apps.py**
   - Rename to: `seed_assess_petitions.py`
   - Major refactor: Create complete petition sets per case group
   - Lines: 112, 165, 222, 273, 388, 434, 476

3. **contracts/seed_assess.py**
   - Update imports

4. **contracts/seed_rses.py**
   - Update if contains visa application references

5. **seed_development_data.py**
   - Lines: 730, 745, 760, 775, 790, 805, 820
   - Update all `visa_application_id` → `petition_id`

6-11. **Other seed scripts**
   - Check and update all references

**Impact**: Seed data generation
**Risk**: **HIGH** (need complete, realistic data)

---

### Database Schema (1 file - but we don't use it)

#### 34. **backend/alembic/versions/2025_11_04_1348-1817d21f2144_initial_schema.py**
- **Action**: **IGNORE** (per AI_DEVELOPMENT_GUIDELINES.md)
- **Note**: We use database reset via `setup_dev_environment.py`
- Lines affected: 226, 271-274, 277, 286, 289, 297, 300, 305, 320, 323, 329, 332, 334-336

---

## 🎨 Frontend Files Requiring Changes

### API Client (1 file)

#### 35. **frontend/lib/api.ts**
- **Action**: RENAME API CLIENT + UPDATE TYPES
- **Changes**:
  ```typescript
  // Rename:
  export const visaApplicationsAPI → export const petitionsAPI
  
  // Update all endpoint paths:
  '/api/v1/visa-applications' → '/api/v1/petitions'
  
  // Update type imports:
  VisaApplication → Petition
  VisaTypeEnum → PetitionType
  ```
- **Impact**: All frontend API calls
- **Risk**: **CRITICAL**

### Type Definitions (1 file)

#### 36. **frontend/types/index.ts**
- **Action**: UPDATE TYPE DEFINITIONS
- **Changes**:
  ```typescript
  export interface VisaApplication → export interface Petition
  export enum VisaTypeEnum → export enum PetitionType
  export interface CaseGroup {
      visa_applications: VisaApplication[] → petitions: Petition[]
  }
  ```
- **Impact**: All TypeScript type checking
- **Risk**: **HIGH**

### Pages (4 files)

#### 37. **frontend/app/cases/[id]/page.tsx**
- **Action**: UPDATE ALL REFERENCES
- **Changes**:
  - Lines 599-627: Visa applications display → Petitions display
  - Update all `visa_applications` → `petitions`
  - Update API calls: `visaApplicationsAPI` → `petitionsAPI`
  - Update type annotations
- **Impact**: Case detail page
- **Risk**: **HIGH**

#### 38. **frontend/app/cases/page.tsx**
- **Action**: UPDATE TABLE COLUMNS
- **Changes**: Update case list table to use new field names
- **Impact**: Case list page
- **Risk**: **LOW-MEDIUM**

#### 39. **frontend/app/visas/page.tsx** → **frontend/app/petitions/page.tsx**
- **Action**: RENAME PAGE (if exists)
- **Changes**: Update all references
- **Impact**: Petition list page (if exists)
- **Risk**: **MEDIUM**

#### 40. **frontend/app/dashboard/page.tsx** (if exists)
- **Action**: UPDATE DASHBOARD WIDGETS
- **Changes**: Update to use new petition API
- **Impact**: Dashboard display
- **Risk**: **LOW**

---

## 🔗 Related Systems Affected

### 1. **Audit Logging System**
- **Files**: `audit.py`, `audit_logs.py`, `audit_service.py`
- **Impact**: All audit logs reference `resource_type = "visa_application"`
- **Changes Needed**:
  - Update all logs to use `resource_type = "petition"`
  - Clean break - no backward compatibility needed (alpha stage)
- **Data Migration**: None needed (fresh database on each reset)
- **Risk**: **LOW** - Clean break, no legacy data

### 2. **Reporting System**
- **Files**: `reports.py`, `reports_service.py`, `dashboard.py`
- **Impact**: **ALL REPORTS** query `visa_applications` table
- **Changes Needed**:
  - Visa status reports
  - User activity reports (petition creation/updates)
  - Executive summaries
  - Department statistics
  - Analytics trends
  - Dashboard widgets
- **Risk**: **HIGH** - Critical business intelligence

### 3. **Notification System**
- **Files**: `notification.py`, `notifications.py`
- **Impact**: Visa expiration notifications
- **Changes Needed**:
  - Update email log table references
  - Update notification queries
  - Update notification templates (if they reference visa_application)
- **Risk**: **MEDIUM**

### 4. **RBAC System**
- **Files**: `rbac_service.py`
- **Impact**: Role-based access filtering
- **Changes Needed**:
  - Update `apply_visa_application_filters()` → `apply_petition_filters()`
  - Update all permission checks
- **Risk**: **MEDIUM-HIGH** - Security critical

### 5. **Todo System**
- **Files**: `todo.py`, `todos.py`
- **Impact**: Todos linked to visa applications
- **Changes Needed**:
  - Update `visa_application_id` → `petition_id`
  - Update denormalization logic (comments mention auto-population)
- **Risk**: **LOW-MEDIUM**

### 6. **Milestone System**
- **Files**: `milestone.py`, `milestones.py`
- **Impact**: **MAJOR** - Core progress tracking
- **Changes Needed**:
  - Add case group level milestones
  - Rename `visa_application_id` → `petition_id`
  - Add check constraint for case_group_id XOR petition_id
  - Update ALL pipeline logic
- **Risk**: **HIGH** - Core functionality

### 7. **RFE Tracking**
- **Files**: `rfe.py`
- **Impact**: RFEs linked to visa applications
- **Changes Needed**: Rename `visa_application_id` → `petition_id`
- **Risk**: **LOW**

### 8. **Email Logging**
- **Files**: `notification.py` (EmailLog model)
- **Impact**: Email logs linked to visa applications
- **Changes Needed**: Rename `visa_application_id` → `petition_id`
- **Risk**: **LOW**

---

## 📊 Database Schema Changes Summary

### Tables to Rename
- `visa_applications` → `petitions`

### Tables to Update (FK changes)
- `application_milestones`: 
  - Add `case_group_id` (nullable)
  - Rename `visa_application_id` → `petition_id` (nullable)
  - Add check constraint
- `todos`: Rename `visa_application_id` → `petition_id`
- `email_logs`: Rename `visa_application_id` → `petition_id`
- `rfe_tracking`: Rename `visa_application_id` → `petition_id`

### Tables to Remove
- `visa_types` (lookup table - replaced by enum)

### New Fields
- `petitions.dependent_id` (FK to dependents)

### Enum Changes
- `CaseType` → `PathwayType` (rename + cleanup)
- `VisaTypeEnum` → `PetitionType` (rename + restructure)

---

## 🚨 High-Risk Areas

### Critical (Break Everything)
1. **Petition Model Rename** - Core data model
2. **API Endpoint Changes** - All frontend calls break
3. **Pipeline System** - Progress tracking breaks
4. **Reports System** - All reports break

### High Risk (Major Functionality)
1. **Audit Logging** - Need backward compatibility
2. **RBAC Filtering** - Security implications
3. **Milestone System** - Two-level milestone support
4. **Case Group Progress** - Complex calculation logic

### Medium Risk (Important Features)
1. **Notification System** - Email tracking
2. **Dashboard** - Summary statistics
3. **Seed Data** - Need complete, realistic data
4. **Frontend Types** - TypeScript compilation

### Low Risk (Isolated Changes)
1. **Todo System** - Simple FK rename
2. **RFE Tracking** - Simple FK rename
3. **Email Logs** - Simple FK rename
4. **User/Beneficiary relationships** - Simple updates

---

## 🎯 Implementation Strategy

### Phase 1: Preparation (Day 1)
1. Create comprehensive test plan
2. Document all current API endpoints
3. Create rollback script
4. Backup production data (if applicable)

### Phase 2: Backend Models (Day 1-2)
1. Create new `petition.py` model
2. Update all related models (milestone, todo, rfe, notification)
3. Update case_group.py (PathwayType enum)
4. Run basic import tests

### Phase 3: Backend Config & Services (Day 2)
1. Restructure `visa_pipelines.py`
2. Implement YAML company override system
3. Update `reports_service.py`
4. Update `rbac_service.py`
5. Add backward compatibility in `audit_service.py`

### Phase 4: Backend APIs (Day 2-3)
1. Create new `petitions.py` endpoint
2. Update `case_groups.py` (progress endpoint)
3. Update `audit_logs.py` (backward compat)
4. Update `reports.py` (all report queries)
5. Update `dashboard.py` (summary stats)
6. Update `notifications.py` (if applicable)
7. Update `main.py` (router imports)

### Phase 5: Seed Scripts (Day 3)
1. Update all seed scripts
2. Create complete petition sets
3. Add dependent petitions
4. Test seed data generation

### Phase 6: Frontend (Day 3-4)
1. Update type definitions
2. Update API client
3. Update all pages
4. Test UI display

### Phase 7: Testing (Day 4-5)
1. Backend API tests (Swagger)
2. Frontend UI tests
3. Integration tests
4. Performance tests (reports)
5. Security tests (RBAC)

### Phase 8: Data Migration (Day 5)
1. Database reset via `setup_dev_environment.py`
2. Verify seed data
3. Test all features
4. Verify audit logs

---

## ✅ Testing Checklist

### Backend API Tests
- [ ] GET /api/v1/petitions (list)
- [ ] GET /api/v1/petitions/{id} (detail)
- [ ] POST /api/v1/petitions (create)
- [ ] PUT /api/v1/petitions/{id} (update)
- [ ] DELETE /api/v1/petitions/{id} (delete)
- [ ] GET /api/v1/case-groups/{id}/progress (case + petition milestones)
- [ ] GET /api/v1/case-groups (with petitions embedded)
- [ ] GET /api/v1/audit-logs (backward compatibility)
- [ ] GET /api/v1/reports/visa-status (now petition-status)
- [ ] GET /api/v1/dashboard (summary stats)

### Frontend Tests
- [ ] Case list page renders
- [ ] Case detail page shows petitions
- [ ] Progress bars display (case + petition levels)
- [ ] Petition types are human-readable (I-140, not I140)
- [ ] Dependent petitions indicated visually
- [ ] Dashboard widgets work
- [ ] Reports page works

### Data Integrity Tests
- [ ] All case groups have correct pathway_type
- [ ] EB2-NIW cases have I-140 + I-485 + EAD + AP
- [ ] H1B cases have I-129
- [ ] Dependent petitions linked correctly
- [ ] Case-level milestones exist
- [ ] Petition-level milestones exist
- [ ] Progress calculation works for both levels

### Security Tests
- [ ] RBAC filtering works for petitions
- [ ] Audit logs capture petition changes
- [ ] Beneficiaries see only their petitions
- [ ] Managers see team petitions
- [ ] PMs see contract petitions

---

## 📈 Estimated Effort

| Phase | Tasks | Estimated Hours |
|-------|-------|-----------------|
| Preparation | Documentation, planning | 2 hours (reduced) |
| Backend Models | 8 files | 6 hours (reduced) |
| Backend Config | 1 file + YAML system | 4 hours |
| Backend Services | 3 files | 4 hours (reduced) |
| Backend APIs | 6 files | 8 hours (reduced) |
| Seed Scripts | 11 files | 8 hours |
| Frontend | 6 files | 6 hours |
| Testing | Comprehensive | 8 hours |
| **TOTAL** | **47+ files** | **46 hours** |

**Timeline**: 6 days with focused work

**Note**: Reduced from 54 hours because no backward compatibility needed (alpha stage)

---

## 🔄 Rollback Plan

If refactor fails:

```bash
# Restore from git
git reset --hard 91e89a4  # Current checkpoint commit

# Reset database
cd backend
python scripts/setup_dev_environment.py

# Restart services
cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 7001 &
cd frontend && npm run dev &
```

**Data Loss**: None (development environment only)

---

## 💬 Case Notes Feature - Separate Implementation

Since this is requested as part of the refactor, here's the plan:

### Model
```python
class CaseNote(Base):
    __tablename__ = "case_notes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_group_id = Column(String(36), ForeignKey("case_groups.id"), nullable=False)
    author_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)  # Plain text
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    case_group = relationship("CaseGroup", back_populates="notes")
    author = relationship("User", back_populates="case_notes")
```

### API Endpoints
- POST `/api/v1/case-groups/{id}/notes` - Add note
- GET `/api/v1/case-groups/{id}/notes` - List notes
- PUT `/api/v1/case-groups/{id}/notes/{note_id}` - Edit note (author only)
- DELETE `/api/v1/case-groups/{id}/notes/{note_id}` - Delete note (author + admins)

### Frontend UI
- Notes section in case detail page
- Simple textarea for adding notes
- List of notes with author, timestamp
- Edit/delete buttons (if permissions allow)
- No rich text formatting (plain text only per user request)

### Effort
- Model + API: 2 hours
- Frontend UI: 2 hours
- Testing: 1 hour
- **Total**: 5 hours

---

## 🎨 YAML Configuration System

### File Structure
```
backend/config/companies/
├── default.yaml
├── assess.yaml
└── rses.yaml
```

### Example YAML
```yaml
# config/companies/assess.yaml
company_slug: assess

case_group_pipelines:
  EB2_NIW:
    name: "EB-2 NIW for ASSESS"
    stages:
      - order: 1
        milestone_type: CASE_OPENED
        weight: 5
        custom_field: "Requires NASA clearance check"
      - order: 2
        milestone_type: STRATEGY_MEETING
        weight: 10

petition_pipelines:
  I140:
    name: "I-140 for ASSESS"
    stages:
      - order: 1
        milestone_type: DOCUMENTS_REQUESTED
        weight: 20
        required_documents:
          - "Reference letters (3)"
          - "Publications list"
          - "Citation report"
```

### Loader Implementation
```python
import yaml
from pathlib import Path

def load_company_pipeline_config(company_slug: str) -> dict:
    """Load company-specific pipeline configuration."""
    config_dir = Path(__file__).parent / "companies"
    config_file = config_dir / f"{company_slug}.yaml"
    
    # Load default config
    with open(config_dir / "default.yaml") as f:
        config = yaml.safe_load(f)
    
    # Merge company-specific overrides
    if config_file.exists():
        with open(config_file) as f:
            company_config = yaml.safe_load(f)
            config = deep_merge(config, company_config)
    
    return config
```

### Effort
- YAML structure design: 1 hour
- Loader implementation: 2 hours
- Default config creation: 2 hours
- Company-specific configs: 2 hours
- Testing: 1 hour
- **Total**: 8 hours

---

## 🎯 Priority Order

1. **Create US Visa Types Reference** ✅ DONE
2. **Analyze Full Scope** ✅ IN PROGRESS
3. **Update REFACTOR_DESIGN.md** ← NEXT
4. **Execute Refactor (Models → APIs → Frontend)**
5. **Implement YAML Config System**
6. **Add Case Notes Feature**
7. **Comprehensive Testing**

---

This document provides complete visibility into the refactor scope. Review carefully before proceeding.
