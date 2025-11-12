# AMA-IMPACT Data Model Refactor Design

## Executive Summary

This document outlines a comprehensive refactor of the immigration case management data model to resolve architectural confusion between visa **categories/pathways** (H1B, EB2-NIW) and **petitions/forms** (I-140, I-485). The refactor will break everything temporarily but result in a cleaner, more maintainable system.

**Key Change**: `CaseGroup` (pathway) → `Petition` (forms) with proper separation of concerns.

## Current Architecture (What's Wrong)

### Problems Identified

1. **Three Redundant Visa-Related Fields** in `VisaApplication`:
   ```python
   visa_type = Column(Enum(VisaTypeEnum))           # H1B, EB2NIW, PERM (mixed)
   visa_type_id = Column(ForeignKey("visa_types"))  # Redundant lookup
   petition_type = Column(String(50))               # "I-140", "I-485" (free text)
   ```

2. **CaseType Enum Confusion** (pathways mixed with steps):
   ```python
   class CaseType(str, enum.Enum):
       EB2_NIW = "EB2_NIW"          # ✅ Pathway
       H1B_INITIAL = "H1B_INITIAL"  # ✅ Pathway
       PERM = "PERM"                # ❌ This is a STEP, not a pathway
       SINGLE = "SINGLE"            # ❌ Unclear purpose
   ```

3. **VisaTypeEnum Mixed Concepts** (categories mixed with forms and statuses):
   ```python
   class VisaTypeEnum(str, enum.Enum):
       H1B = "H1B"               # ✅ Category
       EB2NIW = "EB2NIW"         # ✅ Category
       PERM = "PERM"             # ❌ This is a FORM (labor certification)
       GREEN_CARD = "GREEN_CARD" # ❌ This is a STATUS, not a visa type
   ```

4. **visa_types Table Mixes Categories and Forms**:
   - Contains: H1B, L1, TN (categories) + I140, I485, PERM (forms)
   - Should be split into two tables or removed entirely

5. **No Dependent Tracking**:
   - No way to link dependent's derivative applications to principal's case
   - Example: David's EB2-NIW case can't track Sarah's derivative I-485

6. **Single-Level Milestones**:
   - Milestones only at petition level
   - Need case group level milestones (e.g., "Case Opened", "Strategy Meeting")

7. **Incomplete Seed Data**:
   - EB2-NIW cases only have I-140, missing I-485
   - No EAD (I-765) or AP (I-131) applications
   - No dependent applications

## Proposed Architecture (What It Should Be)

### Core Concepts

1. **CaseGroup**: Immigration **pathway** (one per beneficiary)
   - Examples: "David's EB2-NIW", "Maria's H1B", "John's TN"
   - Has case-level milestones (e.g., "Case Opened", "Strategy Meeting")
   - Contains multiple petitions

2. **Petition**: Individual **forms/applications** (many per case group)
   - Examples: I-140, I-485, I-129, I-765 (EAD), I-131 (AP), PERM
   - Has petition-level milestones (e.g., "I-140 Filed", "I-140 Approved")
   - Linked to case group and optionally to dependent

3. **Dependent**: Beneficiary's family members
   - Spouse, children
   - Can have derivative petitions (e.g., derivative I-485)

### Data Model Changes

#### 1. Rename `VisaApplication` → `Petition`

**File**: `backend/app/models/visa.py` → `backend/app/models/petition.py`

**Before**:
```python
class VisaApplication(Base):
    __tablename__ = "visa_applications"
    
    id = Column(Integer, primary_key=True)
    case_group_id = Column(Integer, ForeignKey("case_groups.id"))
    visa_type = Column(Enum(VisaTypeEnum))
    visa_type_id = Column(Integer, ForeignKey("visa_types.id"))
    petition_type = Column(String(50))
    case_status = Column(Enum(CaseStatus))
    receipt_number = Column(String(50))
    filing_date = Column(Date)
    approval_date = Column(Date)
```

**After**:
```python
class Petition(Base):
    __tablename__ = "petitions"
    
    id = Column(Integer, primary_key=True)
    case_group_id = Column(Integer, ForeignKey("case_groups.id"), nullable=False)
    petition_type = Column(Enum(PetitionType), nullable=False)
    dependent_id = Column(Integer, ForeignKey("dependents.id"), nullable=True)  # NEW
    case_status = Column(Enum(CaseStatus))
    receipt_number = Column(String(50))
    filing_date = Column(Date)
    approval_date = Column(Date)
    priority_date = Column(Date)
    
    # Relationships
    case_group = relationship("CaseGroup", back_populates="petitions")
    dependent = relationship("Dependent", back_populates="petitions")  # NEW
    milestones = relationship("Milestone", back_populates="petition")
```

#### 2. Create `PetitionType` Enum (replaces VisaTypeEnum)

**File**: `backend/app/models/petition.py`

```python
class PetitionType(str, enum.Enum):
    """Types of immigration petitions/forms"""
    # Employment-Based
    I140 = "I140"           # Immigrant Petition for Alien Worker
    I485 = "I485"           # Application to Register Permanent Residence
    I129 = "I129"           # Petition for Nonimmigrant Worker
    I765 = "I765"           # Application for Employment Authorization (EAD)
    I131 = "I131"           # Application for Travel Document (AP)
    
    # Labor Certification
    PERM = "PERM"           # Labor Certification
    
    # Family-Based
    I130 = "I130"           # Petition for Alien Relative
    
    # Add more as needed
```

#### 3. Update `CaseGroup` Model

**File**: `backend/app/models/case_group.py`

**Before**:
```python
class CaseType(str, enum.Enum):
    EB2_NIW = "EB2_NIW"
    H1B_INITIAL = "H1B_INITIAL"
    PERM = "PERM"           # ❌ Remove this
    SINGLE = "SINGLE"       # ❌ Remove or clarify
```

**After**:
```python
class PathwayType(str, enum.Enum):
    """Immigration pathways (case group types)"""
    # Employment-Based Green Card Pathways
    EB2_NIW = "EB2_NIW"                 # EB-2 National Interest Waiver
    EB2_PERM = "EB2_PERM"               # EB-2 with PERM labor cert
    EB3_PERM = "EB3_PERM"               # EB-3 with PERM labor cert
    
    # Nonimmigrant Pathways
    H1B_INITIAL = "H1B_INITIAL"         # H-1B initial petition
    H1B_EXTENSION = "H1B_EXTENSION"     # H-1B extension
    H1B_TRANSFER = "H1B_TRANSFER"       # H-1B transfer
    L1A = "L1A"                         # L-1A Intracompany Transferee Executive
    L1B = "L1B"                         # L-1B Intracompany Transferee Specialized
    TN = "TN"                           # TN NAFTA Professional
    
    # Family-Based
    FAMILY_BASED = "FAMILY_BASED"
    
    # Add more as needed

class CaseGroup(Base):
    __tablename__ = "case_groups"
    
    id = Column(Integer, primary_key=True)
    pathway_type = Column(Enum(PathwayType), nullable=False)  # RENAMED from case_type
    beneficiary_id = Column(Integer, ForeignKey("beneficiaries.id"))
    company_id = Column(Integer, ForeignKey("companies.id"))
    case_status = Column(Enum(CaseStatus))
    
    # Relationships
    petitions = relationship("Petition", back_populates="case_group")  # RENAMED
    milestones = relationship("Milestone", back_populates="case_group")  # NEW
```

#### 4. Update `Dependent` Model

**File**: `backend/app/models/dependent.py`

```python
class Dependent(Base):
    __tablename__ = "dependents"
    
    id = Column(Integer, primary_key=True)
    beneficiary_id = Column(Integer, ForeignKey("beneficiaries.id"))
    relationship = Column(Enum(RelationshipType))
    first_name = Column(String(100))
    last_name = Column(String(100))
    date_of_birth = Column(Date)
    
    # Relationships
    beneficiary = relationship("Beneficiary", back_populates="dependents")
    petitions = relationship("Petition", back_populates="dependent")  # NEW
```

#### 5. Update `Milestone` Model

**File**: `backend/app/models/milestone.py`

```python
class Milestone(Base):
    __tablename__ = "milestones"
    
    id = Column(Integer, primary_key=True)
    case_group_id = Column(Integer, ForeignKey("case_groups.id"), nullable=True)  # NEW
    petition_id = Column(Integer, ForeignKey("petitions.id"), nullable=True)  # Changed from visa_application_id
    milestone_type = Column(Enum(MilestoneType))
    status = Column(Enum(MilestoneStatus))
    due_date = Column(Date)
    completed_date = Column(Date)
    
    # Relationships
    case_group = relationship("CaseGroup", back_populates="milestones")  # NEW
    petition = relationship("Petition", back_populates="milestones")  # RENAMED
    
    # Constraint: Either case_group_id OR petition_id must be set, not both
    __table_args__ = (
        CheckConstraint(
            '(case_group_id IS NOT NULL AND petition_id IS NULL) OR '
            '(case_group_id IS NULL AND petition_id IS NOT NULL)',
            name='check_milestone_parent'
        ),
    )
```

#### 6. Remove `visa_types` Table

No longer needed since petition types are now an enum.

### Pipeline Configuration Changes

**File**: `backend/app/config/visa_pipelines.py`

**New Structure**:
```python
# Case Group Level Pipelines
CASE_GROUP_PIPELINES = {
    PathwayType.EB2_NIW: {
        "name": "EB-2 National Interest Waiver",
        "stages": [
            {
                "order": 1,
                "milestone_type": MilestoneType.CASE_OPENED,
                "weight": 5,
                "name": "Case Opened",
                "description": "Initial case assessment and strategy"
            },
            {
                "order": 2,
                "milestone_type": MilestoneType.STRATEGY_MEETING,
                "weight": 10,
                "name": "Strategy Meeting",
                "description": "Meet with client to discuss approach"
            },
            # More case-level milestones...
        ]
    }
}

# Petition Level Pipelines
PETITION_PIPELINES = {
    PetitionType.I140: {
        "name": "I-140 Immigrant Petition",
        "stages": [
            {
                "order": 1,
                "milestone_type": MilestoneType.DOCUMENTS_REQUESTED,
                "weight": 20,
                "name": "Documents Requested"
            },
            {
                "order": 2,
                "milestone_type": MilestoneType.I140_FILED,
                "weight": 60,
                "name": "I-140 Filed"
            },
            {
                "order": 3,
                "milestone_type": MilestoneType.I140_APPROVED,
                "weight": 100,
                "name": "I-140 Approved"
            }
        ]
    },
    PetitionType.I485: {
        "name": "I-485 Adjustment of Status",
        "stages": [
            {
                "order": 1,
                "milestone_type": MilestoneType.DOCUMENTS_REQUESTED,
                "weight": 20,
                "name": "Documents Requested"
            },
            {
                "order": 2,
                "milestone_type": MilestoneType.I485_FILED,
                "weight": 50,
                "name": "I-485 Filed"
            },
            {
                "order": 3,
                "milestone_type": MilestoneType.INTERVIEW_SCHEDULED,
                "weight": 80,
                "name": "Interview Scheduled"
            },
            {
                "order": 4,
                "milestone_type": MilestoneType.I485_APPROVED,
                "weight": 100,
                "name": "I-485 Approved"
            }
        ]
    },
    PetitionType.PERM: {
        "name": "PERM Labor Certification",
        "stages": [
            {
                "order": 1,
                "milestone_type": MilestoneType.PERM_FILED,
                "weight": 50,
                "name": "PERM Filed"
            },
            {
                "order": 2,
                "milestone_type": MilestoneType.PERM_APPROVED,
                "weight": 100,
                "name": "PERM Approved"
            }
        ]
    },
    # More petition types...
}

# Company-Specific Overrides (Future Feature)
COMPANY_PIPELINES = {
    "company_slug": {
        PathwayType.EB2_NIW: {
            # Override default EB2_NIW pipeline
        }
    }
}
```

## Migration Strategy

### NO ALEMBIC - Full Database Reset

Following `AI_DEVELOPMENT_GUIDELINES.md`:

```bash
cd backend
python scripts/setup_dev_environment.py
```

This will:
1. Delete `devel.db`
2. Create fresh database with new schema
3. Run all seed scripts
4. Verify data integrity

### Files to Update

#### Backend Models (8 files)
- [ ] `backend/app/models/visa.py` → `backend/app/models/petition.py`
- [ ] `backend/app/models/case_group.py` (update PathwayType enum)
- [ ] `backend/app/models/milestone.py` (add case_group_id)
- [ ] `backend/app/models/dependent.py` (add petitions relationship)
- [ ] `backend/app/models/__init__.py` (update imports)
- [ ] `backend/app/database.py` (update Base imports)

#### Backend API Endpoints (4 files)
- [ ] `backend/app/api/v1/visa_applications.py` → `backend/app/api/v1/petitions.py`
- [ ] `backend/app/api/v1/case_groups.py` (update to use Petition)
- [ ] `backend/app/api/v1/milestones.py` (handle case_group_id)
- [ ] `backend/app/api/__init__.py` (update router imports)

#### Backend Schemas (2 files)
- [ ] `backend/app/schemas/visa.py` → `backend/app/schemas/petition.py`
- [ ] `backend/app/schemas/case_group.py` (update PathwayType)

#### Backend Config (1 file)
- [ ] `backend/app/config/visa_pipelines.py` (restructure as shown above)

#### Backend Seed Scripts (6 files)
- [ ] `backend/scripts/fixtures/companies.py`
- [ ] `backend/scripts/fixtures/beneficiaries.py`
- [ ] `backend/scripts/fixtures/case_groups.py` (use PathwayType)
- [ ] `backend/scripts/fixtures/petitions.py` (rename from visa_applications.py)
- [ ] `backend/scripts/fixtures/dependents.py` (add petition links)
- [ ] `backend/scripts/fixtures/milestones.py` (add case-level milestones)

#### Frontend Components (6 files)
- [ ] `frontend/lib/api.ts` (rename visaApplicationsAPI → petitionsAPI)
- [ ] `frontend/app/cases/[id]/page.tsx` (use Petition instead of VisaApplication)
- [ ] `frontend/app/cases/page.tsx` (update table)
- [ ] `frontend/app/visas/page.tsx` (if exists, rename to petitions)
- [ ] `frontend/types/index.ts` (update type definitions)

## Detailed Implementation Plan

### Phase 1: Backend Models (Day 1)

1. **Create new `petition.py` model**
   - Copy from `visa.py`
   - Rename class and table
   - Add `PetitionType` enum
   - Add `dependent_id` field
   - Remove redundant fields

2. **Update `case_group.py`**
   - Rename `CaseType` → `PathwayType`
   - Clean up enum values
   - Rename relationship: `visa_applications` → `petitions`
   - Add `milestones` relationship

3. **Update `milestone.py`**
   - Add `case_group_id` field
   - Add check constraint
   - Update relationships

4. **Update `dependent.py`**
   - Add `petitions` relationship

5. **Update imports**
   - `backend/app/models/__init__.py`
   - `backend/app/database.py`

### Phase 2: Backend Config (Day 1)

6. **Restructure `visa_pipelines.py`**
   - Split into `CASE_GROUP_PIPELINES` and `PETITION_PIPELINES`
   - Update keys to use new enums
   - Test structure is valid Python

### Phase 3: Backend Schemas (Day 1)

7. **Create new `petition.py` schemas**
   - Copy from `visa.py`
   - Update to use `PetitionType`
   - Add `dependent_id` field

8. **Update `case_group.py` schemas**
   - Use `PathwayType`
   - Update nested petition schemas

### Phase 4: Backend API Endpoints (Day 2)

9. **Create `petitions.py` endpoint**
   - Copy from `visa_applications.py`
   - Update all references to Petition model
   - Update path: `/api/v1/petitions`

10. **Update `case_groups.py` endpoint**
    - Change all `visa_application` → `petition`
    - Update progress calculation for two-level milestones
    - Update filters

11. **Update `milestones.py` endpoint**
    - Handle case_group_id parameter
    - Support filtering by case group or petition

12. **Update router imports**
    - `backend/app/api/__init__.py`

### Phase 5: Backend Seed Scripts (Day 2)

13. **Update `case_groups.py` seed**
    - Use `PathwayType` enum
    - Update all case group definitions

14. **Create `petitions.py` seed** (rename from visa_applications.py)
    - Create complete petition sets per pathway:
      * EB2-NIW: I-140 + I-485 + I-765 (EAD) + I-131 (AP)
      * H1B: I-129
      * TN: Direct (no petition)
    - Link dependents to derivative petitions
    - Use `PetitionType` enum

15. **Update `dependents.py` seed**
    - Create dependents for some beneficiaries
    - Link to petitions

16. **Update `milestones.py` seed**
    - Create case-level milestones
    - Create petition-level milestones
    - Ensure both case_group_id and petition_id are used

### Phase 6: Frontend Updates (Day 3)

17. **Update `frontend/lib/api.ts`**
    - Rename `visaApplicationsAPI` → `petitionsAPI`
    - Update all endpoint paths
    - Update type annotations

18. **Update `frontend/types/index.ts`**
    - Rename `VisaApplication` → `Petition`
    - Add `PetitionType` enum
    - Update `CaseGroup` to use `PathwayType`

19. **Update `frontend/app/cases/[id]/page.tsx`**
    - Change all references: VisaApplication → Petition
    - Update API calls to use petitionsAPI
    - Update UI labels (Visa Applications → Petitions)
    - Handle case-level vs petition-level milestones

20. **Update `frontend/app/cases/page.tsx`**
    - Update table columns
    - Use PathwayType

21. **Check for visa-related pages**
    - Rename if exists: `frontend/app/visas/` → `frontend/app/petitions/`

### Phase 7: Database Reset & Test (Day 3)

22. **Reset database**
    ```bash
    cd backend
    python scripts/setup_dev_environment.py
    ```

23. **Backend Testing**
    - [ ] Start backend: `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 7001`
    - [ ] Test Swagger UI: `http://localhost:7001/docs`
    - [ ] Test GET `/api/v1/case-groups` - should return 11 case groups with PathwayType
    - [ ] Test GET `/api/v1/petitions` - should return all petitions with PetitionType
    - [ ] Test GET `/api/v1/case-groups/{id}` - should show petitions grouped correctly
    - [ ] Test GET `/api/v1/case-groups/{id}/progress` - should show case + petition milestones
    - [ ] Verify dependent petitions exist and are linked correctly

24. **Frontend Testing**
    - [ ] Start frontend: `cd frontend && npm run dev`
    - [ ] Test case list page: Should show PathwayType
    - [ ] Test case detail page: Should show petitions (not visa applications)
    - [ ] Test progress display: Should show case-level + petition-level
    - [ ] Verify petition types display correctly (I-140, I-485, etc.)

### Phase 8: Additional Features (Day 4)

25. **Add Case Notes Feature**
    - Create `CaseNote` model with author tracking
    - Add API endpoint: POST/GET `/api/v1/case-groups/{id}/notes`
    - Add frontend component for viewing/adding notes

26. **Add Custom Timeline Events**
    - Allow users to add custom events to timeline
    - Store in separate table or as milestone type

## Testing Checklist

### Backend Tests
- [ ] All models can be created
- [ ] Relationships work correctly
- [ ] Check constraint on Milestone works
- [ ] All API endpoints return 200
- [ ] Progress calculation includes case + petition milestones
- [ ] Seed data creates complete petition sets
- [ ] Dependent petitions are linked correctly

### Frontend Tests
- [ ] Case list displays PathwayType
- [ ] Case detail shows petitions correctly
- [ ] Progress bars display for case group
- [ ] Progress bars display per petition
- [ ] Petition types are readable (I-140, not I140)
- [ ] Dependent petitions are indicated visually

### Integration Tests
- [ ] Create new case group with EB2-NIW pathway
- [ ] Create I-140 petition for case
- [ ] Create I-485 petition for case
- [ ] Link I-485 to dependent
- [ ] Add milestones at case level
- [ ] Add milestones at petition level
- [ ] Verify progress calculation

## Rollback Plan

If refactor fails catastrophically:

```bash
git reset --hard 91e89a4  # Current checkpoint commit
cd backend
python scripts/setup_dev_environment.py
```

## Success Criteria

- [ ] All backend tests pass
- [ ] All frontend pages render without errors
- [ ] Progress tracking works at both levels
- [ ] Dependent petitions can be created and linked
- [ ] Seed data creates realistic, complete cases
- [ ] No references to VisaApplication remain
- [ ] No references to visa_type remain
- [ ] PathwayType and PetitionType are clearly separated

## Timeline Estimate

- **Day 1**: Backend models, config, schemas (6 hours)
- **Day 2**: Backend API, seed scripts (6 hours)
- **Day 3**: Frontend updates, testing (6 hours)
- **Day 4**: Additional features, polish (4 hours)

**Total**: 22 hours over 4 days

## Notes

- This refactor WILL break everything temporarily
- We have a safe rollback point (commit 91e89a4)
- Follow AI_DEVELOPMENT_GUIDELINES.md: NO ALEMBIC
- Test thoroughly after each phase
- Document any issues discovered during refactor

## Questions to Resolve Before Starting

1. Should we support TN visas (which don't require petitions)?
2. How to handle EAD/AP combo cards (I-765/I-131)?
3. Should company-specific pipeline overrides be implemented now or later?
4. Do we need audit logging for who changes what?
5. Should case notes have rich text formatting?
