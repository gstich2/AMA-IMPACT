# Fixtures System

Modular database fixtures for AMA-IMPACT.

## Overview

Fixtures are organized by responsibility:
- **Global resources**: Visa types, law firms (shared across contracts)
- **Contract-specific**: Each contract has its own setup file
- **Development data**: Test beneficiaries, cases, todos

## Structure

```
fixtures/
├── README.md                     # This file
├── seed_visa_types.py            # Global: 14 visa type definitions
├── seed_law_firms.py             # Global: Law firm vendors
├── contracts/                    # Contract-specific setups
│   ├── seed_assess.py            # ASSESS contract + depts + PM/Manager
│   └── seed_rses.py              # RSES contract + depts + PM
└── seed_development_data.py      # Test data: beneficiaries, cases, todos
```

## Running Fixtures

**All fixtures (recommended):**
```bash
cd backend
python scripts/setup_dev_environment.py
```

**Individual fixtures:**
```bash
cd backend
python scripts/fixtures/seed_visa_types.py
python scripts/fixtures/contracts/seed_assess.py
python scripts/fixtures/contracts/seed_rses.py
python scripts/fixtures/seed_law_firms.py
python scripts/fixtures/seed_development_data.py
```

## Contract Fixtures (contracts/)

Each contract fixture is self-contained and creates:
1. **Contract** - Name, code, dates, client info
2. **Departments** - Organizational hierarchy
3. **Program Manager** - With `force_password_change=True`
4. **Managers** - Department leads with `force_password_change=True`

### ASSESS Contract
```bash
python scripts/fixtures/contracts/seed_assess.py
```
Creates:
- ASSESS contract (NASA ARC, 2025-2030)
- **13 departments in complete NASA Ames organizational hierarchy:**
  - **⚠️ CRITICAL: This is the COMPLETE structure. DO NOT SIMPLIFY.**
  
  **L1: Entry Systems and Technology Division (TS)** - David Chen (Manager)
    - L2: TSM (Thermal Protection Materials Branch) - Arnaud Borner
    - L2: TSA (Aerothermodynamics Branch) - Bhaskaran Rathakrishnan
    - L2: TSF (Thermo-Physics Facilities Branch) - No manager
    - L2: TSS (Entry Systems and Vehicle Development Branch) - Blake Hannah
  
  **L1: NASA Advanced Supercomputing Division (TN)** - Parent department
    - L2: TNA (Computational Aerosciences Branch) - Gerrit-Daniel Stich
    - L2: TNP (Computational Physics Branch) - Patricia Ventura Diaz
  
  **L1: Aeronautics Directorate (A)** - Parent department
    - L2: AV (Aeromechanics Office) - Gerrit-Daniel Stich (dual role)
    - L2: AA (Systems Analysis Office) - Blake Hannah (dual role)
  
  **L1: Aeroflightdynamics Directorate (Y)** - US Army, Parent department
    - L2: YA (Computational Aeromechanics Tech Area) - Shirzad Hoseinverdy

- **Users (8 total):**
  - PM: pm.assess@ama-impact.com (Dave Cornelius)
  - Tech Lead/TS Manager: techlead.assess@ama-impact.com (David Chen)
  - **6 Department Managers:**
    - bhaskaran.rathakrishnan@ama-inc.com (TSA)
    - arnaud.borner@ama-inc.com (TSM)
    - blake.Hannah@ama-inc.com (TSS, AA - dual role)
    - patricia.ventura@ama-inc.com (TNP)
    - gerrit-daniel.stich@ama-inc.com (TNA, AV - dual role)
    - shirzad.hoseinverdy@ama-inc.com (YA - Army)

- All passwords: `TempPassword123!` with `force_password_change=True`

**Note:** Blake Hannah and Gerrit-Daniel Stich each manage two departments (dual roles).

### RSES Contract
```bash
python scripts/fixtures/contracts/seed_rses.py
```
Creates:
- RSES contract (NASA LaRC, 2024-2026)
- 2 departments: RD, ES
- PM: pm.rses@ama-impact.com (temp password: TempPassword123!)

## Security: Force Password Change

**Production users** (PMs, Managers) are created with `force_password_change=True`:
- Must change password on first login
- Login returns 403 error until password is changed
- Temporary password: `TempPassword123!`

**Development users** (in `seed_development_data.py`) have `force_password_change=False` for convenience.

## Adding a New Contract

1. Copy `contracts/seed_assess.py` to `contracts/seed_yourcontract.py`
2. Update contract details, departments, and users
3. Add to `scripts/setup_dev_environment.py`:
   ```python
   (SCRIPTS_DIR / "fixtures" / "contracts" / "seed_yourcontract.py", "Seed Your Contract"),
   ```

## Development Data

`seed_development_data.py` creates test data:
- Beneficiaries with various visa statuses
- Case groups (immigration pathways)
- Visa applications (H1B, EB2-NIW, etc.)
- Todos with different priorities
- Sample dependents

**All development users have `force_password_change=False`** for testing convenience.
