#!/usr/bin/env python3
"""
Seed RSES contract with departments and users.
Complete setup for Research, Science & Engineering Services.
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


def seed_rses():
    """Seed RSES contract, departments, and users."""
    db = SessionLocal()
    
    try:
        print("\n📋 Seeding RSES contract...")
        
        # Check if RSES already exists
        existing = db.query(Contract).filter(Contract.code == 'RSES').first()
        if existing:
            print(f"   ⚠️  RSES contract already exists. Skipping...")
            return True
        
        # ============================================================
        # 1. CREATE CONTRACT
        # ============================================================
        rses_contract = Contract(
            name='Research, Science & Engineering Services (RSES)',
            code='RSES',
            start_date=date(2024, 1, 1),
            end_date=date(2026, 12, 31),
            status=ContractStatus.ACTIVE,
            client_name='NASA LaRC',
            description='Under RSES AMA supports autonomous systems, acoustics, aerosciences, avionics and systems design'
        )
        db.add(rses_contract)
        db.flush()
        
        print(f"   ✓ Created contract: {rses_contract.code}")
        
        # ============================================================
        # 2. CREATE DEPARTMENTS
        # ============================================================
        
        # Sample department structure for RSES
        dept_research = Department(
            name='Research Division',
            code='RD',
            description='Core research activities',
            contract_id=rses_contract.id,
            parent_id=None,
            level=1
        )
        db.add(dept_research)
        db.flush()
        
        dept_engineering = Department(
            name='Engineering Support',
            code='ES',
            description='Engineering support services',
            contract_id=rses_contract.id,
            parent_id=None,
            level=1
        )
        db.add(dept_engineering)
        db.flush()
        
        print(f"   ✓ Created 2 departments (RD, ES)")
        
        # ============================================================
        # 3. CREATE PROGRAM MANAGER (PRODUCTION USER)
        # ============================================================
        
        pm_user = User(
            email='pm.rses@ama-impact.com',
            hashed_password=get_password_hash('TempPassword123!'),
            full_name='Sarah Johnson',
            role=UserRole.PM,
            contract_id=rses_contract.id,
            department_id=None,  # Contract level
            is_active=True,
            force_password_change=True  # ⭐ PRODUCTION: Must change password
        )
        db.add(pm_user)
        db.flush()
        
        # Set PM as contract manager
        rses_contract.manager_user_id = pm_user.id
        
        print(f"   ✓ Created PM: {pm_user.email} (password change required)")
        
        # ============================================================
        # COMMIT ALL
        # ============================================================
        
        db.commit()
        
        print(f"\n✅ RSES contract seeded successfully!")
        print(f"   Contract: {rses_contract.code}")
        print(f"   Departments: 2 (RD, ES)")
        print(f"   Users: 1 (PM)")
        print(f"   ⚠️  Temp Password: TempPassword123! (must be changed on first login)")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error seeding RSES contract: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = seed_rses()
    sys.exit(0 if success else 1)
