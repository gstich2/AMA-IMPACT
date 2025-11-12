# AMA-IMPACT Development Guidelines - AI Reference Document

**CRITICAL: Read this EVERY time before making changes!**

---

## 1. Database Management - NO ALEMBIC IN ALPHA

### ❌ NEVER DO:
- Run alembic migrations
- Suggest `alembic upgrade head`
- Create new migration files
- Mention database migration strategies

### ✅ ALWAYS DO:
```bash
cd backend
python scripts/setup_dev_environment.py
```

**This script does EVERYTHING:**
- Deletes old database (`devel.db`)
- Creates fresh schema from SQLAlchemy models
- Seeds ALL fixtures in correct order:
  1. Visa types (14 types)
  2. Contracts (ASSESS, RSES)
  3. Law firms
  4. Development data (users, beneficiaries, cases, todos)

**When schema changes:** Just run `setup_dev_environment.py` - NO migrations needed!

---

## 2. No Sample/Mock Data in Frontend

### ❌ NEVER DO:
```typescript
// DON'T DO THIS!
const mockUsers = [
  { id: 1, name: "John Doe" },
  { id: 2, name: "Jane Smith" }
]
```

### ✅ ALWAYS DO:
1. **Missing data?** → Add to backend fixtures:
   - `backend/scripts/fixtures/seed_visa_types.py`
   - `backend/scripts/fixtures/contracts/seed_assess.py`
   - `backend/scripts/fixtures/contracts/seed_rses.py`
   - `backend/scripts/fixtures/seed_development_data.py`
   - `backend/scripts/fixtures/seed_law_firms.py`

2. **BEFORE modifying backend scripts:**
   - ✅ Read the entire file first
   - ✅ Understand existing data structure
   - ✅ Confirm changes won't break existing data
   - ✅ Preserve NASA Ames structure (13 departments)
   - ✅ Ask user to confirm if unsure about changes
   - ❌ NEVER blindly modify fixtures without understanding context

3. **Then reset database:**
   ```bash
   cd backend
   python scripts/setup_dev_environment.py
   ```

4. **Frontend fetches real data:**
   ```typescript
   const data = await someAPI.getAll()
   // Use actual API responses, never hardcoded data
   ```

**Display Labels vs Data:**
- ✅ OK: Label/badge mappings for display (e.g., status colors, priority labels)
- ❌ NOT OK: Arrays of objects with sample names, dates, details

---

## 3. UI Components - Common Issues

### ⚠️ RECURRING: Dropdown Transparency Problem

**Problem:** Select dropdowns render with transparent background, making text unreadable.

**Solution:** ALWAYS add `bg-white` or `bg-background` class to SelectTrigger:
```typescript
<SelectTrigger className="bg-white">  // ← REQUIRED!
  <SelectValue placeholder="..." />
</SelectTrigger>
```

**Check before committing:**
- [ ] All `<SelectTrigger>` components have background class
- [ ] Dropdowns are readable in both light and dark themes

---

## 4. NASA Ames Organizational Structure - NEVER SIMPLIFY

### ⚠️ CRITICAL: This is the COMPLETE structure. DO NOT MODIFY.

**13 Departments Total (4 L1 + 9 L2):**

#### L1: Entry Systems and Technology Division (TS)
- Manager: Dave Cornelius / PM (pm.assess@ama-impact.com)
- **L2: TSM** - Thermal Protection Materials Branch
  - Manager: Arnaud Borner (arnaud.borner@ama-inc.com)
- **L2: TSA** - Aerothermodynamics Branch
  - Manager: Bhaskaran Rathakrishnan (bhaskaran.rathakrishnan@ama-inc.com)
- **L2: TSF** - Thermo-Physics Facilities Branch
  - No manager assigned
- **L2: TSS** - Entry Systems and Vehicle Development Branch
  - Manager: Blake Hannah (blake.hannah@ama-inc.com) ⭐ DUAL ROLE

#### L1: NASA Advanced Supercomputing Division (TN) - Parent Dept
- **L2: TNA** - Computational Aerosciences Branch
  - Manager: Gerrit-Daniel Stich (gerrit-daniel.stich@ama-inc.com) ⭐ DUAL ROLE
- **L2: TNP** - Computational Physics Branch
  - Manager: Patricia Ventura Diaz (patricia.ventura@ama-inc.com)

#### L1: Aeronautics Directorate (A) - Parent Dept
- **L2: AV** - Aeromechanics Office
  - Manager: Gerrit-Daniel Stich (gerrit-daniel.stich@ama-inc.com) ⭐ DUAL ROLE
- **L2: AA** - Systems Analysis Office
  - Manager: Blake hannah (blake.hannah@ama-inc.com) ⭐ DUAL ROLE

#### L1: Aeroflightdynamics Directorate (Y) - Parent Dept (US Army)
- **L2: YA** - Computational Aeromechanics Tech Area
  - Manager: Shirzad Hoseinverdy (shirzad.hoseinverdy@ama-inc.com)

**Dual Role Managers:**
- Blake Hannah: TSS + AA
- Gerrit-Daniel Stich: TNA + AV


## 4. Documentation Style - Alpha Stage

### ❌ NEVER DO:
- Include "AI-generated" disclaimers
- Keep historical change logs ("Added on 2024-01-15 by AI")
- Document every single change
- Write in first person ("I added this feature")
- Include migration histories

### ✅ ALWAYS DO:
- Write as if a senior developer wrote it
- **Current state documentation only**
- Focus on:
  - What exists NOW
  - How to use it NOW
  - What it does NOW
- Use present tense: "The system provides..." not "We added..."
- Be concise and practical

**Good Documentation Example:**
```markdown
## Case Tracking

The case tracking system manages immigration cases through an approval workflow.

### Features
- List view with comprehensive filtering
- Role-based approval workflow (Manager → PM)
- Case detail view with beneficiary information

### Usage
Navigate to `/cases` to view all cases. Managers can create cases and submit for PM approval.
```

**Bad Documentation Example:**
```markdown
## Case Tracking (Added by AI on Nov 10, 2025)

We have implemented a case tracking system with the following history:
- v1.0: Initial implementation with basic CRUD
- v1.1: Added approval workflow (AI-generated)
- v1.2: Fixed bugs in approval dialog

[AI Note: This was created using GPT-4...]
```

---

## 5. Project Structure Quick Reference

### Backend


TODO CHECK AGAIN WAS UPDATED 

### Frontend

TODO CHECK AGAIN WAS UPDATED 

## 6. Common Tasks - Copy/Paste Commands

### Reset Entire Database
```bash
cd backend
python scripts/setup_dev_environment.py
```

### Start Backend Server
check if backend is running on 7001 in background terminal, if not tell me to do it 

### Start Frontend Dev Server
Ask me to restart it in 3000 port if needed 

### Verify NASA Structure
```bash
cd backend
sqlite3 devel.db "SELECT code, name, level FROM departments WHERE contract_id IN (SELECT id FROM contracts WHERE code='ASSESS') ORDER BY level, code;"
```

### Check All Managers
```bash
cd backend
sqlite3 devel.db "SELECT email, full_name, role FROM users WHERE role='MANAGER' ORDER BY email;"
```

---

## 7. API Client Pattern


## 8. User Roles and Permissions

| Role | Can Do |
|------|--------|
| **ADMIN** | Everything (system-wide) |
| **PM** | Approve/reject cases, view all contracts |
| **MANAGER** | Create cases, submit for approval, manage team |
| **HR** | Create cases, manage beneficiaries |
| **BENEFICIARY** | View own visa applications, todos |

---

## 9. Important Files to NEVER Modify Carelessly

1. **`backend/scripts/fixtures/contracts/seed_assess.py`**
   - Contains complete NASA structure
   - Has warnings: "⚠️ CRITICAL: DO NOT SIMPLIFY"

2. **`NASA_AMES_ORGANIZATIONAL_STRUCTURE.md`**
   - Authoritative reference for structure
   - Created to prevent future loss

3. **`backend/app/models/`**
   - Schema changes require DB reset
   - Always test with `setup_dev_environment.py`

---

## 10. Workflow - Adding New Features

1. **Backend Model Change?**
   ```bash
   # Edit model in backend/app/models/
   cd backend
   python scripts/setup_dev_environment.py  # Rebuilds schema
   ```

2. **Need Sample Data?**
   ```bash
   # Edit appropriate fixture file
   # backend/scripts/fixtures/seed_development_data.py
   cd backend
   python scripts/setup_dev_environment.py  # Re-seeds data
   ```

3. **Frontend Page?**
   - Create in `frontend/app/`
   - Add API client to `frontend/lib/api.ts`
   - Use real API calls, NO mock data
   - Use AppLayout wrapper

4. **Test Everything:**
   ```bash
   # Terminal 1: Backend
   cd backend && ./start_server.sh
   
   # Terminal 2: Frontend
   cd frontend && npm run dev
   
   # Terminal 3: Check DB
   cd backend && sqlite3 devel.db
   ```

---

## 11. Git Commit Messages (for reference, not rules)

Keep them descriptive but concise:
```
feat: Add case approval workflow with PM/Manager roles
fix: Correct NASA Ames department parent relationships
docs: Update API reference for case endpoints
refactor: Simplify department tree query logic
```

---

## 12. When Things Break

### "Table doesn't exist" error?
```bash
cd backend
python scripts/setup_dev_environment.py
```

### "No data showing" in frontend?
```bash
# 1. Check backend is running
cd backend && ./start_server.sh

# 2. Check database has data
cd backend
sqlite3 devel.db "SELECT COUNT(*) FROM users;"

# 3. If empty, reseed
python scripts/setup_dev_environment.py
```

### "Import error" in Python?
```bash
cd backend
source .venv/bin/activate  # or venv/Scripts/activate on Windows
pip install -r requirements.txt
```

### "Module not found" in Next.js?
```bash
cd frontend
npm install
```

---

## 13. Key Passwords for Testing

**PM account:**
- Email: `pm.assess@ama-impact.com`
- Password: `TempPassword123!`
- force_password_change: `True` (will prompt on first login)

**All ASSESS beneficiaries:**
- Password: `Dev123!`
- force_password_change: `False` (for testing convenience)

**All other manager accounts:**
- Password: `TempPassword123!`
- force_password_change: `True` (will prompt on first login)

**Development accounts (seed_development_data.py):**
- Password: `Ben123!` (beneficiaries)
- Password: `HR123!` (hr@ama-impact.com)
- Password: `PM123!` (pm@ama-impact.com)

**Admin:**
- Email: `admin@ama-impact.com`
- Password: `Admin123!`

---

## REMEMBER:
1. ✅ Always use `setup_dev_environment.py` for DB changes
2. ✅ Never hardcode data in frontend
3. ✅ Never simplify NASA structure (13 departments!)
4. ✅ Write docs like a senior dev, present tense, current state only
5. ✅ Add API endpoints to `lib/api.ts`
6. ✅ Test with real backend data

**When in doubt: Reset the database and start fresh!**
