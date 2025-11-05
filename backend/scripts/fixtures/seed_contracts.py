#!/usr/bin/env python3
"""
Seed contracts into the database.
Adds ASSESS and RESESS contracts.
"""

import sys
from pathlib import Path
from datetime import date

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.core.database import SessionLocal
from app.models.contract import Contract, ContractStatus


def seed_contracts():
    """Seed contracts into database."""
    db = SessionLocal()
    
    try:
        print("\n📋 Seeding contracts...")
        
        # Check if contracts already exist
        existing = db.query(Contract).count()
        if existing > 0:
            print(f"   ⚠️  {existing} contracts already exist. Skipping...")
            return True
        
        contracts = [
            Contract(
                name='Aircraft and Spaceflight Systems Engineering Support Services (ASSESS)',
                code='ASSESS',
                start_date=date(2025, 4, 1),
                end_date=date(2030,  3, 31),
                status=ContractStatus.ACTIVE,
                client_name='NASA ARC',
                description='Under ASSESS AMA supports scientific research, engineering design, analysis, and development'
            ),
            Contract(
                name='Research, Science & Engineering Services (RSES)',
                code='RSES',
                start_date=date(2024, 1, 1),
                end_date=date(2026, 12, 31),
                status=ContractStatus.ACTIVE,
                client_name='NASA LaRC',
                description='Under RSES AMA supports autonomous systems, acoustics, aerosciences, avionics and scre systems, systems design, ....'
            ),
        ]
        
        db.add_all(contracts)
        db.commit()
        
        print(f"   ✓ Created {len(contracts)} contracts")
        for c in contracts:
            print(f"     - {c.code}: {c.name}")
        
        print("\n✅ Contracts seeded successfully!")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error seeding contracts: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = seed_contracts()
    sys.exit(0 if success else 1)
