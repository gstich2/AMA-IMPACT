# AMA-IMPACT Data Model Documentation

**Version:** 3.0 - Complete Implementation with CaseGroup and Todo  
**Date:** November 5, 2025  
**Status:** ✅ Implemented and Deployed

---

## Overview

This document describes the complete data model for the AMA-IMPACT immigration management system.

### Core Philosophy

**Separation of Concerns:**
- **User** = System access, authentication, organizational structure
- **Beneficiary** = Foreign national with visa cases (may or may not have User account)
- **CaseGroup** = Collection of related visa applications (e.g., H1B → Green Card pathway)
- **VisaApplication** = Individual visa petitions
- **Todo** = Task tracking with hierarchical case relationships
- **Dependent** = Family members of Beneficiaries

**Data Minimization:**
- Only store data necessary for visa case tracking
- No sensitive personal data (passport numbers, personal phones)
- Minimal attorney data (stored as text fields on applications)

---

## Entity Relationship Diagram

```
Contract ─┬─→ User* ──→ Beneficiary? ──┬─→ CaseGroup* ──→ VisaApplication*
          │                            │
          └─→ Department* ──→ User*    └─→ Dependent*
                                       └─→ Todo* (via beneficiary_id)

VisaApplication ──→ VisaType
                 ──→ LawFirm
                 ──→ ApplicationMilestone*
                 ──→ RFETracking*
                 ──→ Todo* (via visa_application_id)

CaseGroup ──→ Todo* (via case_group_id)

Todo ──→ User (assigned_to, created_by)
     ──→ Beneficiary (optional)
     ──→ CaseGroup (optional)
     ──→ VisaApplication (optional)

* = One-to-Many relationship
? = Optional/Nullable
```

---

## 1. User Model

**Purpose:** System authentication, authorization, and organizational hierarchy

```python
User:
    # Identity & Authentication
    id: UUID (PK)
    email: String (unique, indexed) - Login email
    hashed_password: String
    full_name: String - Display name
    
    # Authorization
    role: Enum - ADMIN, HR, PM, MANAGER, BENEFICIARY
    
    # Organizational Structure
    contract_id: FK → Contract
    department_id: FK → Department  
    reports_to_id: FK → User (self-reference)
    
    # Status
    is_active: Boolean
    last_login: DateTime
    force_password_change: Boolean
    
    # Timestamps
    created_at: DateTime
    updated_at: DateTime
    
    # Relationships
    → contract: Contract
    → department: Department
    → reports_to: User
    → direct_reports: List[User]
    → beneficiary: Beneficiary (one-to-one, nullable)
    → assigned_todos: List[Todo]
    → created_todos: List[Todo]
    → audit_logs: List[AuditLog]
    → notifications: List[Notification]
    → settings: UserSettings
```

**Roles:**
- **ADMIN** - Full system access, manage all data
- **HR** - Manage visa applications and user accounts
- **PM** - Project Manager, view all data + advanced metrics
- **MANAGER** - Team lead, view direct/indirect reports
- **BENEFICIARY** - Foreign national employee, view own cases only

**User Creation Permissions:**
- **ADMIN**: Can create any role (ADMIN, HR, PM, MANAGER, BENEFICIARY)
- **HR, PM, MANAGER**: Can only create BENEFICIARY users
- **BENEFICIARY**: Cannot create users

---

## 2. Beneficiary Model

**Purpose:** Foreign nationals who have visa cases (employees, future hires, contractors)

```python
Beneficiary:
    # Identity
    id: UUID (PK)
    user_id: FK → User (nullable, unique) - Links to User if system access
    first_name: String
    last_name: String
    
    # Immigration Information
    country_of_citizenship: String
    country_of_birth: String
    passport_country: String - For dual citizens
    passport_expiration: Date - For renewal warnings
    
    # Current Visa Status
    current_visa_type: String - H1B, TN, L1, etc.
    current_visa_expiration: Date - Critical for renewals
    i94_expiration: Date - Compliance tracking
    
    # Employment Information
    job_title: String - For USCIS documents
    employment_start_date: Date
    
    # Status
    is_active: Boolean
    notes: Text
    
    # Timestamps
    created_at: DateTime
    updated_at: DateTime
    
    # Relationships
    → user: User (nullable)
    → case_groups: List[CaseGroup]
    → visa_applications: List[VisaApplication]
    → dependents: List[Dependent]
    → todos: List[Todo]
    
    # Indexes
    - beneficiary_user_id_idx ON (user_id) WHERE user_id IS NOT NULL
    - beneficiary_active_idx ON (is_active)
    - beneficiary_visa_expiration_idx ON (current_visa_expiration)
```

---

## 3. CaseGroup Model ⭐ NEW

**Purpose:** Organize related visa applications into immigration pathways

```python
CaseGroup:
    # Identity
    id: UUID (PK)
    beneficiary_id: FK → Beneficiary
    
    # Case Information
    name: String - "H1B to Green Card Pathway"
    description: Text - "Path from H1B through EB2-NIW to permanent residence"
    case_type: Enum - H1B_EXTENSION, GREEN_CARD_PATHWAY, TN_TO_H1B, etc.
    
    # Status
    status: Enum - PLANNING, ACTIVE, COMPLETED, CANCELLED
    priority: Enum - LOW, MEDIUM, HIGH, URGENT
    
    # Important Dates
    start_date: Date - When case group initiated
    target_completion_date: Date - Target for completion
    actual_completion_date: Date - When finalized
    
    # Management
    responsible_party_id: FK → User - AMA staff managing case group
    
    # Additional
    notes: Text
    is_active: Boolean
    
    # Timestamps
    created_at: DateTime
    updated_at: DateTime
    
    # Relationships
    → beneficiary: Beneficiary
    → responsible_party: User
    → visa_applications: List[VisaApplication]
    → todos: List[Todo]
    
    # Indexes
    - case_group_beneficiary_idx ON (beneficiary_id)
    - case_group_status_idx ON (status)
    - case_group_active_idx ON (is_active)
```

**CaseType Enum:**
```python
H1B_EXTENSION         # Extending existing H1B
H1B_TRANSFER          # Changing employers on H1B
GREEN_CARD_PATHWAY    # Full pathway to permanent residence
TN_TO_H1B            # Canadian/Mexican TN transitioning to H1B
L1_TO_GREEN_CARD     # L1 to permanent residence
EB2_NIW              # EB2 National Interest Waiver path
PERM_BASED           # Labor certification based
FAMILY_BASED         # Family sponsorship
OTHER                # Custom case types
```

**Example Case Group:**
```
Name: "Luis Fernandes - EB2-NIW to Green Card"
Type: GREEN_CARD_PATHWAY
Applications:
  1. I-140 EB2-NIW (Approved Nov 2024)
  2. I-485 Adjustment of Status (In Progress)
  3. I-765 EAD (Pending)
  4. I-131 Advance Parole (Pending)
```

---

## 4. Todo Model ⭐ NEW

**Purpose:** Task tracking with hierarchical case relationships and computed metrics

```python
Todo:
    # Identity
    id: UUID (PK)
    
    # Task Information
    title: String - "Submit I-485 Application"
    description: Text - Detailed task description
    
    # Assignment
    assigned_to_user_id: FK → User - Who is responsible
    created_by_user_id: FK → User - Who created the todo
    
    # Hierarchy (Denormalized for Performance)
    visa_application_id: FK → VisaApplication (nullable)
    case_group_id: FK → CaseGroup (nullable)
    beneficiary_id: FK → Beneficiary (nullable)
    
    # Status & Priority
    status: Enum - TODO, IN_PROGRESS, BLOCKED, COMPLETED, CANCELLED
    priority: Enum - LOW, MEDIUM, HIGH, URGENT
    
    # Important Dates
    due_date: Date (nullable)
    completed_at: DateTime (nullable)
    
    # Timestamps
    created_at: DateTime
    updated_at: DateTime
    
    # Relationships
    → assigned_to: User
    → created_by: User
    → visa_application: VisaApplication
    → case_group: CaseGroup
    → beneficiary: Beneficiary
    
    # Indexes
    - todo_assigned_status_idx ON (assigned_to_user_id, status)
    - todo_assigned_priority_idx ON (assigned_to_user_id, priority)
    - todo_beneficiary_status_idx ON (beneficiary_id, status) WHERE beneficiary_id IS NOT NULL
    - todo_due_date_status_idx ON (due_date, status) WHERE due_date IS NOT NULL
```

**TodoStatus Enum:**
```python
TODO           # Not started
IN_PROGRESS    # Actively being worked on
BLOCKED        # Waiting on external dependency
COMPLETED      # Successfully finished
CANCELLED      # No longer needed
```

**TodoPriority Enum:**
```python
LOW      # Nice to have
MEDIUM   # Standard priority
HIGH     # Important, time-sensitive
URGENT   # Critical, immediate attention
```

### Computed Metrics (API Response Only)

These fields are **computed dynamically** when retrieving todos, not stored in database:

```python
TodoResponse (API Schema):
    # ... all Todo fields ...
    
    # Computed Metrics
    is_overdue: bool | None
        # True if: due_date < now AND status NOT IN (COMPLETED, CANCELLED)
        
    days_overdue: int | None
        # (now - due_date).days if overdue
        
    days_to_complete: int | None
        # (completed_at - created_at).days if completed
        
    completed_on_time: bool | None
        # True if completed_at <= due_date
```

**Why Computed Metrics?**
- ✅ Always accurate (no stale data)
- ✅ Flexible for reporting (can filter/aggregate dynamically)
- ✅ No need for background jobs to update status
- ✅ Simpler data model (no redundant fields)

### Hierarchical Auto-Population

When creating a todo:
- **If visa_application_id provided**: Auto-fills case_group_id and beneficiary_id
- **If case_group_id provided**: Auto-fills beneficiary_id
- **If beneficiary_id only**: Todo at beneficiary level
- **If none provided**: General todo not tied to any case

Example:
```python
# Create todo for specific visa application
POST /api/v1/todos
{
  "title": "Submit I-140 petition",
  "assigned_to_user_id": "hr-user-id",
  "visa_application_id": "visa-123",  # Only specify this
  "due_date": "2025-12-01"
}

# System automatically populates:
# - case_group_id (from VisaApplication.case_group_id)
# - beneficiary_id (from VisaApplication.beneficiary_id)
```

---

## 5. VisaApplication Model

**Purpose:** Individual visa petitions/applications with comprehensive tracking

```python
VisaApplication:
    # Identity
    id: UUID (PK)
    beneficiary_id: FK → Beneficiary
    case_group_id: FK → CaseGroup (nullable) - Optional grouping
    visa_type_id: FK → VisaType
    created_by: FK → User
    
    # Case Classification
    visa_type: Enum - H1B, TN, EB2NIW, etc.
    petition_type: String - I-129, I-140, I-485, etc.
    status: Enum - DRAFT, SUBMITTED, IN_PROGRESS, APPROVED, DENIED, EXPIRED
    case_status: Enum - UPCOMING, ACTIVE, FINALIZED
    priority: Enum - LOW, MEDIUM, HIGH, CRITICAL
    current_stage: String - "I-140 Filed", "RFE Response Submitted"
    
    # Important Dates
    filing_date: Date
    approval_date: Date
    expiration_date: Date
    i94_expiration_date: Date
    next_action_date: Date
    
    # USCIS Tracking
    receipt_number: String - WAC2190012345
    company_case_id: String - Internal tracking
    
    # Law Firm & Attorney
    law_firm_id: FK → LawFirm
    attorney_name: String
    attorney_email: String
    attorney_phone: String
    responsible_party_id: FK → User - AMA staff managing case
    
    # RFE Tracking
    rfe_received: Boolean
    rfe_received_date: Date
    rfe_response_date: Date
    rfe_notes: Text
    
    # Cost Tracking
    filing_fee: String
    attorney_fee: String
    premium_processing: Boolean
    premium_processing_fee: String
    total_cost: String
    
    # Status & Notes
    is_active: Boolean
    notes: Text
    
    # Timestamps
    created_at: DateTime
    updated_at: DateTime
    
    # Relationships
    → beneficiary: Beneficiary
    → case_group: CaseGroup
    → visa_type_info: VisaType
    → law_firm: LawFirm
    → responsible_party: User
    → creator: User
    → milestones: List[ApplicationMilestone]
    → rfes: List[RFETracking]
    → todos: List[Todo]
    → email_logs: List[EmailLog]
```

---

## 6. Dependent Model

**Purpose:** Track family members (spouses, children) of Beneficiaries

```python
Dependent:
    # Identity
    id: UUID (PK)
    beneficiary_id: FK → Beneficiary
    first_name: String
    last_name: String
    
    # Relationship
    relationship_type: Enum - SPOUSE, CHILD, OTHER
    date_of_birth: Date (optional)
    
    # Immigration Status
    country_of_citizenship: String
    country_of_birth: String
    passport_country: String
    passport_expiration: Date
    
    # Current Visa Status
    current_visa_type: String - H4, L2, F2, etc.
    visa_expiration: Date
    i94_expiration: Date
    
    # Timestamps
    created_at: DateTime
    updated_at: DateTime
    
    # Relationships
    → beneficiary: Beneficiary
```

---

## 7. Contract Model

**Purpose:** Projects/contracts that organize employees

```python
Contract:
    # Identity
    id: UUID (PK)
    name: String - "ASSESS"
    code: String (unique) - "ASSESS-2024"
    
    # Dates
    start_date: Date
    end_date: Date
    status: Enum - ACTIVE, ARCHIVED
    
    # Management
    manager_user_id: FK → User - Project Manager
    
    # Client Information
    client_name: String - "NASA"
    client_contact_name: String
    client_contact_email: String
    client_contact_phone: String
    
    # Additional
    description: Text
    notes: Text
    
    # Timestamps
    created_at: DateTime
    updated_at: DateTime
    
    # Relationships
    → manager: User
    → users: List[User]
    → departments: List[Department]
```

---

## 8. Department Model

**Purpose:** Organizational hierarchy within contracts

```python
Department:
    # Identity
    id: UUID (PK)
    name: String - "Technical Numerical Analysis"
    code: String - "TNA"
    
    # Hierarchy
    contract_id: FK → Contract
    parent_id: FK → Department (self-reference, nullable)
    
    # Status
    is_active: Boolean
    
    # Timestamps
    created_at: DateTime
    updated_at: DateTime
    
    # Relationships
    → contract: Contract
    → parent: Department
    → children: List[Department]
    → users: List[User]
```

---

## 9. LawFirm Model

**Purpose:** Track law firms handling visa cases

```python
LawFirm:
    # Identity
    id: UUID (PK)
    name: String
    
    # Primary Contact
    contact_person: String
    email: String
    phone: String
    
    # Address
    address: Text
    website: String
    
    # Status & Notes
    is_preferred_vendor: Boolean
    performance_rating: String
    is_active: Boolean
    notes: Text
    
    # Timestamps
    created_at: DateTime
    updated_at: DateTime
    
    # Relationships
    → applications: List[VisaApplication]
```

---

## 10. VisaType Model

**Purpose:** Visa type definitions for dropdowns and validation

```python
VisaType:
    # Identity
    id: UUID (PK)
    code: String (unique) - "H1B", "EB2NIW"
    name: String - "H-1B Specialty Occupation"
    description: Text
    
    # Configuration
    default_renewal_lead_days: String - "180"
    is_active: Boolean
    
    # Timestamps
    created_at: DateTime
    
    # Relationships
    → applications: List[VisaApplication]
```

---

## Supporting Models

### ApplicationMilestone
```python
ApplicationMilestone:
    id: UUID (PK)
    visa_application_id: FK → VisaApplication
    created_by: FK → User
    milestone_type: Enum
    milestone_date: Date
    title: String (optional)
    description: Text
    created_at: DateTime
    updated_at: DateTime
```

### RFETracking
```python
RFETracking:
    id: UUID (PK)
    visa_application_id: FK → VisaApplication
    created_by: FK → User
    rfe_type: Enum
    status: Enum
    rfe_received_date: Date
    rfe_deadline: Date
    response_submitted_date: Date
    resolution_date: Date
    rfe_subject: String
    description: Text
    response_summary: Text
    notes: Text
    created_at: DateTime
    updated_at: DateTime
```

### AuditLog
```python
AuditLog:
    id: UUID (PK)
    user_id: FK → User
    action: String
    entity_type: String
    entity_id: String
    changes: JSON
    ip_address: String
    created_at: DateTime (indexed)
```

### Notification
```python
Notification:
    id: UUID (PK)
    user_id: FK → User
    title: String
    message: Text
    type: Enum
    is_read: Boolean (indexed)
    read_at: DateTime
    created_at: DateTime
```

### UserSettings
```python
UserSettings:
    id: UUID (PK)
    user_id: FK → User (unique)
    email_notifications: Boolean
    theme: String
    language: String
    timezone: String
    created_at: DateTime
    updated_at: DateTime
```

### EmailLog
```python
EmailLog:
    id: UUID (PK)
    visa_application_id: FK → VisaApplication
    recipient_email: String
    subject: String
    body: Text
    sent_at: DateTime
    status: String
```

---

## Complete Relationships Summary

```
Contract
 ├─→ manager: User
 ├─→ users: List[User]
 └─→ departments: List[Department]

Department
 ├─→ contract: Contract
 ├─→ parent: Department
 └─→ users: List[User]

User
 ├─→ contract: Contract
 ├─→ department: Department
 ├─→ reports_to: User
 ├─→ direct_reports: List[User]
 ├─→ beneficiary: Beneficiary (one-to-one, nullable)
 ├─→ assigned_todos: List[Todo]
 └─→ created_todos: List[Todo]

Beneficiary
 ├─→ user: User (nullable)
 ├─→ case_groups: List[CaseGroup]  ⭐ NEW
 ├─→ visa_applications: List[VisaApplication]
 ├─→ dependents: List[Dependent]
 └─→ todos: List[Todo]  ⭐ NEW

CaseGroup  ⭐ NEW
 ├─→ beneficiary: Beneficiary
 ├─→ responsible_party: User
 ├─→ visa_applications: List[VisaApplication]
 └─→ todos: List[Todo]

VisaApplication
 ├─→ beneficiary: Beneficiary
 ├─→ case_group: CaseGroup  ⭐ NEW
 ├─→ law_firm: LawFirm
 ├─→ responsible_party: User
 ├─→ milestones: List[ApplicationMilestone]
 ├─→ rfes: List[RFETracking]
 └─→ todos: List[Todo]  ⭐ NEW

Todo  ⭐ NEW
 ├─→ assigned_to: User
 ├─→ created_by: User
 ├─→ visa_application: VisaApplication (nullable)
 ├─→ case_group: CaseGroup (nullable)
 └─→ beneficiary: Beneficiary (nullable)

Dependent
 └─→ beneficiary: Beneficiary
```

---

## Database Enums

```python
# User Roles
UserRole: ADMIN, HR, PM, MANAGER, BENEFICIARY

# Visa Application Status
VisaStatus: DRAFT, SUBMITTED, IN_PROGRESS, APPROVED, DENIED, EXPIRED, RENEWED

# Case Status
VisaCaseStatus: UPCOMING, ACTIVE, FINALIZED

# Priority (shared by VisaApplication, CaseGroup, Todo)
Priority: LOW, MEDIUM, HIGH, URGENT

# CaseGroup Status  ⭐ NEW
CaseGroupStatus: PLANNING, ACTIVE, COMPLETED, CANCELLED

# CaseGroup Type  ⭐ NEW
CaseType: H1B_EXTENSION, H1B_TRANSFER, GREEN_CARD_PATHWAY, TN_TO_H1B, 
          L1_TO_GREEN_CARD, EB2_NIW, PERM_BASED, FAMILY_BASED, OTHER

# Todo Status  ⭐ NEW
TodoStatus: TODO, IN_PROGRESS, BLOCKED, COMPLETED, CANCELLED

# Todo Priority  ⭐ NEW
TodoPriority: LOW, MEDIUM, HIGH, URGENT

# Relationship Types
RelationshipType: SPOUSE, CHILD, OTHER

# Milestone Types
MilestoneType: CASE_OPENED, DOCUMENTS_REQUESTED, FILED, RFE_RECEIVED, 
               APPROVED, DENIED, CLOSED

# RFE Types
RFEType: INITIAL_EVIDENCE, ADDITIONAL_EVIDENCE, INTENT_TO_DENY, 
         INTENT_TO_REVOKE, OTHER

# RFE Status
RFEStatus: RECEIVED, IN_PROGRESS, RESPONDED, RESOLVED

# Contract Status
ContractStatus: ACTIVE, ARCHIVED
```

---

## Example Data Scenarios

### Scenario 1: Complete Immigration Pathway

```
Beneficiary: Luis Fernandes
 ↓
CaseGroup: "EB2-NIW to Green Card Pathway"
 ├─→ VisaApplication 1: I-140 EB2-NIW (APPROVED, Nov 2024)
 │    └─→ Todo: "File I-485 within priority date" (COMPLETED)
 ├─→ VisaApplication 2: I-485 Adjustment of Status (IN_PROGRESS)
 │    ├─→ Todo: "Submit medical exam" (IN_PROGRESS)
 │    └─→ Todo: "Prepare employment letter" (TODO, URGENT)
 ├─→ VisaApplication 3: I-765 EAD (SUBMITTED)
 └─→ VisaApplication 4: I-131 Advance Parole (SUBMITTED)
      └─→ Todo: "Check case status online" (TODO)
```

### Scenario 2: H1B Extension

```
Beneficiary: Elena Rodriguez
 ↓
CaseGroup: "H1B Extension 2025"
 └─→ VisaApplication: I-129 H1B Extension (IN_PROGRESS)
      ├─→ Todo: "Request LCA from law firm" (COMPLETED on time)
      ├─→ Todo: "Gather support documents" (COMPLETED late, 2 days overdue)
      └─→ Todo: "Review petition draft" (TODO, due in 5 days)
```

### Scenario 3: Future Hire with No User Account

```
Beneficiary: Jacob Hjord Friedrichson (NO User account)
 - user_id: NULL
 ↓
CaseGroup: "New Hire H1B Petition"
 └─→ VisaApplication: I-129 H1B (DRAFT)
      └─→ Todo: "Collect credential evaluation" (assigned to HR)

# Later, when hired:
# 1. Create User account
# 2. Link beneficiary.user_id = new_user.id
# 3. Jacob can now log in and see his cases
```

---

## Key Design Decisions

### 1. Denormalized Todo Hierarchy
**Why?** Performance and query simplicity
- Storing beneficiary_id, case_group_id, and visa_application_id on Todo allows fast filtering
- No need for complex joins to find "all todos for a beneficiary"
- Auto-populated from visa_application → case_group → beneficiary

### 2. Computed Metrics Instead of Stored Status
**Why?** Always accurate, flexible reporting
- `is_overdue` calculated dynamically: `due_date < now AND status NOT IN (COMPLETED, CANCELLED)`
- Avoids background jobs to update overdue status
- Enables flexible dashboard queries (e.g., "todos overdue by >7 days")

### 3. CaseGroup as Optional Parent
**Why?** Flexibility
- Visa applications can exist without a case group (standalone cases)
- Case groups organize related applications for better management
- Not all visa cases are part of a multi-step pathway

### 4. Text Fields for Attorney Info
**Why?** Simplicity
- No need for separate Attorney model (fewer joins)
- Attorney assignment can change per case
- Avoids complex many-to-many relationships

---

## Change Log

**v3.0 (Nov 5, 2025):**
- ✅ Added CaseGroup model
- ✅ Added Todo model with hierarchical relationships
- ✅ Added computed metrics documentation
- ✅ Updated all relationships
- ✅ Added user creation permission rules

**v2.0 (Nov 4, 2025):**
- ✅ Beneficiary-User separation
- ✅ Simplified LawFirm model
- ✅ Removed sensitive personal data

**v1.0 (Nov 3, 2025):**
- Initial data model design

---

**Status:** ✅ All models implemented and deployed
