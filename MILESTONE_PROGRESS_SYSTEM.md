# Milestone Progress Tracking System

**Last Updated:** November 14, 2025  
**Status:** Production Ready

---

## Overview

The milestone progress tracking system provides real-time visualization of immigration case progress through a pipeline-based approach. Each petition type (I-140, I-485, H-1B, etc.) has a specific pipeline defining the expected milestones and their completion weights.

## Architecture

### Core Components

1. **Milestone Model** (`backend/app/models/milestone.py`)
   - Tracks individual milestones for petitions or case groups
   - Links to either a petition or case group (not both)
   - Stores milestone type, status, completion date, and description

2. **Pipeline Configuration** (`backend/app/config/petition_pipelines.py`)
   - Defines petition-specific pipelines with ordered stages
   - Maps petition types to appropriate milestone sequences
   - Provides progress calculation weights

3. **Progress API** (`backend/app/api/v1/case_groups.py`)
   - `/api/v1/case-groups/{id}/progress` endpoint
   - Calculates progress by comparing completed milestones against pipeline stages
   - Returns overall case progress and individual petition progress

4. **Frontend Display** (`frontend/app/cases/[id]/page.tsx`)
   - Progress panel component showing visual pipeline
   - Progress bars with percentage completion
   - Timeline of completed milestones with dates

---

## Petition Pipelines

### I-140: Immigrant Petition for Alien Worker

**Used for:** EB-2, EB-3 employment-based immigrant petitions

**Pipeline Stages:**
| Order | Milestone Type | Label | Weight | Required |
|-------|---------------|-------|--------|----------|
| 1 | `CASE_OPENED` | Case Opened | 10% | No |
| 2 | `DOCUMENTS_REQUESTED` | Documents Requested | 20% | No |
| 3 | `DOCUMENTS_SUBMITTED` | Documents Submitted | 40% | No |
| 4 | `I140_FILED` | I-140 Filed | 60% | Yes |
| 5 | `RFE_RECEIVED` | RFE Received | 70% | No |
| 6 | `RFE_RESPONDED` | RFE Responded | 80% | No |
| 7 | `I140_APPROVED` | I-140 Approved | 100% | Yes |
| 8 | `I140_DENIED` | I-140 Denied | 100% | No |

**Progress Calculation:**
- Progress = highest weight of completed milestones
- Example: If `I140_FILED` and `I140_APPROVED` are complete → 100%

---

### I-485: Adjustment of Status (Green Card)

**Used for:** Green Card applications for beneficiaries in the US

**Pipeline Stages:**
| Order | Milestone Type | Label | Weight | Required |
|-------|---------------|-------|--------|----------|
| 1 | `CASE_OPENED` | Case Opened | 10% | No |
| 2 | `DOCUMENTS_REQUESTED` | Documents Requested | 20% | No |
| 3 | `DOCUMENTS_SUBMITTED` | Documents Submitted | 30% | No |
| 4 | `I485_FILED` | I-485 Filed | 45% | Yes |
| 5 | `BIOMETRICS_SCHEDULED` | Biometrics Scheduled | 55% | No |
| 6 | `BIOMETRICS_COMPLETED` | Biometrics Completed | 65% | No |
| 7 | `INTERVIEW_SCHEDULED` | Interview Scheduled | 75% | No |
| 8 | `INTERVIEW_COMPLETED` | Interview Completed | 85% | No |
| 9 | `I485_APPROVED` | I-485 Approved | 95% | Yes |
| 10 | `GREEN_CARD_RECEIVED` | Green Card Received | 100% | Yes |

**Progress Calculation:**
- Progress = highest weight of completed milestones
- Terminal milestone: `GREEN_CARD_RECEIVED` (100%)

---

### I-129: Petition for Nonimmigrant Worker (H-1B, L-1, etc.)

**Used for:** H-1B, L-1, O-1, and other nonimmigrant work petitions

**Pipeline Stages:**
| Order | Milestone Type | Label | Weight | Required |
|-------|---------------|-------|--------|----------|
| 1 | `CASE_OPENED` | Case Opened | 10% | No |
| 2 | `LCA_FILED` | LCA Filed | 30% | No |
| 3 | `LCA_APPROVED` | LCA Approved | 50% | No |
| 4 | `H1B_FILED` | H-1B Filed | 70% | Yes |
| 5 | `RFE_RECEIVED` | RFE Received | 80% | No |
| 6 | `RFE_RESPONDED` | RFE Responded | 90% | No |
| 7 | `H1B_APPROVED` | H-1B Approved | 100% | Yes |

**Progress Calculation:**
- LCA stages are optional (some petitions may not require LCA)
- Progress = highest weight of completed milestones

---

### PERM: Labor Certification

**Used for:** Permanent labor certification (precedes I-140 for EB-2/EB-3)

**Pipeline Stages:**
| Order | Milestone Type | Label | Weight | Required |
|-------|---------------|-------|--------|----------|
| 1 | `PWD_FILED` | PWD Filed | 15% | Yes |
| 2 | `PWD_APPROVED` | PWD Approved | 30% | Yes |
| 3 | `RECRUITMENT_STARTED` | Recruitment Started | 45% | Yes |
| 4 | `RECRUITMENT_COMPLETED` | Recruitment Completed | 60% | Yes |
| 5 | `PERM_FILED` | PERM Filed | 75% | Yes |
| 6 | `PERM_AUDIT` | PERM Audit | 85% | No |
| 7 | `PERM_APPROVED` | PERM Approved | 100% | Yes |

**Progress Calculation:**
- All stages required except `PERM_AUDIT` (only if selected)
- Terminal milestone: `PERM_APPROVED` (100%)

---

### TN: NAFTA Professional

**Used for:** TN visa applications for Canadian/Mexican professionals

**Pipeline Stages:**
| Order | Milestone Type | Label | Weight | Required |
|-------|---------------|-------|--------|----------|
| 1 | `CASE_OPENED` | Case Opened | 20% | No |
| 2 | `DOCUMENTS_REQUESTED` | Documents Requested | 40% | No |
| 3 | `DOCUMENTS_SUBMITTED` | Documents Submitted | 60% | No |
| 4 | `TN_BORDER_APPOINTMENT` | Border/Consulate Appointment | 80% | Yes |
| 5 | `TN_APPROVED` | TN Approved | 100% | Yes |

**Progress Calculation:**
- Simplified pipeline (TN can be approved at port of entry)
- Terminal milestone: `TN_APPROVED` (100%)

---

### DEFAULT: Generic Immigration Process

**Used for:** Petition types without specific pipeline definitions

**Pipeline Stages:**
| Order | Milestone Type | Label | Weight | Required |
|-------|---------------|-------|--------|----------|
| 1 | `CASE_OPENED` | Case Opened | 15% | True |
| 2 | `DOCUMENTS_REQUESTED` | Documents Requested | 30% | True |
| 3 | `DOCUMENTS_SUBMITTED` | Documents Submitted | 50% | True |
| 4 | `FILED_WITH_USCIS` | Filed with USCIS | 75% | True |
| 5 | `APPROVED` | Approved | 100% | True |

---

## Database Schema

### Milestones Table

```sql
CREATE TABLE milestones (
    id VARCHAR(36) PRIMARY KEY,
    case_group_id VARCHAR(36),  -- FK to case_groups (nullable)
    petition_id VARCHAR(36),    -- FK to petitions (nullable)
    created_by VARCHAR(36) NOT NULL,  -- FK to users
    milestone_type VARCHAR(50) NOT NULL,  -- Enum: MilestoneType
    status VARCHAR(20) NOT NULL,  -- Enum: PENDING, IN_PROGRESS, COMPLETED, SKIPPED
    due_date DATE,
    completed_date DATE,
    title VARCHAR(255),
    description TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    CONSTRAINT check_milestone_parent CHECK (
        (case_group_id IS NOT NULL AND petition_id IS NULL) OR
        (case_group_id IS NULL AND petition_id IS NOT NULL)
    )
);
```

**Key Constraints:**
- Either `case_group_id` OR `petition_id` must be set (not both)
- `milestone_type` must be a valid `MilestoneType` enum value
- `completed_date` is set when milestone status becomes `COMPLETED`

---

## API Usage

### Get Case Group Progress

**Endpoint:** `GET /api/v1/case-groups/{case_group_id}/progress`

**Response:**
```json
{
  "case_group_id": "56d21c2c-87b6-4cae-acde-7db59bb89eaa",
  "overall_percentage": 100,
  "overall_stage": "Complete",
  "petitions": [
    {
      "petition_id": "72ffbba9-c8e4-47ba-ae8b-7e769dd91abf",
      "petition_type": "I140",
      "visa_status": "APPROVED",
      "case_status": "FINALIZED",
      "percentage": 100,
      "current_stage": "I-140 Approved",
      "next_stage": null,
      "pipeline_name": "I-140 Immigrant Petition",
      "pipeline": [
        {
          "order": 1,
          "milestone_type": "case_opened",
          "label": "Case Opened",
          "description": "I-140 petition case initiated",
          "weight": 10,
          "required": false,
          "terminal": false,
          "completed": false,
          "completion_date": null
        },
        {
          "order": 4,
          "milestone_type": "i140_filed",
          "label": "I-140 Filed",
          "description": "I-140 petition filed with USCIS",
          "weight": 60,
          "required": true,
          "terminal": false,
          "completed": true,
          "completion_date": "2018-01-15"
        },
        {
          "order": 7,
          "milestone_type": "i140_approved",
          "label": "I-140 Approved",
          "description": "USCIS approved the I-140 petition",
          "weight": 100,
          "required": true,
          "terminal": true,
          "completed": true,
          "completion_date": "2018-06-10"
        }
      ]
    }
  ]
}
```

**Overall Stage Calculation:**
- 100%: "Complete"
- 80-99%: "Nearing Completion"
- 50-79%: "In Progress"
- 25-49%: "Early Stage"
- 0-24%: "Getting Started"

---

## Adding New Milestones

### Backend: Creating Milestones

```python
from app.models.milestone import Milestone, MilestoneType, MilestoneStatus
from datetime import date

# Create milestone for a petition
milestone = Milestone(
    petition_id="petition-uuid-here",
    created_by="user-uuid-here",
    milestone_type=MilestoneType.I140_FILED,
    status=MilestoneStatus.COMPLETED,
    completed_date=date(2024, 1, 15),
    description="I-140 petition filed with premium processing"
)
db.add(milestone)
db.commit()
```

### Frontend: Displaying Progress

The progress panel automatically fetches and displays progress when a case detail page loads:

```typescript
// In frontend/app/cases/[id]/page.tsx
const progressData = await petitionsAPI.getCaseGroupProgress(id);

// Progress panel renders automatically with:
// - Overall percentage bar
// - Individual petition pipelines
// - Completed milestones with dates
// - Next action items
```

---

## Troubleshooting

### Issue: Progress Shows 0% Despite Completed Milestones

**Cause:** Pipeline milestone types don't match database milestone types

**Solution:**
1. Check what milestones exist in database:
```sql
SELECT milestone_type FROM milestones WHERE petition_id = 'petition-id';
```

2. Verify pipeline includes those milestone types:
```python
pipeline = get_pipeline_for_petition_type(PetitionType.I140)
print([s['milestone_type'].value for s in pipeline['stages']])
```

3. If mismatch, update pipeline in `petition_pipelines.py`

---

### Issue: Pipeline Missing for New Petition Type

**Cause:** New petition type added but no pipeline defined

**Solution:**
1. Add new pipeline constant in `petition_pipelines.py`:
```python
NEW_PETITION_PIPELINE = {
    "name": "New Petition Type",
    "description": "Description here",
    "stages": [...]
}
```

2. Update `get_pipeline_for_petition_type()` mapping:
```python
pipeline_map = {
    PetitionType.NEW_TYPE: NEW_PETITION_PIPELINE,
    # ... other mappings
}
```

3. Restart backend

---

### Issue: Frontend Shows "No petitions found for progress tracking"

**Causes & Solutions:**

1. **No milestones in database:**
   - Check: `SELECT * FROM milestones WHERE petition_id IN (SELECT id FROM petitions WHERE case_group_id = 'case-id');`
   - Fix: Create milestones using admin panel or seed data

2. **API returning wrong field name:**
   - Check browser console for API response
   - Verify response has `petitions` field (not `visa_applications`)

3. **Backend crash before response:**
   - Check backend logs for errors
   - Verify `petition_pipelines.py` imports without errors

---

## Development Guidelines

### Adding a New Pipeline

1. **Define milestone types** in `backend/app/models/milestone.py`:
```python
class MilestoneType(str, enum.Enum):
    # Add new types
    NEW_MILESTONE = "new_milestone"
```

2. **Create pipeline** in `backend/app/config/petition_pipelines.py`:
```python
NEW_PIPELINE = {
    "name": "Pipeline Name",
    "description": "Description",
    "stages": [
        {
            "order": 1,
            "milestone_type": MilestoneType.NEW_MILESTONE,
            "label": "User-Facing Label",
            "description": "Stage description",
            "weight": 50,  # Progress percentage
            "required": True,  # or False for optional
            "terminal": False,  # True for final stage
        },
    ]
}
```

3. **Map petition type** to pipeline:
```python
def get_pipeline_for_petition_type(petition_type: PetitionType) -> Dict[str, Any]:
    pipeline_map = {
        PetitionType.NEW_TYPE: NEW_PIPELINE,
        # ... existing mappings
    }
    return pipeline_map.get(petition_type, DEFAULT_PIPELINE)
```

4. **Test import:**
```bash
cd backend
python -c "from app.config.petition_pipelines import get_pipeline_for_petition_type; print('OK')"
```

5. **Restart backend** and test in UI

---

### Seeding Milestone Data

When creating development fixtures, add milestones that match pipelines:

```python
# In backend/scripts/fixtures/seed_development_data.py

from app.models.milestone import Milestone, MilestoneType, MilestoneStatus

milestones = [
    Milestone(
        petition_id=petition.id,
        created_by=manager.id,
        milestone_type=MilestoneType.I140_FILED,
        status=MilestoneStatus.COMPLETED,
        completed_date=date(2024, 1, 15)
    ),
    Milestone(
        petition_id=petition.id,
        created_by=manager.id,
        milestone_type=MilestoneType.I140_APPROVED,
        status=MilestoneStatus.COMPLETED,
        completed_date=date(2024, 6, 10)
    ),
]

db.add_all(milestones)
```

---

## Performance Considerations

### Database Queries

The progress endpoint makes these queries per case group:
1. Fetch case group with petitions (1 query with joins)
2. Fetch milestones for each petition (N queries where N = number of petitions)

**Optimization:** The milestone queries are necessary since different petitions have different milestone sets. Consider eager loading if performance issues arise.

### Caching

Progress calculations are NOT cached because:
- Milestones change frequently during active case work
- Data freshness is critical for user experience
- Calculation is fast (O(n*m) where n=petitions, m=pipeline stages)

If caching is needed:
- Cache at frontend level with TTL (e.g., 60 seconds)
- Invalidate cache when milestones are updated

---

## Testing

### Manual Testing Checklist

- [ ] Create case with I-140 petition
- [ ] Add milestone: `I140_FILED`
- [ ] Verify progress shows 60%
- [ ] Add milestone: `I140_APPROVED`
- [ ] Verify progress shows 100%
- [ ] Check pipeline displays all stages with correct completion status
- [ ] Verify completion dates display correctly
- [ ] Test with multiple petitions in same case
- [ ] Verify overall case progress calculates correctly

### API Testing

```bash
# Get JWT token
TOKEN=$(curl -X POST http://localhost:7001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@ama-impact.com","password":"Admin123!"}' \
  | jq -r '.access_token')

# Test progress endpoint
curl -X GET http://localhost:7001/api/v1/case-groups/{case-group-id}/progress \
  -H "Authorization: Bearer $TOKEN" | jq
```

---

## Future Enhancements

### Planned Features

1. **Configurable Pipelines per Contract**
   - Allow contracts to customize milestone pipelines
   - Store pipeline definitions in database vs hardcoded

2. **Milestone Notifications**
   - Auto-notify beneficiaries when milestones complete
   - Email/SMS alerts for critical milestones

3. **Predictive Timeline**
   - Use historical data to predict completion dates
   - Display estimated time to next milestone

4. **Milestone Dependencies**
   - Enforce that certain milestones must complete before others
   - Block out-of-order milestone creation

5. **Bulk Milestone Operations**
   - Update milestones for multiple petitions at once
   - Import milestones from USCIS case status tool

---

## Maintenance Log

| Date | Change | Author | Notes |
|------|--------|--------|-------|
| 2025-11-14 | Initial implementation of petition-specific pipelines | System | Fixed progress calculation by matching pipeline milestone types to database milestone types. Created I140, I485, I129, PERM, and TN pipelines. |

---

## References

- **Milestone Model:** `backend/app/models/milestone.py`
- **Pipeline Config:** `backend/app/config/petition_pipelines.py`
- **Progress API:** `backend/app/api/v1/case_groups.py` (line 880)
- **Frontend Display:** `frontend/app/cases/[id]/page.tsx`
- **AI Dev Guidelines:** `AI_DEVELOPMENT_GUIDELINES.md`

---

**Questions or Issues?**
- Check troubleshooting section above
- Review backend logs: `backend/uvilogDebug`
- Test API directly with curl commands
- Verify database has correct milestone data
