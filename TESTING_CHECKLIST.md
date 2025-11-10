# Testing Checklist - Case Approval Workflow

## Before Testing
- [ ] Backend server is running: `cd backend && ./start_server.sh`
- [ ] Frontend server is running: `cd frontend && npm run dev`
- [ ] Database has test data: `cd backend && python scripts/setup_dev_environment.py`

## Test Accounts
- **PM Account**: `pm@ama-impact.com` / `PM123!`
- **Manager Account**: Any manager (e.g., `arnaud.borner@ama-inc.com` / `TempPassword123!`)
- **HR Account**: `hr@ama-impact.com` / `HR123!`

## Test Scenarios

### 1. Manager Creates Draft Case
- [ ] Login as Manager
- [ ] Navigate to `/cases`
- [ ] Check if "New Case" button is visible
- [ ] (Note: Case creation page not yet built - use database directly for now)

### 2. Manager Submits Case for Approval
- [ ] Login as Manager
- [ ] Find a case with status "DRAFT"
- [ ] Click on the case to view details
- [ ] Verify "Submit for Approval" button is visible
- [ ] Click "Submit for Approval"
- [ ] Verify case status changes to "PENDING_PM_APPROVAL"

### 3. PM Approves Case (PRIMARY TEST)
- [ ] Login as PM (`pm@ama-impact.com` / `PM123!`)
- [ ] Navigate to `/cases`
- [ ] Filter for "Pending Approval" (click on yellow stat card)
- [ ] Click on a pending case
- [ ] Verify "Approve" and "Reject" buttons are visible
- [ ] Click "Approve" button
- [ ] Verify dialog opens with:
  - [ ] Title: "Approve Case"
  - [ ] HR User dropdown with real users loaded
  - [ ] Law Firm dropdown with real firms loaded
  - [ ] Optional notes textarea
- [ ] Test validation:
  - [ ] Click "Approve & Assign" without selecting HR user → Should show alert
  - [ ] Select HR user, click "Approve & Assign" without law firm → Should show alert
- [ ] Select both HR user and law firm
- [ ] Optionally add approval notes
- [ ] Click "Approve & Assign"
- [ ] Verify dialog closes
- [ ] Verify case status updates to "PM_APPROVED"
- [ ] Verify approval info banner shows:
  - [ ] "Approved by [PM Name]"
  - [ ] Approval notes (if provided)
  - [ ] Approval timestamp
- [ ] Check "Team Members" section shows assigned HR user

### 4. PM Rejects Case
- [ ] Login as PM
- [ ] Find a case with status "PENDING_PM_APPROVAL"
- [ ] Click "Reject" button
- [ ] Verify dialog opens with:
  - [ ] Title: "Reject Case"
  - [ ] Rejection reason textarea (required)
- [ ] Test validation:
  - [ ] Click "Reject" without notes → Should show alert
- [ ] Add rejection reason
- [ ] Click "Reject"
- [ ] Verify case status updates to "PM_REJECTED"
- [ ] Verify rejection info banner shows in red

### 5. Permission Checks
- [ ] Login as Beneficiary account
- [ ] Navigate to a case
- [ ] Verify NO approval buttons are visible
- [ ] Login as HR
- [ ] Verify "Submit for Approval" button visible for drafts
- [ ] Verify NO "Approve/Reject" buttons visible

## Browser Console Checks

Open browser developer tools (F12) and check for:
- [ ] No error messages in Console tab
- [ ] Network tab shows successful API calls:
  - [ ] `GET /api/v1/users/?role=HR` returns 200
  - [ ] `GET /api/v1/law-firms/` returns 200
  - [ ] `POST /api/v1/case-groups/{id}/approve` returns 200
- [ ] Console logs show:
  ```
  Current user loaded: [email] Role: [role]
  Case loaded: [case object]
  ```

## Backend Verification

After approval, check database:
```bash
cd backend
sqlite3 devel.db

-- Check case was approved
SELECT id, case_number, approval_status, approved_by_pm_id, 
       responsible_party_id, law_firm_id, pm_approval_date
FROM case_groups 
WHERE approval_status = 'PM_APPROVED';

-- Check todos were created
SELECT id, title, assigned_to_user_id, due_date, status
FROM todos
WHERE case_group_id = '[case_id]';

-- Check audit logs were created
SELECT id, action, resource_type, resource_id, user_id, timestamp, new_values
FROM audit_logs
WHERE resource_type = 'case_group' AND resource_id = '[case_id]'
ORDER BY timestamp DESC
LIMIT 5;
```

Expected:
- [ ] `approval_status` = `PM_APPROVED`
- [ ] `approved_by_pm_id` is set to PM's user ID
- [ ] `responsible_party_id` is set to selected HR user ID
- [ ] `law_firm_id` is set to selected law firm ID
- [ ] `pm_approval_date` has timestamp
- [ ] Two todos created:
  1. "Schedule Pre-Filing Meeting" (due 7 days)
  2. "Schedule Law Firm Consultation" (due 14 days)
- [ ] Audit logs show CREATE, UPDATE, and approval actions

### Test Timeline Endpoint (Backend API)
```bash
# Get auth token
TOKEN=$(curl -s -X POST http://localhost:7001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"pm@ama-impact.com","password":"PM123!"}' | jq -r .access_token)

# Test timeline endpoint
curl -s http://localhost:7001/api/v1/case-groups/1/timeline \
  -H "Authorization: Bearer $TOKEN" | jq

# Expected response:
# {
#   "case_group_id": 1,
#   "total_events": N,
#   "events": [
#     {
#       "event_type": "case_approved",
#       "timestamp": "2025-11-05T12:00:00Z",
#       "user_name": "Program Manager",
#       "title": "Case Approved",
#       "description": "Case approved by PM with HR and law firm assignment"
#     },
#     ...
#   ]
# }
```

## Known Limitations (Not Yet Implemented)
- Case creation page (using database seed data for now)
- Case edit functionality
- Timeline view UI component (backend `/case-groups/{id}/timeline` endpoint exists)
- Documents upload
- Comments/notes system

## If Something Breaks

### Frontend errors?
```bash
cd frontend
npm run dev
# Check terminal for errors
# Check browser console for errors
```

### Backend errors?
```bash
cd backend
# Check terminal running uvicorn for errors
# Check if port 8001 is in use
```

### No data showing?
```bash
cd backend
python scripts/setup_dev_environment.py
# This resets everything and adds fresh test data
```

### Dropdown backgrounds transparent?
- Check SelectTrigger has `className="bg-white"` or `className="w-full bg-white"`
- This is a known issue documented in AI_DEVELOPMENT_GUIDELINES.md

## Success Criteria
✅ All test scenarios pass
✅ No console errors
✅ Database reflects correct state after approval
✅ Todos are auto-created
✅ UI updates in real-time after approval/rejection
