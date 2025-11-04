"""
Seed script for AMA-IMPACT database.
Creates initial admin user and sample data.
"""

import sys
from datetime import date

# Add parent directory to path
sys.path.insert(0, '.')

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import get_password_hash

# Import all models to ensure relationships are configured
from app.models.user import User, UserRole
from app.models.contract import Contract, ContractStatus
from app.models.department import Department
from app.models.visa import VisaType, VisaApplication
from app.models.audit import AuditLog
from app.models.notification import Notification
from app.models.settings import UserSettings


def seed_database():
    """Seed the database with initial data."""
    db = SessionLocal()
    
    try:
        print("🌱 Seeding database...")
        
        # Create Admin User
        admin = User(
            email='admin@ama-impact.com',
            hashed_password=get_password_hash('Admin123!'),
            full_name='System Administrator',
            phone='+1-555-0100',
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin)
        db.flush()
        print('✅ Admin user created')
        
        # Create sample contracts
        contract_assess = Contract(
            name='ASSESS Program',
            code='ASSESS-2025',
            start_date=date(2025, 1, 1),
            status=ContractStatus.ACTIVE
        )
        contract_resess = Contract(
            name='RESESS Program',
            code='RESESS-2025',
            start_date=date(2025, 1, 1),
            status=ContractStatus.ACTIVE
        )
        db.add(contract_assess)
        db.add(contract_resess)
        db.flush()
        print('✅ Sample contracts created')
        
        # Create departments for ASSESS contract
        # Option 1: Hierarchical structure (TS → TSM, TSA)
        dept_ts = Department(
            name='Code TS',
            code='TS',
            description='Technology Systems',
            contract_id=contract_assess.id,
            parent_id=None,
            level=1
        )
        db.add(dept_ts)
        db.flush()
        
        dept_tsm = Department(
            name='TSM Division',
            code='TSM',
            description='Technology Systems Management',
            contract_id=contract_assess.id,
            parent_id=dept_ts.id,
            level=2
        )
        dept_tsa = Department(
            name='TSA Division',
            code='TSA',
            description='Technology Systems Administration',
            contract_id=contract_assess.id,
            parent_id=dept_ts.id,
            level=2
        )
        db.add(dept_tsm)
        db.add(dept_tsa)
        
        # Option 2: Flat departments (no parent)
        dept_tna = Department(
            name='TNA Division',
            code='TNA',
            description='Technology Network Administration',
            contract_id=contract_assess.id,
            parent_id=None,
            level=1
        )
        dept_av = Department(
            name='AV Division',
            code='AV',
            description='Audio Visual',
            contract_id=contract_assess.id,
            parent_id=None,
            level=1
        )
        db.add(dept_tna)
        db.add(dept_av)
        db.flush()
        print('✅ Departments created (TS→TSM/TSA, TNA, AV)')
        
        # Create HR User
        hr_user = User(
            email='hr@ama-impact.com',
            hashed_password=get_password_hash('HR123!'),
            full_name='HR Manager',
            phone='+1-555-0200',
            role=UserRole.HR,
            contract_id=contract_assess.id,
            is_active=True
        )
        db.add(hr_user)
        db.flush()
        print('✅ HR user created')
        
        # Create PM User (Contract level - sees all departments)
        pm_user = User(
            email='pm@ama-impact.com',
            hashed_password=get_password_hash('PM123!'),
            full_name='Program Manager',
            phone='+1-555-0300',
            role=UserRole.PROGRAM_MANAGER,
            contract_id=contract_assess.id,
            department_id=None,  # PM at contract level
            is_active=True
        )
        db.add(pm_user)
        db.flush()
        print('✅ Program Manager created')
        
        # Create Tech Lead User (TS department lead - sees TS, TSM, TSA)
        tech_lead = User(
            email='techlead@ama-impact.com',
            hashed_password=get_password_hash('Tech123!'),
            full_name='Technical Lead',
            phone='+1-555-0400',
            role=UserRole.TECH_LEAD,
            contract_id=contract_assess.id,
            department_id=dept_ts.id,
            reports_to_id=pm_user.id,
            is_active=True
        )
        db.add(tech_lead)
        db.flush()
        
        # Set tech lead as manager of TS department
        dept_ts.manager_id = tech_lead.id
        print('✅ Tech Lead created (TS Manager)')
        
        # Create Staff Users in different departments
        staff_tsm = User(
            email='staff@ama-impact.com',
            hashed_password=get_password_hash('Staff123!'),
            full_name='Staff Member (TSM)',
            phone='+1-555-0500',
            role=UserRole.STAFF,
            contract_id=contract_assess.id,
            department_id=dept_tsm.id,
            reports_to_id=tech_lead.id,
            is_active=True
        )
        staff_tna = User(
            email='staff.tna@ama-impact.com',
            hashed_password=get_password_hash('Staff123!'),
            full_name='Staff Member (TNA)',
            phone='+1-555-0501',
            role=UserRole.STAFF,
            contract_id=contract_assess.id,
            department_id=dept_tna.id,
            reports_to_id=pm_user.id,
            is_active=True
        )
        db.add(staff_tsm)
        db.add(staff_tna)
        db.flush()
        print('✅ Staff users created (TSM, TNA)')
        
        # Create Visa Types
        visa_types = [
            VisaType(code='H1B', name='H-1B Specialty Occupation', description='Temporary work visa for specialty occupations', default_renewal_lead_days='180'),
            VisaType(code='L1', name='L-1 Intracompany Transfer', description='Transfer within multinational company', default_renewal_lead_days='180'),
            VisaType(code='O1', name='O-1 Extraordinary Ability', description='For individuals with extraordinary ability', default_renewal_lead_days='180'),
            VisaType(code='TN', name='TN NAFTA Professional', description='For Canadian and Mexican professionals', default_renewal_lead_days='90'),
            VisaType(code='EB1A', name='EB-1A Extraordinary Ability', description='Green Card for extraordinary ability', default_renewal_lead_days='365'),
            VisaType(code='EB1B', name='EB-1B Outstanding Researcher', description='Green Card for outstanding researchers', default_renewal_lead_days='365'),
            VisaType(code='EB2', name='EB-2 Advanced Degree', description='Green Card for advanced degree holders', default_renewal_lead_days='365'),
            VisaType(code='EB2NIW', name='EB-2 National Interest Waiver', description='Green Card with national interest waiver', default_renewal_lead_days='365'),
            VisaType(code='PERM', name='PERM Labor Certification', description='Labor certification for employment-based green card', default_renewal_lead_days='180'),
            VisaType(code='OPT', name='Optional Practical Training', description='Work authorization for F-1 students', default_renewal_lead_days='90'),
            VisaType(code='EAD', name='Employment Authorization Document', description='Work permit', default_renewal_lead_days='120'),
            VisaType(code='GREEN_CARD', name='Permanent Resident Card', description='Permanent residence status', default_renewal_lead_days='365'),
        ]
        db.add_all(visa_types)
        db.flush()
        print('✅ Visa types created')
        
        db.commit()
        print('✅ All data committed successfully')
        return True
        
    except Exception as e:
        db.rollback()
        print(f'❌ Error seeding database: {e}')
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = seed_database()
    sys.exit(0 if success else 1)
