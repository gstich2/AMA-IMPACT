#!/usr/bin/env python3
"""
Seed development data for testing.
Creates sample data using existing ASSESS contract structure:
- Uses departments from seed_assess.py (TS, TSM, TSA, TNA, AV)
- Creates additional test users (HR, Managers, Beneficiaries)
- Creates beneficiaries with visa information
- Creates case groups (for multi-step processes)
- Creates visa applications
- Creates dependents

Prerequisites: Run these fixtures first:
1. seed_visa_types.py
2. seed_assess.py (creates contract + departments + PM)
3. seed_law_firms.py
"""

import sys
from pathlib import Path
from datetime import date, datetime, timedelta
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.contract import Contract
from app.models.department import Department
from app.models.beneficiary import Beneficiary
from app.models.dependent import Dependent, RelationshipType
from app.models.law_firm import LawFirm
from app.models.visa import VisaType, VisaApplication, VisaTypeEnum, VisaStatus, VisaCaseStatus, VisaPriority
from app.models.case_group import CaseGroup, CaseType, CaseStatus, ApprovalStatus
from app.models.audit import AuditLog, AuditAction


def seed_development_data():
    """Seed development data into database."""
    db = SessionLocal()
    
    try:
        print("\n📋 Seeding development data...")
        
        # ============================================================
        # 1. GET EXISTING DATA
        # ============================================================
        
        # Get admin user
        admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if not admin:
            print("   ❌ Admin user not found! Run init_database.py first.")
            return False
        
        # Get ASSESS contract
        assess_contract = db.query(Contract).filter(Contract.code == 'ASSESS').first()
        if not assess_contract:
            print("   ❌ ASSESS contract not found! Run seed_contracts.py first.")
            return False
        
        # Get law firm
        law_firm = db.query(LawFirm).filter(LawFirm.is_preferred_vendor == True).first()
        if not law_firm:
            print("   ❌ No law firm found! Run seed_law_firms.py first.")
            return False
        
        # Get visa types
        h1b_type = db.query(VisaType).filter(VisaType.code == 'H1B').first()
        i140_type = db.query(VisaType).filter(VisaType.code == 'I140').first()
        i485_type = db.query(VisaType).filter(VisaType.code == 'I485').first()
        ead_type = db.query(VisaType).filter(VisaType.code == 'EAD').first()
        
        if not all([h1b_type, i140_type, i485_type, ead_type]):
            print("   ❌ Required visa types not found! Run seed_visa_types.py first.")
            return False
        
        print("   ✓ Found existing data (admin, contract, law firm, visa types)")
        
        # ============================================================
        # 2. GET EXISTING DEPARTMENTS (created by seed_assess.py)
        # ============================================================
        
        print("\n   Loading existing departments...")
        
        # Query departments created by seed_assess.py
        dept_ts = db.query(Department).filter(
            Department.code == 'TS',
            Department.contract_id == assess_contract.id
        ).first()
        dept_tsm = db.query(Department).filter(
            Department.code == 'TSM',
            Department.contract_id == assess_contract.id
        ).first()
        dept_tsa = db.query(Department).filter(
            Department.code == 'TSA',
            Department.contract_id == assess_contract.id
        ).first()
        dept_tna = db.query(Department).filter(
            Department.code == 'TNA',
            Department.contract_id == assess_contract.id
        ).first()
        dept_av = db.query(Department).filter(
            Department.code == 'AV',
            Department.contract_id == assess_contract.id
        ).first()
        
        if not all([dept_ts, dept_tsm, dept_tsa, dept_tna, dept_av]):
            print("   ❌ ASSESS departments not found! Run seed_assess.py first.")
            return False
        
        print(f"      ✓ Created 5 departments (TS→TSM/TSA, TNA, AV)")
        
        # ============================================================
        # 3. CREATE USERS
        # ============================================================
        
        print("\n   Creating users...")
        
        # HR User
        hr_user = User(
            email='hr@ama-impact.com',
            hashed_password=get_password_hash('HR123!'),
            full_name='Maria Rodriguez',
            role=UserRole.HR,
            contract_id=assess_contract.id,
            is_active=True
        )
        db.add(hr_user)
        
        # Program Manager (sees everything in ASSESS)
        pm_user = User(
            email='pm@ama-impact.com',
            hashed_password=get_password_hash('PM123!'),
            full_name='John Smith',
            role=UserRole.PM,
            contract_id=assess_contract.id,
            department_id=None,  # Contract level
            is_active=True
        )
        db.add(pm_user)
        db.flush()
        
        # Update contract manager
        assess_contract.manager_user_id = pm_user.id
        
        # Tech Lead (TS Manager - sees TS, TSM, TSA)
        tech_lead = User(
            email='techlead@ama-impact.com',
            hashed_password=get_password_hash('Tech123!'),
            full_name='David Chen',
            role=UserRole.MANAGER,
            contract_id=assess_contract.id,
            department_id=dept_ts.id,
            reports_to_id=pm_user.id,
            is_active=True
        )
        db.add(tech_lead)
        db.flush()
        
        # Set tech lead as TS manager
        dept_ts.manager_id = tech_lead.id
        
        # Beneficiary Users (will have visa cases)
        beneficiary_users = [
            {
                'email': 'priya.sharma@ama-impact.com',
                'full_name': 'Priya Sharma',
                'department_id': dept_tsm.id,
                'first_name': 'Priya',
                'last_name': 'Sharma',
                'country_of_citizenship': 'India',
                'country_of_birth': 'India',
                'passport_country': 'India',
                'passport_expiration': date(2028, 6, 15),
                'current_visa_type': 'H1B',
                'current_visa_expiration': date(2026, 9, 30),
                'i94_expiration': date(2026, 9, 30),
                'job_title': 'Senior Software Engineer',
                'employment_start_date': date(2020, 3, 1),
            },
            {
                'email': 'lei.zhang@ama-impact.com',
                'full_name': 'Lei Zhang',
                'department_id': dept_tsa.id,
                'first_name': 'Lei',
                'last_name': 'Zhang',
                'country_of_citizenship': 'China',
                'country_of_birth': 'China',
                'passport_country': 'China',
                'passport_expiration': date(2029, 12, 31),
                'current_visa_type': 'H1B',
                'current_visa_expiration': date(2025, 12, 31),
                'i94_expiration': date(2025, 12, 31),
                'job_title': 'Systems Administrator',
                'employment_start_date': date(2021, 6, 15),
            },
            {
                'email': 'carlos.mendoza@ama-impact.com',
                'full_name': 'Carlos Mendoza',
                'department_id': dept_tna.id,
                'first_name': 'Carlos',
                'last_name': 'Mendoza',
                'country_of_citizenship': 'Mexico',
                'country_of_birth': 'Mexico',
                'passport_country': 'Mexico',
                'passport_expiration': date(2027, 3, 20),
                'current_visa_type': 'TN',
                'current_visa_expiration': date(2026, 2, 28),
                'i94_expiration': date(2026, 2, 28),
                'job_title': 'Network Engineer',
                'employment_start_date': date(2022, 1, 10),
            },
            {
                'email': 'elena.popov@ama-impact.com',
                'full_name': 'Elena Popov',
                'department_id': dept_av.id,
                'first_name': 'Elena',
                'last_name': 'Popov',
                'country_of_citizenship': 'Russia',
                'country_of_birth': 'Russia',
                'passport_country': 'Russia',
                'passport_expiration': date(2030, 8, 10),
                'current_visa_type': None,  # Future hire - being sponsored
                'current_visa_expiration': None,
                'i94_expiration': None,
                'job_title': 'AV Specialist',
                'employment_start_date': date(2023, 7, 1),
            },
            {
                'email': 'kiran.ravikumar@ama-impact.com',
                'full_name': 'Kiran Ravikumar',
                'department_id': dept_tsm.id,
                'first_name': 'Kiran',
                'last_name': 'Ravikumar',
                'country_of_citizenship': 'India',
                'country_of_birth': 'India',
                'passport_country': 'India',
                'passport_expiration': date(2029, 4, 20),
                'current_visa_type': 'H1B',
                'current_visa_expiration': date(2027, 3, 15),
                'i94_expiration': date(2027, 3, 15),
                'job_title': 'Senior Data Scientist',
                'employment_start_date': date(2021, 9, 1),
            },
            {
                'email': 'david.craig@ama-impact.com',
                'full_name': 'David Abraham Penner Craig',
                'department_id': dept_tna.id,
                'first_name': 'David',
                'last_name': 'Craig',
                'country_of_citizenship': 'Canada',
                'country_of_birth': 'Canada',
                'passport_country': 'Canada',
                'passport_expiration': date(2031, 1, 10),
                'current_visa_type': 'TN',
                'current_visa_expiration': date(2026, 6, 30),
                'i94_expiration': date(2026, 6, 30),
                'job_title': 'Network Architect',
                'employment_start_date': date(2020, 5, 15),
            },
        ]
        
        created_beneficiaries = []
        for ben_data in beneficiary_users:
            # Create User account
            user = User(
                email=ben_data['email'],
                hashed_password=get_password_hash('Ben123!'),
                full_name=ben_data['full_name'],
                role=UserRole.BENEFICIARY,
                contract_id=assess_contract.id,
                department_id=ben_data['department_id'],
                reports_to_id=tech_lead.id,
                is_active=True
            )
            db.add(user)
            db.flush()
            
            # Create Beneficiary record
            beneficiary = Beneficiary(
                user_id=user.id,
                first_name=ben_data['first_name'],
                last_name=ben_data['last_name'],
                country_of_citizenship=ben_data['country_of_citizenship'],
                country_of_birth=ben_data['country_of_birth'],
                passport_country=ben_data['passport_country'],
                passport_expiration=ben_data['passport_expiration'],
                current_visa_type=ben_data['current_visa_type'],
                current_visa_expiration=ben_data['current_visa_expiration'],
                i94_expiration=ben_data['i94_expiration'],
                job_title=ben_data['job_title'],
                employment_start_date=ben_data['employment_start_date'],
                is_active=True
            )
            db.add(beneficiary)
            db.flush()
            created_beneficiaries.append((user, beneficiary))
        
        print(f"      ✓ Created 8 users (1 HR, 1 PM, 1 Manager, 6 Beneficiaries)")
        
        # ============================================================
        # 4. CREATE CASE GROUPS AND VISA APPLICATIONS
        # ============================================================
        
        print("\n   Creating case groups and visa applications...")
        
        # CASE 1: Priya - EB2 Green Card Case (Active)
        # I-140 approved, I-485 and EAD being prepared
        priya_user, priya_ben = created_beneficiaries[0]
        
        priya_case = CaseGroup(
            beneficiary_id=priya_ben.id,
            case_type=CaseType.EB2,
            case_number='EB2-2024-001',
            status=CaseStatus.IN_PROGRESS,
            priority=VisaPriority.HIGH,
            case_started_date=date(2024, 1, 15),
            target_completion_date=date(2025, 6, 30),
            responsible_party_id=pm_user.id,
            notes='EB2 green card process. I-140 approved, preparing I-485 and EAD.'
        )
        db.add(priya_case)
        db.flush()
        
        # Priya's I-140 (approved)
        priya_i140 = VisaApplication(
            beneficiary_id=priya_ben.id,
            case_group_id=priya_case.id,
            visa_type_id=i140_type.id,
            created_by=admin.id,
            law_firm_id=law_firm.id,
            responsible_party_id=pm_user.id,
            attorney_name=law_firm.contact_person,
            attorney_email=law_firm.email,
            visa_type=VisaTypeEnum.EB2,
            petition_type='I-140',
            status=VisaStatus.APPROVED,
            case_status=VisaCaseStatus.FINALIZED,
            priority=VisaPriority.HIGH,
            filing_date=date(2024, 3, 1),
            approval_date=date(2024, 10, 15),
            receipt_number='LIN2490123456',
            company_case_id='ASSESS-EB2-PRIYA-I140',
            notes='I-140 approved without RFE'
        )
        db.add(priya_i140)
        
        # Priya's I-485 (in preparation)
        priya_i485 = VisaApplication(
            beneficiary_id=priya_ben.id,
            case_group_id=priya_case.id,
            visa_type_id=i485_type.id,
            created_by=admin.id,
            law_firm_id=law_firm.id,
            responsible_party_id=pm_user.id,
            attorney_name=law_firm.contact_person,
            attorney_email=law_firm.email,
            visa_type=VisaTypeEnum.GREEN_CARD,
            petition_type='I-485',
            status=VisaStatus.DRAFT,
            case_status=VisaCaseStatus.UPCOMING,
            priority=VisaPriority.HIGH,
            company_case_id='ASSESS-EB2-PRIYA-I485',
            notes='Awaiting priority date to become current'
        )
        db.add(priya_i485)
        
        # Priya's EAD (to file with I-485)
        priya_ead = VisaApplication(
            beneficiary_id=priya_ben.id,
            case_group_id=priya_case.id,
            visa_type_id=ead_type.id,
            created_by=admin.id,
            law_firm_id=law_firm.id,
            responsible_party_id=pm_user.id,
            attorney_name=law_firm.contact_person,
            attorney_email=law_firm.email,
            visa_type=VisaTypeEnum.EAD,
            petition_type='I-765',
            status=VisaStatus.DRAFT,
            case_status=VisaCaseStatus.UPCOMING,
            priority=VisaPriority.MEDIUM,
            company_case_id='ASSESS-EB2-PRIYA-EAD',
            notes='Will file concurrent with I-485'
        )
        db.add(priya_ead)
        
        # CASE 2: Lei - H1B Renewal (Standalone)
        lei_user, lei_ben = created_beneficiaries[1]
        
        # Create realistic expiration date (45 days from now - URGENT)
        lei_expiration = (datetime.now() + timedelta(days=45)).date()
        
        lei_h1b = VisaApplication(
            beneficiary_id=lei_ben.id,
            case_group_id=None,  # Standalone application
            visa_type_id=h1b_type.id,
            created_by=admin.id,
            law_firm_id=law_firm.id,
            responsible_party_id=pm_user.id,
            attorney_name=law_firm.contact_person,
            attorney_email=law_firm.email,
            visa_type=VisaTypeEnum.H1B,
            petition_type='I-129',
            status=VisaStatus.IN_PROGRESS,
            case_status=VisaCaseStatus.ACTIVE,
            priority=VisaPriority.CRITICAL,
            current_stage='Filed - Awaiting Receipt',
            filing_date=date(2024, 10, 1),
            expiration_date=lei_expiration,
            receipt_number='WAC2590234567',
            company_case_id='ASSESS-H1B-LEI-RENEWAL',
            premium_processing=True,
            notes=f'H1B extension - expires {lei_expiration.strftime("%m/%d/%Y")}, urgent'
        )
        db.add(lei_h1b)
        
        # CASE 3: Carlos - TN Extension (Standalone)
        carlos_user, carlos_ben = created_beneficiaries[2]
        
        # Create expiration date (90 days from now - MEDIUM urgency)
        carlos_expiration = (datetime.now() + timedelta(days=90)).date()
        
        carlos_tn = VisaApplication(
            beneficiary_id=carlos_ben.id,
            case_group_id=None,
            visa_type_id=db.query(VisaType).filter(VisaType.code == 'TN').first().id,
            created_by=admin.id,
            responsible_party_id=pm_user.id,
            visa_type=VisaTypeEnum.TN,
            petition_type='TN Application',
            status=VisaStatus.IN_PROGRESS,
            case_status=VisaCaseStatus.ACTIVE,
            priority=VisaPriority.MEDIUM,
            expiration_date=carlos_expiration,
            company_case_id='ASSESS-TN-CARLOS-RENEWAL',
            notes=f'TN renewal - expires {carlos_expiration.strftime("%m/%d/%Y")}'
        )
        db.add(carlos_tn)
        
        # CASE 4: Elena - EB2 Case (All Planning)
        elena_user, elena_ben = created_beneficiaries[3]
        
        elena_case = CaseGroup(
            beneficiary_id=elena_ben.id,
            case_type=CaseType.EB2,
            case_number='EB2-2025-002',
            status=CaseStatus.PLANNING,
            priority=VisaPriority.MEDIUM,
            target_completion_date=date(2026, 12, 31),
            responsible_party_id=pm_user.id,
            notes='EB2 case in early planning stages'
        )
        db.add(elena_case)
        db.flush()
        
        # Elena's I-140 (planned)
        elena_i140 = VisaApplication(
            beneficiary_id=elena_ben.id,
            case_group_id=elena_case.id,
            visa_type_id=i140_type.id,
            created_by=admin.id,
            law_firm_id=law_firm.id,
            responsible_party_id=pm_user.id,
            visa_type=VisaTypeEnum.EB2,
            petition_type='I-140',
            status=VisaStatus.DRAFT,
            case_status=VisaCaseStatus.UPCOMING,
            priority=VisaPriority.MEDIUM,
            company_case_id='ASSESS-EB2-ELENA-I140',
            notes='Gathering documents for I-140 filing'
        )
        db.add(elena_i140)
        
        # CASE 5: Add an OVERDUE H1B for testing urgent scenarios
        # Use fourth beneficiary (if exists) or create a simple standalone overdue visa
        if len(created_beneficiaries) > 3:
            fourth_user, fourth_ben = created_beneficiaries[3]
        else:
            # Use Lei's beneficiary for an additional overdue visa
            fourth_user, fourth_ben = created_beneficiaries[1]
        
        overdue_expiration = (datetime.now() - timedelta(days=15)).date()  # 15 days overdue
        
        overdue_h1b = VisaApplication(
            beneficiary_id=fourth_ben.id,
            case_group_id=None,
            visa_type_id=h1b_type.id,
            created_by=admin.id,
            law_firm_id=law_firm.id,
            responsible_party_id=pm_user.id,
            attorney_name=law_firm.contact_person,
            attorney_email=law_firm.email,
            visa_type=VisaTypeEnum.H1B,
            petition_type='I-129',
            status=VisaStatus.APPROVED,
            case_status=VisaCaseStatus.FINALIZED,  # Use FINALIZED for expired visa
            priority=VisaPriority.CRITICAL,
            current_stage='Expired - Extension Required',
            filing_date=date(2021, 8, 1),
            approval_date=date(2021, 10, 1),
            expiration_date=overdue_expiration,
            receipt_number='WAC2190123456',
            company_case_id='ASSESS-H1B-EXPIRED-TEST',
            premium_processing=False,
            notes=f'H1B EXPIRED on {overdue_expiration.strftime("%m/%d/%Y")} - URGENT EXTENSION NEEDED'
        )
        db.add(overdue_h1b)
        
        # CASE 6: Add an EAD expiring in 6 months (not urgent but within range)
        future_expiration = (datetime.now() + timedelta(days=180)).date()
        
        future_ead = VisaApplication(
            beneficiary_id=priya_ben.id,
            case_group_id=None,
            visa_type_id=ead_type.id,
            created_by=admin.id,
            law_firm_id=law_firm.id,
            responsible_party_id=pm_user.id,
            attorney_name=law_firm.contact_person,
            attorney_email=law_firm.email,
            visa_type=VisaTypeEnum.EAD,
            petition_type='I-765',
            status=VisaStatus.APPROVED,
            case_status=VisaCaseStatus.ACTIVE,
            priority=VisaPriority.LOW,
            current_stage='Approved - Valid Until Expiration',
            approval_date=date(2023, 6, 1),
            expiration_date=future_expiration,
            receipt_number='MSC2390567890',
            company_case_id='ASSESS-EAD-PRIYA-CURRENT',
            premium_processing=False,
            notes=f'Current EAD valid until {future_expiration.strftime("%m/%d/%Y")}'
        )
        db.add(future_ead)
        
        # ============================================================
        # APPROVAL WORKFLOW TEST CASES
        # ============================================================
        
        # CASE 7: Kiran Ravikumar - EB-1A case PENDING PM APPROVAL
        kiran_user, kiran_ben = created_beneficiaries[4]
        
        kiran_case = CaseGroup(
            beneficiary_id=kiran_ben.id,
            case_type=CaseType.EB1,
            case_number='EB1A-2025-003',
            status=CaseStatus.PLANNING,
            priority=VisaPriority.HIGH,
            case_started_date=date.today(),
            target_completion_date=date(2026, 3, 31),
            responsible_party_id=pm_user.id,
            created_by_manager_id=tech_lead.id,
            approval_status=ApprovalStatus.PENDING_PM_APPROVAL,  # Submitted for PM approval
            notes='EB-1A Extraordinary Ability application - AI/ML researcher with multiple publications and conference presentations.',
            attorney_portal_link='https://example-law-firm.com/cases/kiran-ravikumar-eb1a'
        )
        db.add(kiran_case)
        db.flush()
        
        # Kiran's current H1B (active)
        kiran_h1b = VisaApplication(
            beneficiary_id=kiran_ben.id,
            case_group_id=None,  # Not part of case group, just current status
            visa_type_id=h1b_type.id,
            created_by=admin.id,
            law_firm_id=law_firm.id,
            responsible_party_id=pm_user.id,
            attorney_name=law_firm.contact_person,
            attorney_email=law_firm.email,
            visa_type=VisaTypeEnum.H1B,
            petition_type='I-129',
            status=VisaStatus.APPROVED,
            case_status=VisaCaseStatus.ACTIVE,
            priority=VisaPriority.MEDIUM,
            approval_date=date(2024, 3, 15),
            expiration_date=date(2027, 3, 15),
            receipt_number='WAC2490345678',
            company_case_id='ASSESS-H1B-KIRAN',
            notes='Current H1B valid until 2027'
        )
        db.add(kiran_h1b)
        
        # Kiran's EB-1A I-140 (draft - in case group)
        kiran_i140 = VisaApplication(
            beneficiary_id=kiran_ben.id,
            case_group_id=kiran_case.id,
            visa_type_id=i140_type.id,
            created_by=admin.id,
            law_firm_id=law_firm.id,
            responsible_party_id=pm_user.id,
            attorney_name=law_firm.contact_person,
            attorney_email=law_firm.email,
            visa_type=VisaTypeEnum.EB1A,
            petition_type='I-140',
            status=VisaStatus.DRAFT,
            case_status=VisaCaseStatus.UPCOMING,
            priority=VisaPriority.HIGH,
            company_case_id='ASSESS-EB1A-KIRAN-I140',
            notes='EB-1A I-140 petition in preparation - awaiting PM approval to proceed'
        )
        db.add(kiran_i140)
        
        # CASE 8: David Craig - H1B Transfer PENDING PM APPROVAL
        david_user, david_ben = created_beneficiaries[5]
        
        david_h1b_case = CaseGroup(
            beneficiary_id=david_ben.id,
            case_type=CaseType.H1B_TRANSFER,
            case_number='H1B-TRANS-2025-004',
            status=CaseStatus.PLANNING,
            priority=VisaPriority.MEDIUM,
            case_started_date=date.today(),
            target_completion_date=date(2026, 1, 31),
            responsible_party_id=pm_user.id,
            created_by_manager_id=tech_lead.id,
            approval_status=ApprovalStatus.PENDING_PM_APPROVAL,  # Submitted for PM approval
            notes='H1B transfer from TN status. Position change to Network Architect role.',
            attorney_portal_link='https://example-law-firm.com/cases/david-craig-h1b-transfer'
        )
        db.add(david_h1b_case)
        db.flush()
        
        # David's H1B transfer application (draft - in case group)
        david_h1b_app = VisaApplication(
            beneficiary_id=david_ben.id,
            case_group_id=david_h1b_case.id,
            visa_type_id=h1b_type.id,
            created_by=admin.id,
            law_firm_id=law_firm.id,
            responsible_party_id=pm_user.id,
            attorney_name=law_firm.contact_person,
            attorney_email=law_firm.email,
            visa_type=VisaTypeEnum.H1B,
            petition_type='I-129',
            status=VisaStatus.DRAFT,
            case_status=VisaCaseStatus.UPCOMING,
            priority=VisaPriority.MEDIUM,
            company_case_id='ASSESS-H1B-DAVID',
            notes='H1B initial petition - awaiting PM approval to proceed with filing'
        )
        db.add(david_h1b_app)
        
        # CASE 9: David Craig - EB-2 NIW at I-140 stage (APPROVED by PM, in progress)
        david_eb2_case = CaseGroup(
            beneficiary_id=david_ben.id,
            case_type=CaseType.EB2_NIW,
            case_number='EB2-NIW-2024-005',
            status=CaseStatus.IN_PROGRESS,
            priority=VisaPriority.HIGH,
            case_started_date=date(2024, 6, 1),
            target_completion_date=date(2025, 12, 31),
            responsible_party_id=pm_user.id,
            created_by_manager_id=tech_lead.id,
            approval_status=ApprovalStatus.PM_APPROVED,  # Already approved
            approved_by_pm_id=pm_user.id,
            pm_approval_date=datetime(2024, 6, 15, 10, 30, 0),
            pm_approval_notes='Approved - strong NIW case with network security expertise',
            notes='EB-2 NIW case at I-140 stage. National interest in cybersecurity infrastructure.',
            attorney_portal_link='https://example-law-firm.com/cases/david-craig-eb2-niw'
        )
        db.add(david_eb2_case)
        db.flush()
        
        # David's EB-2 NIW I-140 (filed - in case group)
        david_i140 = VisaApplication(
            beneficiary_id=david_ben.id,
            case_group_id=david_eb2_case.id,
            visa_type_id=i140_type.id,
            created_by=admin.id,
            law_firm_id=law_firm.id,
            responsible_party_id=pm_user.id,
            attorney_name=law_firm.contact_person,
            attorney_email=law_firm.email,
            visa_type=VisaTypeEnum.EB2NIW,
            petition_type='I-140',
            status=VisaStatus.IN_PROGRESS,
            case_status=VisaCaseStatus.ACTIVE,
            priority=VisaPriority.HIGH,
            filing_date=date(2024, 7, 1),
            receipt_number='LIN2490456789',
            company_case_id='ASSESS-EB2NIW-DAVID-I140',
            notes='I-140 filed and pending USCIS review - no RFE yet'
        )
        db.add(david_i140)
        
        print(f"      ✓ Created 5 case groups (2 with approval workflow) and 13 visa applications")
        
        # ============================================================
        # 5. CREATE DEPENDENTS
        # ============================================================
        
        print("\n   Creating dependents...")
        
        # Priya's dependent
        priya_dependent = Dependent(
            beneficiary_id=priya_ben.id,
            first_name='Arjun',
            last_name='Sharma',
            date_of_birth=date(2018, 5, 12),
            relationship_type=RelationshipType.CHILD,
            country_of_citizenship='India',
            country_of_birth='United States',
            current_visa_type='H4',
            visa_expiration=date(2026, 9, 30),
            i94_expiration=date(2026, 9, 30),
            passport_country='India',
            passport_expiration=date(2028, 6, 15)
        )
        db.add(priya_dependent)
        
        print(f"      ✓ Created 1 dependent")
        
        # ============================================================
        # 6. CREATE TODOS
        # ============================================================
        
        print("\n   Creating todos...")
        
        from app.models.todo import Todo, TodoStatus, TodoPriority
        # timedelta already imported at top level
        
        # Todo 1: Submit I-485 for Priya (urgent, assigned to HR)
        todo1 = Todo(
            title='Submit I-485 application for Priya Sharma',
            description='Complete and file I-485 adjustment of status petition. I-140 already approved.',
            assigned_to_user_id=hr_user.id,
            created_by_user_id=pm_user.id,
            visa_application_id=priya_i485.id,
            case_group_id=priya_case.id,
            beneficiary_id=priya_ben.id,
            status=TodoStatus.TODO,
            priority=TodoPriority.URGENT,
            due_date=datetime.utcnow() + timedelta(days=30)
        )
        db.add(todo1)
        
        # Todo 2: Prepare EAD application for Priya
        todo2 = Todo(
            title='Prepare EAD application for Priya',
            description='Prepare I-765 Employment Authorization Document concurrent with I-485',
            assigned_to_user_id=hr_user.id,
            created_by_user_id=pm_user.id,
            visa_application_id=priya_ead.id,
            case_group_id=priya_case.id,
            beneficiary_id=priya_ben.id,
            status=TodoStatus.IN_PROGRESS,
            priority=TodoPriority.HIGH,
            due_date=datetime.utcnow() + timedelta(days=30)
        )
        db.add(todo2)
        
        # Todo 3: H1B renewal for Lei Zhang (urgent - expires soon)
        todo3 = Todo(
            title='Process H1B renewal for Lei Zhang',
            description='Current H1B expires 12/31/2025. Must file extension at least 6 months prior.',
            assigned_to_user_id=hr_user.id,
            created_by_user_id=pm_user.id,
            visa_application_id=lei_h1b.id,
            case_group_id=None,
            beneficiary_id=lei_ben.id,
            status=TodoStatus.IN_PROGRESS,
            priority=TodoPriority.URGENT,
            due_date=datetime(2025, 6, 30, 0, 0, 0)  # 6 months before expiration
        )
        db.add(todo3)
        
        # Todo 4: Schedule I-140 consultation for Elena
        todo4 = Todo(
            title='Schedule EB2 consultation for Elena Popov',
            description='Initial consultation with immigration attorney to review EB2 eligibility and requirements',
            assigned_to_user_id=pm_user.id,
            created_by_user_id=pm_user.id,
            visa_application_id=elena_i140.id,
            case_group_id=elena_case.id,
            beneficiary_id=elena_ben.id,
            status=TodoStatus.TODO,
            priority=TodoPriority.MEDIUM,
            due_date=datetime.utcnow() + timedelta(days=14)
        )
        db.add(todo4)
        
        # Todo 5: Gather documents for Carlos TN renewal
        todo5 = Todo(
            title='Gather TN renewal documents for Carlos Mendoza',
            description='Collect updated employer letter, credentials, and supporting docs for TN renewal',
            assigned_to_user_id=carlos_user.id,  # Assigned to beneficiary himself
            created_by_user_id=hr_user.id,
            visa_application_id=carlos_tn.id,
            case_group_id=None,
            beneficiary_id=carlos_ben.id,
            status=TodoStatus.TODO,
            priority=TodoPriority.MEDIUM,
            due_date=datetime(2025, 11, 1, 0, 0, 0)
        )
        db.add(todo5)
        
        # Todo 6: Review all expiring visas Q1 2026 (general todo for HR)
        todo6 = Todo(
            title='Review all visas expiring Q1 2026',
            description='Quarterly review of all visa expirations to ensure renewals are planned',
            assigned_to_user_id=hr_user.id,
            created_by_user_id=pm_user.id,
            visa_application_id=None,
            case_group_id=None,
            beneficiary_id=None,
            status=TodoStatus.TODO,
            priority=TodoPriority.HIGH,
            due_date=datetime(2025, 12, 15, 0, 0, 0)
        )
        db.add(todo6)
        
        # Todo 7: Update Priya's employment letter (case-level todo)
        todo7 = Todo(
            title='Update employment verification letter',
            description='Get updated employment letter from David Chen for EB2 case documentation',
            assigned_to_user_id=tech_lead.id,  # Assigned to manager
            created_by_user_id=hr_user.id,
            visa_application_id=None,
            case_group_id=priya_case.id,
            beneficiary_id=priya_ben.id,
            status=TodoStatus.TODO,
            priority=TodoPriority.MEDIUM,
            due_date=datetime.utcnow() + timedelta(days=7)
        )
        db.add(todo7)
        
        print(f"      ✓ Created 7 todos (1 urgent, 2 high, 2 medium priority)")

        # ============================================================
        # 7. CREATE SAMPLE AUDIT LOGS (if none exist)
        # ============================================================
        try:
            existing_logs = db.query(AuditLog).count()
        except Exception:
            existing_logs = 0

        if existing_logs == 0:
            print("\n   Creating sample audit logs...")
            now = datetime.utcnow()
            sample_logs = [
                AuditLog(user_id=pm_user.id, action=AuditAction.CREATE, resource_type='case_group', resource_id=str(priya_case.id), new_value={'case_number': priya_case.case_number}, created_at=now - timedelta(hours=2)),
                AuditLog(user_id=hr_user.id, action=AuditAction.CREATE, resource_type='todo', resource_id=str(todo1.id), new_value={'title': todo1.title}, created_at=now - timedelta(hours=5)),
                AuditLog(user_id=tech_lead.id, action=AuditAction.UPDATE, resource_type='department', resource_id=str(dept_ts.id), new_value={'manager_id': tech_lead.id}, created_at=now - timedelta(days=1)),
                AuditLog(user_id=admin.id, action=AuditAction.SYSTEM, resource_type='seed', resource_id=None, new_value={'message': 'Development seed created'}, created_at=now - timedelta(days=1, hours=3)),
            ]
            for log in sample_logs:
                db.add(log)
            db.flush()
            print("      ✓ Created sample audit logs")
        
        # ============================================================
        # COMMIT ALL
        # ============================================================
        
        db.commit()
        
        print("\n✅ Development data seeded successfully!")
        print(f"\n   Summary:")
        print(f"   - 5 Departments (TS→TSM/TSA, TNA, AV)")
        print(f"   - 8 Users (HR, PM, Manager, 6 Beneficiaries)")
        print(f"   - 6 Beneficiaries with visa info")
        print(f"   - 5 Case Groups (2 EB2, 1 EB-1A, 1 H1B Transfer, 1 EB2-NIW with approval workflow)")
        print(f"   - 13 Visa Applications (various stages)")
        print(f"   - 1 Dependent")
        print(f"   - 7 Todos (3 critical/urgent, 2 high, 2 medium)")
        
        print(f"\n   Test Logins:")
        print(f"   HR:            hr@ama-impact.com / HR123!")
        print(f"   PM:            pm@ama-impact.com / PM123!")
        print(f"   Tech Lead:     techlead@ama-impact.com / Tech123!")
        print(f"   Beneficiaries: priya.sharma@ama-impact.com / Ben123!")
        print(f"                  kiran.ravikumar@ama-impact.com / Ben123! (EB-1A pending approval)")
        print(f"                  david.craig@ama-impact.com / Ben123! (H1B + EB2-NIW cases)")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error seeding development data: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = seed_development_data()
    sys.exit(0 if success else 1)
