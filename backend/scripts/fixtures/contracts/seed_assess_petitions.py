"""
Seed ASSESS petitions and milestones (Step 3 of 3).
Creates Petition records with complete petition sets (I-140 + I-485 + I-765 + I-131)
and two-level Milestones (case-level + petition-level) for realistic case tracking.

Based on Employee data.md - 13 real ASSESS employees with immigration cases.

Run order:
1. seed_assess_beneficiary_users.py
2. seed_assess_case_groups.py
3. seed_assess_petitions.py (this file)

Prerequisites:
- seed_visa_types.py
- seed_assess.py
- seed_assess_beneficiary_users.py
- seed_assess_case_groups.py
"""

import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.core.database import SessionLocal
from app.models.petition import Petition, PetitionType, PetitionStatus, CaseStatus as PetitionCaseStatus, PetitionPriority
from app.models.milestone import Milestone, MilestoneType, MilestoneStatus
from app.models.case_group import CaseGroup
from app.models.beneficiary import Beneficiary
from app.models.user import User
from app.models.law_firm import LawFirm


def seed_assess_petitions():
    """Seed ASSESS petitions and milestones with complete petition sets."""
    db = SessionLocal()
    
    try:
        print("\n📋 Seeding ASSESS petitions and milestones...")
        
        # Get PM user for created_by and responsible_party
        pm_user = db.query(User).filter(User.email == "pm.assess@ama-impact.com").first()
        if not pm_user:
            print("   ❌ PM user not found!")
            return False
        
        # Get law firm
        law_firm = db.query(LawFirm).filter(LawFirm.name.like("%Visa Law%")).first()
        if not law_firm:
            print("   ⚠️  No law firm found, petitions will not have law firm assigned")
        
        # Track created items
        petitions_created = 0
        milestones_created = 0
        
        # Get all case groups by case number for easy lookup
        case_groups = {}
        for cg in db.query(CaseGroup).all():
            case_groups[cg.case_number] = cg
        
        print(f"   ✓ Found {len(case_groups)} case groups")
        
        # ==========================================
        # COMPLETED LPR CASES (4 cases)
        # ==========================================
        
        # 1. Gerrit-Daniel Stich - EB3-PERM → LPR (ASSESS-EB3-2017-001)
        if "ASSESS-EB3-2017-001" in case_groups:
            cg = case_groups["ASSESS-EB3-2017-001"]
            
            # Case-level milestones
            case_milestones = [
                (MilestoneType.CASE_OPENED, date(2017, 6, 15), "Case opened - EB3-PERM pathway initiated"),
                (MilestoneType.STRATEGY_MEETING, date(2017, 7, 1), "Strategy meeting with attorney"),
            ]
            for m_type, m_date, m_desc in case_milestones:
                milestone = Milestone(
                    case_group_id=cg.id,
                    petition_id=None,
                    created_by=pm_user.id,
                    milestone_type=m_type,
                    completed_date=m_date,
                    status=MilestoneStatus.COMPLETED,
                    description=m_desc
                )
                db.add(milestone)
                milestones_created += 1
            
            # H1B (2017-2021) - prerequisite before EB3
            h1b = Petition(
                beneficiary_id=cg.beneficiary_id,
                case_group_id=cg.id,  # Part of the same case group (prerequisite)
                created_by=pm_user.id,
                law_firm_id=law_firm.id if law_firm else None,
                responsible_party_id=pm_user.id,
                petition_type=PetitionType.I129,
                status=PetitionStatus.APPROVED,
                case_status=PetitionCaseStatus.FINALIZED,
                priority=PetitionPriority.MEDIUM,
                filing_date=date(2017, 3, 1),
                approval_date=date(2017, 5, 15),
                expiration_date=date(2023, 5, 15),  # Extended until LPR
                receipt_number="WAC1790023456",
                notes="H1B approved, valid during EB3 processing"
            )
            db.add(h1b)
            db.flush()
            petitions_created += 1
            
            # PERM Labor Certification (2018-2019)
            perm = Petition(
                beneficiary_id=cg.beneficiary_id,
                case_group_id=cg.id,
                created_by=pm_user.id,
                law_firm_id=law_firm.id if law_firm else None,
                responsible_party_id=pm_user.id,
                petition_type=PetitionType.PERM,
                status=PetitionStatus.APPROVED,
                case_status=PetitionCaseStatus.FINALIZED,
                priority=PetitionPriority.HIGH,
                filing_date=date(2018, 3, 1),
                approval_date=date(2019, 8, 15),
                receipt_number="PERM-2018-030123",
                notes="PERM approved after audit"
            )
            db.add(perm)
            db.flush()
            petitions_created += 1
            
            # PERM milestones
            perm_milestones = [
                (MilestoneType.PERM_FILED, date(2018, 3, 1), "PERM filed with DOL"),
                (MilestoneType.PERM_AUDIT, date(2018, 9, 15), "PERM audit issued by DOL"),
                (MilestoneType.PERM_APPROVED, date(2019, 8, 15), "PERM approved by DOL"),
            ]
            for m_type, m_date, m_desc in perm_milestones:
                milestone = Milestone(
                    case_group_id=None,
                    petition_id=perm.id,
                    created_by=pm_user.id,
                    milestone_type=m_type,
                    completed_date=m_date,
                    status=MilestoneStatus.COMPLETED,
                    description=m_desc
                )
                db.add(milestone)
                milestones_created += 1
            
            # I-140 (EB3)
            i140 = Petition(
                beneficiary_id=cg.beneficiary_id,
                case_group_id=cg.id,
                created_by=pm_user.id,
                law_firm_id=law_firm.id if law_firm else None,
                responsible_party_id=pm_user.id,
                petition_type=PetitionType.I140,
                status=PetitionStatus.APPROVED,
                case_status=PetitionCaseStatus.FINALIZED,
                priority=PetitionPriority.HIGH,
                filing_date=date(2019, 10, 1),
                approval_date=date(2020, 3, 15),
                receipt_number="LIN1990056789",
                notes="I-140 approved for EB3"
            )
            db.add(i140)
            db.flush()
            petitions_created += 1
            
            # I-140 milestones
            i140_milestones = [
                (MilestoneType.I140_FILED, date(2019, 10, 1), "I-140 filed"),
                (MilestoneType.I140_APPROVED, date(2020, 3, 15), "I-140 approved"),
            ]
            for m_type, m_date, m_desc in i140_milestones:
                milestone = Milestone(
                    case_group_id=None,
                    petition_id=i140.id,
                    created_by=pm_user.id,
                    milestone_type=m_type,
                    completed_date=m_date,
                    status=MilestoneStatus.COMPLETED,
                    description=m_desc
                )
                db.add(milestone)
                milestones_created += 1
            
            # I-485 (Green Card)
            i485 = Petition(
                beneficiary_id=cg.beneficiary_id,
                case_group_id=cg.id,
                created_by=pm_user.id,
                law_firm_id=law_firm.id if law_firm else None,
                responsible_party_id=pm_user.id,
                petition_type=PetitionType.I485,
                status=PetitionStatus.APPROVED,
                case_status=PetitionCaseStatus.FINALIZED,
                priority=PetitionPriority.HIGH,
                filing_date=date(2020, 6, 1),
                approval_date=date(2021, 10, 15),
                receipt_number="LIN2090067890",
                notes="I-485 approved, green card received"
            )
            db.add(i485)
            db.flush()
            petitions_created += 1
            
            # I-485 milestones
            i485_milestones = [
                (MilestoneType.I485_FILED, date(2020, 6, 1), "I-485 filed"),
                (MilestoneType.BIOMETRICS_COMPLETED, date(2020, 9, 15), "Biometrics completed"),
                (MilestoneType.INTERVIEW_COMPLETED, date(2021, 8, 10), "I-485 interview completed"),
                (MilestoneType.I485_APPROVED, date(2021, 10, 15), "I-485 approved"),
                (MilestoneType.GREEN_CARD_RECEIVED, date(2021, 11, 1), "Green card received in mail"),
            ]
            for m_type, m_date, m_desc in i485_milestones:
                milestone = Milestone(
                    case_group_id=None,
                    petition_id=i485.id,
                    created_by=pm_user.id,
                    milestone_type=m_type,
                    completed_date=m_date,
                    status=MilestoneStatus.COMPLETED,
                    description=m_desc
                )
                db.add(milestone)
                milestones_created += 1
            
            print(f"   ✓ Created 4 petitions + {3 + 3 + 2 + 5} milestones for Gerrit-Daniel Stich (EB3-PERM → LPR)")
        
        # 2. Bhaskaran Rathakrishnan - EB2-NIW → LPR (ASSESS-EB2-2017-002)
        if "ASSESS-EB2-2017-002" in case_groups:
            cg = case_groups["ASSESS-EB2-2017-002"]
            
            # Case-level milestones
            case_milestones = [
                (MilestoneType.CASE_OPENED, date(2017, 9, 1), "Case opened - EB2-NIW pathway initiated"),
                (MilestoneType.STRATEGY_MEETING, date(2017, 9, 15), "Strategy meeting completed"),
            ]
            for m_type, m_date, m_desc in case_milestones:
                milestone = Milestone(
                    case_group_id=cg.id,
                    petition_id=None,
                    created_by=pm_user.id,
                    milestone_type=m_type,
                    completed_date=m_date,
                    status=MilestoneStatus.COMPLETED,
                    description=m_desc
                )
                db.add(milestone)
                milestones_created += 1
            
            # I-140 (EB2-NIW)
            i140 = Petition(
                beneficiary_id=cg.beneficiary_id,
                case_group_id=cg.id,
                created_by=pm_user.id,
                law_firm_id=law_firm.id if law_firm else None,
                responsible_party_id=pm_user.id,
                petition_type=PetitionType.I140,
                status=PetitionStatus.APPROVED,
                case_status=PetitionCaseStatus.FINALIZED,
                priority=PetitionPriority.MEDIUM,
                filing_date=date(2018, 1, 15),
                approval_date=date(2018, 6, 10),
                receipt_number="LIN1890012345",
                notes="I-140 EB2-NIW approved"
            )
            db.add(i140)
            db.flush()
            petitions_created += 1
            
            # I-140 milestones
            i140_milestones = [
                (MilestoneType.I140_FILED, date(2018, 1, 15), "I-140 filed"),
                (MilestoneType.I140_APPROVED, date(2018, 6, 10), "I-140 approved"),
            ]
            for m_type, m_date, m_desc in i140_milestones:
                milestone = Milestone(
                    case_group_id=None,
                    petition_id=i140.id,
                    created_by=pm_user.id,
                    milestone_type=m_type,
                    completed_date=m_date,
                    status=MilestoneStatus.COMPLETED,
                    description=m_desc
                )
                db.add(milestone)
                milestones_created += 1
            
            # I-485
            i485 = Petition(
                beneficiary_id=cg.beneficiary_id,
                case_group_id=cg.id,
                created_by=pm_user.id,
                law_firm_id=law_firm.id if law_firm else None,
                responsible_party_id=pm_user.id,
                petition_type=PetitionType.I485,
                status=PetitionStatus.APPROVED,
                case_status=PetitionCaseStatus.FINALIZED,
                priority=PetitionPriority.MEDIUM,
                filing_date=date(2018, 11, 1),
                approval_date=date(2019, 11, 20),
                receipt_number="LIN1890078901",
                notes="I-485 approved, green card received"
            )
            db.add(i485)
            db.flush()
            petitions_created += 1
            
            # I-485 milestones
            i485_milestones = [
                (MilestoneType.I485_FILED, date(2018, 11, 1), "I-485 filed"),
                (MilestoneType.BIOMETRICS_COMPLETED, date(2019, 2, 15), "Biometrics completed"),
                (MilestoneType.I485_APPROVED, date(2019, 11, 20), "I-485 approved"),
                (MilestoneType.GREEN_CARD_RECEIVED, date(2019, 12, 5), "Green card received"),
            ]
            for m_type, m_date, m_desc in i485_milestones:
                milestone = Milestone(
                    case_group_id=None,
                    petition_id=i485.id,
                    created_by=pm_user.id,
                    milestone_type=m_type,
                    completed_date=m_date,
                    status=MilestoneStatus.COMPLETED,
                    description=m_desc
                )
                db.add(milestone)
                milestones_created += 1
            
            print(f"   ✓ Created 2 petitions + {2 + 2 + 4} milestones for Bhaskaran Rathakrishnan (EB2-NIW → LPR)")
        
        # 3. Arnaud Borner - EB2-NIW → LPR (ASSESS-EB2-2019-003)
        if "ASSESS-EB2-2019-003" in case_groups:
            cg = case_groups["ASSESS-EB2-2019-003"]
            
            # Case-level milestones
            case_milestones = [
                (MilestoneType.CASE_OPENED, date(2019, 4, 15), "Case opened - EB2-NIW pathway"),
            ]
            for m_type, m_date, m_desc in case_milestones:
                milestone = Milestone(
                    case_group_id=cg.id,
                    petition_id=None,
                    created_by=pm_user.id,
                    milestone_type=m_type,
                    completed_date=m_date,
                    status=MilestoneStatus.COMPLETED,
                    description=m_desc
                )
                db.add(milestone)
                milestones_created += 1
            
            # I-140
            i140 = Petition(
                beneficiary_id=cg.beneficiary_id,
                case_group_id=cg.id,
                created_by=pm_user.id,
                law_firm_id=law_firm.id if law_firm else None,
                responsible_party_id=pm_user.id,
                petition_type=PetitionType.I140,
                status=PetitionStatus.APPROVED,
                case_status=PetitionCaseStatus.FINALIZED,
                priority=PetitionPriority.MEDIUM,
                filing_date=date(2019, 7, 1),
                approval_date=date(2020, 1, 10),
                receipt_number="LIN1990034567",
                notes="I-140 EB2-NIW approved"
            )
            db.add(i140)
            db.flush()
            petitions_created += 1
            
            # I-140 milestones
            i140_milestones = [
                (MilestoneType.I140_FILED, date(2019, 7, 1), "I-140 filed"),
                (MilestoneType.I140_APPROVED, date(2020, 1, 10), "I-140 approved"),
            ]
            for m_type, m_date, m_desc in i140_milestones:
                milestone = Milestone(
                    case_group_id=None,
                    petition_id=i140.id,
                    created_by=pm_user.id,
                    milestone_type=m_type,
                    completed_date=m_date,
                    status=MilestoneStatus.COMPLETED,
                    description=m_desc
                )
                db.add(milestone)
                milestones_created += 1
            
            # I-485
            i485 = Petition(
                beneficiary_id=cg.beneficiary_id,
                case_group_id=cg.id,
                created_by=pm_user.id,
                law_firm_id=law_firm.id if law_firm else None,
                responsible_party_id=pm_user.id,
                petition_type=PetitionType.I485,
                status=PetitionStatus.APPROVED,
                case_status=PetitionCaseStatus.FINALIZED,
                priority=PetitionPriority.MEDIUM,
                filing_date=date(2020, 6, 1),
                approval_date=date(2021, 5, 30),
                receipt_number="LIN2090056789",
                notes="I-485 approved, green card received"
            )
            db.add(i485)
            db.flush()
            petitions_created += 1
            
            # I-485 milestones
            i485_milestones = [
                (MilestoneType.I485_FILED, date(2020, 6, 1), "I-485 filed"),
                (MilestoneType.BIOMETRICS_COMPLETED, date(2020, 10, 15), "Biometrics completed"),
                (MilestoneType.I485_APPROVED, date(2021, 5, 30), "I-485 approved"),
                (MilestoneType.GREEN_CARD_RECEIVED, date(2021, 6, 15), "Green card received"),
            ]
            for m_type, m_date, m_desc in i485_milestones:
                milestone = Milestone(
                    case_group_id=None,
                    petition_id=i485.id,
                    created_by=pm_user.id,
                    milestone_type=m_type,
                    completed_date=m_date,
                    status=MilestoneStatus.COMPLETED,
                    description=m_desc
                )
                db.add(milestone)
                milestones_created += 1
            
            print(f"   ✓ Created 2 petitions + {1 + 2 + 4} milestones for Arnaud Borner (EB2-NIW → LPR)")
        
        # 4. Victor Sousa - EB2-NIW → LPR (ASSESS-EB2-2022-004)
        if "ASSESS-EB2-2022-004" in case_groups:
            cg = case_groups["ASSESS-EB2-2022-004"]
            
            # Case-level milestones
            case_milestones = [
                (MilestoneType.CASE_OPENED, date(2022, 3, 1), "Case opened - EB2-NIW pathway"),
            ]
            for m_type, m_date, m_desc in case_milestones:
                milestone = Milestone(
                    case_group_id=cg.id,
                    petition_id=None,
                    created_by=pm_user.id,
                    milestone_type=m_type,
                    completed_date=m_date,
                    status=MilestoneStatus.COMPLETED,
                    description=m_desc
                )
                db.add(milestone)
                milestones_created += 1
            
            # I-140
            i140 = Petition(
                beneficiary_id=cg.beneficiary_id,
                case_group_id=cg.id,
                created_by=pm_user.id,
                law_firm_id=law_firm.id if law_firm else None,
                responsible_party_id=pm_user.id,
                petition_type=PetitionType.I140,
                status=PetitionStatus.APPROVED,
                case_status=PetitionCaseStatus.FINALIZED,
                priority=PetitionPriority.MEDIUM,
                filing_date=date(2022, 5, 1),
                approval_date=date(2022, 10, 15),
                receipt_number="LIN2290045678",
                notes="I-140 EB2-NIW approved"
            )
            db.add(i140)
            db.flush()
            petitions_created += 1
            
            # I-140 milestones
            i140_milestones = [
                (MilestoneType.I140_FILED, date(2022, 5, 1), "I-140 filed"),
                (MilestoneType.I140_APPROVED, date(2022, 10, 15), "I-140 approved"),
            ]
            for m_type, m_date, m_desc in i140_milestones:
                milestone = Milestone(
                    case_group_id=None,
                    petition_id=i140.id,
                    created_by=pm_user.id,
                    milestone_type=m_type,
                    completed_date=m_date,
                    status=MilestoneStatus.COMPLETED,
                    description=m_desc
                )
                db.add(milestone)
                milestones_created += 1
            
            # I-485
            i485 = Petition(
                beneficiary_id=cg.beneficiary_id,
                case_group_id=cg.id,
                created_by=pm_user.id,
                law_firm_id=law_firm.id if law_firm else None,
                responsible_party_id=pm_user.id,
                petition_type=PetitionType.I485,
                status=PetitionStatus.APPROVED,
                case_status=PetitionCaseStatus.FINALIZED,
                priority=PetitionPriority.MEDIUM,
                filing_date=date(2022, 11, 1),
                approval_date=date(2023, 1, 15),
                receipt_number="LIN2290067890",
                notes="I-485 approved, green card received"
            )
            db.add(i485)
            db.flush()
            petitions_created += 1
            
            # I-485 milestones
            i485_milestones = [
                (MilestoneType.I485_FILED, date(2022, 11, 1), "I-485 filed"),
                (MilestoneType.BIOMETRICS_COMPLETED, date(2022, 12, 15), "Biometrics completed"),
                (MilestoneType.I485_APPROVED, date(2023, 1, 15), "I-485 approved"),
                (MilestoneType.GREEN_CARD_RECEIVED, date(2023, 2, 1), "Green card received"),
            ]
            for m_type, m_date, m_desc in i485_milestones:
                milestone = Milestone(
                    case_group_id=None,
                    petition_id=i485.id,
                    created_by=pm_user.id,
                    milestone_type=m_type,
                    completed_date=m_date,
                    status=MilestoneStatus.COMPLETED,
                    description=m_desc
                )
                db.add(milestone)
                milestones_created += 1
            
            print(f"   ✓ Created 2 petitions + {1 + 2 + 4} milestones for Victor Sousa (EB2-NIW → LPR)")
        
        # ==========================================
        # ACTIVE CASES (6 cases)
        # ==========================================
        
        # 5. Luis Fernandes - EB2-NIW (I-140 received, I-485 prep) (ASSESS-EB2-2024-005)
        if "ASSESS-EB2-2024-005" in case_groups:
            cg = case_groups["ASSESS-EB2-2024-005"]
            
            # Case-level milestones
            case_milestones = [
                (MilestoneType.CASE_OPENED, date(2024, 8, 20), "Case opened - EB2-NIW pathway"),
            ]
            for m_type, m_date, m_desc in case_milestones:
                milestone = Milestone(
                    case_group_id=cg.id,
                    petition_id=None,
                    created_by=pm_user.id,
                    milestone_type=m_type,
                    completed_date=m_date,
                    status=MilestoneStatus.COMPLETED,
                    description=m_desc
                )
                db.add(milestone)
                milestones_created += 1
            
            # I-140 (APPROVED - received 2 weeks ago)
            i140 = Petition(
                beneficiary_id=cg.beneficiary_id,
                case_group_id=cg.id,
                created_by=pm_user.id,
                law_firm_id=law_firm.id if law_firm else None,
                responsible_party_id=pm_user.id,
                petition_type=PetitionType.I140,
                status=PetitionStatus.APPROVED,
                case_status=PetitionCaseStatus.ACTIVE,
                priority=PetitionPriority.HIGH,
                filing_date=date(2024, 9, 15),
                approval_date=date(2024, 10, 28),
                receipt_number="LIN2490056789",
                notes="I-140 approved! Approval notice received Oct 28, 2024."
            )
            db.add(i140)
            db.flush()
            petitions_created += 1
            
            # I-140 milestones
            i140_milestones = [
                (MilestoneType.I140_FILED, date(2024, 9, 15), "I-140 filed"),
                (MilestoneType.I140_APPROVED, date(2024, 10, 28), "I-140 approved!"),
            ]
            for m_type, m_date, m_desc in i140_milestones:
                milestone = Milestone(
                    case_group_id=None,
                    petition_id=i140.id,
                    created_by=pm_user.id,
                    milestone_type=m_type,
                    completed_date=m_date,
                    status=MilestoneStatus.COMPLETED,
                    description=m_desc
                )
                db.add(milestone)
                milestones_created += 1
            
            # I-485 (IN_PREPARATION - collecting documents)
            i485 = Petition(
                beneficiary_id=cg.beneficiary_id,
                case_group_id=cg.id,
                created_by=pm_user.id,
                law_firm_id=law_firm.id if law_firm else None,
                responsible_party_id=pm_user.id,
                petition_type=PetitionType.I485,
                status=PetitionStatus.DRAFT,
                case_status=PetitionCaseStatus.ACTIVE,
                priority=PetitionPriority.HIGH,
                notes="Collecting documents for I-485 filing"
            )
            db.add(i485)
            db.flush()
            petitions_created += 1
            
            # I-765 (EAD - IN_PREPARATION)
            i765 = Petition(
                beneficiary_id=cg.beneficiary_id,
                case_group_id=cg.id,
                created_by=pm_user.id,
                law_firm_id=law_firm.id if law_firm else None,
                responsible_party_id=pm_user.id,
                petition_type=PetitionType.I765,
                status=PetitionStatus.DRAFT,
                case_status=PetitionCaseStatus.ACTIVE,
                priority=PetitionPriority.MEDIUM,
                notes="Will file concurrent with I-485"
            )
            db.add(i765)
            db.flush()
            petitions_created += 1
            
            # I-131 (AP - IN_PREPARATION)
            i131 = Petition(
                beneficiary_id=cg.beneficiary_id,
                case_group_id=cg.id,
                created_by=pm_user.id,
                law_firm_id=law_firm.id if law_firm else None,
                responsible_party_id=pm_user.id,
                petition_type=PetitionType.I131,
                status=PetitionStatus.DRAFT,
                case_status=PetitionCaseStatus.ACTIVE,
                priority=PetitionPriority.MEDIUM,
                notes="Will file concurrent with I-485"
            )
            db.add(i131)
            db.flush()
            petitions_created += 1
            
            print(f"   ✓ Created 4 petitions + {1 + 2} milestones for Luis Fernandes (I-140 approved, I-485 prep)")
        
        # 6. Kiran Ravikumar - EB2-NIW (I-140 just filed) (ASSESS-EB2-2024-006)
        if "ASSESS-EB2-2024-006" in case_groups:
            cg = case_groups["ASSESS-EB2-2024-006"]
            
            # Case-level milestones
            case_milestones = [
                (MilestoneType.CASE_OPENED, date(2024, 9, 15), "Case opened - EB2-NIW pathway"),
            ]
            for m_type, m_date, m_desc in case_milestones:
                milestone = Milestone(
                    case_group_id=cg.id,
                    petition_id=None,
                    created_by=pm_user.id,
                    milestone_type=m_type,
                    completed_date=m_date,
                    status=MilestoneStatus.COMPLETED,
                    description=m_desc
                )
                db.add(milestone)
                milestones_created += 1
            
            # I-140 (FILED - awaiting receipt notice)
            i140 = Petition(
                beneficiary_id=cg.beneficiary_id,
                case_group_id=cg.id,
                created_by=pm_user.id,
                law_firm_id=law_firm.id if law_firm else None,
                responsible_party_id=pm_user.id,
                petition_type=PetitionType.I140,
                status=PetitionStatus.SUBMITTED,
                case_status=PetitionCaseStatus.ACTIVE,
                priority=PetitionPriority.HIGH,
                filing_date=date(2024, 11, 1),
                receipt_number="LIN2490078901",  # Just received
                notes="I-140 filed on Nov 1, 2024. Awaiting USCIS processing."
            )
            db.add(i140)
            db.flush()
            petitions_created += 1
            
            # I-140 milestones
            i140_milestones = [
                (MilestoneType.I140_FILED, date(2024, 11, 1), "I-140 filed with USCIS"),
            ]
            for m_type, m_date, m_desc in i140_milestones:
                milestone = Milestone(
                    case_group_id=None,
                    petition_id=i140.id,
                    created_by=pm_user.id,
                    milestone_type=m_type,
                    completed_date=m_date,
                    status=MilestoneStatus.COMPLETED,
                    description=m_desc
                )
                db.add(milestone)
                milestones_created += 1
            
            print(f"   ✓ Created 1 petition + {1 + 1} milestones for Kiran Ravikumar (I-140 just filed)")
        
        # 7. David Craig Penner - TN renewal (PM approved, waiting on HR) (ASSESS-TN-2024-007)
        if "ASSESS-TN-2024-007" in case_groups:
            cg = case_groups["ASSESS-TN-2024-007"]
            
            # TN renewal petition (DRAFT - waiting on HR to schedule)
            tn = Petition(
                beneficiary_id=cg.beneficiary_id,
                case_group_id=cg.id,
                created_by=pm_user.id,
                responsible_party_id=pm_user.id,
                petition_type=PetitionType.TN_APPLICATION,
                status=PetitionStatus.DRAFT,
                case_status=PetitionCaseStatus.UPCOMING,
                priority=PetitionPriority.MEDIUM,
                notes="PM approved on Oct 1, 2024. Waiting for HR to schedule initial meeting."
            )
            db.add(tn)
            db.flush()
            petitions_created += 1
            
            print(f"   ✓ Created 1 petition for David Craig Penner (TN renewal, waiting on HR)")
        
        # 8. Jacob Friedrichson - Future hire H1B (PM approved, no user yet) (ASSESS-H1B-2024-008)
        if "ASSESS-H1B-2024-008" in case_groups:
            cg = case_groups["ASSESS-H1B-2024-008"]
            
            # H1B petition (DRAFT - future hire)
            h1b = Petition(
                beneficiary_id=cg.beneficiary_id,
                case_group_id=cg.id,
                created_by=pm_user.id,
                law_firm_id=law_firm.id if law_firm else None,
                responsible_party_id=pm_user.id,
                petition_type=PetitionType.I129,
                status=PetitionStatus.DRAFT,
                case_status=PetitionCaseStatus.UPCOMING,
                priority=PetitionPriority.HIGH,
                notes="H1B for new hire. PM approved Sep 15, 2024. Awaiting HR onboarding."
            )
            db.add(h1b)
            db.flush()
            petitions_created += 1
            
            print(f"   ✓ Created 1 petition for Jacob Friedrichson (H1B new hire, waiting on HR)")
        
        # 9. Georgios - EB2-PERM (PERM approved, I-140 prep) (ASSESS-EB2-2024-009)
        if "ASSESS-EB2-2024-009" in case_groups:
            cg = case_groups["ASSESS-EB2-2024-009"]
            
            # Case-level milestones
            case_milestones = [
                (MilestoneType.CASE_OPENED, date(2024, 1, 15), "Case opened - EB2-PERM pathway"),
            ]
            for m_type, m_date, m_desc in case_milestones:
                milestone = Milestone(
                    case_group_id=cg.id,
                    petition_id=None,
                    created_by=pm_user.id,
                    milestone_type=m_type,
                    completed_date=m_date,
                    status=MilestoneStatus.COMPLETED,
                    description=m_desc
                )
                db.add(milestone)
                milestones_created += 1
            
            # PERM (APPROVED)
            perm = Petition(
                beneficiary_id=cg.beneficiary_id,
                case_group_id=cg.id,
                created_by=pm_user.id,
                law_firm_id=law_firm.id if law_firm else None,
                responsible_party_id=pm_user.id,
                petition_type=PetitionType.PERM,
                status=PetitionStatus.APPROVED,
                case_status=PetitionCaseStatus.ACTIVE,
                priority=PetitionPriority.HIGH,
                filing_date=date(2024, 3, 1),
                approval_date=date(2024, 9, 15),
                receipt_number="PERM-2024-030145",
                notes="PERM approved by DOL on Sep 15, 2024"
            )
            db.add(perm)
            db.flush()
            petitions_created += 1
            
            # PERM milestones
            perm_milestones = [
                (MilestoneType.PERM_FILED, date(2024, 3, 1), "PERM filed with DOL"),
                (MilestoneType.PERM_APPROVED, date(2024, 9, 15), "PERM approved by DOL"),
            ]
            for m_type, m_date, m_desc in perm_milestones:
                milestone = Milestone(
                    case_group_id=None,
                    petition_id=perm.id,
                    created_by=pm_user.id,
                    milestone_type=m_type,
                    completed_date=m_date,
                    status=MilestoneStatus.COMPLETED,
                    description=m_desc
                )
                db.add(milestone)
                milestones_created += 1
            
            # I-140 (IN_PREPARATION)
            i140 = Petition(
                beneficiary_id=cg.beneficiary_id,
                case_group_id=cg.id,
                created_by=pm_user.id,
                law_firm_id=law_firm.id if law_firm else None,
                responsible_party_id=pm_user.id,
                petition_type=PetitionType.I140,
                status=PetitionStatus.DRAFT,
                case_status=PetitionCaseStatus.ACTIVE,
                priority=PetitionPriority.HIGH,
                notes="Preparing I-140 documents with Goel & Anderson"
            )
            db.add(i140)
            db.flush()
            petitions_created += 1
            
            print(f"   ✓ Created 2 petitions + {1 + 2} milestones for Georgios (PERM approved, I-140 prep)")
        
        # 10. Timothy Chau - Marriage-based GC (PM approved, not started) (ASSESS-MARRIAGE-2024-011)
        if "ASSESS-MARRIAGE-2024-011" in case_groups:
            cg = case_groups["ASSESS-MARRIAGE-2024-011"]
            
            # I-130 (DRAFT)
            i130 = Petition(
                beneficiary_id=cg.beneficiary_id,
                case_group_id=cg.id,
                created_by=pm_user.id,
                law_firm_id=law_firm.id if law_firm else None,
                responsible_party_id=pm_user.id,
                petition_type=PetitionType.I130,
                status=PetitionStatus.DRAFT,
                case_status=PetitionCaseStatus.UPCOMING,
                priority=PetitionPriority.MEDIUM,
                notes="I-130 for marriage-based green card. PM approved Oct 30, 2024."
            )
            db.add(i130)
            db.flush()
            petitions_created += 1
            
            # I-485 (DRAFT)
            i485 = Petition(
                beneficiary_id=cg.beneficiary_id,
                case_group_id=cg.id,
                created_by=pm_user.id,
                law_firm_id=law_firm.id if law_firm else None,
                responsible_party_id=pm_user.id,
                petition_type=PetitionType.I485,
                status=PetitionStatus.DRAFT,
                case_status=PetitionCaseStatus.UPCOMING,
                priority=PetitionPriority.MEDIUM,
                notes="Will file concurrent with I-130"
            )
            db.add(i485)
            db.flush()
            petitions_created += 1
            
            print(f"   ✓ Created 2 petitions for Timothy Chau (Marriage-based GC, draft)")
        
        # ==========================================
        # PENDING PM APPROVAL (1 case)
        # ==========================================
        
        # 10. Brandon Lowe - EB2-NIW (PENDING_PM_APPROVAL) (ASSESS-EB2-2024-010)
        if "ASSESS-EB2-2024-010" in case_groups:
            cg = case_groups["ASSESS-EB2-2024-010"]
            
            # I-140 (DRAFT - awaiting PM approval)
            i140 = Petition(
                beneficiary_id=cg.beneficiary_id,
                case_group_id=cg.id,
                created_by=cg.created_by_manager_id,
                law_firm_id=law_firm.id if law_firm else None,
                responsible_party_id=pm_user.id,
                petition_type=PetitionType.I140,
                status=PetitionStatus.DRAFT,
                case_status=PetitionCaseStatus.UPCOMING,
                priority=PetitionPriority.MEDIUM,
                notes="EB2-NIW case submitted for PM approval on Oct 25, 2024. Awaiting decision."
            )
            db.add(i140)
            db.flush()
            petitions_created += 1
            
            print(f"   ✓ Created 1 petition for Brandon Lowe (PENDING PM APPROVAL)")
        
        # ==========================================
        # DRAFT CASES (2 cases)
        # ==========================================
        
        # 12. Tove Aagen - EB2-NIW (DRAFT) (ASSESS-EB2-2024-012)
        if "ASSESS-EB2-2024-012" in case_groups:
            cg = case_groups["ASSESS-EB2-2024-012"]
            
            # I-140 (DRAFT)
            i140 = Petition(
                beneficiary_id=cg.beneficiary_id,
                case_group_id=cg.id,
                created_by=cg.created_by_manager_id,
                law_firm_id=law_firm.id if law_firm else None,
                responsible_party_id=pm_user.id,
                petition_type=PetitionType.I140,
                status=PetitionStatus.DRAFT,
                case_status=PetitionCaseStatus.UPCOMING,
                priority=PetitionPriority.LOW,
                notes="Draft EB2-NIW case. Initial assessment in progress."
            )
            db.add(i140)
            db.flush()
            petitions_created += 1
            
            print(f"   ✓ Created 1 petition for Tove Aagen (DRAFT)")
        
        # 13. David Garcia Perez - EB2-NIW (DRAFT) (ASSESS-EB2-2024-013)
        if "ASSESS-EB2-2024-013" in case_groups:
            cg = case_groups["ASSESS-EB2-2024-013"]
            
            # I-140 (DRAFT)
            i140 = Petition(
                beneficiary_id=cg.beneficiary_id,
                case_group_id=cg.id,
                created_by=cg.created_by_manager_id,
                law_firm_id=law_firm.id if law_firm else None,
                responsible_party_id=pm_user.id,
                petition_type=PetitionType.I140,
                status=PetitionStatus.DRAFT,
                case_status=PetitionCaseStatus.UPCOMING,
                priority=PetitionPriority.LOW,
                notes="Draft EB2-NIW case. Initial assessment in progress."
            )
            db.add(i140)
            db.flush()
            petitions_created += 1
            
            print(f"   ✓ Created 1 petition for David Garcia Perez (DRAFT)")
        
        db.commit()
        print(f"\n✅ ASSESS petitions and milestones seeded successfully!")
        print(f"   Petitions created: {petitions_created}")
        print(f"   Milestones created: {milestones_created}")
        print(f"   Breakdown:")
        print(f"     - 4 COMPLETED LPR cases (Gerrit, Bhaskaran, Arnaud, Victor)")
        print(f"       * Gerrit: 4 petitions (H1B + PERM + I-140 + I-485)")
        print(f"       * Others: 2 petitions each (I-140 + I-485)")
        print(f"     - 6 ACTIVE cases (Luis, Kiran, David Craig, Jacob, Georgios, Timothy)")
        print(f"       * Luis: 4 petitions (I-140 approved + I-485/I-765/I-131 prep)")
        print(f"       * Kiran: 1 petition (I-140 filed)")
        print(f"       * Others: 1-2 petitions each")
        print(f"     - 1 PENDING PM APPROVAL (Brandon)")
        print(f"     - 2 DRAFT (Tove, David Garcia)")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding petitions: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    seed_assess_petitions()
