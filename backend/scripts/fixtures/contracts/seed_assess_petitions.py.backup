"""
Seed ASSESS petitions and milestones (Step 3 of 3).
Creates Petition records with complete petition sets (I-140 + I-485 + I-765 + I-131)
and two-level Milestones (case-level + petition-level) for realistic case tracking.

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
        # COMPLETED CASES
        # ==========================================
        
        # 1. Gerrit-Daniel Stich - Completed EB2-NIW (ASSESS-EB2-2021-001)
        if "ASSESS-EB2-2021-001" in case_groups:
            cg = case_groups["ASSESS-EB2-2021-001"]
            visa_app = VisaApplication(
                beneficiary_id=cg.beneficiary_id,
                case_group_id=cg.id,
                visa_type_id=eb2niw_type.id,
                created_by=pm_user.id,
                law_firm_id=law_firm.id if law_firm else None,
                responsible_party_id=pm_user.id,
                attorney_name="Sarah Immigration Attorney",
                attorney_email="sarah@visalawgroup.com",
                visa_type=VisaTypeEnum.EB2NIW,
                petition_type="I-140",
                status=VisaStatus.APPROVED,
                case_status=VisaCaseStatus.FINALIZED,
                priority=VisaPriority.MEDIUM,
                current_stage="Green Card Received",
                filing_date=date(2021, 2, 15),
                approval_date=date(2021, 10, 20),
                receipt_number="LIN2190012345",
                company_case_id="ASSESS-EB2-2021-001",
                premium_processing=False,
                filing_fee="$700",
                attorney_fee="$8,500",
                notes="Successfully completed EB2-NIW case. Green card received."
            )
            db.add(visa_app)
            db.flush()
            visa_apps_created += 1
            
            # Add milestones
            milestones = [
                (MilestoneType.CASE_OPENED, date(2021, 1, 15), "Initial consultation completed"),
                (MilestoneType.DOCUMENTS_REQUESTED, date(2021, 1, 20), "Document checklist provided to beneficiary"),
                (MilestoneType.DOCUMENTS_SUBMITTED, date(2021, 2, 10), "All documents collected and reviewed"),
                (MilestoneType.FILED_WITH_USCIS, date(2021, 2, 15), "I-140 petition filed with USCIS"),
                (MilestoneType.APPROVED, date(2021, 10, 20), "I-140 approved"),
                (MilestoneType.CASE_CLOSED, date(2021, 11, 20), "Green card received"),
            ]
            for m_type, m_date, m_desc in milestones:
                milestone = ApplicationMilestone(
                    visa_application_id=visa_app.id,
                    created_by=pm_user.id,
                    milestone_type=m_type,
                    milestone_date=m_date,
                    description=m_desc
                )
                db.add(milestone)
                milestones_created += 1
            
            print(f"   ✓ Created visa app + {len(milestones)} milestones for Gerrit-Daniel Stich (COMPLETED)")
        
        # 2. Victor Sousa - Completed EB2-NIW (ASSESS-EB2-2022-002)
        if "ASSESS-EB2-2022-002" in case_groups:
            cg = case_groups["ASSESS-EB2-2022-002"]
            visa_app = VisaApplication(
                beneficiary_id=cg.beneficiary_id,
                case_group_id=cg.id,
                visa_type_id=eb2niw_type.id,
                created_by=pm_user.id,
                law_firm_id=law_firm.id if law_firm else None,
                responsible_party_id=pm_user.id,
                attorney_name="Sarah Immigration Attorney",
                attorney_email="sarah@visalawgroup.com",
                visa_type=VisaTypeEnum.EB2NIW,
                petition_type="I-140",
                status=VisaStatus.APPROVED,
                case_status=VisaCaseStatus.FINALIZED,
                priority=VisaPriority.MEDIUM,
                current_stage="Green Card Received",
                filing_date=date(2022, 4, 1),
                approval_date=date(2022, 12, 15),
                receipt_number="LIN2290023456",
                company_case_id="ASSESS-EB2-2022-002",
                premium_processing=False,
                filing_fee="$700",
                attorney_fee="$8,500",
                notes="Successfully completed EB2-NIW case. Green card received."
            )
            db.add(visa_app)
            db.flush()
            visa_apps_created += 1
            
            # Add milestones
            milestones = [
                (MilestoneType.CASE_OPENED, date(2022, 3, 1), "Initial consultation completed"),
                (MilestoneType.DOCUMENTS_REQUESTED, date(2022, 3, 5), "Document checklist provided"),
                (MilestoneType.DOCUMENTS_SUBMITTED, date(2022, 3, 25), "All documents collected"),
                (MilestoneType.FILED_WITH_USCIS, date(2022, 4, 1), "I-140 petition filed"),
                (MilestoneType.APPROVED, date(2022, 12, 15), "I-140 approved"),
                (MilestoneType.CASE_CLOSED, date(2023, 1, 15), "Green card received"),
            ]
            for m_type, m_date, m_desc in milestones:
                milestone = ApplicationMilestone(
                    visa_application_id=visa_app.id,
                    created_by=pm_user.id,
                    milestone_type=m_type,
                    milestone_date=m_date,
                    description=m_desc
                )
                db.add(milestone)
                milestones_created += 1
            
            print(f"   ✓ Created visa app + {len(milestones)} milestones for Victor Sousa (COMPLETED)")
        
        # ==========================================
        # PM_APPROVED ACTIVE CASES
        # ==========================================
        
        # 3. Luis Fernandes - I-140 received 2 weeks ago (ASSESS-EB2-2024-003)
        if "ASSESS-EB2-2024-003" in case_groups:
            cg = case_groups["ASSESS-EB2-2024-003"]
            visa_app = VisaApplication(
                beneficiary_id=cg.beneficiary_id,
                case_group_id=cg.id,
                visa_type_id=eb2niw_type.id,
                created_by=pm_user.id,
                law_firm_id=law_firm.id if law_firm else None,
                responsible_party_id=pm_user.id,
                attorney_name="Sarah Immigration Attorney",
                attorney_email="sarah@visalawgroup.com",
                visa_type=VisaTypeEnum.EB2NIW,
                petition_type="I-140",
                status=VisaStatus.APPROVED,
                case_status=VisaCaseStatus.ACTIVE,
                priority=VisaPriority.HIGH,
                current_stage="I-140 Approved - Awaiting Priority Date",
                filing_date=date(2024, 9, 1),
                approval_date=date(2024, 10, 28),
                receipt_number="LIN2490034567",
                company_case_id="ASSESS-EB2-2024-003",
                premium_processing=True,
                premium_processing_fee="$2,500",
                filing_fee="$700",
                attorney_fee="$9,000",
                notes="I-140 approved and received on Oct 28, 2024. Awaiting priority date."
            )
            db.add(visa_app)
            db.flush()
            visa_apps_created += 1
            
            # Add milestones
            milestones = [
                (MilestoneType.CASE_OPENED, date(2024, 8, 20), "Initial consultation and case strategy discussion"),
                (MilestoneType.DOCUMENTS_REQUESTED, date(2024, 8, 22), "Comprehensive document checklist sent to beneficiary"),
                (MilestoneType.DOCUMENTS_SUBMITTED, date(2024, 8, 28), "All supporting documents collected and reviewed"),
                (MilestoneType.FILED_WITH_USCIS, date(2024, 9, 1), "I-140 petition filed with premium processing"),
                (MilestoneType.APPROVED, date(2024, 10, 28), "I-140 approved! Approval notice received."),
            ]
            for m_type, m_date, m_desc in milestones:
                milestone = ApplicationMilestone(
                    visa_application_id=visa_app.id,
                    created_by=pm_user.id,
                    milestone_type=m_type,
                    milestone_date=m_date,
                    description=m_desc
                )
                db.add(milestone)
                milestones_created += 1
            
            print(f"   ✓ Created visa app + {len(milestones)} milestones for Luis Fernandes (I-140 APPROVED)")
        
        # 4. Kiran Ravikumar - I-140 just filed (ASSESS-EB2-2024-004)
        if "ASSESS-EB2-2024-004" in case_groups:
            cg = case_groups["ASSESS-EB2-2024-004"]
            visa_app = VisaApplication(
                beneficiary_id=cg.beneficiary_id,
                case_group_id=cg.id,
                visa_type_id=eb2niw_type.id,
                created_by=pm_user.id,
                law_firm_id=law_firm.id if law_firm else None,
                responsible_party_id=pm_user.id,
                attorney_name="Sarah Immigration Attorney",
                attorney_email="sarah@visalawgroup.com",
                visa_type=VisaTypeEnum.EB2NIW,
                petition_type="I-140",
                status=VisaStatus.IN_PROGRESS,
                case_status=VisaCaseStatus.ACTIVE,
                priority=VisaPriority.HIGH,
                current_stage="I-140 Filed - Awaiting Receipt Notice",
                filing_date=date(2024, 11, 1),
                receipt_number=None,  # Not received yet
                company_case_id="ASSESS-EB2-2024-004",
                premium_processing=True,
                premium_processing_fee="$2,500",
                filing_fee="$700",
                attorney_fee="$9,000",
                notes="I-140 filed on Nov 1, 2024. Awaiting USCIS receipt notice."
            )
            db.add(visa_app)
            db.flush()
            visa_apps_created += 1
            
            # Add milestones
            milestones = [
                (MilestoneType.CASE_OPENED, date(2024, 9, 15), "Initial consultation completed"),
                (MilestoneType.DOCUMENTS_REQUESTED, date(2024, 9, 18), "Document checklist provided"),
                (MilestoneType.DOCUMENTS_SUBMITTED, date(2024, 10, 25), "All documents collected and petition prepared"),
                (MilestoneType.FILED_WITH_USCIS, date(2024, 11, 1), "I-140 petition filed with premium processing"),
            ]
            for m_type, m_date, m_desc in milestones:
                milestone = ApplicationMilestone(
                    visa_application_id=visa_app.id,
                    created_by=pm_user.id,
                    milestone_type=m_type,
                    milestone_date=m_date,
                    description=m_desc
                )
                db.add(milestone)
                milestones_created += 1
            
            print(f"   ✓ Created visa app + {len(milestones)} milestones for Kiran Ravikumar (I-140 FILED)")
        
        # 5. David Craig Penner - TN renewal (ASSESS-TN-2024-005)
        if "ASSESS-TN-2024-005" in case_groups:
            cg = case_groups["ASSESS-TN-2024-005"]
            visa_app = VisaApplication(
                beneficiary_id=cg.beneficiary_id,
                case_group_id=cg.id,
                visa_type_id=tn_type.id,
                created_by=pm_user.id,
                law_firm_id=law_firm.id if law_firm else None,
                responsible_party_id=pm_user.id,
                attorney_name="Sarah Immigration Attorney",
                attorney_email="sarah@visalawgroup.com",
                visa_type=VisaTypeEnum.TN,
                petition_type="TN Renewal",
                status=VisaStatus.DRAFT,
                case_status=VisaCaseStatus.UPCOMING,
                priority=VisaPriority.MEDIUM,
                current_stage="Awaiting HR to Schedule Initial Meeting",
                filing_date=None,
                company_case_id="ASSESS-TN-2024-005",
                premium_processing=False,
                filing_fee="$50",
                attorney_fee="$2,500",
                notes="PM approved on Oct 1, 2024. Waiting for HR to schedule initial consultation meeting."
            )
            db.add(visa_app)
            db.flush()
            visa_apps_created += 1
            
            # No milestones yet - waiting to start
            print(f"   ✓ Created visa app for David Craig Penner (WAITING TO START)")
        
        # 6. Jacob Friedrichson - Future hire H1B (ASSESS-H1B-2024-006)
        if "ASSESS-H1B-2024-006" in case_groups:
            cg = case_groups["ASSESS-H1B-2024-006"]
            visa_app = VisaApplication(
                beneficiary_id=cg.beneficiary_id,
                case_group_id=cg.id,
                visa_type_id=h1b_type.id,
                created_by=pm_user.id,
                law_firm_id=law_firm.id if law_firm else None,
                responsible_party_id=pm_user.id,
                attorney_name="Sarah Immigration Attorney",
                attorney_email="sarah@visalawgroup.com",
                visa_type=VisaTypeEnum.H1B,
                petition_type="I-129",
                status=VisaStatus.DRAFT,
                case_status=VisaCaseStatus.UPCOMING,
                priority=VisaPriority.HIGH,
                current_stage="Awaiting Onboarding and HR Meeting",
                filing_date=None,
                company_case_id="ASSESS-H1B-2024-006",
                premium_processing=False,
                filing_fee="$460",
                attorney_fee="$3,500",
                notes="Future hire. PM approved on Sep 15, 2024. Waiting for HR to schedule onboarding."
            )
            db.add(visa_app)
            db.flush()
            visa_apps_created += 1
            
            # No milestones yet - future hire
            print(f"   ✓ Created visa app for Jacob Friedrichson (FUTURE HIRE)")
        
        # 7. Georgios Bellas-Chatzigeorgis - PERM approved, preparing I-140 (ASSESS-EB2-2024-007)
        if "ASSESS-EB2-2024-007" in case_groups:
            cg = case_groups["ASSESS-EB2-2024-007"]
            visa_app = VisaApplication(
                beneficiary_id=cg.beneficiary_id,
                case_group_id=cg.id,
                visa_type_id=eb2niw_type.id,
                created_by=pm_user.id,
                law_firm_id=law_firm.id if law_firm else None,
                responsible_party_id=pm_user.id,
                attorney_name="Sarah Immigration Attorney",
                attorney_email="sarah@visalawgroup.com",
                visa_type=VisaTypeEnum.EB2NIW,
                petition_type="I-140",
                status=VisaStatus.IN_PROGRESS,
                case_status=VisaCaseStatus.ACTIVE,
                priority=VisaPriority.HIGH,
                current_stage="PERM Approved - Preparing I-140 Documents",
                filing_date=None,  # Not filed yet
                receipt_number=None,
                company_case_id="ASSESS-EB2-2024-007",
                premium_processing=False,
                filing_fee="$700",
                attorney_fee="$9,000",
                notes="PERM approved on Sep 15, 2024. Currently preparing I-140 documents."
            )
            db.add(visa_app)
            db.flush()
            visa_apps_created += 1
            
            # Add milestones
            milestones = [
                (MilestoneType.CASE_OPENED, date(2024, 1, 15), "PERM case initiated"),
                (MilestoneType.DOCUMENTS_REQUESTED, date(2024, 2, 1), "Labor certification documents requested"),
                (MilestoneType.DOCUMENTS_SUBMITTED, date(2024, 3, 15), "PERM application submitted to DOL"),
                (MilestoneType.APPROVED, date(2024, 9, 15), "PERM approved by Department of Labor"),
                (MilestoneType.DOCUMENTS_REQUESTED, date(2024, 10, 1), "I-140 documents requested from beneficiary"),
            ]
            for m_type, m_date, m_desc in milestones:
                milestone = ApplicationMilestone(
                    visa_application_id=visa_app.id,
                    created_by=pm_user.id,
                    milestone_type=m_type,
                    milestone_date=m_date,
                    description=m_desc
                )
                db.add(milestone)
                milestones_created += 1
            
            print(f"   ✓ Created visa app + {len(milestones)} milestones for Georgios (PERM APPROVED)")
        
        # ==========================================
        # PENDING PM APPROVAL
        # ==========================================
        
        # 8. Brandon Lowe - Pending approval (ASSESS-EB2-2024-008)
        if "ASSESS-EB2-2024-008" in case_groups:
            cg = case_groups["ASSESS-EB2-2024-008"]
            visa_app = VisaApplication(
                beneficiary_id=cg.beneficiary_id,
                case_group_id=cg.id,
                visa_type_id=eb2niw_type.id,
                created_by=cg.created_by_manager_id,
                law_firm_id=law_firm.id if law_firm else None,
                responsible_party_id=pm_user.id,
                attorney_name="Sarah Immigration Attorney",
                attorney_email="sarah@visalawgroup.com",
                visa_type=VisaTypeEnum.EB2NIW,
                petition_type="I-140",
                status=VisaStatus.DRAFT,
                case_status=VisaCaseStatus.UPCOMING,
                priority=VisaPriority.MEDIUM,
                current_stage="Pending PM Approval",
                filing_date=None,
                company_case_id="ASSESS-EB2-2024-008",
                premium_processing=False,
                filing_fee="$700",
                attorney_fee="$9,000",
                notes="Submitted for PM approval on Oct 25, 2024. Awaiting decision."
            )
            db.add(visa_app)
            db.flush()
            visa_apps_created += 1
            
            # Add initial milestone
            milestone = ApplicationMilestone(
                visa_application_id=visa_app.id,
                created_by=cg.created_by_manager_id,
                milestone_type=MilestoneType.CASE_OPENED,
                milestone_date=date(2024, 10, 20),
                description="Case package submitted to PM for approval"
            )
            db.add(milestone)
            milestones_created += 1
            
            print(f"   ✓ Created visa app + 1 milestone for Brandon Lowe (PENDING APPROVAL)")
        
        # 9. Timothy Chau - Pending approval (ASSESS-EB2-2024-009)
        if "ASSESS-EB2-2024-009" in case_groups:
            cg = case_groups["ASSESS-EB2-2024-009"]
            visa_app = VisaApplication(
                beneficiary_id=cg.beneficiary_id,
                case_group_id=cg.id,
                visa_type_id=eb2niw_type.id,
                created_by=cg.created_by_manager_id,
                law_firm_id=law_firm.id if law_firm else None,
                responsible_party_id=pm_user.id,
                attorney_name="Sarah Immigration Attorney",
                attorney_email="sarah@visalawgroup.com",
                visa_type=VisaTypeEnum.EB2NIW,
                petition_type="I-140",
                status=VisaStatus.DRAFT,
                case_status=VisaCaseStatus.UPCOMING,
                priority=VisaPriority.MEDIUM,
                current_stage="Pending PM Approval",
                filing_date=None,
                company_case_id="ASSESS-EB2-2024-009",
                premium_processing=False,
                filing_fee="$700",
                attorney_fee="$9,000",
                notes="Submitted for PM approval on Oct 30, 2024. Awaiting decision."
            )
            db.add(visa_app)
            db.flush()
            visa_apps_created += 1
            
            # Add initial milestone
            milestone = ApplicationMilestone(
                visa_application_id=visa_app.id,
                created_by=cg.created_by_manager_id,
                milestone_type=MilestoneType.CASE_OPENED,
                milestone_date=date(2024, 10, 25),
                description="Case package submitted to PM for approval"
            )
            db.add(milestone)
            milestones_created += 1
            
            print(f"   ✓ Created visa app + 1 milestone for Timothy Chau (PENDING APPROVAL)")
        
        # ==========================================
        # DRAFT CASES
        # ==========================================
        
        # 10. Tove Aagen - Draft (ASSESS-EB2-2024-010)
        if "ASSESS-EB2-2024-010" in case_groups:
            cg = case_groups["ASSESS-EB2-2024-010"]
            visa_app = VisaApplication(
                beneficiary_id=cg.beneficiary_id,
                case_group_id=cg.id,
                visa_type_id=eb2niw_type.id,
                created_by=cg.created_by_manager_id,
                law_firm_id=law_firm.id if law_firm else None,
                responsible_party_id=pm_user.id,
                visa_type=VisaTypeEnum.EB2NIW,
                petition_type="I-140",
                status=VisaStatus.DRAFT,
                case_status=VisaCaseStatus.UPCOMING,
                priority=VisaPriority.LOW,
                current_stage="Initial Assessment",
                filing_date=None,
                company_case_id="ASSESS-EB2-2024-010",
                premium_processing=False,
                filing_fee="$700",
                attorney_fee="$9,000",
                notes="Draft case. Initial assessment in progress."
            )
            db.add(visa_app)
            db.flush()
            visa_apps_created += 1
            
            print(f"   ✓ Created visa app for Tove Aagen (DRAFT)")
        
        # 11. David Garcia Perez - Draft (ASSESS-EB2-2024-011)
        if "ASSESS-EB2-2024-011" in case_groups:
            cg = case_groups["ASSESS-EB2-2024-011"]
            visa_app = VisaApplication(
                beneficiary_id=cg.beneficiary_id,
                case_group_id=cg.id,
                visa_type_id=eb2niw_type.id,
                created_by=cg.created_by_manager_id,
                law_firm_id=law_firm.id if law_firm else None,
                responsible_party_id=pm_user.id,
                visa_type=VisaTypeEnum.EB2NIW,
                petition_type="I-140",
                status=VisaStatus.DRAFT,
                case_status=VisaCaseStatus.UPCOMING,
                priority=VisaPriority.LOW,
                current_stage="Initial Assessment",
                filing_date=None,
                company_case_id="ASSESS-EB2-2024-011",
                premium_processing=False,
                filing_fee="$700",
                attorney_fee="$9,000",
                notes="Draft case. Initial assessment in progress."
            )
            db.add(visa_app)
            db.flush()
            visa_apps_created += 1
            
            print(f"   ✓ Created visa app for David Garcia Perez (DRAFT)")
        
        db.commit()
        print(f"\n✅ ASSESS visa applications and milestones seeded successfully!")
        print(f"   Visa applications created: {visa_apps_created}")
        print(f"   Milestones created: {milestones_created}")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding visa applications: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    seed_assess_visa_apps()
