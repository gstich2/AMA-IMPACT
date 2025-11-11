#!/usr/bin/env python3
"""
Seed ASSESS beneficiaries with realistic employee data.
Creates beneficiary users, case groups, visa applications, and milestones.

Prerequisites: Run these fixtures first:
1. seed_visa_types.py
2. seed_assess.py (creates contract + departments + managers)
3. seed_law_firms.py
"""

import sys
from pathlib import Path
from datetime import date, datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.contract import Contract
from app.models.department import Department
from app.models.beneficiary import Beneficiary
from app.models.law_firm import LawFirm
from app.models.visa import VisaType, VisaApplication, VisaTypeEnum, VisaStatus, VisaCaseStatus, VisaPriority
from app.models.case_group import CaseGroup, CaseType, CaseStatus, ApprovalStatus
from app.models.milestone import ApplicationMilestone, MilestoneType
from app.models.audit import AuditLog, AuditAction


def seed_assess_beneficiaries():
    """Seed ASSESS beneficiaries with realistic employee data."""
    db = SessionLocal()
    
    try:
        print("\n📋 Seeding ASSESS beneficiaries...")
        
        # ============================================================
        # 1. GET EXISTING DATA
        # ============================================================
        
        # Get ASSESS contract
        assess_contract = db.query(Contract).filter(Contract.code == 'ASSESS').first()
        if not assess_contract:
            print("   ❌ ASSESS contract not found! Run seed_assess.py first.")
            return False
        
        # Get PM (Dave Cornelius)
        pm_user = db.query(User).filter(
            User.email == 'pm.assess@ama-impact.com'
        ).first()
        if not pm_user:
            print("   ❌ PM user not found! Run seed_assess.py first.")
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
        dept_tsa = db.query(Department).filter(
            Department.code == 'TSA',
            Department.contract_id == assess_contract.id
        ).first()
        dept_tsm = db.query(Department).filter(
            Department.code == 'TSM',
            Department.contract_id == assess_contract.id
        ).first()
        dept_tss = db.query(Department).filter(
            Department.code == 'TSS',
            Department.contract_id == assess_contract.id
        ).first()
        
        if not all([dept_tna, dept_tnp, dept_av, dept_tsa, dept_tsm, dept_tss]):
            print("   ❌ ASSESS departments not found! Run seed_assess.py first.")
            return False
        
        # Get managers
        manager_gerrit = db.query(User).filter(
            User.email == 'gerrit-daniel.stich@ama-inc.com'
        ).first()
        manager_patricia = db.query(User).filter(
            User.email == 'patricia.ventura@ama-inc.com'
        ).first()
        manager_bhaskaran = db.query(User).filter(
            User.email == 'bhaskaran.rathakrishnan@ama-inc.com'
        ).first()
        manager_arnaud = db.query(User).filter(
            User.email == 'arnaud.borner@ama-inc.com'
        ).first()
        
        if not all([manager_gerrit, manager_patricia, manager_bhaskaran, manager_arnaud]):
            print("   ❌ Managers not found! Run seed_assess.py first.")
            return False
        
        # Get law firms
        goel_anderson = db.query(LawFirm).filter(LawFirm.name.like('%Goel%')).first()
        if not goel_anderson:
            print("   ❌ Law firm not found! Run seed_law_firms.py first.")
            return False
        
        # Get visa types
        h1b_type = db.query(VisaType).filter(VisaType.code == 'H1B').first()
        tn_type = db.query(VisaType).filter(VisaType.code == 'TN').first()
        i140_type = db.query(VisaType).filter(VisaType.code == 'I140').first()
        i485_type = db.query(VisaType).filter(VisaType.code == 'I485').first()
        perm_type = db.query(VisaType).filter(VisaType.code == 'PERM').first()
        
        if not all([h1b_type, tn_type, i140_type, i485_type, perm_type]):
            print("   ❌ Required visa types not found! Run seed_visa_types.py first.")
            return False
        
        print("   ✓ Found existing data (contract, managers, departments, law firms, visa types)")
        
        # ============================================================
        # 2. CREATE MANAGER BENEFICIARIES WITH COMPLETED LPR CASES
        # ============================================================
        
        print("\n   Creating manager beneficiaries with completed LPR cases...")
        
        # Gerrit-Daniel Stich - TNA Manager (ALREADY A USER from seed_assess.py)
        beneficiary_gerrit = Beneficiary(
            user_id=manager_gerrit.id,
            first_name='Gerrit-Daniel',
            last_name='Stich',
            country_of_citizenship='Germany',
            country_of_birth='Germany',
            passport_country='Germany',
            passport_expiration=date(2032, 12, 31),  # Made up - LPR holders keep passports
            current_visa_type='LPR',
            current_visa_expiration=date(2033, 1, 1),
            i94_expiration=None,  # LPR holders don't have I-94
            job_title='Branch Technical Lead, Principal Associate',
            employment_start_date=date(2015, 1, 1)
        )
        db.add(beneficiary_gerrit)
        db.flush()
        
        # Case Group: Gerrit's EB2-NIW to Green Card (COMPLETED)
        case_gerrit = CaseGroup(
            beneficiary_id=beneficiary_gerrit.id,
            name='Gerrit-Daniel Stich - EB2-NIW to Green Card',
            description='EB2-NIW pathway to lawful permanent resident status',
            case_type=CaseType.EB2_NIW,
            priority=VisaPriority.MEDIUM,
            status=CaseStatus.IN_PROGRESS,
            approval_status=ApprovalStatus.PM_APPROVED,
            start_date=date(2018, 3, 1),
            target_completion_date=date(2020, 6, 30),
            actual_completion_date=date(2020, 5, 15),
            assigned_hr_user_id=pm_user.id,
            law_firm_id=goel_anderson.id,
            approved_by_pm_id=pm_user.id,
            approval_notes='Approved EB2-NIW case for Principal Associate position',
            created_by_id=pm_user.id
        )
        db.add(case_gerrit)
        db.flush()
        
        # Visa Applications for Gerrit
        visa_gerrit_i140 = VisaApplication(
            beneficiary_id=beneficiary_gerrit.id,
            user_id=manager_gerrit.id,
            case_group_id=case_gerrit.id,
            visa_type_id=i140_type.id,
            current_status=VisaCaseStatus.APPROVED,
            priority=VisaPriority.MEDIUM,
            filing_date=date(2018, 6, 15),
            approval_date=date(2019, 2, 10),
            start_date=date(2019, 2, 10),
            end_date=None,  # I-140 doesn't expire
            law_firm_id=goel_anderson.id,
            receipt_number='SRC1890012345',
            notes='I-140 approved for EB2-NIW'
        )
        visa_gerrit_i485 = VisaApplication(
            beneficiary_id=beneficiary_gerrit.id,
            user_id=manager_gerrit.id,
            case_group_id=case_gerrit.id,
            visa_type_id=i485_type.id,
            current_status=VisaCaseStatus.APPROVED,
            priority=VisaPriority.MEDIUM,
            filing_date=date(2019, 9, 1),
            approval_date=date(2020, 5, 15),
            start_date=date(2020, 5, 15),
            end_date=date(2033, 1, 1),  # Green card expiration
            law_firm_id=goel_anderson.id,
            receipt_number='SRC1990056789',
            notes='I-485 approved, received green card'
        )
        db.add_all([visa_gerrit_i140, visa_gerrit_i485])
        db.flush()
        
        # Milestones for Gerrit's completed case
        milestones_gerrit = [
            ApplicationMilestone(
                visa_application_id=visa_gerrit_i140.id,
                milestone_type=MilestoneType.FILED_WITH_USCIS,
                milestone_date=date(2018, 6, 15),
                description='I-140 filed with USCIS',
                created_by=pm_user.id
            ),
            ApplicationMilestone(
                visa_application_id=visa_gerrit_i140.id,
                milestone_type=MilestoneType.APPROVED,
                milestone_date=date(2019, 2, 10),
                description='I-140 approved',
                created_by=pm_user.id
            ),
            ApplicationMilestone(
                visa_application_id=visa_gerrit_i485.id,
                milestone_type=MilestoneType.FILED_WITH_USCIS,
                milestone_date=date(2019, 9, 1),
                description='I-485 filed with USCIS',
                created_by=pm_user.id
            ),
            ApplicationMilestone(
                visa_application_id=visa_gerrit_i485.id,
                milestone_type=MilestoneType.APPROVED,
                milestone_date=date(2020, 5, 15),
                description='I-485 approved, green card received',
                created_by=pm_user.id
            )
        ]
        db.add_all(milestones_gerrit)
        
        # Bhaskaran Rathakrishnan - TSA Manager (ALREADY A USER from seed_assess.py)
        beneficiary_bhaskaran = Beneficiary(
            user_id=manager_bhaskaran.id,
            first_name='Bhaskaran',
            last_name='Rathakrishnan',
            country_of_citizenship='India',
            country_of_birth='India',
            passport_country='India',
            passport_expiration=date(2031, 8, 15),
            current_visa_type='LPR',
            current_visa_expiration=date(2032, 6, 1),
            i94_expiration=None,
            job_title='Branch Manager, Aerothermodynamics',
            employment_start_date=date(2014, 9, 1)
        )
        db.add(beneficiary_bhaskaran)
        db.flush()
        
        # Case Group: Bhaskaran's EB2-NIW to Green Card (COMPLETED)
        case_bhaskaran = CaseGroup(
            beneficiary_id=beneficiary_bhaskaran.id,
            name='Bhaskaran Rathakrishnan - EB2-NIW to Green Card',
            description='EB2-NIW pathway to lawful permanent resident status',
            case_type=CaseType.EB2_NIW,
            priority=VisaPriority.MEDIUM,
            status=CaseStatus.IN_PROGRESS,
            approval_status=ApprovalStatus.PM_APPROVED,
            start_date=date(2017, 6, 1),
            target_completion_date=date(2019, 12, 31),
            actual_completion_date=date(2019, 11, 20),
            assigned_hr_user_id=pm_user.id,
            law_firm_id=goel_anderson.id,
            approved_by_pm_id=pm_user.id,
            approval_notes='Approved EB2-NIW case for Branch Manager position',
            created_by_id=pm_user.id
        )
        db.add(case_bhaskaran)
        db.flush()
        
        # Visa Applications for Bhaskaran (simplified, similar to Gerrit)
        visa_bhaskaran_i140 = VisaApplication(
            beneficiary_id=beneficiary_bhaskaran.id,
            user_id=manager_bhaskaran.id,
            case_group_id=case_bhaskaran.id,
            visa_type_id=i140_type.id,
            current_status=VisaCaseStatus.APPROVED,
            priority=VisaPriority.MEDIUM,
            filing_date=date(2017, 9, 1),
            approval_date=date(2018, 5, 10),
            start_date=date(2018, 5, 10),
            end_date=None,
            law_firm_id=goel_anderson.id,
            receipt_number='SRC1790023456',
            notes='I-140 approved for EB2-NIW'
        )
        visa_bhaskaran_i485 = VisaApplication(
            beneficiary_id=beneficiary_bhaskaran.id,
            user_id=manager_bhaskaran.id,
            case_group_id=case_bhaskaran.id,
            visa_type_id=i485_type.id,
            current_status=VisaCaseStatus.APPROVED,
            priority=VisaPriority.MEDIUM,
            filing_date=date(2018, 11, 1),
            approval_date=date(2019, 11, 20),
            start_date=date(2019, 11, 20),
            end_date=date(2032, 6, 1),
            law_firm_id=goel_anderson.id,
            receipt_number='SRC1890067890',
            notes='I-485 approved, received green card'
        )
        db.add_all([visa_bhaskaran_i140, visa_bhaskaran_i485])
        
        # Arnaud Borner - TSM Manager (ALREADY A USER from seed_assess.py)
        beneficiary_arnaud = Beneficiary(
            user_id=manager_arnaud.id,
            first_name='Arnaud',
            last_name='Borner',
            country_of_citizenship='France',
            country_of_birth='France',
            passport_country='France',
            passport_expiration=date(2033, 3, 20),
            current_visa_type='LPR',
            current_visa_expiration=date(2034, 2, 15),
            i94_expiration=None,
            job_title='Branch Manager, Thermal Protection Materials',
            employment_start_date=date(2016, 2, 15)
        )
        db.add(beneficiary_arnaud)
        db.flush()
        
        # Case Group: Arnaud's EB2-NIW to Green Card (COMPLETED)
        case_arnaud = CaseGroup(
            beneficiary_id=beneficiary_arnaud.id,
            name='Arnaud Borner - EB2-NIW to Green Card',
            description='EB2-NIW pathway to lawful permanent resident status',
            case_type=CaseType.EB2_NIW,
            priority=VisaPriority.MEDIUM,
            status=CaseStatus.IN_PROGRESS,
            approval_status=ApprovalStatus.PM_APPROVED,
            start_date=date(2019, 1, 10),
            target_completion_date=date(2021, 6, 30),
            actual_completion_date=date(2021, 5, 30),
            assigned_hr_user_id=pm_user.id,
            law_firm_id=goel_anderson.id,
            approved_by_pm_id=pm_user.id,
            approval_notes='Approved EB2-NIW case for Branch Manager position',
            created_by_id=pm_user.id
        )
        db.add(case_arnaud)
        db.flush()
        
        # Visa Applications for Arnaud (simplified)
        visa_arnaud_i140 = VisaApplication(
            beneficiary_id=beneficiary_arnaud.id,
            user_id=manager_arnaud.id,
            case_group_id=case_arnaud.id,
            visa_type_id=i140_type.id,
            current_status=VisaCaseStatus.APPROVED,
            priority=VisaPriority.MEDIUM,
            filing_date=date(2019, 4, 15),
            approval_date=date(2020, 1, 10),
            start_date=date(2020, 1, 10),
            end_date=None,
            law_firm_id=goel_anderson.id,
            receipt_number='SRC1990034567',
            notes='I-140 approved for EB2-NIW'
        )
        visa_arnaud_i485 = VisaApplication(
            beneficiary_id=beneficiary_arnaud.id,
            user_id=manager_arnaud.id,
            case_group_id=case_arnaud.id,
            visa_type_id=i485_type.id,
            current_status=VisaCaseStatus.APPROVED,
            priority=VisaPriority.MEDIUM,
            filing_date=date(2020, 6, 1),
            approval_date=date(2021, 5, 30),
            start_date=date(2021, 5, 30),
            end_date=date(2034, 2, 15),
            law_firm_id=goel_anderson.id,
            receipt_number='SRC2090078901',
            notes='I-485 approved, received green card'
        )
        db.add_all([visa_arnaud_i140, visa_arnaud_i485])
        
        print(f"   ✓ Created 3 manager beneficiaries with completed LPR cases")
        print(f"     - Gerrit-Daniel Stich (TNA)")
        print(f"     - Bhaskaran Rathakrishnan (TSA)")
        print(f"     - Arnaud Borner (TSM)")
        
        # ============================================================
        # 3. CREATE EMPLOYEE BENEFICIARIES (Active Cases)
        # ============================================================
        
        print("\n   Creating employee beneficiaries with active cases...")
        
        # Current date for calculations
        today = date.today()  # 2025-11-11
        
        # Brandon Lowe - PENDING_PM_APPROVAL (EB2-NIW)
        user_brandon = User(
            hashed_password=get_password_hash('Dev123!'),
            full_name='Brandon Lowe',
            role=UserRole.BENEFICIARY,
            contract_id=assess_contract.id,
            department_id=dept_tna.id,
            reports_to_id=manager_gerrit.id,
            is_active=True,
            force_password_change=False
        )
        db.add(user_brandon)
        db.flush()
        
        beneficiary_brandon = Beneficiary(
            user_id=user_brandon.id,
            first_name='Brandon',
            last_name='Lowe',
            country_of_citizenship='Canada',
            country_of_birth='Canada',
            passport_country='Canada',
            passport_expiration=date(2030, 6, 15),
            current_visa_type='TN',
            current_visa_expiration=date(2026, 1, 5),
            i94_expiration=date(2026, 1, 5),
            job_title='Senior Research Scientist',
            employment_start_date=date(2022, 5, 15)
        )
        db.add(beneficiary_brandon)
        db.flush()
        
        case_brandon = CaseGroup(
            beneficiary_id=beneficiary_brandon.id,
            name='Brandon Lowe - EB2-NIW Green Card',
            description='EB2-NIW pathway for Senior Research Scientist',
            case_type=CaseType.EB2_NIW,
            priority=VisaPriority.HIGH,
            status=CaseStatus.ACTIVE,
            approval_status=ApprovalStatus.PENDING_PM_APPROVAL,
            start_date=date(2025, 9, 15),
            target_completion_date=date(2027, 3, 31),
            assigned_hr_user_id=None,  # Not assigned yet
            law_firm_id=None,  # Not assigned yet
            approved_by_pm_id=None,
            created_by_id=pm_user.id
        )
        db.add(case_brandon)
        db.flush()
        
        # Audit log for submission
        audit_brandon = AuditLog(
            user_id=pm_user.id,
            action=AuditAction.UPDATE,
            resource_type='case_group',
            resource_id=case_brandon.id,
            old_values={'approval_status': 'DRAFT'},
            new_values={'approval_status': 'PENDING_PM_APPROVAL'},
            ip_address='127.0.0.1',
            timestamp=datetime.now() - timedelta(days=5)
        )
        db.add(audit_brandon)
        
        print(f"     ✓ Brandon Lowe - EB2-NIW (PENDING_PM_APPROVAL)")
        
        # David Craig Penner - APPROVED, HR hasn't scheduled meetings (TN to H1B)
        user_david_craig = User(
            hashed_password=get_password_hash('Dev123!'),
            full_name='David Craig Penner',
            role=UserRole.BENEFICIARY,
            contract_id=assess_contract.id,
            department_id=dept_tna.id,
            reports_to_id=manager_gerrit.id,
            is_active=True,
            force_password_change=False
        )
        db.add(user_david_craig)
        db.flush()
        
        beneficiary_david_craig = Beneficiary(
            user_id=user_david_craig.id,
            first_name='David Craig',
            last_name='Penner',
            country_of_citizenship='Canada',
            country_of_birth='Canada',
            passport_country='Canada',
            passport_expiration=date(2031, 4, 10),
            current_visa_type='TN',
            current_visa_expiration=date(2027, 1, 4),
            i94_expiration=date(2027, 1, 4),
            job_title='Senior Research Scientist',
            employment_start_date=date(2022, 7, 15)
        )
        db.add(beneficiary_david_craig)
        db.flush()
        
        case_david_craig = CaseGroup(
            beneficiary_id=beneficiary_david_craig.id,
            name='David Craig Penner - H1B Conversion',
            description='TN to H1B conversion for Senior Research Scientist',
            case_type=CaseType.TN_TO_H1B,
            priority=VisaPriority.HIGH,
            status=CaseStatus.ACTIVE,
            approval_status=ApprovalStatus.PM_APPROVED,
            start_date=date(2025, 8, 1),
            target_completion_date=date(2026, 3, 31),
            assigned_hr_user_id=pm_user.id,
            law_firm_id=goel_anderson.id,
            approved_by_pm_id=pm_user.id,
            approval_notes='Approved H1B conversion case, proceeding with application',
            created_by_id=pm_user.id
        )
        db.add(case_david_craig)
        db.flush()
        
        # H1B Application in planning
        visa_david_h1b = VisaApplication(
            beneficiary_id=beneficiary_david_craig.id,
            user_id=user_david_craig.id,
            case_group_id=case_david_craig.id,
            visa_type_id=h1b_type.id,
            current_status=VisaCaseStatus.PLANNING,
            priority=VisaPriority.HIGH,
            filing_date=None,
            approval_date=None,
            start_date=None,
            end_date=None,
            law_firm_id=goel_anderson.id,
            notes='H1B application in preparation, awaiting HR meetings'
        )
        db.add(visa_david_h1b)
        db.flush()
        
        # Milestones for David Craig
        milestone_david_approved = ApplicationMilestone(
            visa_application_id=visa_david_h1b.id,
            milestone_type=MilestoneType.CASE_OPENED,
            milestone_date=date(2025, 8, 1),
            description='Case opened and approved by PM',
            created_by=pm_user.id
        )
        milestone_david_docs = ApplicationMilestone(
            visa_application_id=visa_david_h1b.id,
            milestone_type=MilestoneType.DOCUMENTS_REQUESTED,
            milestone_date=date(2025, 10, 15),
            description='Initial documents requested from beneficiary',
            created_by=pm_user.id
        )
        db.add_all([milestone_david_approved, milestone_david_docs])
        
        print(f"     ✓ David Craig Penner - H1B Conversion (APPROVED, waiting for HR meetings)")
        
        # Timothy Chau - PENDING_PM_APPROVAL (EB2-NIW)
        user_timothy = User(
            hashed_password=get_password_hash('Dev123!'),
            full_name='Timothy Chau',
            role=UserRole.BENEFICIARY,
            contract_id=assess_contract.id,
            department_id=dept_tna.id,
            reports_to_id=manager_gerrit.id,
            is_active=True,
            force_password_change=False
        )
        db.add(user_timothy)
        db.flush()
        
        beneficiary_timothy = Beneficiary(
            user_id=user_timothy.id,
            first_name='Timothy',
            last_name='Chau',
            country_of_citizenship='Canada',
            country_of_birth='Canada',
            passport_country='Canada',
            passport_expiration=date(2032, 5, 20),
            current_visa_type='H1B',
            current_visa_expiration=date(2027, 1, 7),
            i94_expiration=date(2027, 1, 7),
            job_title='Senior Research Scientist',
            employment_start_date=date(2018, 3, 11)
        )
        db.add(beneficiary_timothy)
        db.flush()
        
        case_timothy = CaseGroup(
            beneficiary_id=beneficiary_timothy.id,
            name='Timothy Chau - EB2-NIW Green Card',
            description='EB2-NIW pathway for Senior Research Scientist',
            case_type=CaseType.EB2_NIW,
            priority=VisaPriority.MEDIUM,
            status=CaseStatus.ACTIVE,
            approval_status=ApprovalStatus.PENDING_PM_APPROVAL,
            start_date=date(2025, 10, 1),
            target_completion_date=date(2027, 6, 30),
            assigned_hr_user_id=None,
            law_firm_id=None,
            approved_by_pm_id=None,
            created_by_id=pm_user.id
        )
        db.add(case_timothy)
        
        print(f"     ✓ Timothy Chau - EB2-NIW (PENDING_PM_APPROVAL)")
        
        # Luis Fernandes - APPROVED, I-140 received 2 weeks ago
        user_luis = User(
            hashed_password=get_password_hash('Dev123!'),
            full_name='Luis Fernandes',
            role=UserRole.BENEFICIARY,
            contract_id=assess_contract.id,
            department_id=dept_tna.id,
            reports_to_id=manager_gerrit.id,
            is_active=True,
            force_password_change=False
        )
        db.add(user_luis)
        db.flush()
        
        beneficiary_luis = Beneficiary(
            user_id=user_luis.id,
            first_name='Luis',
            last_name='Fernandes',
            country_of_citizenship='Portugal',
            country_of_birth='Portugal',
            passport_country='Portugal',
            passport_expiration=date(2030, 9, 10),
            current_visa_type='H1B',
            current_visa_expiration=date(2026, 1, 5),
            i94_expiration=date(2026, 1, 5),
            job_title='Senior Research Scientist',
            employment_start_date=date(2018, 7, 5)
        )
        db.add(beneficiary_luis)
        db.flush()
        
        case_luis = CaseGroup(
            beneficiary_id=beneficiary_luis.id,
            name='Luis Fernandes - EB2-NIW Green Card',
            description='EB2-NIW pathway for Senior Research Scientist',
            case_type=CaseType.EB2_NIW,
            priority=VisaPriority.HIGH,
            status=CaseStatus.ACTIVE,
            approval_status=ApprovalStatus.PM_APPROVED,
            start_date=date(2024, 6, 1),
            target_completion_date=date(2026, 12, 31),
            assigned_hr_user_id=pm_user.id,
            law_firm_id=goel_anderson.id,
            approved_by_pm_id=pm_user.id,
            approval_notes='Approved EB2-NIW case, I-140 approved',
            created_by_id=pm_user.id
        )
        db.add(case_luis)
        db.flush()
        
        # I-140 Application - APPROVED (received 2 weeks ago)
        two_weeks_ago = today - timedelta(days=14)
        visa_luis_i140 = VisaApplication(
            beneficiary_id=beneficiary_luis.id,
            user_id=user_luis.id,
            case_group_id=case_luis.id,
            visa_type_id=i140_type.id,
            current_status=VisaCaseStatus.APPROVED,
            priority=VisaPriority.HIGH,
            filing_date=date(2024, 9, 15),
            approval_date=two_weeks_ago,
            start_date=two_weeks_ago,
            end_date=None,
            law_firm_id=goel_anderson.id,
            receipt_number='SRC2490045678',
            notes='I-140 approved under EB2-NIW'
        )
        db.add(visa_luis_i140)
        db.flush()
        
        # Milestones for Luis
        milestones_luis = [
            ApplicationMilestone(
                visa_application_id=visa_luis_i140.id,
                milestone_type=MilestoneType.CASE_OPENED,
                milestone_date=date(2024, 6, 1),
                description='Case opened and approved by PM',
                created_by=pm_user.id
            ),
            ApplicationMilestone(
                visa_application_id=visa_luis_i140.id,
                milestone_type=MilestoneType.DOCUMENTS_REQUESTED,
                milestone_date=date(2024, 6, 15),
                description='Documents requested from beneficiary',
                created_by=pm_user.id
            ),
            ApplicationMilestone(
                visa_application_id=visa_luis_i140.id,
                milestone_type=MilestoneType.DOCUMENTS_SUBMITTED,
                milestone_date=date(2024, 8, 10),
                description='All documents submitted to law firm',
                created_by=pm_user.id
            ),
            ApplicationMilestone(
                visa_application_id=visa_luis_i140.id,
                milestone_type=MilestoneType.FILED_WITH_USCIS,
                milestone_date=date(2024, 9, 15),
                description='I-140 filed with USCIS',
                created_by=pm_user.id
            ),
            ApplicationMilestone(
                visa_application_id=visa_luis_i140.id,
                milestone_type=MilestoneType.APPROVED,
                milestone_date=two_weeks_ago,
                description='I-140 approved by USCIS',
                created_by=pm_user.id
            )
        ]
        db.add_all(milestones_luis)
        
        print(f"     ✓ Luis Fernandes - EB2-NIW (APPROVED, I-140 received)")
        
        # Kiran Ravikumar - APPROVED, I-140 just filed
        user_kiran = User(
            hashed_password=get_password_hash('Dev123!'),
            full_name='Kiran Ravikumar',
            role=UserRole.BENEFICIARY,
            contract_id=assess_contract.id,
            department_id=dept_tna.id,
            reports_to_id=manager_gerrit.id,
            is_active=True,
            force_password_change=False
        )
        db.add(user_kiran)
        db.flush()
        
        beneficiary_kiran = Beneficiary(
            user_id=user_kiran.id,
            first_name='Kiran',
            last_name='Ravikumar',
            country_of_citizenship='India',
            country_of_birth='India',
            passport_country='India',
            passport_expiration=date(2033, 11, 20),
            current_visa_type='H1B',
            current_visa_expiration=date(2029, 11, 5),
            i94_expiration=date(2029, 11, 5),
            job_title='Senior Research Scientist',
            employment_start_date=date(2023, 7, 5)
        )
        db.add(beneficiary_kiran)
        db.flush()
        
        case_kiran = CaseGroup(
            beneficiary_id=beneficiary_kiran.id,
            name='Kiran Ravikumar - EB2-NIW Green Card',
            description='EB2-NIW pathway for Senior Research Scientist',
            case_type=CaseType.EB2_NIW,
            priority=VisaPriority.HIGH,
            status=CaseStatus.ACTIVE,
            approval_status=ApprovalStatus.PM_APPROVED,
            start_date=date(2025, 3, 1),
            target_completion_date=date(2027, 3, 31),
            assigned_hr_user_id=pm_user.id,
            law_firm_id=goel_anderson.id,
            approved_by_pm_id=pm_user.id,
            approval_notes='Approved EB2-NIW case, proceeding with I-140',
            created_by_id=pm_user.id
        )
        db.add(case_kiran)
        db.flush()
        
        # I-140 Application - IN_PROGRESS (just filed)
        visa_kiran_i140 = VisaApplication(
            beneficiary_id=beneficiary_kiran.id,
            user_id=user_kiran.id,
            case_group_id=case_kiran.id,
            visa_type_id=i140_type.id,
            current_status=VisaCaseStatus.IN_PROGRESS,
            priority=VisaPriority.HIGH,
            filing_date=date(2025, 10, 15),
            approval_date=None,
            start_date=None,
            end_date=None,
            law_firm_id=goel_anderson.id,
            receipt_number='SRC2590056789',
            notes='I-140 filed, awaiting USCIS processing'
        )
        db.add(visa_kiran_i140)
        db.flush()
        
        # Milestones for Kiran
        milestones_kiran = [
            ApplicationMilestone(
                visa_application_id=visa_kiran_i140.id,
                milestone_type=MilestoneType.CASE_OPENED,
                milestone_date=date(2025, 3, 1),
                description='Case opened and approved by PM',
                created_by=pm_user.id
            ),
            ApplicationMilestone(
                visa_application_id=visa_kiran_i140.id,
                milestone_type=MilestoneType.DOCUMENTS_REQUESTED,
                milestone_date=date(2025, 3, 15),
                description='Documents requested from beneficiary',
                created_by=pm_user.id
            ),
            ApplicationMilestone(
                visa_application_id=visa_kiran_i140.id,
                milestone_type=MilestoneType.DOCUMENTS_SUBMITTED,
                milestone_date=date(2025, 9, 1),
                description='All documents submitted to law firm',
                created_by=pm_user.id
            ),
            ApplicationMilestone(
                visa_application_id=visa_kiran_i140.id,
                milestone_type=MilestoneType.FILED_WITH_USCIS,
                milestone_date=date(2025, 10, 15),
                description='I-140 filed with USCIS',
                created_by=pm_user.id
            )
        ]
        db.add_all(milestones_kiran)
        
        print(f"     ✓ Kiran Ravikumar - EB2-NIW (APPROVED, I-140 just filed)")
        
        # Victor Sousa - COMPLETED LPR (EB2-NIW pathway)
        user_victor = User(
            hashed_password=get_password_hash('Dev123!'),
            full_name='Victor DeCarvalho Sousa',
            role=UserRole.BENEFICIARY,
            contract_id=assess_contract.id,
            department_id=dept_tna.id,
            reports_to_id=manager_gerrit.id,
            is_active=True,
            force_password_change=False
        )
        db.add(user_victor)
        db.flush()
        
        beneficiary_victor = Beneficiary(
            user_id=user_victor.id,
            first_name='Victor DeCarvalho',
            last_name='Sousa',
            country_of_citizenship='Brazil',
            country_of_birth='Brazil',
            passport_country='Brazil',
            passport_expiration=date(2031, 7, 15),
            current_visa_type='LPR',
            current_visa_expiration=date(2035, 1, 1),
            i94_expiration=None,
            job_title='Senior Research Scientist',
            employment_start_date=date(2020, 1, 1)
        )
        db.add(beneficiary_victor)
        db.flush()
        
        case_victor = CaseGroup(
            beneficiary_id=beneficiary_victor.id,
            name='Victor Sousa - EB2-NIW to Green Card',
            description='EB2-NIW pathway to lawful permanent resident status',
            case_type=CaseType.EB2_NIW,
            priority=VisaPriority.MEDIUM,
            status=CaseStatus.IN_PROGRESS,
            approval_status=ApprovalStatus.PM_APPROVED,
            start_date=date(2021, 6, 1),
            target_completion_date=date(2023, 12, 31),
            actual_completion_date=date(2023, 11, 15),
            assigned_hr_user_id=pm_user.id,
            law_firm_id=goel_anderson.id,
            approved_by_pm_id=pm_user.id,
            approval_notes='Approved EB2-NIW case, green card received',
            created_by_id=pm_user.id
        )
        db.add(case_victor)
        db.flush()
        
        # Visa Applications for Victor (completed)
        visa_victor_i140 = VisaApplication(
            beneficiary_id=beneficiary_victor.id,
            user_id=user_victor.id,
            case_group_id=case_victor.id,
            visa_type_id=i140_type.id,
            current_status=VisaCaseStatus.APPROVED,
            priority=VisaPriority.MEDIUM,
            filing_date=date(2021, 9, 1),
            approval_date=date(2022, 5, 15),
            start_date=date(2022, 5, 15),
            end_date=None,
            law_firm_id=goel_anderson.id,
            receipt_number='SRC2190067890',
            notes='I-140 approved for EB2-NIW'
        )
        visa_victor_i485 = VisaApplication(
            beneficiary_id=beneficiary_victor.id,
            user_id=user_victor.id,
            case_group_id=case_victor.id,
            visa_type_id=i485_type.id,
            current_status=VisaCaseStatus.APPROVED,
            priority=VisaPriority.MEDIUM,
            filing_date=date(2022, 11, 1),
            approval_date=date(2023, 11, 15),
            start_date=date(2023, 11, 15),
            end_date=date(2035, 1, 1),
            law_firm_id=goel_anderson.id,
            receipt_number='SRC2290089012',
            notes='I-485 approved, received green card'
        )
        db.add_all([visa_victor_i140, visa_victor_i485])
        
        print(f"     ✓ Victor Sousa - EB2-NIW (COMPLETED LPR)")
        
        # David Garcia Perez - DRAFT (preparing for PM approval)
        user_david_perez = User(
            hashed_password=get_password_hash('Dev123!'),
            full_name='David Garcia Perez',
            role=UserRole.BENEFICIARY,
            contract_id=assess_contract.id,
            department_id=dept_tnp.id,
            reports_to_id=manager_patricia.id,
            is_active=True,
            force_password_change=False
        )
        db.add(user_david_perez)
        db.flush()
        
        beneficiary_david_perez = Beneficiary(
            user_id=user_david_perez.id,
            first_name='David',
            last_name='Garcia Perez',
            country_of_citizenship='Spain',
            country_of_birth='Spain',
            passport_country='Spain',
            passport_expiration=date(2032, 8, 20),
            current_visa_type='H1B',
            current_visa_expiration=date(2027, 1, 5),
            i94_expiration=date(2027, 1, 5),
            job_title='Senior Research Scientist',
            employment_start_date=date(2021, 7, 5)
        )
        db.add(beneficiary_david_perez)
        db.flush()
        
        case_david_perez = CaseGroup(
            beneficiary_id=beneficiary_david_perez.id,
            name='David Garcia Perez - EB2-NIW Green Card',
            description='EB2-NIW pathway for Senior Research Scientist',
            case_type=CaseType.EB2_NIW,
            priority=VisaPriority.MEDIUM,
            status=CaseStatus.PLANNING,
            approval_status=ApprovalStatus.DRAFT,
            start_date=date(2025, 11, 1),
            target_completion_date=date(2027, 12, 31),
            assigned_hr_user_id=None,
            law_firm_id=None,
            approved_by_pm_id=None,
            created_by_id=pm_user.id
        )
        db.add(case_david_perez)
        
        print(f"     ✓ David Garcia Perez - EB2-NIW (DRAFT)")
        
        # Tove Aagen - DRAFT (not yet submitted for approval)
        user_tove = User(
            hashed_password=get_password_hash('Dev123!'),
            full_name='Tove Aagen',
            role=UserRole.BENEFICIARY,
            contract_id=assess_contract.id,
            department_id=dept_av.id,
            reports_to_id=manager_gerrit.id,
            is_active=True,
            force_password_change=False
        )
        db.add(user_tove)
        db.flush()
        
        beneficiary_tove = Beneficiary(
            user_id=user_tove.id,
            first_name='Tove',
            last_name='Aagen',
            country_of_citizenship='Sweden',
            country_of_birth='Sweden',
            passport_country='Sweden',
            passport_expiration=date(2033, 4, 10),
            current_visa_type='H1B',
            current_visa_expiration=date(2029, 1, 5),
            i94_expiration=date(2029, 1, 5),
            job_title='Senior Research Scientist',
            employment_start_date=date(2021, 7, 5)
        )
        db.add(beneficiary_tove)
        db.flush()
        
        case_tove = CaseGroup(
            beneficiary_id=beneficiary_tove.id,
            name='Tove Aagen - EB2-NIW Green Card',
            description='EB2-NIW pathway for Senior Research Scientist',
            case_type=CaseType.EB2_NIW,
            priority=VisaPriority.MEDIUM,
            status=CaseStatus.PLANNING,
            approval_status=ApprovalStatus.DRAFT,
            start_date=date(2025, 10, 1),
            target_completion_date=date(2027, 12, 31),
            assigned_hr_user_id=None,
            law_firm_id=None,
            approved_by_pm_id=None,
            created_by_id=pm_user.id
        )
        db.add(case_tove)
        
        print(f"     ✓ Tove Aagen - EB2-NIW (DRAFT)")
        
        # Jacob Friedrichson - APPROVED H1B (future hire, no user account)
        beneficiary_jacob = Beneficiary(
            user_id=None,  # No user account yet (future hire)
            first_name='Jacob',
            last_name='Friedrichson',
            country_of_citizenship='Sweden',
            country_of_birth='Sweden',
            passport_country='Sweden',
            passport_expiration=date(2032, 9, 15),
            current_visa_type=None,  # Future hire
            current_visa_expiration=None,
            i94_expiration=None,
            job_title='Senior Research Scientist',
            employment_start_date=None  # Not hired yet
        )
        db.add(beneficiary_jacob)
        db.flush()
        
        case_jacob = CaseGroup(
            beneficiary_id=beneficiary_jacob.id,
            name='Jacob Friedrichson - H1B New Hire',
            description='H1B sponsorship for new hire Senior Research Scientist',
            case_type=CaseType.H1B_TRANSFER,
            priority=VisaPriority.HIGH,
            status=CaseStatus.ACTIVE,
            approval_status=ApprovalStatus.PM_APPROVED,
            start_date=date(2025, 9, 1),
            target_completion_date=date(2026, 3, 31),
            assigned_hr_user_id=pm_user.id,
            law_firm_id=goel_anderson.id,
            approved_by_pm_id=pm_user.id,
            approval_notes='Approved H1B for new hire, awaiting HR meetings',
            created_by_id=pm_user.id
        )
        db.add(case_jacob)
        db.flush()
        
        # H1B Application for Jacob
        visa_jacob_h1b = VisaApplication(
            beneficiary_id=beneficiary_jacob.id,
            user_id=None,  # No user yet
            case_group_id=case_jacob.id,
            visa_type_id=h1b_type.id,
            current_status=VisaCaseStatus.PLANNING,
            priority=VisaPriority.HIGH,
            filing_date=None,
            approval_date=None,
            start_date=None,
            end_date=None,
            law_firm_id=goel_anderson.id,
            notes='H1B application for new hire, awaiting HR scheduling'
        )
        db.add(visa_jacob_h1b)
        db.flush()
        
        # Milestones for Jacob
        milestone_jacob_approved = ApplicationMilestone(
            visa_application_id=visa_jacob_h1b.id,
            milestone_type=MilestoneType.CASE_OPENED,
            milestone_date=date(2025, 9, 1),
            description='Case opened and approved by PM for new hire',
            created_by=pm_user.id
        )
        db.add(milestone_jacob_approved)
        
        print(f"     ✓ Jacob Friedrichson - H1B New Hire (APPROVED, no user account yet)")
        
        # Georgios Bellas-Chatzigeorgis - APPROVED, PERM approved, preparing I-140
        user_georgios = User(
            hashed_password=get_password_hash('Dev123!'),
            full_name='Georgios Bellas-Chatzigeorgis',
            role=UserRole.BENEFICIARY,
            contract_id=assess_contract.id,
            department_id=dept_tss.id,
            reports_to_id=manager_arnaud.id,  # Reports to Arnaud Borner
            is_active=True,
            force_password_change=False
        )
        db.add(user_georgios)
        db.flush()
        
        beneficiary_georgios = Beneficiary(
            user_id=user_georgios.id,
            first_name='Georgios',
            last_name='Bellas-Chatzigeorgis',
            country_of_citizenship='Greece',
            country_of_birth='Greece',
            passport_country='Greece',
            passport_expiration=date(2030, 6, 25),
            current_visa_type='H1B',
            current_visa_expiration=date(2026, 1, 5),
            i94_expiration=date(2026, 1, 5),
            job_title='Senior Research Scientist',
            employment_start_date=date(2020, 1, 15)
        )
        db.add(beneficiary_georgios)
        db.flush()
        
        case_georgios = CaseGroup(
            beneficiary_id=beneficiary_georgios.id,
            name='Georgios Bellas-Chatzigeorgis - PERM-Based Green Card',
            description='PERM-based EB2 pathway for Senior Research Scientist',
            case_type=CaseType.PERM_BASED,
            priority=VisaPriority.HIGH,
            status=CaseStatus.ACTIVE,
            approval_status=ApprovalStatus.PM_APPROVED,
            start_date=date(2023, 3, 1),
            target_completion_date=date(2026, 6, 30),
            assigned_hr_user_id=pm_user.id,
            law_firm_id=goel_anderson.id,
            approved_by_pm_id=pm_user.id,
            approval_notes='Approved PERM-based case, PERM approved, preparing I-140',
            created_by_id=pm_user.id
        )
        db.add(case_georgios)
        db.flush()
        
        # PERM Application - APPROVED
        visa_georgios_perm = VisaApplication(
            beneficiary_id=beneficiary_georgios.id,
            user_id=user_georgios.id,
            case_group_id=case_georgios.id,
            visa_type_id=perm_type.id,
            current_status=VisaCaseStatus.APPROVED,
            priority=VisaPriority.HIGH,
            filing_date=date(2023, 9, 1),
            approval_date=date(2025, 10, 20),
            start_date=date(2025, 10, 20),
            end_date=None,
            law_firm_id=goel_anderson.id,
            receipt_number='PERM-2023-090123',
            notes='PERM approved, preparing I-140 documents'
        )
        db.add(visa_georgios_perm)
        db.flush()
        
        # I-140 Application - PLANNING
        visa_georgios_i140 = VisaApplication(
            beneficiary_id=beneficiary_georgios.id,
            user_id=user_georgios.id,
            case_group_id=case_georgios.id,
            visa_type_id=i140_type.id,
            current_status=VisaCaseStatus.PLANNING,
            priority=VisaPriority.HIGH,
            filing_date=None,
            approval_date=None,
            start_date=None,
            end_date=None,
            law_firm_id=goel_anderson.id,
            notes='Preparing I-140 documents with Goel & Anderson'
        )
        db.add(visa_georgios_i140)
        db.flush()
        
        # Milestones for Georgios
        milestones_georgios = [
            ApplicationMilestone(
                visa_application_id=visa_georgios_perm.id,
                milestone_type=MilestoneType.CASE_OPENED,
                milestone_date=date(2023, 3, 1),
                description='PERM case opened and approved by PM',
                created_by=pm_user.id
            ),
            ApplicationMilestone(
                visa_application_id=visa_georgios_perm.id,
                milestone_type=MilestoneType.FILED_WITH_USCIS,
                milestone_date=date(2023, 9, 1),
                description='PERM application filed with DOL',
                created_by=pm_user.id
            ),
            ApplicationMilestone(
                visa_application_id=visa_georgios_perm.id,
                milestone_type=MilestoneType.APPROVED,
                milestone_date=date(2025, 10, 20),
                description='PERM approved by DOL',
                created_by=pm_user.id
            ),
            ApplicationMilestone(
                visa_application_id=visa_georgios_i140.id,
                milestone_type=MilestoneType.DOCUMENTS_REQUESTED,
                milestone_date=date(2025, 10, 25),
                description='I-140 documents requested from law firm',
                created_by=pm_user.id
            )
        ]
        db.add_all(milestones_georgios)
        
        print(f"     ✓ Georgios Bellas-Chatzigeorgis - PERM-Based EB2 (APPROVED, PERM approved)")
        
        # ============================================================
        # COMMIT ALL
        # ============================================================
        
        db.commit()
        
        print(f"\n✅ ASSESS beneficiaries seeded successfully!")
        print(f"   Beneficiaries: 14 total")
        print(f"     - 3 Managers with completed LPR cases")
        print(f"     - 11 Employees with active/draft cases")
        print(f"   Case Groups: 14 total")
        print(f"     - 4 COMPLETED (LPR received)")
        print(f"     - 7 APPROVED (active processing)")
        print(f"     - 2 PENDING_PM_APPROVAL")
        print(f"     - 2 DRAFT (preparing)")
        print(f"   Visa Applications: 25+ total")
        print(f"   Milestones: 40+ total")
        print(f"   ⚠️  All beneficiary passwords: Dev123!")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error seeding ASSESS beneficiaries: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = seed_assess_beneficiaries()
    sys.exit(0 if success else 1)
