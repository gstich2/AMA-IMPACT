# Visa Pipeline System - Implementation Plan

**Created:** November 11, 2025  
**Status:** Ready to Execute  
**Reference:** See `VISA_PIPELINE_SYSTEM_DESIGN.md` for detailed design rationale

---

## 🎯 Goal

Replace hardcoded frontend progress calculation with visa-type-specific pipelines where each visa (H1B, EB2-NIW, TN, etc.) has its own milestone progression.

**Key Principle:** Milestones belong to **VisaApplications**, not CaseGroups. Each visa app has its own pipeline based on its visa type.

---

## 📋 Implementation Phases

### Phase 1: Frontend Fixes (DO FIRST) ⚠️

**Why First:** These improvements are independent and will make the case details page better regardless of pipeline system.

#### Task 1.1: Redesign Case Details Header
**File:** `frontend/app/cases/[id]/page.tsx`

**Changes:**
- ✅ Remove large green PM approval banner
- ✅ Make Status PRIMARY (large colored badge)
- ✅ Make Priority SECONDARY (smaller badge)
- ✅ Show PM approval as compact indicator (✓ PM Approved)
- ✅ Add "Visa Applications in this Case" section listing all visas
- ✅ Add dates section (Started, Target Completion, Last Updated)

**Design:**
```
┌─────────────────────────────────────────────────┐
│ [IN PROGRESS]  [HIGH]  ✓ PM Approved            │
│ EB2_NIW Case Group                              │
├─────────────────────────────────────────────────┤
│ Visa Applications in this Case:                 │
│ 📄 I-140 - Employment-Based - Status: APPROVED  │
│ 📄 I-485 - Adjustment of Status - IN_PROGRESS   │
│                                                  │
│ Started: Aug 19, 2024 | Target: Aug 30, 2025   │
└─────────────────────────────────────────────────┘
```

#### Task 1.2: Add Section Edit Buttons
**Files:** `frontend/app/cases/[id]/page.tsx`

**Changes:**
- ✅ Add [Edit] button to Beneficiary Information card header
- ✅ Add [Edit] button to Case Group Details card header
- ✅ Remove top-right standalone Edit button
- ✅ Add role-based permissions (ADMIN, HR, PM, MANAGER can edit)

#### Task 1.3: Test Frontend Changes
- Verify layout works on desktop and mobile
- Test with Luis's case (EB2-NIW with 2 visas)
- Test with Jacob's case (H1B with 1 visa)

---

### Phase 2: Backend Pipeline Configuration (CORE SYSTEM)

#### Task 2.1: Expand MilestoneType Enum
**File:** `backend/app/models/milestone.py`

**Add visa-specific milestone types:**
```python
class MilestoneType(str, enum.Enum):
    # Generic (keep existing)
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
    
    # EB2/EB3 Specific
    I140_FILED = "i140_filed"
    I140_APPROVED = "i140_approved"
    I485_FILED = "i485_filed"
    BIOMETRICS_COMPLETED = "biometrics_completed"
    
    # PERM Specific
    PWD_FILED = "pwd_filed"
    PWD_APPROVED = "pwd_approved"
    PERM_FILED = "perm_filed"
    PERM_APPROVED = "perm_approved"
    
    # TN Specific
    TN_BORDER_APPOINTMENT = "tn_border_appointment"
    
    # USCIS General (keep for backward compatibility)
    FILED_WITH_USCIS = "filed_with_uscis"
    RFE_RECEIVED = "rfe_received"
    RFE_RESPONDED = "rfe_responded"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEW_COMPLETED = "interview_completed"
    
    OTHER = "other"
```

#### Task 2.2: Create Pipeline Configuration File
**File:** `backend/app/config/visa_pipelines.py` (NEW)

**Content:**
```python
from typing import Dict, Any, List
from app.models.visa import VisaTypeEnum
from app.models.milestone import MilestoneType

def get_pipeline_for_visa_type(visa_type: VisaTypeEnum) -> Dict[str, Any]:
    """Get milestone pipeline for a visa type."""
    return VISA_PIPELINES.get(visa_type, DEFAULT_PIPELINE)

def get_next_milestone(visa_type: VisaTypeEnum, completed_milestones: List[str]) -> Dict[str, Any]:
    """Get the next incomplete milestone in the pipeline."""
    pipeline = get_pipeline_for_visa_type(visa_type)
    completed_set = set(completed_milestones)
    
    for stage in pipeline["stages"]:
        if stage["milestone_type"] not in completed_set:
            return stage
    
    return None  # All milestones completed

VISA_PIPELINES = {
    VisaTypeEnum.H1B: {
        "name": "H-1B Specialty Occupation",
        "description": "Employer-sponsored temporary work visa",
        "stages": [
            {"order": 1, "milestone_type": MilestoneType.CASE_OPENED, "label": "Case Opened", "weight": 10, "required": True},
            {"order": 2, "milestone_type": MilestoneType.DOCUMENTS_REQUESTED, "label": "Documents Requested", "weight": 25, "required": True},
            {"order": 3, "milestone_type": MilestoneType.DOCUMENTS_SUBMITTED, "label": "Documents Submitted", "weight": 40, "required": True},
            {"order": 4, "milestone_type": MilestoneType.LCA_FILED, "label": "LCA Filed with DOL", "weight": 55, "required": True},
            {"order": 5, "milestone_type": MilestoneType.LCA_APPROVED, "label": "LCA Approved", "weight": 70, "required": True},
            {"order": 6, "milestone_type": MilestoneType.H1B_FILED, "label": "H-1B Petition Filed", "weight": 85, "required": True},
            {"order": 7, "milestone_type": MilestoneType.APPROVED, "label": "H-1B Approved", "weight": 100, "required": True, "terminal": True},
        ]
    },
    
    VisaTypeEnum.EB2NIW: {
        "name": "EB-2 National Interest Waiver",
        "description": "Employment-based second preference with NIW",
        "stages": [
            {"order": 1, "milestone_type": MilestoneType.CASE_OPENED, "label": "Case Opened", "weight": 10, "required": True},
            {"order": 2, "milestone_type": MilestoneType.DOCUMENTS_REQUESTED, "label": "Documents Requested", "weight": 20, "required": True},
            {"order": 3, "milestone_type": MilestoneType.DOCUMENTS_SUBMITTED, "label": "Documents Submitted", "weight": 35, "required": True},
            {"order": 4, "milestone_type": MilestoneType.I140_FILED, "label": "I-140 Filed with USCIS", "weight": 60, "required": True},
            {"order": 5, "milestone_type": MilestoneType.RFE_RECEIVED, "label": "RFE Received", "weight": 65, "required": False},
            {"order": 6, "milestone_type": MilestoneType.RFE_RESPONDED, "label": "RFE Response Submitted", "weight": 75, "required": False},
            {"order": 7, "milestone_type": MilestoneType.I140_APPROVED, "label": "I-140 Approved", "weight": 90, "required": True},
            {"order": 8, "milestone_type": MilestoneType.CASE_CLOSED, "label": "Case Closed", "weight": 100, "required": True, "terminal": True},
        ]
    },
    
    VisaTypeEnum.TN: {
        "name": "TN NAFTA Professional",
        "description": "Canadian/Mexican professional work authorization",
        "stages": [
            {"order": 1, "milestone_type": MilestoneType.CASE_OPENED, "label": "Case Opened", "weight": 15, "required": True},
            {"order": 2, "milestone_type": MilestoneType.DOCUMENTS_REQUESTED, "label": "Documents Requested", "weight": 35, "required": True},
            {"order": 3, "milestone_type": MilestoneType.DOCUMENTS_SUBMITTED, "label": "Documents Submitted", "weight": 60, "required": True},
            {"order": 4, "milestone_type": MilestoneType.TN_BORDER_APPOINTMENT, "label": "Border Appointment", "weight": 85, "required": True},
            {"order": 5, "milestone_type": MilestoneType.APPROVED, "label": "TN Approved", "weight": 100, "required": True, "terminal": True},
        ]
    },
    
    VisaTypeEnum.GREEN_CARD: {
        "name": "I-485 Adjustment of Status",
        "description": "Green Card application (Adjustment of Status)",
        "stages": [
            {"order": 1, "milestone_type": MilestoneType.CASE_OPENED, "label": "Case Opened", "weight": 10, "required": True},
            {"order": 2, "milestone_type": MilestoneType.DOCUMENTS_REQUESTED, "label": "Documents Requested", "weight": 20, "required": True},
            {"order": 3, "milestone_type": MilestoneType.DOCUMENTS_SUBMITTED, "label": "Documents Submitted", "weight": 30, "required": True},
            {"order": 4, "milestone_type": MilestoneType.I485_FILED, "label": "I-485 Filed with USCIS", "weight": 50, "required": True},
            {"order": 5, "milestone_type": MilestoneType.BIOMETRICS_COMPLETED, "label": "Biometrics Completed", "weight": 65, "required": True},
            {"order": 6, "milestone_type": MilestoneType.INTERVIEW_SCHEDULED, "label": "Interview Scheduled", "weight": 75, "required": False},
            {"order": 7, "milestone_type": MilestoneType.INTERVIEW_COMPLETED, "label": "Interview Completed", "weight": 85, "required": False},
            {"order": 8, "milestone_type": MilestoneType.APPROVED, "label": "Green Card Approved", "weight": 100, "required": True, "terminal": True},
        ]
    },
}

# Default pipeline for undefined visa types
DEFAULT_PIPELINE = {
    "name": "Standard Immigration Process",
    "description": "Generic immigration case workflow",
    "stages": [
        {"order": 1, "milestone_type": MilestoneType.CASE_OPENED, "label": "Case Opened", "weight": 15, "required": True},
        {"order": 2, "milestone_type": MilestoneType.DOCUMENTS_REQUESTED, "label": "Documents Requested", "weight": 30, "required": True},
        {"order": 3, "milestone_type": MilestoneType.DOCUMENTS_SUBMITTED, "label": "Documents Submitted", "weight": 50, "required": True},
        {"order": 4, "milestone_type": MilestoneType.FILED_WITH_USCIS, "label": "Filed with USCIS", "weight": 75, "required": True},
        {"order": 5, "milestone_type": MilestoneType.APPROVED, "label": "Approved", "weight": 100, "required": True, "terminal": True},
    ]
}
```

**Note:** Add pipelines for other visa types (EB2, EB3, PERM, L1, O1, etc.) as needed.

#### Task 2.3: Create Progress Calculation Endpoint
**File:** `backend/app/api/v1/case_groups.py`

**Add new endpoint:**
```python
@router.get("/{case_group_id}/progress")
def get_case_group_progress(
    *,
    db: Session = Depends(get_db),
    case_group_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """
    Calculate progress for ALL visa applications in case group.
    Each visa has its own pipeline based on visa_type.
    Returns aggregate progress for case group.
    """
    from app.config.visa_pipelines import get_pipeline_for_visa_type
    
    # Get case group with permissions check
    case_group = db.query(CaseGroup).filter(CaseGroup.id == case_group_id).first()
    if not case_group:
        raise HTTPException(status_code=404, detail="Case group not found")
    
    # Check permissions (same logic as get_case_group)
    # ... (copy permission checks from existing endpoint)
    
    if not case_group.applications:
        return {
            "case_group_id": case_group_id,
            "overall_percentage": 0,
            "overall_stage": "No visa applications",
            "visa_applications": []
        }
    
    visa_progress_list = []
    total_progress = 0
    
    # Calculate progress for EACH visa application
    for visa_app in case_group.applications:
        # Get pipeline config for THIS visa type
        pipeline = get_pipeline_for_visa_type(visa_app.visa_type)
        
        # Get milestones for THIS visa app only
        milestones = db.query(ApplicationMilestone).filter(
            ApplicationMilestone.visa_application_id == visa_app.id
        ).all()
        
        completed_types = {m.milestone_type for m in milestones}
        
        # Calculate progress
        max_weight = 0
        current_stage_label = "Not Started"
        next_stage = None
        pipeline_with_status = []
        
        for stage in pipeline["stages"]:
            is_completed = stage["milestone_type"] in completed_types
            
            if is_completed and stage["weight"] > max_weight:
                max_weight = stage["weight"]
                current_stage_label = stage["label"]
            
            # Find completion date
            completion_date = None
            if is_completed:
                for m in milestones:
                    if m.milestone_type == stage["milestone_type"]:
                        completion_date = m.milestone_date.isoformat()
                        break
            
            pipeline_with_status.append({
                "order": stage["order"],
                "milestone_type": stage["milestone_type"],
                "label": stage["label"],
                "description": stage.get("description"),
                "weight": stage["weight"],
                "required": stage["required"],
                "terminal": stage.get("terminal", False),
                "completed": is_completed,
                "completion_date": completion_date,
            })
            
            # Track next incomplete stage
            if not is_completed and next_stage is None:
                next_stage = stage["label"]
        
        visa_progress_list.append({
            "visa_application_id": visa_app.id,
            "visa_type": visa_app.visa_type,
            "petition_type": visa_app.petition_type,
            "visa_status": visa_app.status,
            "case_status": visa_app.visa_case_status,
            "percentage": max_weight,
            "current_stage": current_stage_label,
            "next_stage": next_stage,
            "pipeline_name": pipeline["name"],
            "pipeline": pipeline_with_status,
        })
        
        total_progress += max_weight
    
    # Overall case group progress = average of all visa apps
    overall_percentage = total_progress // len(case_group.applications) if case_group.applications else 0
    
    # Determine overall stage description
    if overall_percentage == 100:
        overall_stage = "Complete"
    elif overall_percentage >= 80:
        overall_stage = "Nearing Completion"
    elif overall_percentage >= 50:
        overall_stage = "In Progress"
    elif overall_percentage >= 25:
        overall_stage = "Early Stage"
    else:
        overall_stage = "Getting Started"
    
    return {
        "case_group_id": case_group_id,
        "overall_percentage": overall_percentage,
        "overall_stage": overall_stage,
        "visa_applications": visa_progress_list,
    }
```

#### Task 2.4: Create Available Milestones Endpoint
**File:** `backend/app/api/v1/visa_applications.py`

**Add endpoint to get milestones available for a visa:**
```python
@router.get("/{visa_application_id}/available-milestones")
def get_available_milestones(
    *,
    db: Session = Depends(get_db),
    visa_application_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """
    Get available milestone types for this visa application based on its visa type.
    Returns the full pipeline with status (completed/incomplete).
    """
    from app.config.visa_pipelines import get_pipeline_for_visa_type
    
    visa_app = db.query(VisaApplication).filter(VisaApplication.id == visa_application_id).first()
    if not visa_app:
        raise HTTPException(status_code=404, detail="Visa application not found")
    
    # Permission check
    # ... (same as other visa app endpoints)
    
    # Get pipeline for this visa type
    pipeline = get_pipeline_for_visa_type(visa_app.visa_type)
    
    # Get completed milestones
    milestones = db.query(ApplicationMilestone).filter(
        ApplicationMilestone.visa_application_id == visa_application_id
    ).all()
    completed_types = {m.milestone_type for m in milestones}
    
    # Return pipeline with completion status
    available_milestones = []
    for stage in pipeline["stages"]:
        available_milestones.append({
            "milestone_type": stage["milestone_type"],
            "label": stage["label"],
            "description": stage.get("description"),
            "required": stage["required"],
            "completed": stage["milestone_type"] in completed_types,
        })
    
    return {
        "visa_application_id": visa_application_id,
        "visa_type": visa_app.visa_type,
        "pipeline_name": pipeline["name"],
        "milestones": available_milestones,
    }
```

#### Task 2.5: Update Database Schema
**Run database reset:**
```bash
cd backend
python scripts/setup_dev_environment.py
```

**Why:** New MilestoneType enum values need to be in database.

---

### Phase 3: Frontend Integration (CONNECT TO API)

#### Task 3.1: Add API Client Methods
**File:** `frontend/lib/api.ts`

**Add to caseGroupsAPI:**
```typescript
export const caseGroupsAPI = {
  // ... existing methods ...
  
  getProgress: async (caseGroupId: string) => {
    const response = await api.get(`/case-groups/${caseGroupId}/progress`)
    return response.data
  },
}

// Add new visaApplicationsAPI if it doesn't exist
export const visaApplicationsAPI = {
  getAvailableMilestones: async (visaAppId: string) => {
    const response = await api.get(`/visa-applications/${visaAppId}/available-milestones`)
    return response.data
  },
}
```

#### Task 3.2: Update Case Details Page Progress Calculation
**File:** `frontend/app/cases/[id]/page.tsx`

**Replace hardcoded `calculateProgress()` with API call:**

```typescript
// REMOVE the entire calculateProgress() function (lines ~310-370)

// ADD state for progress data
const [progressData, setProgressData] = useState<any>(null)
const [progressLoading, setProgressLoading] = useState(true)

// ADD useEffect to fetch progress
useEffect(() => {
  if (caseGroup?.id) {
    setProgressLoading(true)
    caseGroupsAPI.getProgress(caseGroup.id)
      .then(data => {
        setProgressData(data)
        setProgressLoading(false)
      })
      .catch(err => {
        console.error('Failed to fetch progress:', err)
        setProgressLoading(false)
      })
  }
}, [caseGroup?.id])

// UPDATE Case Progress card to use API data
{progressLoading ? (
  <div>Loading progress...</div>
) : progressData ? (
  <Card>
    <CardHeader>
      <CardTitle>Case Progress</CardTitle>
      <CardDescription>
        {progressData.overall_percentage}% Complete - {progressData.overall_stage}
      </CardDescription>
    </CardHeader>
    <CardContent>
      {/* Show progress for EACH visa application */}
      {progressData.visa_applications.map((visa: any) => (
        <div key={visa.visa_application_id} className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <div>
              <div className="font-semibold">{visa.pipeline_name}</div>
              <div className="text-sm text-muted-foreground">
                {visa.petition_type} - {visa.percentage}% Complete
              </div>
            </div>
            <Badge variant={visa.percentage === 100 ? "success" : "default"}>
              {visa.current_stage}
            </Badge>
          </div>
          
          {/* Progress bar */}
          <div className="h-2 bg-gray-200 rounded-full mb-3">
            <div 
              className="h-full bg-blue-600 rounded-full transition-all"
              style={{ width: `${visa.percentage}%` }}
            />
          </div>
          
          {/* Pipeline stages */}
          <div className="space-y-2">
            {visa.pipeline.map((stage: any) => (
              <div key={stage.order} className="flex items-center gap-3">
                <div className={`w-4 h-4 rounded-full flex-shrink-0 ${
                  stage.completed 
                    ? 'bg-green-500' 
                    : stage.order === visa.pipeline.find((s: any) => !s.completed)?.order
                      ? 'bg-blue-500'
                      : 'bg-gray-300'
                }`} />
                
                <div className="flex-1">
                  <div className="text-sm font-medium">{stage.label}</div>
                  {stage.completed && stage.completion_date && (
                    <div className="text-xs text-muted-foreground">
                      {new Date(stage.completion_date).toLocaleDateString()}
                    </div>
                  )}
                </div>
                
                {!stage.required && (
                  <Badge variant="outline" className="text-xs">Optional</Badge>
                )}
              </div>
            ))}
          </div>
          
          {/* Next step indicator */}
          {visa.next_stage && (
            <div className="mt-3 p-3 bg-blue-50 rounded-lg">
              <div className="text-sm font-medium text-blue-900">Next Step</div>
              <div className="text-sm text-blue-700">{visa.next_stage}</div>
            </div>
          )}
        </div>
      ))}
    </CardContent>
  </Card>
) : (
  <div>No progress data available</div>
)}
```

#### Task 3.3: Remove Debug Console Logs
**File:** `frontend/app/cases/[id]/page.tsx`

Remove any `console.log` statements added during debugging.

---

### Phase 4: Testing & Validation

#### Task 4.1: Backend API Testing
Test with curl or Postman:

```bash
# Get progress for Luis's case (EB2-NIW with I-140 + I-485)
curl http://localhost:8000/api/v1/case-groups/{luis_case_id}/progress \
  -H "Authorization: Bearer {token}"

# Expected: 2 visa applications, each with its own pipeline

# Get available milestones for an I-140 visa application
curl http://localhost:8000/api/v1/visa-applications/{i140_id}/available-milestones \
  -H "Authorization: Bearer {token}"

# Expected: I-140 specific milestones (not H1B milestones)
```

#### Task 4.2: Frontend UI Testing
1. Navigate to Luis's case details page
2. Verify progress shows TWO visa applications (I-140 and I-485)
3. Each visa should show its own pipeline with different stages
4. Verify percentages are accurate based on milestones
5. Check mobile responsive layout

#### Task 4.3: Test Multiple Visa Types
- H1B case (Jacob) - should show LCA milestones, not USCIS filing
- EB2-NIW case (Luis) - should show I-140 specific milestones
- Test with case that has no milestones yet (0% progress)

#### Task 4.4: Edge Cases
- Case group with no visa applications
- Visa application with completed terminal milestone (approved/denied)
- Visa with optional milestones (RFE) - should skip if not completed

---

## 🚀 Execution Order

**Week 1: Frontend Fixes**
1. Task 1.1 - Redesign header (2-3 hours)
2. Task 1.2 - Add edit buttons (1 hour)
3. Task 1.3 - Test frontend (1 hour)
4. Commit and push

**Week 2: Backend Pipeline System**
5. Task 2.1 - Expand MilestoneType (30 min)
6. Task 2.2 - Create visa_pipelines.py (2 hours)
7. Task 2.3 - Progress endpoint (2-3 hours)
8. Task 2.4 - Available milestones endpoint (1 hour)
9. Task 2.5 - Database reset (5 min)
10. Test backend with curl (1 hour)

**Week 3: Frontend Integration**
11. Task 3.1 - API client methods (30 min)
12. Task 3.2 - Update progress UI (2-3 hours)
13. Task 3.3 - Clean up debug logs (15 min)
14. Task 4.1-4.4 - Full testing (2 hours)
15. Final commit and push

**Total Estimated Time:** 15-20 hours spread over 3 weeks

---

## ✅ Success Criteria

1. **No more hardcoded pipeline** - Frontend fetches progress from API
2. **Visa-specific milestones** - H1B shows LCA stages, EB2-NIW shows I-140 stages
3. **Per-visa progress** - Each visa in case group shows its own percentage
4. **Accurate progress** - Percentages match actual milestone completion
5. **Better UX** - Users see "what's next" for their specific visa type
6. **Role-based editing** - Edit buttons respect user permissions

---

## 📚 References

- **Design Rationale:** `VISA_PIPELINE_SYSTEM_DESIGN.md`
- **Data Model:** `DATA_MODEL.md`
- **API Reference:** `API_REFERENCE.md`
- **Development Guidelines:** `AI_DEVELOPMENT_GUIDELINES.md`

---

## 🔧 Troubleshooting

**Issue:** Database errors after adding new MilestoneType values  
**Solution:** Run `python scripts/setup_dev_environment.py` to reset database

**Issue:** Frontend shows "undefined" for progress  
**Solution:** Check browser console for API errors, verify token is valid

**Issue:** Progress calculation returns 0% for completed case  
**Solution:** Verify milestones exist in database, check visa_application_id foreign key

**Issue:** Pipeline shows wrong milestones for visa type  
**Solution:** Verify visa_type field in VisaApplication matches VisaTypeEnum value

---

**Last Updated:** November 11, 2025  
**Next Review:** After Phase 1 completion
