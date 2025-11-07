# AMA-IMPACT Data Model Documentation

**Version:** 2.0 - Beneficiary Separation Model  
**Date:** November 4, 2025  
**Status:** Design Approved - Ready for Implementation

---

## Core Philosophy

**Separation of Concerns:**
- **User** = System access, authentication, organizational structure
- **Beneficiary** = Foreign national with visa cases (may or may not have User account)
- **Dependent** = Family members of Beneficiaries
- **VisaApplication** = Individual visa cases/petitions

**Data Minimization:**
- Only store data necessary for visa case tracking
- No sensitive personal data (passport numbers, DOB, personal phone)
- Minimal attorney data (no bar numbers, licenses)

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
    role: Enum - ADMIN, PM, MANAGER, BENEFICIARY
    
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
    → audit_logs: List[AuditLog]
    → notifications: List[Notification]
    → settings: UserSettings
```

**Roles Explained:**
- **ADMIN** - Full system access, manage all data
- **PM** - Project Manager, sees everything under org structure + metrics/statistics
- **MANAGER** - Team lead, sees reports under hierarchy (no advanced metrics)
- **BENEFICIARY** - Foreign national employee, view own cases only

**Note:** US citizen employees (like David Cornelius) are PM/MANAGER without Beneficiary record.

---

## 2. Beneficiary Model

**Purpose:** Foreign nationals who have visa cases (employees, future hires, contractors)

```python
Beneficiary:
    # Identity
    id: UUID (PK)
    user_id: FK → User (nullable) - Links to User if they have system access
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
    
    # Employment Information (for visa petitions)
    job_title: String - For USCIS documents
    employment_start_date: Date - When started/will start
    
    # Status
    is_active: Boolean
    notes: Text
    
    # Timestamps
    created_at: DateTime
    updated_at: DateTime
    
    # Relationships
    → user: User (nullable - future hires don't have accounts yet)
    → visa_applications: List[VisaApplication]
    → dependents: List[Dependent]
```

**Use Cases:**
- **Current Employee:** Luis (has User + Beneficiary)
- **Future Hire:** Jacob (Beneficiary only, no User yet)
- **Contractor:** May have User + Beneficiary if needs system access

---

## 3. Dependent Model

**Purpose:** Track family members (spouses, children) of Beneficiaries

```python
Dependent:
    # Identity
    id: UUID (PK)
    beneficiary_id: FK → Beneficiary - Primary applicant
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

**Example:** Luis's spouse Maria (H4 visa holder)

---

## 4. VisaApplication Model

**Purpose:** Individual visa petitions/applications with comprehensive tracking

```python
VisaApplication:
    # Identity
    id: UUID (PK)
    beneficiary_id: FK → Beneficiary - Who the case is for
    visa_type_id: FK → VisaType
    created_by: FK → User - Who created the record
    
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
    next_action_date: Date - When something needs to happen
    
    # USCIS Tracking
    receipt_number: String - WAC2190012345
    company_case_id: String - Internal tracking
    
    # Law Firm & Attorney (simplified - no separate Attorney model)
    law_firm_id: FK → LawFirm
    attorney_name: String - "Jane Attorney"
    attorney_email: String
    attorney_phone: String
    responsible_party_id: FK → User - AMA staff managing case
    
    # RFE (Request for Evidence) Tracking
    rfe_received: Boolean
    rfe_received_date: Date
    rfe_response_date: Date
    rfe_notes: Text
    
    # Cost Tracking (for analytics)
    filing_fee: String - "$700"
    attorney_fee: String - "$8,500"
    premium_processing: Boolean
    premium_processing_fee: String - "$2,500"
    total_cost: String - "$11,700"
    
    # Status & Notes
    is_active: Boolean
    notes: Text
    
    # Timestamps
    created_at: DateTime
    updated_at: DateTime
    
    # Relationships
    → beneficiary: Beneficiary
    → visa_type_info: VisaType
    → law_firm: LawFirm
    → responsible_party: User
    → creator: User
    → milestones: List[ApplicationMilestone]
    → rfes: List[RFETracking]
    → email_logs: List[EmailLog]
```

**Note:** Attorney info stored as text fields on application (not FK) for flexibility.

---

## 5. LawFirm Model (Simplified)

**Purpose:** Track law firms handling visa cases

```python
LawFirm:
    # Identity
    id: UUID (PK)
    name: String - "Fragomen, Del Rey, Bernsen & Loewy"
    
    # Primary Contact
    contact_person: String - Main contact at firm
    email: String
    phone: String
    
    # Address
    address: Text - Full address
    website: String
    
    # Status & Notes
    is_preferred_vendor: Boolean
    performance_rating: String - "Excellent", "Good", etc.
    is_active: Boolean
    notes: Text
    
    # Timestamps
    created_at: DateTime
    updated_at: DateTime
    
    # Relationships
    → applications: List[VisaApplication]
```

**Note:** 
- No hourly rates (not needed for tracking)
- Attorney details stored per application (not separate model)
- Focus on firm-level relationship and performance

---

## 6. ApplicationMilestone Model

**Purpose:** Timeline tracking for visa cases

```python
ApplicationMilestone:
    # Identity
    id: UUID (PK)
    visa_application_id: FK → VisaApplication
    created_by: FK → User
    
    # Milestone Details
    milestone_type: Enum - CASE_OPENED, FILED, RFE_RECEIVED, APPROVED, DENIED, etc.
    milestone_date: Date
    title: String (optional) - Custom title if type=OTHER
    description: Text
    
    # Timestamps
    created_at: DateTime
    updated_at: DateTime
    
    # Relationships
    → visa_application: VisaApplication
    → creator: User
```

**Example:** "I-140 EB2-NIW petition approved on November 1, 2024"

---

## 7. RFETracking Model

**Purpose:** Detailed RFE (Request for Evidence) management

```python
RFETracking:
    # Identity
    id: UUID (PK)
    visa_application_id: FK → VisaApplication
    created_by: FK → User
    
    # RFE Classification
    rfe_type: Enum - INITIAL_EVIDENCE, ADDITIONAL_EVIDENCE, INTENT_TO_DENY, etc.
    status: Enum - RECEIVED, IN_PROGRESS, RESPONDED, RESOLVED
    
    # Important Dates
    rfe_received_date: Date
    rfe_deadline: Date - Critical!
    response_submitted_date: Date
    resolution_date: Date
    
    # Details
    rfe_subject: String - Brief title
    description: Text - What was requested
    response_summary: Text - What was submitted
    notes: Text - Internal notes
    
    # Timestamps
    created_at: DateTime
    updated_at: DateTime
    
    # Relationships
    → visa_application: VisaApplication
    → creator: User
```

---

## 8. Contract Model

**Purpose:** Projects/contracts that employees work on

```python
Contract:
    # Identity
    id: UUID (PK)
    name: String - "AERONAUTICS ... IF I COULD ONLY REMEMBER NOW "
    code: String (unique) - "ASSESS"
    
    # Dates
    start_date: Date
    end_date: Date
    status: Enum - ACTIVE, ARCHIVED
    
    # Management
    manager_user_id: FK → User - Project Manager
    
    # Client Information
    client_name: String - "NASA"
    client_contact_name: String - "Client POC"
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

## 9. Department Model

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

## Key Relationships Summary

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
 ├─→ beneficiary: Beneficiary (nullable, one-to-one)
 └─→ created_visa_applications: List[VisaApplication]

Beneficiary
 ├─→ user: User (nullable)
 ├─→ visa_applications: List[VisaApplication]
 └─→ dependents: List[Dependent]

VisaApplication
 ├─→ beneficiary: Beneficiary
 ├─→ law_firm: LawFirm
 ├─→ responsible_party: User
 ├─→ milestones: List[ApplicationMilestone]
 └─→ rfes: List[RFETracking]

Dependent
 └─→ beneficiary: Beneficiary
```

---

## Example Scenarios

### Scenario 1: US Citizen PM (David Cornelius)
```
User (david.cornelius@ama-inc.com)
 - role: PM
 - contract: ASSESS
 - department: TSM
 - beneficiary: NULL ← No visa cases
```

### Scenario 2: Foreign National Employee (Luis)
```
User (luis.fernandes@ama-inc.com)
 - role: BENEFICIARY
 - contract: ASSESS
 - department: TNA
 ↓
Beneficiary
 - user_id: luis's User ID
 - current_visa_type: H1B
 - visa_applications: [EB2-NIW I-140 (approved)]
 ↓
Dependent (Maria, spouse)
 - beneficiary_id: Luis's Beneficiary ID
 - visa_type: H4
```

### Scenario 3: Future Hire (Jacob)
```
Beneficiary ONLY (no User account yet)
 - user_id: NULL
 - first_name: Jacob
 - last_name: Hjord Friedrichson
 - country_of_citizenship: Sweden
 - visa_applications: [H1B petition in progress]

Later, when hired:
 → Create User account
 → Link beneficiary.user_id to new User
```

---

## Data Removed (Privacy/Minimization)

**Removed from all models:**
- ❌ `passport_number` - Too sensitive
- ❌ `date_of_birth` - Not needed for visa tracking
- ❌ `phone` (personal) - Not needed for case management
- ❌ Attorney bar numbers, licenses - Not needed
- ❌ Law firm hourly rates - Not tracking billing details

**What we keep:**
- ✅ `passport_expiration` - For renewal warnings
- ✅ `passport_country` - For dual citizens
- ✅ `email` - For communication (on User only)
- ✅ Attorney contact per case - For case coordination
- ✅ Visa costs - For analytics

---

## Database Enums

```python
# User Roles
UserRole: ADMIN, PM, MANAGER, BENEFICIARY

# Visa Application Status
VisaStatus: DRAFT, SUBMITTED, IN_PROGRESS, APPROVED, DENIED, EXPIRED, RENEWED

# Case Status
VisaCaseStatus: UPCOMING, ACTIVE, FINALIZED

# Priority
VisaPriority: LOW, MEDIUM, HIGH, CRITICAL

# Visa Types (examples)
VisaTypeEnum: H1B, L1, O1, TN, EB1A, EB1B, EB2, EB2NIW, GREEN_CARD, etc.

# Relationship Types
RelationshipType: SPOUSE, CHILD, OTHER

# Milestone Types
MilestoneType: CASE_OPENED, DOCUMENTS_REQUESTED, FILED, RFE_RECEIVED, APPROVED, DENIED, etc.

# RFE Types
RFEType: INITIAL_EVIDENCE, ADDITIONAL_EVIDENCE, INTENT_TO_DENY, INTENT_TO_REVOKE, OTHER

# RFE Status
RFEStatus: RECEIVED, IN_PROGRESS, RESPONDED, RESOLVED

# Contract Status
ContractStatus: ACTIVE, ARCHIVED

# Law Firm Specialty (removed - not needed)
```

---

## Next Steps

1. ✅ Implement Beneficiary model
2. ✅ Update User model (remove immigration fields)
3. ✅ Update Dependent model (beneficiary_id)
4. ✅ Simplify LawFirm (remove Attorney model)
5. ✅ Update VisaApplication (beneficiary_id, attorney text fields)
6. ✅ Update all schemas and APIs
7. ✅ Update ASSESS fixture with new structure
8. ✅ Reset database and test

---

**Document Status:** Ready for implementation approval ✅
