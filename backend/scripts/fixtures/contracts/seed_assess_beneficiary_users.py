#!/usr/bin/env python3
"""
Seed ASSESS beneficiary users (Step 1 of 3).
Creates User accounts and Beneficiary records for ASSESS employees.

Run order:
1. seed_assess_beneficiary_users.py (this file)
2. seed_assess_case_groups.py
3. seed_assess_visa_apps.py

Prerequisites:
- seed_visa_types.py
- seed_assess.py (creates contract + departments + managers)
"""

import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.contract import Contract
from app.models.department import Department
from app.models.beneficiary import Beneficiary


def seed_assess_beneficiary_users():
    """Seed ASSESS beneficiary users and beneficiary records."""
    db = SessionLocal()
    
    try:
        print("\n📋 Seeding ASSESS beneficiary users...")
        
        # Get ASSESS contract
        assess_contract = db.query(Contract).filter(Contract.code == 'ASSESS').first()
        if not assess_contract:
            print("   ❌ ASSESS contract not found! Run seed_assess.py first.")
            return False
        
        # Get departments
        dept_tna = db.query(Department).filter(
            Department.code == 'TNA',
            Department.contract_id == assess_contract.id
        ).first()
        dept_tnp = db.query(Department).filter(
            Department.code == 'TNP',
            Department.contract_id == assess_contract.id
        ).first()
        dept_av = db.query(Department).filter(
            Department.code == 'AV',
            Department.contract_id == assess_contract.id
        ).first()
        dept_tss = db.query(Department).filter(
            Department.code == 'TSS',
            Department.contract_id == assess_contract.id
        ).first()
        
        # Get managers
        manager_gerrit = db.query(User).filter(
            User.email == 'gerrit-daniel.stich@ama-inc.com'
        ).first()
        manager_patricia = db.query(User).filter(
            User.email == 'patricia.ventura@ama-inc.com'
        ).first()
        pm_user = db.query(User).filter(
            User.email == 'pm.assess@ama-impact.com'
        ).first()
        
        if not all([dept_tna, dept_tnp, dept_av, dept_tss, manager_gerrit, manager_patricia, pm_user]):
            print("   ❌ Required departments or managers not found!")
            return False
        
        print("   ✓ Found existing data")
        
        # Employee data from user
        employees = [
            # Managers with LPR (already exist as users, just add beneficiary records)
            {
                'existing_user': manager_gerrit,
                'first_name': 'Gerrit-Daniel',
                'last_name': 'Stich',
                'country_of_citizenship': 'Germany',
                'country_of_birth': 'Germany',
                'passport_country': 'Germany',
                'passport_expiration': date(2032, 12, 31),
                'current_visa_type': 'LPR',
                'current_visa_expiration': date(2033, 1, 1),
                'i94_expiration': None,
                'job_title': 'Branch Technical Lead, Principal Associate',
                'employment_start_date': date(2015, 1, 1)
            },
            # TNA employees
            {
                'email': 'brandon.lowe@ama-inc.com',
                'full_name': 'Brandon Lowe',
                'department': dept_tna,
                'reports_to': manager_gerrit,
                'first_name': 'Brandon',
                'last_name': 'Lowe',
                'country_of_citizenship': 'Canada',
                'country_of_birth': 'Canada',
                'passport_country': 'Canada',
                'passport_expiration': date(2030, 6, 15),
                'current_visa_type': 'TN',
                'current_visa_expiration': date(2026, 1, 5),
                'i94_expiration': date(2026, 1, 5),
                'job_title': 'Senior Research Scientist',
                'employment_start_date': date(2022, 5, 15)
            },
            {
                'email': 'david.c.penner@ama-inc.com',
                'full_name': 'David Craig Penner',
                'department': dept_tna,
                'reports_to': manager_gerrit,
                'first_name': 'David Craig',
                'last_name': 'Penner',
                'country_of_citizenship': 'Canada',
                'country_of_birth': 'Canada',
                'passport_country': 'Canada',
                'passport_expiration': date(2031, 4, 10),
                'current_visa_type': 'TN',
                'current_visa_expiration': date(2027, 1, 4),
                'i94_expiration': date(2027, 1, 4),
                'job_title': 'Senior Research Scientist',
                'employment_start_date': date(2022, 7, 15)
            },
            {
                'email': 'timothy.chau@ama-inc.com',
                'full_name': 'Timothy Chau',
                'department': dept_tna,
                'reports_to': manager_gerrit,
                'first_name': 'Timothy',
                'last_name': 'Chau',
                'country_of_citizenship': 'Canada',
                'country_of_birth': 'Canada',
                'passport_country': 'Canada',
                'passport_expiration': date(2032, 5, 20),
                'current_visa_type': 'H1B',
                'current_visa_expiration': date(2027, 1, 7),
                'i94_expiration': date(2027, 1, 7),
                'job_title': 'Senior Research Scientist',
                'employment_start_date': date(2018, 3, 11)
            },
            {
                'email': 'luis.fernandes@ama-inc.com',
                'full_name': 'Luis Fernandes',
                'department': dept_tna,
                'reports_to': manager_gerrit,
                'first_name': 'Luis',
                'last_name': 'Fernandes',
                'country_of_citizenship': 'Portugal',
                'country_of_birth': 'Portugal',
                'passport_country': 'Portugal',
                'passport_expiration': date(2030, 9, 10),
                'current_visa_type': 'H1B',
                'current_visa_expiration': date(2026, 1, 5),
                'i94_expiration': date(2026, 1, 5),
                'job_title': 'Senior Research Scientist',
                'employment_start_date': date(2018, 7, 5)
            },
            {
                'email': 'kiran.ravikumar@ama-inc.com',
                'full_name': 'Kiran Ravikumar',
                'department': dept_tna,
                'reports_to': manager_gerrit,
                'first_name': 'Kiran',
                'last_name': 'Ravikumar',
                'country_of_citizenship': 'India',
                'country_of_birth': 'India',
                'passport_country': 'India',
                'passport_expiration': date(2033, 11, 20),
                'current_visa_type': 'H1B',
                'current_visa_expiration': date(2029, 11, 5),
                'i94_expiration': date(2029, 11, 5),
                'job_title': 'Senior Research Scientist',
                'employment_start_date': date(2023, 7, 5)
            },
            {
                'email': 'victor.sousa@ama-inc.com',
                'full_name': 'Victor DeCarvalho Sousa',
                'department': dept_tna,
                'reports_to': manager_gerrit,
                'first_name': 'Victor DeCarvalho',
                'last_name': 'Sousa',
                'country_of_citizenship': 'Brazil',
                'country_of_birth': 'Brazil',
                'passport_country': 'Brazil',
                'passport_expiration': date(2031, 7, 15),
                'current_visa_type': 'LPR',
                'current_visa_expiration': date(2035, 1, 1),
                'i94_expiration': None,
                'job_title': 'Senior Research Scientist',
                'employment_start_date': date(2020, 1, 1)
            },
            # TNP employees
            {
                'email': 'david.garciaperez@ama-inc.com',
                'full_name': 'David Garcia Perez',
                'department': dept_tnp,
                'reports_to': manager_patricia,
                'first_name': 'David',
                'last_name': 'Garcia Perez',
                'country_of_citizenship': 'Spain',
                'country_of_birth': 'Spain',
                'passport_country': 'Spain',
                'passport_expiration': date(2032, 8, 20),
                'current_visa_type': 'H1B',
                'current_visa_expiration': date(2027, 1, 5),
                'i94_expiration': date(2027, 1, 5),
                'job_title': 'Senior Research Scientist',
                'employment_start_date': date(2021, 7, 5)
            },
            # AV employees
            {
                'email': 'tove.aagren@ama-inc.com',
                'full_name': 'Tove Aagen',
                'department': dept_av,
                'reports_to': manager_gerrit,
                'first_name': 'Tove',
                'last_name': 'Aagen',
                'country_of_citizenship': 'Sweden',
                'country_of_birth': 'Sweden',
                'passport_country': 'Sweden',
                'passport_expiration': date(2033, 4, 10),
                'current_visa_type': 'H1B',
                'current_visa_expiration': date(2029, 1, 5),
                'i94_expiration': date(2029, 1, 5),
                'job_title': 'Senior Research Scientist',
                'employment_start_date': date(2021, 7, 5)
            },
            # TSS employees
            {
                'email': 'georgios.bellas-chatzigeorgis@ama-inc.com',
                'full_name': 'Georgios Bellas-Chatzigeorgis',
                'department': dept_tss,
                'reports_to': manager_gerrit,  # Note: TSS manager is Arnaud Borner, but data said reports to Arnaud Boerner (typo?)
                'first_name': 'Georgios',
                'last_name': 'Bellas-Chatzigeorgis',
                'country_of_citizenship': 'Greece',
                'country_of_birth': 'Greece',
                'passport_country': 'Greece',
                'passport_expiration': date(2030, 6, 25),
                'current_visa_type': 'H1B',
                'current_visa_expiration': date(2026, 1, 5),
                'i94_expiration': date(2026, 1, 5),
                'job_title': 'Senior Research Scientist',
                'employment_start_date': date(2020, 1, 15)
            },
            # Future hire (no user account)
            {
                'no_user': True,
                'first_name': 'Jacob',
                'last_name': 'Friedrichson',
                'country_of_citizenship': 'Sweden',
                'country_of_birth': 'Sweden',
                'passport_country': 'Sweden',
                'passport_expiration': date(2032, 9, 15),
                'current_visa_type': None,
                'current_visa_expiration': None,
                'i94_expiration': None,
                'job_title': 'Senior Research Scientist',
                'employment_start_date': None
            }
        ]
        
        count_users = 0
        count_beneficiaries = 0
        
        for emp in employees:
            # Handle existing manager users
            if 'existing_user' in emp:
                user = emp['existing_user']
                print(f"   ✓ Using existing user: {user.email}")
            # Handle future hires (no user)
            elif emp.get('no_user'):
                user = None
                print(f"   ✓ Creating beneficiary only (future hire): {emp['first_name']} {emp['last_name']}")
            # Create new user
            else:
                user = User(
                    email=emp['email'],
                    hashed_password=get_password_hash('Dev123!'),
                    full_name=emp['full_name'],
                    role=UserRole.BENEFICIARY,
                    contract_id=assess_contract.id,
                    department_id=emp['department'].id,
                    reports_to_id=emp['reports_to'].id,
                    is_active=True,
                    force_password_change=False
                )
                db.add(user)
                db.flush()
                count_users += 1
                print(f"   ✓ Created user: {emp['email']}")
            
            # Create beneficiary record
            beneficiary = Beneficiary(
                user_id=user.id if user else None,
                first_name=emp['first_name'],
                last_name=emp['last_name'],
                country_of_citizenship=emp['country_of_citizenship'],
                country_of_birth=emp['country_of_birth'],
                passport_country=emp['passport_country'],
                passport_expiration=emp['passport_expiration'],
                current_visa_type=emp['current_visa_type'],
                current_visa_expiration=emp['current_visa_expiration'],
                i94_expiration=emp['i94_expiration'],
                job_title=emp['job_title'],
                employment_start_date=emp['employment_start_date']
            )
            db.add(beneficiary)
            db.flush()
            count_beneficiaries += 1
        
        db.commit()
        
        print(f"\n✅ ASSESS beneficiary users seeded successfully!")
        print(f"   Users created: {count_users}")
        print(f"   Beneficiaries created: {count_beneficiaries}")
        print(f"   All passwords: Dev123!")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error seeding beneficiary users: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = seed_assess_beneficiary_users()
    sys.exit(0 if success else 1)
