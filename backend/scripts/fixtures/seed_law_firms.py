#!/usr/bin/env python3
"""
Seed law firms into the database.
Adds sample immigration law firms.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.core.database import SessionLocal
from app.models.law_firm import LawFirm


def seed_law_firms():
    """Seed law firms into database."""
    db = SessionLocal()
    
    try:
        print("\n📋 Seeding law firms...")
        
        # Check if law firms already exist
        existing = db.query(LawFirm).count()
        if existing > 0:
            print(f"   ⚠️  {existing} law firms already exist. Skipping...")
            return True
        
        law_firms = [
            LawFirm(
                name='Goel And Anderson Corporate Immigration ',
                contact_person='Shiv Singh',
                email='shiv.singh@goellaw.com',
                phone='(703) 796-9898',
                is_preferred_vendor=False,
                performance_rating='Good',
                notes='Used to be only immigration firm for AMA, in re-consideration phase'
            ),
            LawFirm(
                name='Jackson Lewis ',
                contact_person='John E. Exner, IV',
                email='john.exner@jacksonlewis.com',
                phone='(213) 337-3837',
                is_preferred_vendor=True,
                performance_rating='TBD',
                notes='TBD'
            ),
        ]
        
        db.add_all(law_firms)
        db.commit()
        
        print(f"   ✓ Created {len(law_firms)} law firms")
        for firm in law_firms:
            print(f"     - {firm.name} (Contact: {firm.contact_person})")
        
        print("\n✅ Law firms seeded successfully!")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error seeding law firms: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = seed_law_firms()
    sys.exit(0 if success else 1)
