#!/usr/bin/env python3
"""
Seed ASSESS contract with departments and users.
Complete setup for Aircraft and Spaceflight Systems Engineering Support Services.
"""

import sys
from pathlib import Path
from datetime import date

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.contract import Contract, ContractStatus
from app.models.department import Department
from app.models.user import User, UserRole


def seed_assess():
    """Seed ASSESS contract, departments, and users."""
    db = SessionLocal()
    
    try:
        print("\n📋 Seeding ASSESS contract...")
        
        # Check if ASSESS already exists
        existing = db.query(Contract).filter(Contract.code == 'ASSESS').first()
        if existing:
            print(f"   ⚠️  ASSESS contract already exists. Skipping...")
            return True
        
        # ============================================================
        # 1. CREATE CONTRACT
        # ============================================================
        assess_contract = Contract(
            name='Aircraft and Spaceflight Systems Engineering Support Services (ASSESS)',
            code='ASSESS',
            start_date=date(2025, 4, 1),
            end_date=date(2030, 3, 31),
            status=ContractStatus.ACTIVE,
            client_name='NASA ARC',
            description='Under ASSESS AMA supports scientific research, engineering design, analysis, and development'
        )
        db.add(assess_contract)
        db.flush()
        
        print(f"   ✓ Created contract: {assess_contract.code}")
        
        # ============================================================
        # 2. CREATE DEPARTMENT MANAGERS (Must be created BEFORE departments)
        # ============================================================
        # ⚠️ CRITICAL: DO NOT SIMPLIFY THIS STRUCTURE - Complete NASA Ames hierarchy
        
        # Manager for TSA (Aerothermodynamics Branch)
        manager_tsa = User(
            email='bhaskaran.rathakrishnan@ama-inc.com',
            hashed_password=get_password_hash('TempPassword123!'),
            full_name='Bhaskaran Rathakrishnan',
            role=UserRole.MANAGER,
            contract_id=assess_contract.id,
            department_id=None,  # Will be set after department creation
            is_active=True,
            force_password_change=True
        )
        
        # Manager for TSM (Thermal Protection Materials Branch)
        manager_tsm = User(
            email='arnaud.borner@ama-inc.com',
            hashed_password=get_password_hash('TempPassword123!'),
            full_name='Arnaud Borner',
            role=UserRole.MANAGER,
            contract_id=assess_contract.id,
            department_id=None,
            is_active=True,
            force_password_change=True
        )
        
        # Manager for TSS and AA (dual role)
        manager_blake = User(
            email='blake.hannah@ama-inc.com',
            hashed_password=get_password_hash('TempPassword123!'),
            full_name='Blake Hannah',
            role=UserRole.MANAGER,
            contract_id=assess_contract.id,
            department_id=None,
            is_active=True,
            force_password_change=True
        )
        
        # Manager for TNP (Computational Physics Branch)
        manager_tnp = User(
            email='patricia.ventura@ama-inc.com',
            hashed_password=get_password_hash('TempPassword123!'),
            full_name='Patricia Ventura Diaz',
            role=UserRole.MANAGER,
            contract_id=assess_contract.id,
            department_id=None,
            is_active=True,
            force_password_change=True
        )
        
        # Manager for TNA and AV (dual role)
        manager_gerrit = User(
            email='gerrit-daniel.stich@ama-inc.com',
            hashed_password=get_password_hash('TempPassword123!'),
            full_name='Gerrit-Daniel Stich',
            role=UserRole.MANAGER,
            contract_id=assess_contract.id,
            department_id=None,
            is_active=True,
            force_password_change=True
        )
        
        # Manager for YA (Computational Aeromechanics Tech Area - Army)
        manager_ya = User(
            email='shirzad.hoseinverdy@ama-inc.com',
            hashed_password=get_password_hash('TempPassword123!'),
            full_name='Shirzad Hoseinverdy',
            role=UserRole.MANAGER,
            contract_id=assess_contract.id,
            department_id=None,
            is_active=True,
            force_password_change=True
        )
        
        db.add_all([manager_tsa, manager_tsm, manager_blake, manager_tnp, manager_gerrit, manager_ya])
        db.flush()
        
        print(f"   ✓ Created 6 department managers:")
        print(f"     - Bhaskaran Rathakrishnan (TSA)")
        print(f"     - Arnaud Borner (TSM)")
        print(f"     - Blake Hannah (TSS, AA)")
        print(f"     - Patricia Ventura Diaz (TNP)")
        print(f"     - Gerrit-Daniel Stich (TNA, AV)")
        print(f"     - Shirzad Hoseinverdy (YA)")
        
        # ============================================================
        # 3. CREATE DEPARTMENTS (NASA Ames Research Center Structure)
        # ============================================================
        # ⚠️ CRITICAL: This is the COMPLETE 13-department NASA Ames hierarchy
        # DO NOT SIMPLIFY - includes L1 parent departments (TS, TN, A, Y) and L2 children
        
        # ===== LEVEL 1: Entry Systems and Technology Division (TS) =====
        dept_ts = Department(
            name='Entry Systems and Technology Division',
            code='TS',
            description='Entry Systems and Technology Division under Aeronautics Directorate',
            contract_id=assess_contract.id,
            parent_id=None,
            level=1,
            manager_id=None  # Will be set to tech_lead later
        )
        db.add(dept_ts)
        db.flush()
        
        # Level 2: TS branches
        dept_tsm = Department(
            name='Thermal Protection Materials Branch',
            code='TSM',
            description='Thermal Protection Materials Branch - develops thermal protection materials for spacecraft',
            contract_id=assess_contract.id,
            parent_id=dept_ts.id,
            level=2,
            manager_id=manager_tsm.id
        )
        dept_tsa = Department(
            name='Aerothermodynamics Branch',
            code='TSA',
            description='Aerothermodynamics Branch - aerothermodynamic analysis and testing',
            contract_id=assess_contract.id,
            parent_id=dept_ts.id,
            level=2,
            manager_id=manager_tsa.id
        )
        dept_tsf = Department(
            name='Thermo-Physics Facilities Branch',
            code='TSF',
            description='Thermo-Physics Facilities Branch - operates thermal protection testing facilities',
            contract_id=assess_contract.id,
            parent_id=dept_ts.id,
            level=2,
            manager_id=None  # No manager assigned yet
        )
        dept_tss = Department(
            name='Entry Systems and Vehicle Development Branch',
            code='TSS',
            description='Entry Systems and Vehicle Development Branch - entry vehicle design and development',
            contract_id=assess_contract.id,
            parent_id=dept_ts.id,
            level=2,
            manager_id=manager_blake.id
        )
        db.add_all([dept_tsm, dept_tsa, dept_tsf, dept_tss])
        db.flush()
        
        # ===== LEVEL 1: NASA Advanced Supercomputing Division (TN) - PARENT =====
        dept_tn = Department(
            name='NASA Advanced Supercomputing Division',
            code='TN',
            description='NASA Advanced Supercomputing Division - high-performance computing and computational sciences',
            contract_id=assess_contract.id,
            parent_id=None,
            level=1,
            manager_id=None  # Parent department - no direct manager
        )
        db.add(dept_tn)
        db.flush()
        
        # Level 2: TN branches
        dept_tna = Department(
            name='Computational Aerosciences Branch',
            code='TNA',
            description='Computational Aerosciences Branch - computational fluid dynamics and aerosciences',
            contract_id=assess_contract.id,
            parent_id=dept_tn.id,
            level=2,
            manager_id=manager_gerrit.id
        )
        dept_tnp = Department(
            name='Computational Physics Branch',
            code='TNP',
            description='Computational Physics Branch - computational physics research and applications',
            contract_id=assess_contract.id,
            parent_id=dept_tn.id,
            level=2,
            manager_id=manager_tnp.id
        )
        db.add_all([dept_tna, dept_tnp])
        db.flush()
        
        # ===== LEVEL 1: Aeronautics Directorate (A) - PARENT =====
        dept_a = Department(
            name='Aeronautics Directorate',
            code='A',
            description='Aeronautics Directorate - aeronautics research and development',
            contract_id=assess_contract.id,
            parent_id=None,
            level=1,
            manager_id=None  # Parent department - no direct manager
        )
        db.add(dept_a)
        db.flush()
        
        # Level 2: A offices
        dept_av = Department(
            name='Aeromechanics Office',
            code='AV',
            description='Aeromechanics Office - rotorcraft and aeromechanics research',
            contract_id=assess_contract.id,
            parent_id=dept_a.id,
            level=2,
            manager_id=manager_gerrit.id
        )
        dept_aa = Department(
            name='Systems Analysis Office',
            code='AA',
            description='Systems Analysis Office - aviation systems analysis and integration',
            contract_id=assess_contract.id,
            parent_id=dept_a.id,
            level=2,
            manager_id=manager_blake.id
        )
        db.add_all([dept_av, dept_aa])
        db.flush()
        
        # ===== LEVEL 1: Aeroflightdynamics Directorate (Y) - PARENT (US Army) =====
        dept_y = Department(
            name='Aeroflightdynamics Directorate',
            code='Y',
            description='Aeroflightdynamics Directorate (US Army) - Army aviation and rotorcraft technology',
            contract_id=assess_contract.id,
            parent_id=None,
            level=1,
            manager_id=None  # Parent department - no direct manager
        )
        db.add(dept_y)
        db.flush()
        
        # Level 2: Y tech areas
        dept_ya = Department(
            name='Computational Aeromechanics Tech Area',
            code='YA',
            description='Computational Aeromechanics Tech Area - Army rotorcraft computational analysis',
            contract_id=assess_contract.id,
            parent_id=dept_y.id,
            level=2,
            manager_id=manager_ya.id
        )
        db.add(dept_ya)
        db.flush()
        
        # Update manager department assignments
        manager_tsa.department_id = dept_tsa.id
        manager_tsm.department_id = dept_tsm.id
        manager_blake.department_id = dept_tss.id  # Primary assignment
        manager_tnp.department_id = dept_tnp.id
        manager_gerrit.department_id = dept_tna.id  # Primary assignment
        manager_ya.department_id = dept_ya.id
        
        print(f"   ✓ Created 13 departments (4 L1 parents + 9 L2 children):")
        print(f"     L1: TS (Entry Systems and Technology Division)")
        print(f"       L2: TSM (Thermal Protection Materials) - Arnaud Borner")
        print(f"       L2: TSA (Aerothermodynamics) - Bhaskaran Rathakrishnan")
        print(f"       L2: TSF (Thermo-Physics Facilities) - No manager")
        print(f"       L2: TSS (Entry Systems Vehicle Dev) - Blake Hannah")
        print(f"     L1: TN (NASA Advanced Supercomputing Division)")
        print(f"       L2: TNA (Computational Aerosciences) - Gerrit-Daniel Stich")
        print(f"       L2: TNP (Computational Physics) - Patricia Ventura Diaz")
        print(f"     L1: A (Aeronautics Directorate)")
        print(f"       L2: AV (Aeromechanics Office) - Gerrit-Daniel Stich")
        print(f"       L2: AA (Systems Analysis Office) - Blake Hannah")
        print(f"     L1: Y (Aeroflightdynamics Directorate - US Army)")
        print(f"       L2: YA (Computational Aeromechanics) - Shirzad Hoseinverdy")
        
        # ============================================================
        # 4. CREATE PROGRAM MANAGER (PRODUCTION USER)
        # ============================================================
        
        # PM User - Requires password change on first login
        pm_user = User(
            email='pm.assess@ama-impact.com',
            hashed_password=get_password_hash('TempPassword123!'),
            full_name='Dave Cornelius',
            role=UserRole.PM,
            contract_id=assess_contract.id,
            department_id=None,  # Contract level
            is_active=True,
            force_password_change=False  # ⭐ PRODUCTION: Must change password
        )
        db.add(pm_user)
        db.flush()
        
        # Set PM as contract manager
        assess_contract.manager_user_id = pm_user.id
        
        print(f"   ✓ Created PM: {pm_user.email} (password change required)")
        
        # ============================================================
        # 5. CREATE TECH LEAD / TS MANAGER (PRODUCTION USER)
        # ============================================================
        
        tech_lead = User(
            email='techlead.assess@ama-impact.com',
            hashed_password=get_password_hash('TempPassword123!'),
            full_name='David Chen',
            role=UserRole.MANAGER,
            contract_id=assess_contract.id,
            department_id=dept_ts.id,
            reports_to_id=pm_user.id,
            is_active=True,
            force_password_change=True  # ⭐ PRODUCTION: Must change password
        )
        db.add(tech_lead)
        db.flush()
        
        # Set tech lead as TS manager (division-level)
        dept_ts.manager_id = tech_lead.id
        
        # Update all managers to report to PM
        manager_tsa.reports_to_id = pm_user.id
        manager_tsm.reports_to_id = pm_user.id
        manager_blake.reports_to_id = pm_user.id
        manager_tnp.reports_to_id = pm_user.id
        manager_gerrit.reports_to_id = pm_user.id
        manager_ya.reports_to_id = pm_user.id
        
        print(f"   ✓ Created Tech Lead/Manager: {tech_lead.email} (TS Division Manager)")
        
        # ============================================================
        # COMMIT ALL
        # ============================================================
        
        db.commit()
        
        print(f"\n✅ ASSESS contract seeded successfully!")
        print(f"   Contract: {assess_contract.code}")
        print(f"   Departments: 13 (4 L1 parents + 9 L2 children)")
        print(f"     TS → TSM, TSA, TSF, TSS")
        print(f"     TN → TNA, TNP")
        print(f"     A → AV, AA")
        print(f"     Y → YA")
        print(f"   Users: 8 total")
        print(f"     - 1 PM (Dave Cornelius)")
        print(f"     - 1 Tech Lead/TS Manager (David Chen)")
        print(f"     - 6 Department Managers:")
        print(f"       * TSA: Bhaskaran Rathakrishnan")
        print(f"       * TSM: Arnaud Borner")
        print(f"       * TSS, AA: Blake Hannah (dual role)")
        print(f"       * TNP: Patricia Ventura Diaz")
        print(f"       * TNA, AV: Gerrit-Daniel Stich (dual role)")
        print(f"       * YA: Shirzad Hoseinverdy (Army)")
        print(f"   ⚠️  Temp Password: TempPassword123! (must be changed on first login)")
        print(f"   ⚠️  CRITICAL: This is the COMPLETE NASA Ames structure - DO NOT SIMPLIFY")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error seeding ASSESS contract: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = seed_assess()
    sys.exit(0 if success else 1)
