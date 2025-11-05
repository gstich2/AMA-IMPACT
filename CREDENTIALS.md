# AMA-IMPACT Test User Credentials

## Default Test Users

After running `python scripts/setup_dev_environment.py`, the following test users are available:

### 1. Administrator
- **Email**: `admin@ama-impact.com`
- **Password**: `Admin123!`
- **Role**: ADMIN
- **Department**: None (system-wide)
- **Access**: Full system access, all contracts and departments

### 2. HR Manager
- **Email**: `hr@ama-impact.com`
- **Password**: `HR123!`
- **Role**: HR
- **Contract**: ASSESS-2025
- **Department**: None (contract-wide)
- **Access**: Can view and manage assigned contracts

### 3. Program Manager
- **Email**: `pm@ama-impact.com`
- **Password**: `PM123!`
- **Role**: PROGRAM_MANAGER
- **Contract**: ASSESS-2025
- **Department**: None (contract-level)
- **Access**: Full access to ASSESS contract (all departments)

### 4. Technical Lead (TS Manager)
- **Email**: `techlead@ama-impact.com`
- **Password**: `Tech123!`
- **Role**: TECH_LEAD
- **Contract**: ASSESS-2025
- **Department**: TS (Code TS)
- **Reports to**: Program Manager
- **Manages**: TS department (includes TSM, TSA sub-departments)
- **Access**: Can view TS, TSM, and TSA department users and their visas

### 5. Staff Member (TSM)
- **Email**: `staff@ama-impact.com`
- **Password**: `Staff123!`
- **Role**: STAFF
- **Contract**: ASSESS-2025
- **Department**: TSM (under TS)
- **Reports to**: Technical Lead
- **Access**: Can only view own data

### 6. Staff Member (TNA)
- **Email**: `staff.tna@ama-impact.com`
- **Password**: `Staff123!`
- **Role**: STAFF
- **Contract**: ASSESS-2025
- **Department**: TNA
- **Reports to**: Program Manager
- **Access**: Can only view own data

## Organizational Structure

```
ASSESS-2025 (Contract) - NASA Ames Research Center
├── TS - Entry Systems and Technology Division (Parent)
│   ├── TSM - Thermal Protection Materials Branch
│   ├── TSA - Aerothermodynamics Branch
│   ├── TSF - Thermo-Physics Facilities Branch
│   └── TSS - Entry Systems and Vehicle Development Branch
├── TNA - Computational Aerosciences Branch
├── TNC - Advanced Computing Branch
├── TNP - Computational Physics Branch
└── AV - Aeromechanics Office

RSES-2025 (Contract)
├── RS - Robotics Division
└── ES - Earth Science Division
```

## Role & Department Hierarchy

```
ADMIN (System-wide)
├── HR (Multi-contract)
└── CONTRACT (e.g., ASSESS)
    ├── PROGRAM_MANAGER (Contract-wide, all departments)
    └── DEPARTMENTS
        ├── DEPARTMENT MANAGER (Department + sub-departments)
        │   └── TECH_LEAD (Team)
        └── STAFF (Self-only)
```

## Access Rules

1. **ADMIN**: Sees everything across all contracts and departments
2. **HR**: Sees all assigned contracts and their departments
3. **PROGRAM_MANAGER**: Sees entire contract (all departments)
4. **TECH_LEAD** (Department Manager): 
   - Sees own department + all child departments
   - Example: TS manager sees TS, TSM, TSA users
5. **STAFF**: Only sees own data

## Department Features

- **Flexible Hierarchy**: Can be 1-3+ levels deep
- **Self-Referencing**: Departments can have parent departments
- **Flat Structure**: Can add departments without parents (like TNA, AV)
- **Hierarchical Structure**: Can nest departments (TS → TSM, TSA)
- **Department Managers**: Each department can have a manager/lead
- **Tree Traversal**: Managers see all users in their department tree

## Default Contracts

1. **ASSESS-2025**: ASSESS Program (Active) - Has departments
2. **RESESS-2025**: RESESS Program (Active) - No departments yet

## Notes

- All passwords follow the pattern: `[Role]123!`
- Staff can only see their own visa applications
- Department managers can see all users in their department + sub-departments
- Program Managers can see all departments in their contract
- HR can see all departments across assigned contracts
- Admin has full system access

---

## 📊 Sample Data Included

### Contracts
- ASSESS-2025 (Active) - NASA Ames - 9 departments
- RSES-2025 (Active) - NASA Ames - 2 departments

### Departments (11 total)
- **ASSESS**: TS (parent), TSM, TSA, TSF, TSS, TNA, TNC, TNP, AV (9 departments)
- **RSES**: RS, ES (2 departments)

### Visa Types (12 types)
- H1B - H-1B Specialty Occupation
- L1 - L-1 Intracompany Transfer
- O1 - O-1 Extraordinary Ability
- TN - TN NAFTA Professional
- EB1A - EB-1A Extraordinary Ability
- EB1B - EB-1B Outstanding Researcher
- EB2 - EB-2 Advanced Degree
- EB2NIW - EB-2 National Interest Waiver
- PERM - PERM Labor Certification
- OPT - Optional Practical Training
- EAD - Employment Authorization Document
- GREEN_CARD - Permanent Resident Card

---

## 🧪 Quick Test

1. Start backend: `cd backend && uvicorn app.main:app --reload --port 8000`
2. Open: http://localhost:8000/docs
3. Click **Authorize** button
4. Use **POST /api/v1/auth/login** with admin credentials:
   - username: `admin@ama-impact.com`
   - password: `Admin123!`
5. Copy the `access_token` from response
6. Click **Authorize** again and enter: `Bearer <access_token>`
7. Now test any endpoint!

---

## 🔄 Setup Development Database

To initialize the database with all fixtures:

```bash
cd backend
python scripts/setup_dev_environment.py
```

This creates:
- 2 contracts (ASSESS, RSES)
- 11 departments (9 ASSESS + 2 RSES)
- 6 test users (admin, hr, pm, manager, 2 staff)
- Sample beneficiaries, visa applications, case groups, and todos

**Note:** This script will drop and recreate the database, deleting ALL existing data!
