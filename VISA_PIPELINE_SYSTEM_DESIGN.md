# Visa Pipeline System Design Document

**Created:** November 11, 2025  
**Purpose:** Design visa-type-specific milestone pipelines to replace hardcoded frontend progress logic  
**Status:** Planning Phase - Frontend improvements needed first

---

## Table of Contents
1. [Current State Analysis](#current-state-analysis)
2. [Problems with Current System](#problems-with-current-system)
3. [Proposed Solution](#proposed-solution)
4. [Implementation Plan](#implementation-plan)
5. [Prerequisites - Frontend Changes](#prerequisites---frontend-changes)
6. [Next Steps](#next-steps)

---

## Current State Analysis

### Backend Milestone System

**Location:** `backend/app/models/milestone.py`

#### ApplicationMilestone Model
```python
class ApplicationMilestone(Base):
    """Milestone tracking for visa applications."""
    __tablename__ = "application_milestones"
    
    id = Column(String(36), primary_key=True)
    visa_application_id = Column(String(36), ForeignKey("visa_applications.id"), nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    milestone_type = Column(Enum(MilestoneType), nullable=False)
    milestone_date = Column(Date, nullable=False)
    title = Column(String(255), nullable=True)  # Custom title if OTHER
    description = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

#### MilestoneType Enum
**Currently defined milestone types** (generic, not visa-specific):
```python
class MilestoneType(str, enum.Enum):
    CASE_OPENED = "case_opened"
    DOCUMENTS_REQUESTED = "documents_requested"
    DOCUMENTS_SUBMITTED = "documents_submitted"
    FILED_WITH_USCIS = "filed_with_uscis"
    RFE_RECEIVED = "rfe_received"
    RFE_RESPONDED = "rfe_responded"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEW_COMPLETED = "interview_completed"
    APPROVED = "approved"
    DENIED = "denied"
    CASE_CLOSED = "case_closed"
    OTHER = "other"
```

**Issues:**
- Generic milestones don't reflect visa-specific processes
- `FILED_WITH_USCIS` is meaningless for H1B (employer files, not USCIS)
- `INTERVIEW_SCHEDULED` irrelevant for most employment-based visas
- No concept of visa-type-specific workflows

### Backend Timeline API

**Location:** `backend/app/api/v1/case_groups.py` (lines 704-875)

#### Timeline Endpoint
```python
@router.get("/{case_group_id}/timeline", response_model=TimelineResponse)
def get_case_group_timeline(case_group_id: str, ...):
    """
    Get unified timeline for a case group.
    Combines:
    - Audit logs (case creation, updates, approvals)
    - Milestones from all visa applications
    - Completed todos
    """
    # ... filters milestones from visa_applications ...
    milestones = (
        db.query(ApplicationMilestone)
        .filter(ApplicationMilestone.visa_application_id.in_(visa_app_ids))
        .all()
    )
    
    for milestone in milestones:
        events.append(TimelineEvent(
            event_type=TimelineEventType.MILESTONE,  # Returns "milestone" string
            milestone_type=milestone.milestone_type.value,  # Returns lowercase: "case_opened"
            ...
        ))
```

**Returns:** `TimelineResponse` with all events sorted by timestamp

### Frontend Progress Calculation

**Location:** `frontend/app/cases/[id]/page.tsx` (lines 310-370)

#### Hardcoded Pipeline Logic
```typescript
const calculateProgress = () => {
  // HARDCODED pipeline - assumes USCIS filing process for ALL visa types
  const milestoneOrder = [
    { type: 'case_opened', label: 'Case Opened', weight: 12 },
    { type: 'documents_requested', label: 'Docs Requested', weight: 25 },
    { type: 'documents_submitted', label: 'Docs Submitted', weight: 40 },
    { type: 'filed_with_uscis', label: 'Filed USCIS', weight: 60 },  // ❌ WRONG for H1B/TN
    { type: 'rfe_received', label: 'RFE Received', weight: 65 },
    { type: 'rfe_responded', label: 'RFE Responded', weight: 75 },
    { type: 'interview_scheduled', label: 'Interview Scheduled', weight: 80 },
    { type: 'interview_completed', label: 'Interview Done', weight: 90 },
    { type: 'approved', label: 'Approved', weight: 100 },
    { type: 'denied', label: 'Denied', weight: 100 },
    { type: 'case_closed', label: 'Case Closed', weight: 100 },
  ]
  
  // Filters timeline events for milestone_type matches
  const milestoneEvents = timeline.events
    .filter((e: any) => e.event_type === 'MILESTONE' || e.event_type === 'milestone')
    .map((e: any) => e.milestone_type)
  
  // Calculates percentage based on highest milestone reached
  // ...
}
```

**Problems:**
1. **Visa-type agnostic** - Shows same pipeline for H1B, EB-2 NIW, TN, Green Card
2. **Misleading labels** - "Filed USCIS" for cases that never go through USCIS
3. **Incorrect progress** - H1B Extension showing 60% when it's actually just awaiting employer approval
4. **No "what's next"** - Users don't know what milestone comes after current stage

### Visa Types in System

**Location:** `backend/app/models/visa.py`

```python
class VisaTypeEnum(str, enum.Enum):
    H1B = "H1B"              # Employer-sponsored, no USCIS filing by individual
    L1 = "L1"                # Intracompany transfer
    O1 = "O1"                # Extraordinary ability
    TN = "TN"                # NAFTA professional (border/consulate, not USCIS)
    EB1A = "EB1A"            # EB-1 Extraordinary Ability
    EB1B = "EB1B"            # EB-1 Outstanding Researcher
    EB2 = "EB2"              # EB-2 Advanced Degree
    EB2NIW = "EB2NIW"        # EB-2 National Interest Waiver
    PERM = "PERM"            # Labor Certification
    OPT = "OPT"              # Optional Practical Training
    EAD = "EAD"              # Employment Authorization Document
    GREEN_CARD = "GREEN_CARD"  # Lawful Permanent Resident
```

**Each visa type has a DIFFERENT process:**
- **H1B:** Employer files → LCA approval → H1B approval (no USCIS interaction for employee)
- **TN:** Document prep → Border appointment or consulate → Approval (no USCIS filing)
- **EB-2 NIW:** I-140 filing → RFE (optional) → Approval → I-485 filing → Interview → Green Card
- **Green Card (AOS):** I-485 filing → Biometrics → Interview → Approval
- **PERM:** PWD → PERM filing → Approval → I-140 → I-485 (multi-stage)

### Case Group Types

**Location:** `backend/app/models/case_group.py`

```python
class CaseType(str, enum.Enum):
    # Green Card Cases
    EB1 = "EB1"
    EB2 = "EB2"
    EB3 = "EB3"
    EB2_NIW = "EB2_NIW"
    
    # PERM
    PERM = "PERM"
    
    # H1B Cases
    H1B_INITIAL = "H1B_INITIAL"
    H1B_EXTENSION = "H1B_EXTENSION"
    H1B_TRANSFER = "H1B_TRANSFER"
    H1B_AMENDMENT = "H1B_AMENDMENT"
    
    # Other Nonimmigrant
    L1_INITIAL = "L1_INITIAL"
    L1_EXTENSION = "L1_EXTENSION"
    O1 = "O1"
    TN = "TN"
    
    # Student/Training
    F1_OPT = "F1_OPT"
    F1_STEM_OPT = "F1_STEM_OPT"
    
    # Family
    FAMILY_BASED = "FAMILY_BASED"
    
    # Other
    SINGLE = "SINGLE"
    OTHER = "OTHER"
```

**Note:** CaseGroup has `case_type` but milestones are stored at VisaApplication level with generic types

### Fixture Data Examples

**Location:** `backend/scripts/fixtures/contracts/seed_assess_visa_apps.py`

Example milestones created for Gerrit-Daniel Stich (EB-2 NIW completed):
```python
milestones = [
    (MilestoneType.CASE_OPENED, date(2021, 1, 15), "Initial consultation completed"),
    (MilestoneType.DOCUMENTS_REQUESTED, date(2021, 1, 20), "Document checklist provided"),
    (MilestoneType.DOCUMENTS_SUBMITTED, date(2021, 2, 10), "All documents collected"),
    (MilestoneType.FILED_WITH_USCIS, date(2021, 2, 15), "I-140 petition filed with USCIS"),
    (MilestoneType.APPROVED, date(2021, 10, 20), "I-140 approved"),
    (MilestoneType.CASE_CLOSED, date(2021, 11, 20), "Green card received"),
]
```

**Observation:** Even completed cases use generic milestones, but descriptions clarify actual events

---

## Problems with Current System

### 1. Visa-Type Ignorance
- Frontend shows same pipeline for all visa types
- Jacob's H1B case shows "Filed USCIS" at 60% progress (❌ employer files, not USCIS)
- TN visa cases would show interview milestones (❌ no interview for TN)

### 2. Misleading Progress Percentages
- Luis's EB-2 NIW case group shows "0% Complete - Not Started" despite being approved (frontend bug, but also design issue)
- No way to know if 60% means "submitted to USCIS" or "waiting for employer approval"

### 3. No "What's Next" Guidance
- Users don't see upcoming milestones
- No indication of optional vs required stages (e.g., RFE is optional in most cases)

### 4. Inflexible Milestone Types
- Generic `FILED_WITH_USCIS` doesn't distinguish between:
  - I-140 filing (EB-2)
  - I-485 filing (AOS)
  - H1B LCA submission (H1B)
  - PERM filing (PERM process)

### 5. Process Variation Not Captured
- Different companies may track additional steps
- Some contracts might want prevailing wage determination milestone
- No way to customize pipelines per contract/organization

---

## Proposed Solution

### CRITICAL DESIGN CLARIFICATION ⚠️

**Milestones are tied to VISA APPLICATIONS, NOT Case Groups!**

#### The Correct Model:
1. **Case Group** = Container for related visa applications
   - Example: "Luis - EB2-NIW to Green Card" case group
   
2. **Case Group** contains multiple **Visa Applications**:
   - PERM Labor Certification
   - I-140 Immigrant Petition
   - I-485 Adjustment of Status
   - EAD (Employment Authorization)
   
3. **Each Visa Application** has its own pipeline based on its visa type:
   - PERM → PERM-specific pipeline (PWD → PERM Filing → Approval)
   - I-140 → I-140 pipeline (I-140 Filing → RFE → Approval)
   - I-485 → I-485 pipeline (Filing → Biometrics → Interview → Approval)
   
4. **Case Group Progress** = Aggregate of all visa application progresses

#### Workflow:
1. **HR/Manager creates Case Group** (e.g., "Luis - EB2-NIW Green Card")
2. **Add Visa Applications to Case Group**:
   - Add "PERM" visa application → System loads PERM pipeline
   - Add "I-140" visa application → System loads I-140 pipeline
   - Add "I-485" visa application → System loads I-485 pipeline
3. **Activity Timeline shows milestones for each visa**:
   - "PERM filed with DOL" (PERM milestone)
   - "I-140 filed with USCIS" (I-140 milestone)
   - "Biometrics completed" (I-485 milestone)
4. **Case Group Progress** = Weighted average or "furthest stage reached" across all visas

### Design Principles

1. **Visa-Application-Specific Pipelines**: Each visa application has its own milestone sequence
2. **Backend-Driven**: Pipeline definitions live in backend, frontend just displays
3. **Flexible & Configurable**: Pipelines can be customized per contract (future)
4. **Progressive Enhancement**: Keep existing milestones working, add pipeline layer
5. **Percentage Based on Stages**: Reaching stage X = X% complete (even if intermediate stages skipped)
6. **Aggregate Progress**: Case group progress calculated from all visa applications

### Solution Architecture

#### Option 1: Pipeline Configuration Model (RECOMMENDED) ✅

Create a new database model to define visa-specific pipelines:

```python
# backend/app/models/pipeline.py

class VisaPipelineStage(Base):
    """Defines one stage in a visa type's pipeline."""
    __tablename__ = "visa_pipeline_stages"
    
    id = Column(String(36), primary_key=True)
    visa_type = Column(Enum(VisaTypeEnum), nullable=False)  # H1B, EB2NIW, etc.
    stage_order = Column(Integer, nullable=False)  # 1, 2, 3...
    milestone_type = Column(Enum(MilestoneType), nullable=False)
    stage_label = Column(String(100), nullable=False)  # Display name
    description = Column(Text, nullable=True)  # Help text for stage
    is_required = Column(Boolean, default=True)  # Required vs optional (e.g., RFE)
    is_terminal = Column(Boolean, default=False)  # Ends pipeline (approved/denied)
    weight_percentage = Column(Integer, nullable=False)  # 0-100 for progress %
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Unique constraint: one stage order per visa type
    __table_args__ = (
        UniqueConstraint('visa_type', 'stage_order', name='uq_visa_pipeline_stage_order'),
        UniqueConstraint('visa_type', 'milestone_type', name='uq_visa_pipeline_milestone'),
    )
```

**Benefits:**
- ✅ Database-backed, easy to query
- ✅ Can add custom pipelines via admin UI (future)
- ✅ Contract-specific overrides possible (future)
- ✅ Audit trail via created_at/updated_at

**Drawbacks:**
- Requires migration (or setup_dev_environment.py in alpha)
- More complex than config file

#### Option 2: Python Configuration File (Faster Start)

Create `backend/app/config/visa_pipelines.py`:

```python
from app.models.visa import VisaTypeEnum
from app.models.milestone import MilestoneType

VISA_PIPELINES = {
    VisaTypeEnum.H1B: {
        "stages": [
            {
                "milestone_type": MilestoneType.CASE_OPENED,
                "label": "Case Opened",
                "description": "Initial consultation and case assessment",
                "weight": 10,
                "required": True,
            },
            {
                "milestone_type": MilestoneType.DOCUMENTS_REQUESTED,
                "label": "Documents Requested",
                "description": "Document checklist provided to beneficiary",
                "weight": 30,
                "required": True,
            },
            {
                "milestone_type": MilestoneType.DOCUMENTS_SUBMITTED,
                "label": "Documents Submitted",
                "description": "All documents collected and reviewed",
                "weight": 50,
                "required": True,
            },
            {
                "milestone_type": "employer_filed",  # ❌ Would need new MilestoneType
                "label": "Employer Filed H1B",
                "description": "Employer submitted H1B petition",
                "weight": 75,
                "required": True,
            },
            {
                "milestone_type": MilestoneType.APPROVED,
                "label": "H1B Approved",
                "description": "USCIS approved H1B petition",
                "weight": 100,
                "required": True,
                "terminal": True,
            },
        ]
    },
    VisaTypeEnum.EB2NIW: {
        "stages": [
            # ... EB-2 NIW specific pipeline ...
        ]
    },
    # ... other visa types ...
}
```

**Benefits:**
- ✅ Faster to implement
- ✅ Easy to version control
- ✅ No database changes needed

**Drawbacks:**
- ❌ Can't customize per contract without code changes
- ❌ Still need to add new MilestoneTypes for visa-specific events
- ❌ No audit trail for pipeline changes

---

## Recommended Implementation: Hybrid Approach

**Phase 1 (Immediate - Config File):**
1. Create `visa_pipelines.py` with predefined pipelines
2. Add new backend endpoint: `GET /api/v1/visa-pipelines/{visa_type}`
3. Frontend fetches pipeline for case group's primary visa type
4. Display pipeline stages instead of hardcoded list

**Phase 2 (Future - Database Model):**
1. Create `VisaPipelineStage` model
2. Seed default pipelines from config file
3. Admin UI to customize pipelines
4. Contract-specific overrides table

---

## Implementation Plan

### Step 1: Expand MilestoneType Enum

Add visa-specific milestone types to `backend/app/models/milestone.py`:

```python
class MilestoneType(str, enum.Enum):
    # Generic
    CASE_OPENED = "case_opened"
    DOCUMENTS_REQUESTED = "documents_requested"
    DOCUMENTS_SUBMITTED = "documents_submitted"
    APPROVED = "approved"
    DENIED = "denied"
    CASE_CLOSED = "case_closed"
    
    # H1B Specific
    LCA_FILED = "lca_filed"
    LCA_APPROVED = "lca_approved"
    H1B_FILED = "h1b_filed"
    H1B_APPROVED = "h1b_approved"
    
    # EB-2/EB-3 Specific
    I140_FILED = "i140_filed"
    I140_APPROVED = "i140_approved"
    I485_FILED = "i485_filed"
    BIOMETRICS_COMPLETED = "biometrics_completed"
    
    # PERM Specific
    PWD_FILED = "pwd_filed"
    PWD_APPROVED = "pwd_approved"
    PERM_FILED = "perm_filed"
    PERM_APPROVED = "perm_approved"
    
    # General USCIS
    FILED_WITH_USCIS = "filed_with_uscis"  # Keep for backwards compatibility
    RFE_RECEIVED = "rfe_received"
    RFE_RESPONDED = "rfe_responded"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEW_COMPLETED = "interview_completed"
    
    # TN Specific
    TN_BORDER_APPOINTMENT = "tn_border_appointment"
    TN_APPROVED = "tn_approved"
    
    # Other
    OTHER = "other"
```

### Step 2: Create Pipeline Configuration

**File:** `backend/app/config/visa_pipelines.py`

Define pipelines for each visa type:

```python
from typing import List, Dict, Any
from app.models.visa import VisaTypeEnum
from app.models.milestone import MilestoneType

def get_pipeline_for_visa_type(visa_type: VisaTypeEnum) -> Dict[str, Any]:
    """Get the milestone pipeline for a specific visa type."""
    return VISA_PIPELINES.get(visa_type, DEFAULT_PIPELINE)

VISA_PIPELINES = {
    VisaTypeEnum.H1B: {
        "name": "H-1B Specialty Occupation",
        "description": "Employer-sponsored temporary work visa",
        "stages": [
            {
                "order": 1,
                "milestone_type": MilestoneType.CASE_OPENED,
                "label": "Case Opened",
                "description": "Initial consultation and eligibility assessment",
                "weight": 10,
                "required": True,
            },
            {
                "order": 2,
                "milestone_type": MilestoneType.DOCUMENTS_REQUESTED,
                "label": "Documents Requested",
                "description": "Document checklist sent to beneficiary",
                "weight": 25,
                "required": True,
            },
            {
                "order": 3,
                "milestone_type": MilestoneType.DOCUMENTS_SUBMITTED,
                "label": "Documents Submitted",
                "description": "All required documents collected",
                "weight": 40,
                "required": True,
            },
            {
                "order": 4,
                "milestone_type": MilestoneType.LCA_FILED,
                "label": "LCA Filed",
                "description": "Labor Condition Application submitted to DOL",
                "weight": 55,
                "required": True,
            },
            {
                "order": 5,
                "milestone_type": MilestoneType.LCA_APPROVED,
                "label": "LCA Approved",
                "description": "DOL approved Labor Condition Application",
                "weight": 70,
                "required": True,
            },
            {
                "order": 6,
                "milestone_type": MilestoneType.H1B_FILED,
                "label": "H-1B Petition Filed",
                "description": "Employer filed H-1B petition with USCIS",
                "weight": 85,
                "required": True,
            },
            {
                "order": 7,
                "milestone_type": MilestoneType.APPROVED,
                "label": "H-1B Approved",
                "description": "USCIS approved H-1B petition",
                "weight": 100,
                "required": True,
                "terminal": True,
            },
        ]
    },
    
    VisaTypeEnum.EB2NIW: {
        "name": "EB-2 National Interest Waiver",
        "description": "Employment-based second preference with NIW",
        "stages": [
            {"order": 1, "milestone_type": MilestoneType.CASE_OPENED, "label": "Case Opened", "weight": 8, "required": True},
            {"order": 2, "milestone_type": MilestoneType.DOCUMENTS_REQUESTED, "label": "Docs Requested", "weight": 20, "required": True},
            {"order": 3, "milestone_type": MilestoneType.DOCUMENTS_SUBMITTED, "label": "Docs Submitted", "weight": 35, "required": True},
            {"order": 4, "milestone_type": MilestoneType.I140_FILED, "label": "I-140 Filed", "weight": 60, "required": True},
            {"order": 5, "milestone_type": MilestoneType.RFE_RECEIVED, "label": "RFE Received", "weight": 65, "required": False},
            {"order": 6, "milestone_type": MilestoneType.RFE_RESPONDED, "label": "RFE Response Submitted", "weight": 75, "required": False},
            {"order": 7, "milestone_type": MilestoneType.I140_APPROVED, "label": "I-140 Approved", "weight": 90, "required": True},
            {"order": 8, "milestone_type": MilestoneType.APPROVED, "label": "Case Approved", "weight": 100, "required": True, "terminal": True},
        ]
    },
    
    VisaTypeEnum.TN: {
        "name": "TN NAFTA Professional",
        "description": "Canadian/Mexican professional work authorization",
        "stages": [
            {"order": 1, "milestone_type": MilestoneType.CASE_OPENED, "label": "Case Opened", "weight": 15, "required": True},
            {"order": 2, "milestone_type": MilestoneType.DOCUMENTS_REQUESTED, "label": "Docs Requested", "weight": 35, "required": True},
            {"order": 3, "milestone_type": MilestoneType.DOCUMENTS_SUBMITTED, "label": "Docs Submitted", "weight": 60, "required": True},
            {"order": 4, "milestone_type": MilestoneType.TN_BORDER_APPOINTMENT, "label": "Border Appointment", "weight": 85, "required": True},
            {"order": 5, "milestone_type": MilestoneType.APPROVED, "label": "TN Approved", "weight": 100, "required": True, "terminal": True},
        ]
    },
    
    # ... Add pipelines for other visa types: L1, O1, EB2, EB3, PERM, GREEN_CARD, etc.
}

# Default pipeline for visa types without specific definition
DEFAULT_PIPELINE = {
    "name": "Standard Immigration Process",
    "description": "Generic immigration case workflow",
    "stages": [
        {"order": 1, "milestone_type": MilestoneType.CASE_OPENED, "label": "Case Opened", "weight": 12, "required": True},
        {"order": 2, "milestone_type": MilestoneType.DOCUMENTS_REQUESTED, "label": "Docs Requested", "weight": 25, "required": True},
        {"order": 3, "milestone_type": MilestoneType.DOCUMENTS_SUBMITTED, "label": "Docs Submitted", "weight": 40, "required": True},
        {"order": 4, "milestone_type": MilestoneType.FILED_WITH_USCIS, "label": "Filed with USCIS", "weight": 60, "required": True},
        {"order": 5, "milestone_type": MilestoneType.APPROVED, "label": "Approved", "weight": 100, "required": True, "terminal": True},
    ]
}
```

### Step 3: Create Backend API Endpoint

**File:** `backend/app/api/v1/visa_pipelines.py` (new file)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.visa import VisaTypeEnum
from app.config.visa_pipelines import get_pipeline_for_visa_type, VISA_PIPELINES

router = APIRouter()

@router.get("/pipelines/{visa_type}")
def get_visa_pipeline(
    visa_type: VisaTypeEnum,
    current_user: User = Depends(get_current_active_user),
):
    """
    Get the milestone pipeline definition for a specific visa type.
    
    Returns the ordered list of stages with:
    - milestone_type: The MilestoneType enum value
    - label: Display name for the stage
    - description: Help text explaining the stage
    - weight: Progress percentage (0-100) when this stage is reached
    - required: Whether this stage is mandatory
    - terminal: Whether this stage ends the pipeline
    """
    pipeline = get_pipeline_for_visa_type(visa_type)
    
    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No pipeline defined for visa type: {visa_type}"
        )
    
    return {
        "visa_type": visa_type,
        **pipeline
    }

@router.get("/pipelines")
def list_visa_pipelines(
    current_user: User = Depends(get_current_active_user),
):
    """
    List all available visa pipeline definitions.
    
    Useful for admin interfaces or pipeline configuration screens.
    """
    return {
        "pipelines": [
            {
                "visa_type": visa_type,
                "name": config["name"],
                "description": config["description"],
                "total_stages": len(config["stages"])
            }
            for visa_type, config in VISA_PIPELINES.items()
        ]
    }
```

**Register in:** `backend/app/main.py`

```python
from app.api.v1 import visa_pipelines

app.include_router(visa_pipelines.router, prefix="/api/v1/visa-pipelines", tags=["visa-pipelines"])
```

### Step 4: Add Progress Calculation Endpoint

**File:** `backend/app/api/v1/case_groups.py` (add new endpoint)

```python
from app.config.visa_pipelines import get_pipeline_for_visa_type

@router.get("/{case_group_id}/progress")
def get_case_group_progress(
    *,
    db: Session = Depends(get_db),
    case_group_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """
    Calculate case group progress based on ALL visa applications in the group.
    
    Each visa application has its own pipeline based on visa type.
    Case group progress is the aggregate of all visa application progresses.
    
    Returns:
    - percentage: Overall case group progress (weighted average of all visas)
    - visa_applications: Array of visa apps with individual progress
    - current_stage: Description of overall case status
    """
    # Get case group and check permissions
    case_group = db.query(CaseGroup).filter(CaseGroup.id == case_group_id).first()
    if not case_group:
        raise HTTPException(status_code=404, detail="Case group not found")
    
    # ... permission checks ...
    
    if not case_group.applications:
        return {
            "percentage": 0,
            "current_stage": "No visa applications",
            "visa_applications": []
        }
    
    visa_progress_list = []
    total_weight = 0
    
    # Calculate progress for EACH visa application
    for visa_app in case_group.applications:
        # Get pipeline for THIS visa type
        pipeline_config = get_pipeline_for_visa_type(visa_app.visa_type)
        
        # Get milestones for THIS visa application only
        milestones = (
            db.query(ApplicationMilestone)
            .filter(ApplicationMilestone.visa_application_id == visa_app.id)
            .all()
        )
        
        completed_milestone_types = {m.milestone_type for m in milestones}
        
        # Calculate progress for this visa
        max_weight = 0
        current_stage = "Not Started"
        pipeline_with_status = []
        
        for stage in pipeline_config["stages"]:
            is_completed = stage["milestone_type"] in completed_milestone_types
            
            if is_completed:
                max_weight = stage["weight"]
                current_stage = stage["label"]
            
            # Find actual milestone for completion date
            milestone_date = None
            if is_completed:
                for m in milestones:
                    if m.milestone_type == stage["milestone_type"]:
                        milestone_date = m.milestone_date.isoformat()
                        break
            
            pipeline_with_status.append({
                **stage,
                "completed": is_completed,
                "completion_date": milestone_date,
            })
        
        visa_progress_list.append({
            "visa_application_id": visa_app.id,
            "visa_type": visa_app.visa_type,
            "petition_type": visa_app.petition_type,
            "status": visa_app.visa_case_status,
            "percentage": max_weight,
            "current_stage": current_stage,
            "pipeline": pipeline_with_status,
            "pipeline_name": pipeline_config["name"],
        })
        
        total_weight += max_weight
    
    # Overall case group progress = average of all visa apps
    overall_percentage = total_weight // len(case_group.applications)
    
    # Determine overall current stage
    if overall_percentage == 100:
        overall_stage = "Complete"
    elif overall_percentage >= 75:
        overall_stage = "Nearing Completion"
    elif overall_percentage >= 50:
        overall_stage = "In Progress"
    elif overall_percentage >= 25:
        overall_stage = "Early Stage"
    else:
        overall_stage = "Getting Started"
    
    return {
        "percentage": overall_percentage,
        "current_stage": overall_stage,
        "visa_applications": visa_progress_list,
    }
```

### Step 5: Update Frontend to Use New API

**File:** `frontend/app/cases/[id]/page.tsx`

Replace `calculateProgress()` function:

```typescript
// REMOVE hardcoded calculateProgress() function

// ADD API call to fetch progress
const [progress, setProgress] = useState<any>(null)

useEffect(() => {
  if (caseGroup?.id) {
    fetch(`/api/v1/case-groups/${caseGroup.id}/progress`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => setProgress(data))
      .catch(err => console.error('Failed to fetch progress:', err))
  }
}, [caseGroup?.id])

// Update Case Progress card to use API response
{progress && (
  <Card>
    <CardHeader>
      <CardTitle>Case Progress</CardTitle>
      <CardDescription>
        {progress.percentage}% Complete - {progress.current_stage}
      </CardDescription>
    </CardHeader>
    <CardContent>
      <div className="space-y-2">
        {progress.pipeline.map((stage: any, index: number) => (
          <div key={index} className="flex items-center gap-3">
            <div className={`w-5 h-5 rounded-full ${
              stage.completed ? 'bg-green-500' : 
              stage.order === progress.pipeline.find((s: any) => !s.completed)?.order ? 'bg-blue-500' : 
              'bg-gray-300'
            }`}>
              {stage.completed && <CheckCircle className="text-white" />}
            </div>
            <div className="flex-1">
              <div className="font-medium">{stage.label}</div>
              {stage.completed && stage.completion_date && (
                <div className="text-xs text-muted-foreground">
                  Completed: {formatDate(stage.completion_date)}
                </div>
              )}
              {!stage.required && (
                <Badge variant="outline" className="text-xs ml-2">Optional</Badge>
              )}
            </div>
          </div>
        ))}
      </div>
      
      {progress.next_stage && progress.next_stage !== "Complete" && (
        <div className="mt-4 p-3 bg-blue-50 rounded-lg">
          <div className="text-sm font-medium text-blue-900">Next Step</div>
          <div className="text-sm text-blue-700">{progress.next_stage}</div>
        </div>
      )}
    </CardContent>
  </Card>
)}
```

---

## Prerequisites - Frontend Changes

**BEFORE implementing pipeline system, fix these frontend issues:**

### 1. Case Details Header Redesign

**Current Issues:**
- Green approval banner takes too much space
- Status and priority not visually prominent enough
- No visibility into case group composition (visa applications)

**Required Changes:**

#### A. Remove/Reduce Approval Banner
- Keep PM approval info but make it more compact
- Status should be PRIMARY visual indicator (large, colored)
- Priority should be SECONDARY (smaller badge)

#### B. Add Case Group Composition Section
Replace approval banner area with:

```typescript
{/* Case Group Overview */}
<Card>
  <CardHeader>
    <div className="flex items-center justify-between">
      <div className="flex-1">
        <div className="flex items-center gap-4">
          {/* Status - PROMINENT */}
          <Badge 
            variant={getStatusVariant(caseGroup.status)} 
            className="text-lg px-4 py-2"
          >
            {caseGroup.status}
          </Badge>
          
          {/* Priority - SECONDARY */}
          <Badge variant={getPriorityVariant(caseGroup.priority)}>
            {caseGroup.priority}
          </Badge>
          
          {/* PM Approval - COMPACT */}
          {caseGroup.approval_status === 'PM_APPROVED' && (
            <div className="flex items-center gap-2 text-green-700">
              <CheckCircle className="h-4 w-4" />
              <span className="text-sm">PM Approved</span>
            </div>
          )}
        </div>
        
        {/* Case Group Type */}
        <div className="text-sm text-muted-foreground mt-1">
          {caseGroup.case_type} Case Group
        </div>
      </div>
    </div>
  </CardHeader>
  
  <CardContent>
    {/* Visa Applications in Case Group */}
    <div className="space-y-2">
      <div className="font-medium text-sm">Visa Applications in this Case:</div>
      {caseGroup.applications?.map((app: any) => (
        <div key={app.id} className="flex items-center gap-3 p-2 bg-gray-50 rounded">
          <FileText className="h-4 w-4 text-gray-600" />
          <div className="flex-1">
            <div className="font-medium text-sm">{app.visa_type}</div>
            <div className="text-xs text-muted-foreground">
              {app.petition_type} - Status: {app.status}
            </div>
          </div>
          <Badge variant="outline">{app.visa_case_status}</Badge>
        </div>
      ))}
    </div>
    
    {/* Dates */}
    <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t">
      <div>
        <div className="text-xs text-muted-foreground">Started</div>
        <div className="text-sm font-medium">{formatDate(caseGroup.start_date)}</div>
      </div>
      <div>
        <div className="text-xs text-muted-foreground">Target Completion</div>
        <div className="text-sm font-medium">{formatDate(caseGroup.target_completion_date)}</div>
      </div>
      <div>
        <div className="text-xs text-muted-foreground">Last Updated</div>
        <div className="text-sm font-medium">{formatDateTime(caseGroup.updated_at)}</div>
      </div>
    </div>
  </CardContent>
</Card>
```

**Example for Luis's EB-2 NIW case:**
```
┌─────────────────────────────────────────────────────────┐
│ IN PROGRESS   HIGH   ✓ PM Approved                       │
│ EB2_NIW Case Group                                       │
├─────────────────────────────────────────────────────────┤
│ Visa Applications in this Case:                         │
│                                                          │
│ 📄 I-140 - Employment-Based Immigrant - Status: APPROVED│
│    ACTIVE                                                │
│                                                          │
│ 📄 I-485 - Adjustment of Status - Status: IN_PROGRESS   │
│    ACTIVE                                                │
│                                                          │
│ Started             Target Completion    Last Updated   │
│ August 19, 2024     August 30, 2025     Nov 11, 2025    │
└─────────────────────────────────────────────────────────┘
```

**Example for Jacob's H1B case:**
```
┌─────────────────────────────────────────────────────────┐
│ IN PROGRESS   HIGH   ✓ PM Approved                       │
│ H1B_INITIAL Case Group                                  │
├─────────────────────────────────────────────────────────┤
│ Visa Applications in this Case:                         │
│                                                          │
│ 📄 H1B - Specialty Occupation - Status: IN_PROGRESS     │
│    ACTIVE                                                │
│                                                          │
│ Started             Target Completion    Last Updated   │
│ March 1, 2024       March 31, 2025      Nov 11, 2025    │
└─────────────────────────────────────────────────────────┘
```

### 2. Add Edit Buttons to Sections

**Current Issue:**
- Single "Edit" button at top-right has no clear purpose
- Should be section-specific edit buttons

**Required Changes:**

#### Beneficiary Information Card
```typescript
<CardHeader>
  <div className="flex items-center justify-between">
    <CardTitle className="flex items-center gap-2">
      <User className="h-5 w-5" />
      Beneficiary Information
    </CardTitle>
    <Button 
      variant="outline" 
      size="sm"
      onClick={() => {/* TODO: Open beneficiary edit dialog */}}
      disabled={!canEditBeneficiary}  // Role-based
    >
      <Edit className="h-4 w-4 mr-1" />
      Edit
    </Button>
  </div>
</CardHeader>
```

#### Case Group Overview Card
```typescript
<CardHeader>
  <div className="flex items-center justify-between">
    <CardTitle>Case Group Details</CardTitle>
    <Button 
      variant="outline" 
      size="sm"
      onClick={() => {/* TODO: Open case group edit dialog */}}
      disabled={!canEditCaseGroup}  // Role-based
    >
      <Edit className="h-4 w-4 mr-1" />
      Edit
    </Button>
  </div>
</CardHeader>
```

**Role-Based Permission Logic:**
```typescript
const canEditBeneficiary = ['ADMIN', 'HR', 'PM'].includes(currentUser.role)
const canEditCaseGroup = ['ADMIN', 'HR', 'PM', 'MANAGER'].includes(currentUser.role)
```

### 3. Remove Top-Right "Edit" Button

The main "Edit" button should be removed since each section now has its own edit button.

---

## Next Steps

### Immediate (Before Pipeline Implementation):
1. ✅ Create this documentation (DONE)
2. ⚠️ **Fix frontend case details page header** (see "Prerequisites - Frontend Changes")
   - Remove/reduce approval banner
   - Make status prominent, priority secondary
   - Add visa applications list in case group
   - Add dates section
3. ⚠️ **Add section-specific edit buttons**
   - Beneficiary Information card
   - Case Group card
   - Role-based permissions
4. ⚠️ **Remove top-right Edit button** (no longer needed)

### After Frontend Fixes (Pipeline Implementation):
5. Expand `MilestoneType` enum with visa-specific types
6. Create `visa_pipelines.py` config file
7. Create `/api/v1/visa-pipelines` endpoints
8. Create `/api/v1/case-groups/{id}/progress` endpoint
9. Update frontend to call progress API
10. Update fixture files to use new milestone types
11. Test with multiple visa types (H1B, EB-2 NIW, TN)
12. Remove debug console.log statements from frontend

### Future Enhancements:
13. Create `VisaPipelineStage` database model
14. Admin UI for pipeline customization
15. Contract-specific pipeline overrides
16. "What's Next" guidance in UI
17. Milestone auto-suggestions based on pipeline stage

---

## References

### Related Files
- `backend/app/models/milestone.py` - ApplicationMilestone model
- `backend/app/models/visa.py` - VisaTypeEnum definitions
- `backend/app/models/case_group.py` - CaseType definitions
- `backend/app/api/v1/case_groups.py` - Timeline endpoint (lines 704-875)
- `backend/app/schemas/timeline.py` - TimelineEvent schemas
- `backend/scripts/fixtures/contracts/seed_assess_visa_apps.py` - Example milestone data
- `frontend/app/cases/[id]/page.tsx` - Case details page (lines 310-370 calculateProgress)

### Documentation
- `AI_DEVELOPMENT_GUIDELINES.md` - Development standards
- `DATA_MODEL.md` - Database schema documentation
- `PRD.md` - Product requirements and features
- `API_REFERENCE.md` - API endpoint documentation

---

**End of Document**
