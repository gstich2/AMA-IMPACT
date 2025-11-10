# NASA Ames Research Center - ASSESS Contract Organizational Structure

**⚠️ CRITICAL: This is the COMPLETE NASA Ames organizational hierarchy. DO NOT SIMPLIFY.**

Last Updated: 2025-11-10  
Database: Restored and committed to git  
Fixture: `backend/scripts/fixtures/contracts/seed_assess.py`

---

## Complete Structure (13 Departments)

### L1: Entry Systems and Technology Division (TS)
**Manager:** David Chen (techlead.assess@ama-impact.com)

- **L2: TSM** - Thermal Protection Materials Branch  
  **Manager:** Arnaud Borner (arnaud.borner@ama-inc.com)

- **L2: TSA** - Aerothermodynamics Branch  
  **Manager:** Bhaskaran Rathakrishnan (bhaskaran.rathakrishnan@ama-inc.com)

- **L2: TSF** - Thermo-Physics Facilities Branch  
  **Manager:** (No manager assigned)

- **L2: TSS** - Entry Systems and Vehicle Development Branch  
  **Manager:** Blake Lively (blake.lively@ama-inc.com) ⭐ *Dual role*

---

### L1: NASA Advanced Supercomputing Division (TN)
**Type:** Parent department (no direct manager)

- **L2: TNA** - Computational Aerosciences Branch  
  **Manager:** Gerrit-Daniel Stich (gerrit-daniel.stich@ama-inc.com) ⭐ *Dual role*

- **L2: TNP** - Computational Physics Branch  
  **Manager:** Patricia Ventura Diaz (patricia.ventura@ama-inc.com)

---

### L1: Aeronautics Directorate (A)
**Type:** Parent department (no direct manager)

- **L2: AV** - Aeromechanics Office  
  **Manager:** Gerrit-Daniel Stich (gerrit-daniel.stich@ama-inc.com) ⭐ *Dual role*

- **L2: AA** - Systems Analysis Office  
  **Manager:** Blake Lively (blake.lively@ama-inc.com) ⭐ *Dual role*

---

### L1: Aeroflightdynamics Directorate (Y)
**Type:** Parent department (no direct manager) - **US Army**

- **L2: YA** - Computational Aeromechanics Tech Area  
  **Manager:** Shirzad Hoseinverdy (shirzad.hoseinverdy@ama-inc.com)

---

## Manager Summary

### Department Managers (6 total)

1. **David Chen** - TS Division Manager (techlead.assess@ama-impact.com)
2. **Arnaud Borner** - TSM Manager (arnaud.borner@ama-inc.com)
3. **Bhaskaran Rathakrishnan** - TSA Manager (bhaskaran.rathakrishnan@ama-inc.com)
4. **Blake Lively** - TSS & AA Manager (blake.lively@ama-inc.com) - **DUAL ROLE**
5. **Patricia Ventura Diaz** - TNP Manager (patricia.ventura@ama-inc.com)
6. **Gerrit-Daniel Stich** - TNA & AV Manager (gerrit-daniel.stich@ama-inc.com) - **DUAL ROLE**
7. **Shirzad Hoseinverdy** - YA Manager (shirzad.hoseinverdy@ama-inc.com)

**All passwords:** `TempPassword123!` with `force_password_change=True`

### Dual Role Managers

- **Blake Lively** manages both:
  - TSS (Entry Systems and Vehicle Development Branch) under TS
  - AA (Systems Analysis Office) under A

- **Gerrit-Daniel Stich** manages both:
  - TNA (Computational Aerosciences Branch) under TN
  - AV (Aeromechanics Office) under A

---

## Department Statistics

- **Total Departments:** 13
- **L1 (Top Level):** 4 departments (TS, TN, A, Y)
- **L2 (Children):** 9 departments
- **Departments with Managers:** 10
- **Departments without Managers:** 3 (TN, A, Y parent depts + TSF)

---

## Database Verification

Run this query to verify the structure:

```sql
SELECT 
    'L' || d.level || ': ' || d.code as Dept,
    d.name as Name,
    COALESCE(u.full_name, '(no manager)') as Manager,
    COALESCE(p.code, '(top level)') as Parent
FROM departments d
LEFT JOIN users u ON d.manager_id = u.id
LEFT JOIN departments p ON d.parent_id = p.id
WHERE d.contract_id IN (SELECT id FROM contracts WHERE code='ASSESS')
ORDER BY d.level, d.code;
```

Expected output: 13 rows (4 L1 + 9 L2)

---

## Historical Notes

**2025-11-10:** Complete structure restored from user specifications.
- Previously had only 9 departments (missing TN, A, Y parents and AA, YA children)
- TNA, TNP, AV were incorrectly at L1 (should be L2 under TN and A)
- TNC (Advanced Computing Branch) removed - not in requirements
- All 6 department managers created and assigned
- Documentation updated in README files

**⚠️ WARNING:** This structure was lost multiple times in the past. It has now been:
1. Committed to git with detailed commit message
2. Documented in backend/scripts/README.md
3. Documented in backend/scripts/fixtures/README.md
4. Documented in this file
5. Includes warnings in seed_assess.py to prevent future simplification

---

## Files Modified

- `backend/scripts/fixtures/contracts/seed_assess.py` - Complete 13-department structure
- `backend/scripts/README.md` - Updated with full hierarchy and manager list
- `backend/scripts/fixtures/README.md` - Updated with detailed structure
- This file (`NASA_AMES_ORGANIZATIONAL_STRUCTURE.md`) - Reference documentation

---

## Reset Instructions

To reset the database with this complete structure:

```bash
cd backend
python scripts/setup_dev_environment.py
```

This will create all 13 departments with proper L1/L2 hierarchy and all 6 manager users.
