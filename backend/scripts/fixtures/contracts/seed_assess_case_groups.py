"""
Seed ASSESS case groups for beneficiaries.

This script creates case groups with proper workflow status for each beneficiary.
"""

import sys
from pathlib import Path
from datetime import datetime, date

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.core.database import SessionLocal
from app.models.case_group import CaseGroup, PathwayType, CaseStatus, ApprovalStatus
from app.models.petition import PetitionPriority
from app.models.beneficiary import Beneficiary
from app.models.user import User
from app.models.law_firm import LawFirm
from app.models.contract import Contract

def seed_case_groups():
    """Seed ASSESS case groups."""
    print("\n📋 Seeding ASSESS case groups...")
    
    db = SessionLocal()
    try:
        # Get contract
        contract = db.query(Contract).filter(Contract.code == "ASSESS").first()
        if not contract:
            print("❌ ASSESS contract not found. Run seed_assess.py first.")
            return
        
        # Get PM and HR users (for responsible_party and approvers)
        pm_user = db.query(User).filter(User.email == "pm.assess@ama-impact.com").first()
        hr_dept_manager = db.query(User).filter(User.email == "hr.assess@ama-impact.com").first()
        
        # Get law firm
        law_firm = db.query(LawFirm).filter(LawFirm.name.like("%Visa Law%")).first()
        
        # Get beneficiaries by email (all 13 employees)
        beneficiaries = {}
        emails = [
            "gerrit-daniel.stich@ama-inc.com",
            "bhaskaran.rathakrishnan@ama-inc.com",
            "arnaud.borner@ama-inc.com",
            "brandon.lowe@ama-inc.com",
            "david.c.penner@ama-inc.com",
            "timothy.chau@ama-inc.com",
            "luis.fernandes@ama-inc.com",
            "kiran.ravikumar@ama-inc.com",
            "victor.sousa@ama-inc.com",
            "david.garciaperez@ama-inc.com",
            "tove.aagren@ama-inc.com",
            "georgios.bellas-chatzigeorgis@ama-inc.com"
        ]
        
        for email in emails:
            user = db.query(User).filter(User.email == email).first()
            if user and user.beneficiary:
                beneficiaries[email] = user.beneficiary
        
        # Also get beneficiary without user (Jacob)
        jacob = db.query(Beneficiary).filter(
            Beneficiary.first_name == "Jacob",
            Beneficiary.last_name == "Friedrichson"
        ).first()
        if jacob:
            beneficiaries["jacob.future"] = jacob
        
        # Track created case groups
        case_groups_created = 0
        
        # ==========================================
        # COMPLETED CASES (status=APPROVED)
        # ==========================================
        
        # 1. Gerrit-Daniel Stich - Completed EB3-PERM (has LPR)
        if "gerrit-daniel.stich@ama-inc.com" in beneficiaries:
            gerrit_ben = beneficiaries["gerrit-daniel.stich@ama-inc.com"]
            case = CaseGroup(
                beneficiary_id=gerrit_ben.id,
                responsible_party_id=pm_user.id,
                created_by_manager_id=pm_user.id,  # Self-initiated as manager
                law_firm_id=law_firm.id if law_firm else None,
                approval_status=ApprovalStatus.PM_APPROVED,
                approved_by_pm_id=pm_user.id,
                pm_approval_date=date(2017, 6, 1),
                pathway_type=PathwayType.EB3_PERM,  # EB3 with PERM
                case_number="ASSESS-EB3-2017-001",
                status=CaseStatus.APPROVED,
                priority=PetitionPriority.MEDIUM,
                case_started_date=date(2017, 6, 15),
                target_completion_date=date(2021, 12, 31),
                case_completed_date=date(2021, 10, 15),
                notes="Completed EB3-PERM case. Green card received in 2021. H1B from 2017-2021."
            )
            db.add(case)
            case_groups_created += 1
            print(f"   ✓ Created APPROVED case for Gerrit-Daniel Stich (EB3-PERM → LPR)")
        
        # 2. Bhaskaran Rathakrishnan - Completed EB2-NIW (has LPR)
        if "bhaskaran.rathakrishnan@ama-inc.com" in beneficiaries:
            bhaskaran_ben = beneficiaries["bhaskaran.rathakrishnan@ama-inc.com"]
            case = CaseGroup(
                beneficiary_id=bhaskaran_ben.id,
                responsible_party_id=pm_user.id,
                created_by_manager_id=pm_user.id,
                law_firm_id=law_firm.id if law_firm else None,
                approval_status=ApprovalStatus.PM_APPROVED,
                approved_by_pm_id=pm_user.id,
                pm_approval_date=date(2017, 8, 1),
                pathway_type=PathwayType.EB2_NIW,
                case_number="ASSESS-EB2-2017-002",
                status=CaseStatus.APPROVED,
                priority=PetitionPriority.MEDIUM,
                case_started_date=date(2017, 9, 1),
                target_completion_date=date(2019, 12, 31),
                case_completed_date=date(2019, 11, 20),
                notes="Completed EB2-NIW case. Green card received in 2019."
            )
            db.add(case)
            case_groups_created += 1
            print(f"   ✓ Created APPROVED case for Bhaskaran Rathakrishnan (EB2-NIW → LPR)")
        
        # 3. Arnaud Borner - Completed EB2-NIW (has LPR)
        if "arnaud.borner@ama-inc.com" in beneficiaries:
            arnaud_ben = beneficiaries["arnaud.borner@ama-inc.com"]
            case = CaseGroup(
                beneficiary_id=arnaud_ben.id,
                responsible_party_id=pm_user.id,
                created_by_manager_id=pm_user.id,
                law_firm_id=law_firm.id if law_firm else None,
                approval_status=ApprovalStatus.PM_APPROVED,
                approved_by_pm_id=pm_user.id,
                pm_approval_date=date(2019, 1, 10),
                pathway_type=PathwayType.EB2_NIW,
                case_number="ASSESS-EB2-2019-003",
                status=CaseStatus.APPROVED,
                priority=PetitionPriority.MEDIUM,
                case_started_date=date(2019, 4, 15),
                target_completion_date=date(2021, 6, 30),
                case_completed_date=date(2021, 5, 30),
                notes="Completed EB2-NIW case. Green card received in 2021."
            )
            db.add(case)
            case_groups_created += 1
            print(f"   ✓ Created APPROVED case for Arnaud Borner (EB2-NIW → LPR)")
        
        # 4. Victor Sousa - Completed EB2-NIW (has LPR)
        if "victor.sousa@ama-inc.com" in beneficiaries:
            victor_ben = beneficiaries["victor.sousa@ama-inc.com"]
            case = CaseGroup(
                beneficiary_id=victor_ben.id,
                responsible_party_id=pm_user.id,
                created_by_manager_id=victor_ben.user.reports_to_id,
                law_firm_id=law_firm.id if law_firm else None,
                approval_status=ApprovalStatus.PM_APPROVED,
                approved_by_pm_id=pm_user.id,
                pm_approval_date=date(2022, 5, 10),
                pathway_type=PathwayType.EB2_NIW,
                case_number="ASSESS-EB2-2022-004",
                status=CaseStatus.APPROVED,
                priority=PetitionPriority.MEDIUM,
                case_started_date=date(2022, 3, 1),
                target_completion_date=date(2023, 2, 28),
                case_completed_date=date(2023, 1, 15),
                notes="Completed EB2-NIW case. Green card received in 2023."
            )
            db.add(case)
            case_groups_created += 1
            print(f"   ✓ Created APPROVED case for Victor Sousa (EB2-NIW → LPR)")
        
        # ==========================================
        # PM_APPROVED ACTIVE CASES (status=IN_PROGRESS)
        # ==========================================
        
        # 5. Luis Fernandes - Active EB2-NIW (I-140 received 2 weeks ago)
        if "luis.fernandes@ama-inc.com" in beneficiaries:
            luis_ben = beneficiaries["luis.fernandes@ama-inc.com"]
            case = CaseGroup(
                beneficiary_id=luis_ben.id,
                responsible_party_id=pm_user.id,
                created_by_manager_id=luis_ben.user.reports_to_id,
                law_firm_id=law_firm.id if law_firm else None,
                approval_status=ApprovalStatus.PM_APPROVED,
                approved_by_pm_id=pm_user.id,
                pm_approval_date=date(2024, 8, 15),
                pathway_type=PathwayType.EB2_NIW,
                case_number="ASSESS-EB2-2024-005",
                status=CaseStatus.IN_PROGRESS,
                priority=PetitionPriority.HIGH,
                case_started_date=date(2024, 8, 20),
                target_completion_date=date(2025, 8, 31),
                case_completed_date=None,
                notes="I-140 approved and received on Oct 28, 2024. Now collecting documents for I-485."
            )
            db.add(case)
            case_groups_created += 1
            print(f"   ✓ Created IN_PROGRESS case for Luis Fernandes (I-140 received, I-485 prep)")
        
        # 6. Kiran Ravikumar - Active EB2-NIW (I-140 just filed)
        if "kiran.ravikumar@ama-inc.com" in beneficiaries:
            kiran_ben = beneficiaries["kiran.ravikumar@ama-inc.com"]
            case = CaseGroup(
                beneficiary_id=kiran_ben.id,
                responsible_party_id=pm_user.id,
                created_by_manager_id=kiran_ben.user.reports_to_id,
                law_firm_id=law_firm.id if law_firm else None,
                approval_status=ApprovalStatus.PM_APPROVED,
                approved_by_pm_id=pm_user.id,
                pm_approval_date=date(2024, 9, 1),
                pathway_type=PathwayType.EB2_NIW,
                case_number="ASSESS-EB2-2024-006",
                status=CaseStatus.IN_PROGRESS,
                priority=PetitionPriority.HIGH,
                case_started_date=date(2024, 9, 15),
                target_completion_date=date(2025, 9, 30),
                case_completed_date=None,
                notes="I-140 filed on Nov 1, 2024. Awaiting USCIS receipt notice."
            )
            db.add(case)
            case_groups_created += 1
            print(f"   ✓ Created IN_PROGRESS case for Kiran Ravikumar (I-140 just filed)")
        
        # 5. David Craig Penner - PM approved but HR hasn't scheduled meetings
        if "david.c.penner@ama-inc.com" in beneficiaries:
            david_pen_ben = beneficiaries["david.c.penner@ama-inc.com"]
            case = CaseGroup(
                beneficiary_id=david_pen_ben.id,
                responsible_party_id=hr_dept_manager.id if hr_dept_manager else pm_user.id,
                created_by_manager_id=david_pen_ben.user.reports_to_id,
                law_firm_id=law_firm.id if law_firm else None,
                approval_status=ApprovalStatus.PM_APPROVED,
                approved_by_pm_id=pm_user.id,
                pm_approval_date=date(2024, 10, 1),
                pathway_type=PathwayType.TN,
                case_number="ASSESS-TN-2024-007",
                status=CaseStatus.IN_PROGRESS,
                priority=PetitionPriority.MEDIUM,
                case_started_date=None,  # Not started yet, waiting on HR
                target_completion_date=date(2025, 1, 31),
                case_completed_date=None,
                notes="PM approved on Oct 1, 2024. Waiting for HR to schedule initial consultation meeting."
            )
            db.add(case)
            case_groups_created += 1
            print(f"   ✓ Created IN_PROGRESS case for David Craig Penner (waiting on HR)")
        
        # 6. Jacob Friedrichson - Future hire, H1B approved but HR hasn't scheduled
        if "jacob.future" in beneficiaries:
            jacob_ben = beneficiaries["jacob.future"]
            case = CaseGroup(
                beneficiary_id=jacob_ben.id,
                responsible_party_id=hr_dept_manager.id if hr_dept_manager else pm_user.id,
                created_by_manager_id=pm_user.id,  # No manager yet, use PM
                law_firm_id=law_firm.id if law_firm else None,
                approval_status=ApprovalStatus.PM_APPROVED,
                approved_by_pm_id=pm_user.id,
                pm_approval_date=date(2024, 9, 15),
                pathway_type=PathwayType.H1B_INITIAL,
                case_number="ASSESS-H1B-2024-008",
                status=CaseStatus.IN_PROGRESS,
                priority=PetitionPriority.HIGH,
                case_started_date=None,  # Not started yet, waiting on HR
                target_completion_date=date(2025, 4, 1),
                case_completed_date=None,
                notes="Future hire. PM approved on Sep 15, 2024. Waiting for HR to schedule onboarding and initial meeting."
            )
            db.add(case)
            case_groups_created += 1
            print(f"   ✓ Created IN_PROGRESS case for Jacob Friedrichson (future hire)")
        
                # 9. Georgios Bellas-Chatzigeorgis - EB2-PERM (PERM approved, preparing I-140)
        if "georgios.bellas-chatzigeorgis@ama-inc.com" in beneficiaries:
            georgios_ben = beneficiaries["georgios.bellas-chatzigeorgis@ama-inc.com"]
            case = CaseGroup(
                beneficiary_id=georgios_ben.id,
                responsible_party_id=pm_user.id,
                created_by_manager_id=georgios_ben.user.reports_to_id,
                law_firm_id=law_firm.id if law_firm else None,
                approval_status=ApprovalStatus.PM_APPROVED,
                approved_by_pm_id=pm_user.id,
                pm_approval_date=date(2024, 1, 10),
                pathway_type=PathwayType.EB2_PERM,
                case_number="ASSESS-EB2-2024-009",
                status=CaseStatus.IN_PROGRESS,
                priority=PetitionPriority.HIGH,
                case_started_date=date(2024, 1, 15),
                target_completion_date=date(2025, 12, 31),
                case_completed_date=None,
                notes="PERM approved on Sep 15, 2024. Currently preparing I-140 documents with Goel & Anderson."
            )
            db.add(case)
            case_groups_created += 1
            print(f"   ✓ Created IN_PROGRESS case for Georgios Bellas-Chatzigeorgis (EB2-PERM, preparing I-140)")
        
        # ==========================================
        # PENDING PM APPROVAL (status=PENDING)
        # ==========================================
        
        # 8. Brandon Lowe - In approval stage for EB2-NIW
        if "brandon.lowe@ama-inc.com" in beneficiaries:
            brandon_ben = beneficiaries["brandon.lowe@ama-inc.com"]
            case = CaseGroup(
                beneficiary_id=brandon_ben.id,
                responsible_party_id=pm_user.id,
                created_by_manager_id=brandon_ben.user.reports_to_id,
                law_firm_id=law_firm.id if law_firm else None,
                approval_status=ApprovalStatus.PENDING_PM_APPROVAL,
                approved_by_pm_id=None,
                pm_approval_date=None,
                pathway_type=PathwayType.EB2_NIW,
                case_number="ASSESS-EB2-2024-010",
                status=CaseStatus.PENDING,
                priority=PetitionPriority.MEDIUM,
                case_started_date=None,
                target_completion_date=date(2025, 12, 31),
                case_completed_date=None,
                notes="Submitted for PM approval on Oct 25, 2024. Awaiting decision."
            )
            db.add(case)
            case_groups_created += 1
            print(f"   ✓ Created PENDING case for Brandon Lowe (awaiting PM approval)")
        
        # 11. Timothy Chau - Marriage-based GC (PM approved but not started)
        if "timothy.chau@ama-inc.com" in beneficiaries:
            timothy_ben = beneficiaries["timothy.chau@ama-inc.com"]
            case = CaseGroup(
                beneficiary_id=timothy_ben.id,
                responsible_party_id=pm_user.id,
                created_by_manager_id=timothy_ben.user.reports_to_id,
                law_firm_id=law_firm.id if law_firm else None,
                approval_status=ApprovalStatus.PM_APPROVED,
                approved_by_pm_id=pm_user.id,
                pm_approval_date=date(2024, 10, 30),
                pathway_type=PathwayType.MARRIAGE_BASED,
                case_number="ASSESS-MARRIAGE-2024-011",
                status=CaseStatus.IN_PROGRESS,
                priority=PetitionPriority.MEDIUM,
                case_started_date=None,  # Not started yet
                target_completion_date=date(2025, 12, 31),
                case_completed_date=None,
                notes="PM approved on Oct 30, 2024. Marriage-based green card application (I-130 + I-485). Will proceed forward."
            )
            db.add(case)
            case_groups_created += 1
            print(f"   ✓ Created IN_PROGRESS case for Timothy Chau (Marriage-based GC, PM approved)")
        
        # ==========================================
        # DRAFT CASES (status=PLANNING)
        # ==========================================
        
        # 10. Tove Aagen - Draft stage EB2-NIW
        if "tove.aagren@ama-inc.com" in beneficiaries:
            tove_ben = beneficiaries["tove.aagren@ama-inc.com"]
            case = CaseGroup(
                beneficiary_id=tove_ben.id,
                responsible_party_id=pm_user.id,
                created_by_manager_id=tove_ben.user.reports_to_id,
                law_firm_id=law_firm.id if law_firm else None,
                approval_status=ApprovalStatus.DRAFT,
                approved_by_pm_id=None,
                pm_approval_date=None,
                pathway_type=PathwayType.EB2_NIW,
                case_number="ASSESS-EB2-2024-012",
                status=CaseStatus.PLANNING,
                priority=PetitionPriority.LOW,
                case_started_date=None,
                target_completion_date=date(2026, 6, 30),
                case_completed_date=None,
                notes="Draft case. Initial assessment in progress."
            )
            db.add(case)
            case_groups_created += 1
            print(f"   ✓ Created DRAFT case for Tove Aagen")
        
        # 11. David Garcia Perez - Draft stage EB2-NIW
        if "david.garciaperez@ama-inc.com" in beneficiaries:
            david_gar_ben = beneficiaries["david.garciaperez@ama-inc.com"]
            case = CaseGroup(
                beneficiary_id=david_gar_ben.id,
                responsible_party_id=pm_user.id,
                created_by_manager_id=david_gar_ben.user.reports_to_id,
                law_firm_id=law_firm.id if law_firm else None,
                approval_status=ApprovalStatus.DRAFT,
                approved_by_pm_id=None,
                pm_approval_date=None,
                pathway_type=PathwayType.EB2_NIW,
                case_number="ASSESS-EB2-2024-013",
                status=CaseStatus.PLANNING,
                priority=PetitionPriority.LOW,
                case_started_date=None,
                target_completion_date=date(2026, 6, 30),
                case_completed_date=None,
                notes="Draft case. Initial assessment in progress."
            )
            db.add(case)
            case_groups_created += 1
            print(f"   ✓ Created DRAFT case for David Garcia Perez")
        
        db.commit()
        print(f"\n✅ ASSESS case groups seeded successfully!")
        print(f"   Case groups created: {case_groups_created}")
        print(f"   Breakdown:")
        print(f"     - 4 COMPLETED (Gerrit, Bhaskaran, Arnaud, Victor - all have LPR)")
        print(f"     - 6 IN_PROGRESS PM_APPROVED (Luis, Kiran, David Craig, Jacob, Georgios, Timothy)")
        print(f"     - 1 PENDING_PM_APPROVAL (Brandon)")
        print(f"     - 2 DRAFT (Tove, David Garcia Perez)")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding case groups: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_case_groups()
