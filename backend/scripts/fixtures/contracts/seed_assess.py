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
        # 2. CREATE DEPARTMENTS
        # ============================================================
        
        # Top-level department: Technology Systems (TS)
        dept_ts = Department(
            name='Entry Systems and Technology',
            code='TS',
            description='Technology Systems Division',
            contract_id=assess_contract.id,
            parent_id=None,
            level=1
        )
        db.add(dept_ts)
        db.flush()
        
        # Sub-departments under TS
        dept_tsm = Department(
            name='Technology Systems Management',
            code='TSM',
            description='Systems Management Team',
            contract_id=assess_contract.id,
            parent_id=dept_ts.id,
            level=2
        )
        dept_tsa = Department(
            name='Technology Systems Administration',
            code='TSA',
            description='Systems Administration Team',
            contract_id=assess_contract.id,
            parent_id=dept_ts.id,
            level=2
        )
        db.add_all([dept_tsm, dept_tsa])
        
        # Flat departments (no parent)
        dept_tna = Department(
            name='Technology Network Administration',
            code='TNA',
            description='Network Administration Team',
            contract_id=assess_contract.id,
            parent_id=None,
            level=1
        )
        dept_av = Department(
            name='Audio Visual',
            code='AV',
            description='Audio Visual Support Team',
            contract_id=assess_contract.id,
            parent_id=None,
            level=1
        )
        db.add_all([dept_tna, dept_av])
        db.flush()
        
        print(f"   ✓ Created 5 departments (TS→TSM/TSA, TNA, AV)")
        
        # ============================================================
        # 3. CREATE PROGRAM MANAGER (PRODUCTION USER)
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
        # 4. CREATE TECH LEAD / MANAGER (PRODUCTION USER)
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
        
        # Set tech lead as TS manager
        dept_ts.manager_id = tech_lead.id
        
        print(f"   ✓ Created Manager: {tech_lead.email} (password change required)")
        
        # ============================================================
        # COMMIT ALL
        # ============================================================
        
        db.commit()
        
        print(f"\n✅ ASSESS contract seeded successfully!")
        print(f"   Contract: {assess_contract.code}")
        print(f"   Departments: 5 (TS→TSM/TSA, TNA, AV)")
        print(f"   Users: 2 (PM, Manager)")
        print(f"   ⚠️  Temp Password: TempPassword123! (must be changed on first login)")
        
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
