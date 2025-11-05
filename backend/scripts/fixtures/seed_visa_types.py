#!/usr/bin/env python3
"""
Seed visa types into the database.
Adds standard visa type categories used for applications.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.core.database import SessionLocal
from app.models.visa import VisaType


def seed_visa_types():
    """Seed visa types into database."""
    db = SessionLocal()
    
    try:
        print("\n📋 Seeding visa types...")
        
        # Check if visa types already exist
        existing = db.query(VisaType).count()
        if existing > 0:
            print(f"   ⚠️  {existing} visa types already exist. Skipping...")
            return True
        
        visa_types = [
            VisaType(
                code='H1B',
                name='H-1B Specialty Occupation',
                description='Temporary work visa for specialty occupations',
                default_renewal_lead_days='180'
            ),
            VisaType(
                code='L1',
                name='L-1 Intracompany Transfer',
                description='Transfer within multinational company',
                default_renewal_lead_days='180'
            ),
            VisaType(
                code='O1',
                name='O-1 Extraordinary Ability',
                description='For individuals with extraordinary ability',
                default_renewal_lead_days='180'
            ),
            VisaType(
                code='TN',
                name='TN NAFTA Professional',
                description='For Canadian and Mexican professionals',
                default_renewal_lead_days='90'
            ),
            VisaType(
                code='EB1A',
                name='EB-1A Extraordinary Ability',
                description='Green Card for extraordinary ability',
                default_renewal_lead_days='365'
            ),
            VisaType(
                code='EB1B',
                name='EB-1B Outstanding Researcher',
                description='Green Card for outstanding researchers',
                default_renewal_lead_days='365'
            ),
            VisaType(
                code='EB2',
                name='EB-2 Advanced Degree',
                description='Green Card for advanced degree holders',
                default_renewal_lead_days='365'
            ),
            VisaType(
                code='EB2NIW',
                name='EB-2 National Interest Waiver',
                description='Green Card with national interest waiver',
                default_renewal_lead_days='365'
            ),
            VisaType(
                code='PERM',
                name='PERM Labor Certification',
                description='Labor certification for employment-based green card',
                default_renewal_lead_days='180'
            ),
            VisaType(
                code='OPT',
                name='Optional Practical Training',
                description='Work authorization for F-1 students',
                default_renewal_lead_days='90'
            ),
            VisaType(
                code='EAD',
                name='Employment Authorization Document',
                description='Work permit',
                default_renewal_lead_days='120'
            ),
            VisaType(
                code='GREEN_CARD',
                name='Permanent Resident Card',
                description='Permanent residence status',
                default_renewal_lead_days='365'
            ),
            VisaType(
                code='I140',
                name='I-140 Immigrant Petition',
                description='Immigrant Worker Petition',
                default_renewal_lead_days='180'
            ),
            VisaType(
                code='I485',
                name='I-485 Adjustment of Status',
                description='Application to Register Permanent Residence',
                default_renewal_lead_days='180'
            ),
        ]
        
        db.add_all(visa_types)
        db.commit()
        
        print(f"   ✓ Created {len(visa_types)} visa types")
        for vt in visa_types:
            print(f"     - {vt.code}: {vt.name}")
        
        print("\n✅ Visa types seeded successfully!")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error seeding visa types: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = seed_visa_types()
    sys.exit(0 if success else 1)
