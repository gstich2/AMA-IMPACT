#!/usr/bin/env python3
"""
Setup complete development environment.
Runs all fixtures in correct order:
1. Initialize database (drop + recreate + admin)
2. Seed visa types
3. Seed contracts
4. Seed law firms
5. Seed development data

Usage:
    python scripts/setup_dev_environment.py
    
Or run individual scripts:
    python scripts/init_database.py
    # NOTE: seed_visa_types.py removed - PetitionType is now an enum in the model
    python scripts/fixtures/contracts/seed_assess.py
    python scripts/fixtures/contracts/seed_rses.py
    python scripts/fixtures/seed_law_firms.py
    python scripts/fixtures/seed_development_data.py
"""

import sys
import subprocess
from pathlib import Path

# Get script directory
SCRIPTS_DIR = Path(__file__).parent


def run_script(script_path, description):
    """Run a Python script and return success status."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"{'='*60}")
    
    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=SCRIPTS_DIR.parent,  # Run from backend directory
        capture_output=False
    )
    
    if result.returncode != 0:
        print(f"\n❌ Failed: {description}")
        return False
    
    return True


def setup_dev_environment():
    """Setup complete development environment."""
    
    print("\n" + "="*60)
    print("AMA-IMPACT Development Environment Setup")
    print("="*60)
    
    scripts = [
        (SCRIPTS_DIR / "init_database.py", "Initialize Database"),
        # Note: seed_visa_types.py removed - Petition model uses PetitionType enum instead
        (SCRIPTS_DIR / "fixtures" / "contracts" / "seed_assess.py", "Seed ASSESS Contract"),
        (SCRIPTS_DIR / "fixtures" / "contracts" / "seed_rses.py", "Seed RSES Contract"),
        (SCRIPTS_DIR / "fixtures" / "seed_law_firms.py", "Seed Law Firms"),
        (SCRIPTS_DIR / "fixtures" / "contracts" / "seed_assess_beneficiary_users.py", "Seed ASSESS Beneficiary Users"),
        (SCRIPTS_DIR / "fixtures" / "contracts" / "seed_assess_case_groups.py", "Seed ASSESS Case Groups"),
        (SCRIPTS_DIR / "fixtures" / "contracts" / "seed_assess_petitions.py", "Seed ASSESS Petitions"),
        (SCRIPTS_DIR / "fixtures" / "seed_development_data.py", "Seed Development Test Data"),
    ]
    
    for script_path, description in scripts:
        if not run_script(script_path, description):
            print(f"\n❌ Setup failed at: {description}")
            print(f"   You can re-run this script or run individual fixtures.")
            return False
    
    print("\n" + "="*60)
    print("✅ DEVELOPMENT ENVIRONMENT SETUP COMPLETE!")
    print("="*60)
    print("\nYour database is ready with:")
    print("  • Admin user: admin@ama-impact.com / Admin123!")
    print("  • ASSESS & RSES contracts with managers")
    print("  • 3 law firms")
    print("  • 13 ASSESS departments (4 L1 + 9 L2) + 2 RSES departments")
    print("  • 13 ASSESS beneficiaries (11 employees + 2 future hires)")
    print("  • 13 ASSESS case groups (4 completed LPR, 6 active, 1 pending, 2 draft)")
    print("  • ~35 ASSESS petitions (I-140, I-485, I-765, I-131, etc.)")
    print("  • ~60 milestones (case-level + petition-level)")
    print("  • 5 test scenarios (RFE, Denial, Concurrent, Family, Expired)")
    print("  • 3 test staff users (HR, PM, Tech Lead)")
    
    print("\nNext steps:")
    print("  1. Start server: cd backend && uvicorn app.main:app --reload --port 7001")
    print("  2. Access API docs: http://localhost:7001/docs")
    print("  3. Login as admin or manager:")
    print("     Admin: admin@ama-impact.com / Admin123!")
    print("     PM: pm.assess@ama-impact.com / TempPassword123!")
    print("  4. Test users:")
    print("     HR: hr@ama-impact.com / HR123!")
    print("     Test beneficiaries: test.rfe@example.com / Test123!")
    
    return True


if __name__ == "__main__":
    success = setup_dev_environment()
    sys.exit(0 if success else 1)
