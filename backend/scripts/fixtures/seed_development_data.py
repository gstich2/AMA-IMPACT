"""
Seed Development Test Data

This script creates FICTIONAL test data for development purposes only.
Creates 5 creative test scenarios to demonstrate edge cases:
1. Test RFE User - I-140 with RFE handling
2. Test Denial User - I-140 denied with appeal
3. Test Concurrent User - I-140 + I-485 concurrent filing
4. Test Family User - Primary + dependents with derivative petitions
5. Test Expired User - H1B expired with urgent extensio        # Create dependents
        spouse = Dependent(
            beneficiary_id=family_ben.id,
            first_name='Spouse',
            last_name='Family',
            relationship_type=RelationshipType.SPOUSE,
            date_of_birth=date(1988, 5, 15),
            country_of_citizenship='Mexico'
        )
        db.add(spouse)
        db.flush()
        
        child = Dependent(
            beneficiary_id=family_ben.id,
            first_name='Child',
            last_name='Family',
            relationship_type=RelationshipType.CHILD,
            date_of_birth=date(2015, 3, 20),
            country_of_citizenship='Mexico'
        ) PM, and Tech Lead users for testing workflows.
"""

import sys
from pathlib import Path
from datetime import date, datetime, timedelta

# Add backend to path
backend_dir = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.contract import Contract
from app.models.department import Department
from app.models.law_firm import LawFirm
from app.models.beneficiary import Beneficiary
from app.models.petition import Petition, PetitionType, PetitionStatus, CaseStatus as PetitionCaseStatus
from app.models.case_group import CaseGroup, PathwayType, CaseStatus, ApprovalStatus, PetitionPriority
from app.models.milestone import Milestone, MilestoneType, MilestoneStatus
from app.models.dependent import Dependent, RelationshipType
from app.models.todo import Todo, TodoStatus, TodoPriority
from app.models.audit import AuditLog, AuditAction


def seed_development_data():
    """Seed database with development test data"""
    
    db = SessionLocal()
    
    try:
        print("\n🌱 Seeding DEVELOPMENT test data...")
        print("   (Creating fictional test scenarios for edge case testing)")
        
        # ============================================================
        # 1. GET EXISTING ENTITIES
        # ============================================================
        
        # Get ASSESS contract (by code, not name)
        assess_contract = db.query(Contract).filter(Contract.code == 'ASSESS').first()
        if not assess_contract:
            print("      ⚠️  ASSESS contract not found")
            return False
        
        # Get admin user
        admin = db.query(User).filter(User.email == 'admin@ama-impact.com').first()
        if not admin:
            print("      ⚠️  Admin user not found")
            return False
        
        # Get law firm (use correct name with trailing space)
        law_firm = db.query(LawFirm).filter(LawFirm.name == 'Goel And Anderson Corporate Immigration ').first()
        if not law_firm:
            print("      ⚠️  Law firm not found - run seed_law_firms.py first")
            return False
        
        # Note: No visa type validation needed with Petition model
        
        print("      ✓ Found existing entities (contract, admin, law firm)")
        
        # ============================================================
        # 2. CREATE DEPARTMENTS
        # ============================================================
        
        print("\n   Creating departments...")
        
        # Technical Services (TS) - Parent
        dept_ts = Department(
            name='Technical Services',
            code='TS',
            contract_id=assess_contract.id,
            is_active=True
        )
        db.add(dept_ts)
        db.flush()
        
        # Sub-departments under TS
        dept_tsm = Department(
            name='TSM (Mission Operations)',
            code='TSM',
            parent_id=dept_ts.id,
            contract_id=assess_contract.id,
            is_active=True
        )
        dept_tsa = Department(
            name='TSA (Systems Administration)',
            code='TSA',
            parent_id=dept_ts.id,
            contract_id=assess_contract.id,
            is_active=True
        )
        dept_tna = Department(
            name='TNA (Network Administration)',
            code='TNA',
            parent_id=dept_ts.id,
            contract_id=assess_contract.id,
            is_active=True
        )
        dept_av = Department(
            name='AV (Audio/Visual)',
            code='AV',
            parent_id=dept_ts.id,
            contract_id=assess_contract.id,
            is_active=True
        )
        db.add_all([dept_tsm, dept_tsa, dept_tna, dept_av])
        db.flush()
        
        print("      ✓ Created 5 departments (TS → TSM/TSA/TNA/AV)")
        
        # ============================================================
        # 3. CREATE TEST USERS (HR, PM, Tech Lead)
        # ============================================================
        
        print("\n   Creating test users (HR, PM, Tech Lead)...")
        
        # HR User
        hr_user = User(
            email='hr@ama-impact.com',
            hashed_password=get_password_hash('HR123!'),
            full_name='HR Administrator',
            role=UserRole.HR,
            contract_id=assess_contract.id,
            is_active=True
        )
        db.add(hr_user)
        db.flush()
        
        # PM User
        pm_user = User(
            email='pm@ama-impact.com',
            hashed_password=get_password_hash('PM123!'),
            full_name='Program Manager',
            role=UserRole.PM,
            contract_id=assess_contract.id,
            is_active=True
        )
        db.add(pm_user)
        db.flush()
        
        # Tech Lead
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
        
        print("      ✓ Created 3 test users (HR, PM, Tech Lead)")
        
        # ============================================================
        # 4. HELPER FUNCTIONS FOR TEST SCENARIOS
        # ============================================================
        
        def create_test_beneficiary(email, first_name, last_name, country, dept_id):
            """Create a test beneficiary user"""
            user = User(
                email=email,
                hashed_password=get_password_hash('Test123!'),
                full_name=f'{first_name} {last_name}',
                role=UserRole.BENEFICIARY,
                contract_id=assess_contract.id,
                department_id=dept_id,
                reports_to_id=tech_lead.id,
                is_active=True
            )
            db.add(user)
            db.flush()
            
            beneficiary = Beneficiary(
                user_id=user.id,
                first_name=first_name,
                last_name=last_name,
                country_of_citizenship=country,
                country_of_birth=country,
                passport_country=country,
                passport_expiration=date(2030, 12, 31),
                job_title='Test Employee',
                employment_start_date=date(2023, 1, 1),
                is_active=True
            )
            db.add(beneficiary)
            db.flush()
            return user, beneficiary
        
        def create_case_group(beneficiary, pathway_type, case_number, priority, status, notes):
            """Create a case group"""
            case_group = CaseGroup(
                beneficiary_id=beneficiary.id,
                pathway_type=pathway_type,
                case_number=case_number,
                status=status,
                priority=priority,
                case_started_date=date(2024, 1, 15),
                target_completion_date=date(2025, 12, 31),
                responsible_party_id=pm_user.id,
                notes=notes
            )
            db.add(case_group)
            db.flush()
            return case_group
        
        def create_petition(beneficiary, case_group, petition_type, status, case_status, 
                           priority, filing_date=None, approval_date=None,
                           receipt_number=None, notes=''):
            """Create a petition"""
            petition = Petition(
                beneficiary_id=beneficiary.id,
                case_group_id=case_group.id,
                petition_type=petition_type,
                status=status,
                case_status=case_status,
                priority=priority,
                filing_date=filing_date,
                approval_date=approval_date,
                receipt_number=receipt_number,
                law_firm_id=law_firm.id,
                responsible_party_id=pm_user.id,
                attorney_name=law_firm.contact_person,
                attorney_email=law_firm.email,
                created_by=admin.id,
                notes=notes
            )
            db.add(petition)
            db.flush()
            return petition
        
        def add_milestone(petition, case_group, milestone_type, status, due_date=None, 
                         completed_date=None, notes=''):
            """Add a milestone (case-level OR petition-level)"""
            milestone = Milestone(
                case_group_id=case_group.id if milestone_type in [
                    MilestoneType.CASE_OPENED, MilestoneType.STRATEGY_MEETING
                ] else None,
                petition_id=petition.id if milestone_type not in [
                    MilestoneType.CASE_OPENED, MilestoneType.STRATEGY_MEETING
                ] else None,
                milestone_type=milestone_type,
                status=status,
                due_date=due_date,
                completed_date=completed_date,
                description=notes,  # Milestone uses 'description' not 'notes'
                created_by=admin.id  # Milestone uses 'created_by' not 'responsible_party_id'
            )
            db.add(milestone)
            db.flush()
            return milestone
        
        # ============================================================
        # 5. TEST SCENARIO 1: RFE USER
        # ============================================================
        
        print("\n   Creating Test Scenario 1: RFE User...")
        
        rfe_user, rfe_ben = create_test_beneficiary(
            'test.rfe@example.com', 'Test', 'RFE', 'India', dept_tsm.id
        )
        
        rfe_case = create_case_group(
            rfe_ben, PathwayType.EB2_NIW, 'TEST-RFE-2024-001',
            PetitionPriority.HIGH, CaseStatus.IN_PROGRESS,
            'Test case demonstrating RFE (Request for Evidence) handling workflow'
        )
        
        # I-140 with RFE
        rfe_i140 = create_petition(
            rfe_ben, rfe_case, PetitionType.I140,
            PetitionStatus.RFE_RECEIVED, PetitionCaseStatus.ACTIVE,
            PetitionPriority.HIGH,
            filing_date=date(2024, 3, 1),
            receipt_number='LIN2490000001',
            notes='RFE issued on 10/15/2024 - response due 11/29/2024'
        )
        
        # Milestones
        add_milestone(None, rfe_case, MilestoneType.CASE_OPENED, 
                     MilestoneStatus.COMPLETED, completed_date=date(2024, 1, 15))
        add_milestone(rfe_i140, rfe_case, MilestoneType.I140_FILED,
                     MilestoneStatus.COMPLETED, completed_date=date(2024, 3, 1))
        add_milestone(rfe_i140, rfe_case, MilestoneType.RFE_RECEIVED,
                     MilestoneStatus.COMPLETED, completed_date=date(2024, 10, 15),
                     notes='RFE requesting additional evidence of qualifications')
        add_milestone(rfe_i140, rfe_case, MilestoneType.RFE_RESPONDED,
                     MilestoneStatus.IN_PROGRESS, due_date=date(2024, 11, 29),
                     notes='Preparing comprehensive response with attorney')
        
        print("      ✓ Created Test RFE User (I-140 with active RFE)")
        
        # ============================================================
        # 6. TEST SCENARIO 2: DENIAL USER
        # ============================================================
        
        print("\n   Creating Test Scenario 2: Denial User...")
        
        denial_user, denial_ben = create_test_beneficiary(
            'test.denial@example.com', 'Test', 'Denial', 'China', dept_tsa.id
        )
        
        denial_case = create_case_group(
            denial_ben, PathwayType.EB2_NIW, 'TEST-DENIAL-2024-002',
            PetitionPriority.HIGH, CaseStatus.IN_PROGRESS,
            'Test case demonstrating petition denial and appeal workflow'
        )
        
        # I-140 denied, appeal filed
        denial_i140 = create_petition(
            denial_ben, denial_case, PetitionType.I140,
            PetitionStatus.DENIED, PetitionCaseStatus.ACTIVE,
            PetitionPriority.HIGH,
            filing_date=date(2024, 2, 1),
            receipt_number='LIN2490000002',
            notes='Denied on 9/15/2024 - Appeal filed on 10/1/2024'
        )
        
        # Milestones
        add_milestone(None, denial_case, MilestoneType.CASE_OPENED,
                     MilestoneStatus.COMPLETED, completed_date=date(2024, 1, 10))
        add_milestone(denial_i140, denial_case, MilestoneType.I140_FILED,
                     MilestoneStatus.COMPLETED, completed_date=date(2024, 2, 1))
        add_milestone(denial_i140, denial_case, MilestoneType.I140_DENIED,
                     MilestoneStatus.COMPLETED, completed_date=date(2024, 9, 15),
                     notes='Denial reason: Insufficient evidence of national interest waiver')
        add_milestone(denial_i140, denial_case, MilestoneType.OTHER,
                     MilestoneStatus.IN_PROGRESS, due_date=date(2025, 3, 15),
                     notes='Appeal filed - Pending with AAO (Administrative Appeals Office)')
        
        print("      ✓ Created Test Denial User (I-140 denied with appeal)")
        
        # ============================================================
        # 7. TEST SCENARIO 3: CONCURRENT FILING USER
        # ============================================================
        
        print("\n   Creating Test Scenario 3: Concurrent Filing User...")
        
        concurrent_user, concurrent_ben = create_test_beneficiary(
            'test.concurrent@example.com', 'Test', 'Concurrent', 'Brazil', dept_tna.id
        )
        
        # Update beneficiary with current visa
        concurrent_ben.current_visa_type = 'H1B'
        concurrent_ben.current_visa_expiration = date(2026, 6, 30)
        concurrent_ben.i94_expiration = date(2026, 6, 30)
        
        concurrent_case = create_case_group(
            concurrent_ben, PathwayType.EB2_NIW, 'TEST-CONCURRENT-2024-003',
            PetitionPriority.MEDIUM, CaseStatus.IN_PROGRESS,
            'Test case demonstrating concurrent I-140 and I-485 filing strategy'
        )
        
        # All filed on same date (concurrent filing)
        filing_date = date(2024, 8, 1)
        
        concurrent_i140 = create_petition(
            concurrent_ben, concurrent_case, PetitionType.I140,
            PetitionStatus.IN_PROGRESS, PetitionCaseStatus.ACTIVE,
            PetitionPriority.MEDIUM,
            filing_date=filing_date,
            receipt_number='LIN2490000003',
            notes='Filed concurrently with I-485/I-765/I-131'
        )
        
        concurrent_i485 = create_petition(
            concurrent_ben, concurrent_case, PetitionType.I485,
            PetitionStatus.IN_PROGRESS, PetitionCaseStatus.ACTIVE,
            PetitionPriority.MEDIUM,
            filing_date=filing_date,
            receipt_number='LIN2490000004',
            notes='Filed concurrently - priority date current'
        )
        
        concurrent_i765 = create_petition(
            concurrent_ben, concurrent_case, PetitionType.I765,
            PetitionStatus.IN_PROGRESS, PetitionCaseStatus.ACTIVE,
            PetitionPriority.MEDIUM,
            filing_date=filing_date,
            receipt_number='LIN2490000005',
            notes='EAD application filed with I-485'
        )
        
        concurrent_i131 = create_petition(
            concurrent_ben, concurrent_case, PetitionType.I131,
            PetitionStatus.IN_PROGRESS, PetitionCaseStatus.ACTIVE,
            PetitionPriority.MEDIUM,
            filing_date=filing_date,
            receipt_number='LIN2490000006',
            notes='Advance Parole filed with I-485'
        )
        
        # Milestones
        add_milestone(None, concurrent_case, MilestoneType.CASE_OPENED,
                     MilestoneStatus.COMPLETED, completed_date=date(2024, 6, 1))
        add_milestone(concurrent_i140, concurrent_case, MilestoneType.I140_FILED,
                     MilestoneStatus.COMPLETED, completed_date=filing_date,
                     notes='Concurrent filing - all petitions filed together')
        add_milestone(concurrent_i485, concurrent_case, MilestoneType.I485_FILED,
                     MilestoneStatus.COMPLETED, completed_date=filing_date)
        
        print("      ✓ Created Test Concurrent User (I-140/I-485/I-765/I-131 same day)")
        
        # ============================================================
        # 8. TEST SCENARIO 4: FAMILY USER (with Dependents)
        # ============================================================
        
        print("\n   Creating Test Scenario 4: Family User...")
        
        family_user, family_ben = create_test_beneficiary(
            'test.family@example.com', 'Test', 'Family', 'Mexico', dept_av.id
        )
        
        family_case = create_case_group(
            family_ben, PathwayType.EB2_NIW, 'TEST-FAMILY-2024-004',
            PetitionPriority.HIGH, CaseStatus.IN_PROGRESS,
            'Test case demonstrating family petitions with dependents (spouse + child)'
        )
        
        # Create dependents
        spouse = Dependent(
            beneficiary_id=family_ben.id,
            first_name='Spouse',
            last_name='Family',
            relationship_type=RelationshipType.SPOUSE,
            date_of_birth=date(1988, 5, 15),
            country_of_citizenship='Mexico'
        )
        db.add(spouse)
        db.flush()
        
        child = Dependent(
            beneficiary_id=family_ben.id,
            first_name='Child',
            last_name='Family',
            relationship_type=RelationshipType.CHILD,
            date_of_birth=date(2015, 3, 20),
            country_of_citizenship='Mexico'
        )
        db.add(child)
        db.flush()
        
        # Primary petitions (for principal beneficiary)
        family_i140 = create_petition(
            family_ben, family_case, PetitionType.I140,
            PetitionStatus.APPROVED, PetitionCaseStatus.FINALIZED,
            PetitionPriority.HIGH,
            filing_date=date(2024, 1, 15),
            approval_date=date(2024, 7, 1),
            receipt_number='LIN2490000007',
            notes='Primary I-140 approved'
        )
        
        family_i485_primary = create_petition(
            family_ben, family_case, PetitionType.I485,
            PetitionStatus.IN_PROGRESS, PetitionCaseStatus.ACTIVE,
            PetitionPriority.HIGH,
            filing_date=date(2024, 8, 15),
            receipt_number='LIN2490000008',
            notes='Primary I-485 - adjustment of status'
        )
        
        # Derivative petitions for spouse
        family_i485_spouse = create_petition(
            family_ben, family_case, PetitionType.I485,
            PetitionStatus.IN_PROGRESS, PetitionCaseStatus.ACTIVE,
            PetitionPriority.HIGH,
            filing_date=date(2024, 8, 15),
            receipt_number='LIN2490000009',
            notes='Derivative I-485 for spouse'
        )
        family_i485_spouse.dependent_id = spouse.id
        family_i485_spouse.is_derivative = True
        
        family_i765_spouse = create_petition(
            family_ben, family_case, PetitionType.I765,
            PetitionStatus.IN_PROGRESS, PetitionCaseStatus.ACTIVE,
            PetitionPriority.MEDIUM,
            filing_date=date(2024, 8, 15),
            receipt_number='LIN2490000010',
            notes='EAD for spouse'
        )
        family_i765_spouse.dependent_id = spouse.id
        family_i765_spouse.is_derivative = True
        
        family_i131_spouse = create_petition(
            family_ben, family_case, PetitionType.I131,
            PetitionStatus.IN_PROGRESS, PetitionCaseStatus.ACTIVE,
            PetitionPriority.LOW,
            filing_date=date(2024, 8, 15),
            receipt_number='LIN2490000011',
            notes='AP for spouse'
        )
        family_i131_spouse.dependent_id = spouse.id
        family_i131_spouse.is_derivative = True
        
        # Derivative petitions for child
        family_i485_child = create_petition(
            family_ben, family_case, PetitionType.I485,
            PetitionStatus.IN_PROGRESS, PetitionCaseStatus.ACTIVE,
            PetitionPriority.HIGH,
            filing_date=date(2024, 8, 15),
            receipt_number='LIN2490000012',
            notes='Derivative I-485 for child'
        )
        family_i485_child.dependent_id = child.id
        family_i485_child.is_derivative = True
        
        family_i131_child = create_petition(
            family_ben, family_case, PetitionType.I131,
            PetitionStatus.IN_PROGRESS, PetitionCaseStatus.ACTIVE,
            PetitionPriority.LOW,
            filing_date=date(2024, 8, 15),
            receipt_number='LIN2490000013',
            notes='AP for child'
        )
        family_i131_child.dependent_id = child.id
        family_i131_child.is_derivative = True
        
        # Milestones
        add_milestone(None, family_case, MilestoneType.CASE_OPENED,
                     MilestoneStatus.COMPLETED, completed_date=date(2024, 1, 1))
        add_milestone(family_i140, family_case, MilestoneType.I140_FILED,
                     MilestoneStatus.COMPLETED, completed_date=date(2024, 1, 15))
        add_milestone(family_i140, family_case, MilestoneType.I140_APPROVED,
                     MilestoneStatus.COMPLETED, completed_date=date(2024, 7, 1))
        add_milestone(family_i485_primary, family_case, MilestoneType.I485_FILED,
                     MilestoneStatus.COMPLETED, completed_date=date(2024, 8, 15),
                     notes='Filed for primary + spouse + child')
        
        print("      ✓ Created Test Family User (Primary + 2 dependents, 7 petitions)")
        
        # ============================================================
        # 9. TEST SCENARIO 5: EXPIRED VISA USER
        # ============================================================
        
        print("\n   Creating Test Scenario 5: Expired Visa User...")
        
        expired_user, expired_ben = create_test_beneficiary(
            'test.expired@example.com', 'Test', 'Expired', 'South Korea', dept_tsm.id
        )
        
        # H1B expired 15 days ago
        expiration_date = datetime.now().date() - timedelta(days=15)
        expired_ben.current_visa_type = 'H1B'
        expired_ben.current_visa_expiration = expiration_date
        expired_ben.i94_expiration = expiration_date
        
        # Create case group for H1B extension (CRITICAL priority)
        expired_case = create_case_group(
            expired_ben, PathwayType.H1B_EXTENSION, 'TEST-H1B-2024-005',
            PetitionPriority.CRITICAL, CaseStatus.IN_PROGRESS,
            f'URGENT: H1B expired {expiration_date.strftime("%m/%d/%Y")} - extension filed with premium processing'
        )
        
        expired_h1b = create_petition(
            expired_ben, expired_case, PetitionType.I129,
            PetitionStatus.IN_PROGRESS, PetitionCaseStatus.ACTIVE,
            PetitionPriority.CRITICAL,
            filing_date=date(2024, 10, 15),
            receipt_number='WAC2490000014',
            notes=f'URGENT: H1B expired {expiration_date.strftime("%m/%d/%Y")} - extension filed with premium processing'
        )
        expired_h1b.premium_processing = True
        expired_h1b.expiration_date = expiration_date
        
        # Milestones
        add_milestone(None, expired_case, MilestoneType.CASE_OPENED,
                     MilestoneStatus.COMPLETED, completed_date=date(2024, 10, 1),
                     notes='Urgent case opened due to expired H1B')
        add_milestone(expired_h1b, expired_case, MilestoneType.H1B_FILED,
                     MilestoneStatus.COMPLETED, completed_date=date(2024, 10, 15),
                     notes='Filed with premium processing - 15 calendar day response')
        
        print("      ✓ Created Test Expired User (H1B expired 15 days ago)")
        
        # ============================================================
        # 6. CREATE TODOS
        # ============================================================
        
        print("\n   Creating todos...")
        
        # Todo 1: RFE response for Test RFE user
        todo1 = Todo(
            title='Submit RFE response for Test RFE User',
            description='Complete and submit RFE response for I-140 petition. Due by 11/29/2024.',
            assigned_to_user_id=hr_user.id,
            created_by_user_id=pm_user.id,
            petition_id=rfe_i140.id,
            case_group_id=rfe_case.id,
            beneficiary_id=rfe_ben.id,
            status=TodoStatus.IN_PROGRESS,
            priority=TodoPriority.URGENT,
            due_date=datetime(2024, 11, 29, 0, 0, 0)
        )
        db.add(todo1)
        
        # Todo 2: Appeal preparation for Test Denial user
        todo2 = Todo(
            title='Prepare appeal brief for Test Denial User',
            description='Work with attorney to prepare comprehensive appeal brief for AAO',
            assigned_to_user_id=pm_user.id,
            created_by_user_id=hr_user.id,
            petition_id=denial_i140.id,
            case_group_id=denial_case.id,
            beneficiary_id=denial_ben.id,
            status=TodoStatus.IN_PROGRESS,
            priority=TodoPriority.HIGH,
            due_date=datetime(2025, 2, 1, 0, 0, 0)
        )
        db.add(todo2)
        
        # Todo 3: Monitor concurrent case
        todo3 = Todo(
            title='Monitor concurrent filing case status',
            description='Check USCIS case status for all 4 concurrent petitions (I-140/I-485/I-765/I-131)',
            assigned_to_user_id=hr_user.id,
            created_by_user_id=pm_user.id,
            petition_id=None,
            case_group_id=concurrent_case.id,
            beneficiary_id=concurrent_ben.id,
            status=TodoStatus.TODO,
            priority=TodoPriority.MEDIUM,
            due_date=datetime.utcnow() + timedelta(days=7)
        )
        db.add(todo3)
        
        # Todo 4: Family case - biometrics appointment
        todo4 = Todo(
            title='Schedule biometrics for family (3 people)',
            description='Ensure all 3 family members (primary + spouse + child) attend biometrics appointment',
            assigned_to_user_id=family_user.id,
            created_by_user_id=hr_user.id,
            petition_id=None,
            case_group_id=family_case.id,
            beneficiary_id=family_ben.id,
            status=TodoStatus.TODO,
            priority=TodoPriority.HIGH,
            due_date=datetime.utcnow() + timedelta(days=14)
        )
        db.add(todo4)
        
        # Todo 5: Expired visa - URGENT follow-up
        todo5 = Todo(
            title='URGENT: Follow up on expired H1B extension',
            description=f'H1B expired {expiration_date.strftime("%m/%d/%Y")}. Premium processing - expect response within 15 days. Follow up with USCIS immediately.',
            assigned_to_user_id=hr_user.id,
            created_by_user_id=pm_user.id,
            petition_id=expired_h1b.id,
            case_group_id=expired_case.id,
            beneficiary_id=expired_ben.id,
            status=TodoStatus.IN_PROGRESS,
            priority=TodoPriority.URGENT,
            due_date=datetime.utcnow() + timedelta(days=1)
        )
        db.add(todo5)
        
        print(f"      ✓ Created 5 todos (2 urgent/critical, 1 high, 2 medium priority)")

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
                AuditLog(user_id=pm_user.id, action=AuditAction.CREATE, resource_type='case_group', resource_id=str(rfe_case.id), new_value={'case_number': rfe_case.case_number}, created_at=now - timedelta(hours=2)),
                AuditLog(user_id=hr_user.id, action=AuditAction.CREATE, resource_type='todo', resource_id=str(todo1.id), new_value={'title': todo1.title}, created_at=now - timedelta(hours=5)),
                AuditLog(user_id=tech_lead.id, action=AuditAction.UPDATE, resource_type='department', resource_id=str(dept_ts.id), new_value={'manager_id': tech_lead.id}, created_at=now - timedelta(days=1)),
                AuditLog(user_id=admin.id, action=AuditAction.SYSTEM, resource_type='seed', resource_id=None, new_value={'message': 'Development test seed created'}, created_at=now - timedelta(days=1, hours=3)),
            ]
            for log in sample_logs:
                db.add(log)
            db.flush()
            print("      ✓ Created sample audit logs")
        
        # ============================================================
        # COMMIT ALL
        # ============================================================
        
        db.commit()
        
        print("\n✅ Development test data seeded successfully!")
        print(f"\n   Summary:")
        print(f"   - 5 Departments (TS→TSM/TSA/TNA/AV)")
        print(f"   - 3 Test Staff Users (HR, PM, Tech Lead)")
        print(f"   - 5 Test Beneficiaries (creative edge case scenarios)")
        print(f"   - 5 Case Groups (RFE, Denial, Concurrent, Family, Expired)")
        print(f"   - 16 Petitions (demonstrating various petition types and statuses)")
        print(f"   - 2 Dependents (spouse + child)")
        print(f"   - 5 Todos (2 critical/urgent, 1 high, 2 medium)")
        print(f"\n   Test Scenarios:")
        print(f"   1. RFE User:        test.rfe@example.com / Test123!")
        print(f"   2. Denial User:     test.denial@example.com / Test123!")
        print(f"   3. Concurrent User: test.concurrent@example.com / Test123!")
        print(f"   4. Family User:     test.family@example.com / Test123! (with 2 dependents)")
        print(f"   5. Expired User:    test.expired@example.com / Test123! (H1B expired)")
        print(f"\n   Staff Logins:")
        print(f"   HR:            hr@ama-impact.com / HR123!")
        print(f"   PM:            pm@ama-impact.com / PM123!")
        print(f"   Tech Lead:     techlead@ama-impact.com / Tech123!")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error seeding development test data: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = seed_development_data()
    sys.exit(0 if success else 1)
