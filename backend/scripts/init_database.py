#!/usr/bin/env python3
"""
Initialize database from scratch.
- Deletes existing database file
- Creates all tables via SQLAlchemy (development) OR Alembic (production-like)
- Optionally resets Alembic migration history
- Creates initial admin user from .env

Usage:
    python scripts/init_database.py                    # Dev mode: Direct table creation
    python scripts/init_database.py --use-alembic      # Production-like: Use migrations
    python scripts/init_database.py --reset-alembic    # Reset Alembic + create fresh migration

This is for development. Production should only use Alembic migrations.
"""

import sys
import os
import subprocess
import shutil
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import engine, Base, SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.core.config import settings

# Import all models to ensure they're registered with Base
from app.models import (
    user, contract, department, beneficiary, dependent,
    petition, law_firm, case_group, milestone, rfe,
    audit, notification, settings as settings_model, todo
)
# Note: visa module removed - replaced by petition module


def reset_alembic():
    """Reset Alembic migration history (development only)."""
    print("\n🗑️  Resetting Alembic migration history...")
    
    backend_dir = Path(__file__).parent.parent
    versions_dir = backend_dir / "alembic" / "versions"
    
    if versions_dir.exists():
        # Remove all migration files except __init__.py
        for file in versions_dir.glob("*.py"):
            if file.name != "__init__.py":
                print(f"   Removing migration: {file.name}")
                file.unlink()
        
        # Remove __pycache__
        pycache = versions_dir / "__pycache__"
        if pycache.exists():
            shutil.rmtree(pycache)
        
        print("   ✓ Alembic history reset")
    else:
        print("   ⚠️  Alembic versions directory not found")
    
    return True


def create_fresh_migration():
    """Create a fresh Alembic migration (production-like setup)."""
    print("\n📝 Creating fresh Alembic migration...")
    
    backend_dir = Path(__file__).parent.parent
    
    try:
        # Generate migration
        result = subprocess.run(
            ["alembic", "revision", "--autogenerate", "-m", "Initial schema"],
            cwd=backend_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("   ✓ Migration created")
            # Print migration file name if present in output
            for line in result.stdout.split('\n'):
                if 'Generating' in line or 'versions/' in line:
                    print(f"   {line.strip()}")
            return True
        else:
            print(f"   ❌ Migration creation failed: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("   ❌ Alembic not found. Install it: pip install alembic")
        return False


def apply_alembic_migrations():
    """Apply Alembic migrations to database."""
    print("\n📦 Applying Alembic migrations...")
    
    backend_dir = Path(__file__).parent.parent
    
    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=backend_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("   ✓ Migrations applied")
            return True
        else:
            print(f"   ❌ Migration failed: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("   ❌ Alembic not found. Install it: pip install alembic")
        return False


def init_database(use_alembic=False, reset_alembic_history=False):
    """
    Initialize database from scratch.
    
    Args:
        use_alembic: If True, use Alembic migrations instead of direct table creation
        reset_alembic_history: If True, reset Alembic and create fresh migration
    """
    
    print("\n🔄 Initializing database...")
    print(f"   Mode: {'Alembic migrations' if use_alembic or reset_alembic_history else 'Direct table creation (dev)'}")
    
    # Get database file path
    db_path = settings.DB_NAME
    
    # Delete existing database
    if os.path.exists(db_path):
        print(f"   Deleting existing database: {db_path}")
        os.remove(db_path)
        # Also remove WAL files
        for ext in ['-shm', '-wal']:
            wal_file = f"{db_path}{ext}"
            if os.path.exists(wal_file):
                os.remove(wal_file)
    
    # Handle Alembic reset if requested
    if reset_alembic_history:
        if not reset_alembic():
            return False
        if not create_fresh_migration():
            return False
        if not apply_alembic_migrations():
            return False
    elif use_alembic:
        # Use existing migrations
        if not apply_alembic_migrations():
            return False
    else:
        # Development mode: Direct table creation
        alembic_path = Path(__file__).parent.parent / "alembic"
        if alembic_path.exists():
            print(f"   Note: Alembic exists but using direct table creation (dev mode)")
        
        print("   Creating all tables...")
        Base.metadata.create_all(bind=engine)
        print("   ✓ Tables created")
    
    # Create admin user
    db = SessionLocal()
    try:
        print("\n👤 Creating admin user...")
        admin = User(
            email=settings.INITIAL_ADMIN_EMAIL,
            hashed_password=get_password_hash(settings.INITIAL_ADMIN_PASSWORD),
            full_name=settings.INITIAL_ADMIN_NAME,
            role=UserRole.ADMIN,
            is_active=True,
            force_password_change=False
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print(f"   ✓ Admin user created")
        print(f"   Email: {admin.email}")
        print(f"   Password: {settings.INITIAL_ADMIN_PASSWORD}")
        print(f"   ID: {admin.id}")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error creating admin user: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Initialize AMA-IMPACT database from scratch",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/init_database.py                    # Dev: Direct table creation
  python scripts/init_database.py --use-alembic      # Use existing Alembic migrations
  python scripts/init_database.py --reset-alembic    # Reset Alembic + fresh migration

Note: --reset-alembic is for development only. Production should use proper migrations.
        """
    )
    
    parser.add_argument(
        '--use-alembic',
        action='store_true',
        help='Use Alembic migrations instead of direct table creation'
    )
    
    parser.add_argument(
        '--reset-alembic',
        action='store_true',
        help='Reset Alembic history and create fresh migration (dev only)'
    )
    
    args = parser.parse_args()
    
    # Initialize database
    success = init_database(
        use_alembic=args.use_alembic,
        reset_alembic_history=args.reset_alembic
    )
    
    if success:
        print("\n✅ Database initialized successfully!")
        print(f"   Database: {settings.DB_NAME}")
        print(f"\n   Next steps:")
        print(f"   1. Run: # NOTE: seed_visa_types.py removed - PetitionType is now an enum in the model")
        print(f"   2. Run: python scripts/fixtures/seed_contracts.py")
        print(f"   3. Run: python scripts/fixtures/seed_law_firms.py")
        print(f"   4. Run: python scripts/fixtures/seed_development_data.py")
        print(f"   Or use: python scripts/setup_dev_environment.py (runs all)")
    
    sys.exit(0 if success else 1)
