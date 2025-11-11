# Backend Scripts

Python-based database and server management scripts.

## Quick Start

### Development Setup (Recommended)
```bash
cd backend

# One-command setup: Creates DB + seeds all fixture data
python scripts/setup_dev_environment.py
```

This runs:
1. `init_database.py` - Creates schema + admin user
2. `seed_visa_types.py` - Loads visa type reference data
3. `seed_contracts.py` - Creates ASSESS & RSES contracts
4. `seed_law_firms.py` - Adds law firms (Jackson Lewis, Goel And Anderson)
5. `seed_development_data.py` - Loads realistic test users, beneficiaries, visas, case groups, todos

### Manual Development Setup
```bash
cd backend

# Initialize database
python scripts/init_database.py

# Load fixtures individually
python scripts/fixtures/seed_visa_types.py
python scripts/fixtures/seed_contracts.py
python scripts/fixtures/seed_law_firms.py
python scripts/fixtures/seed_development_data.py

# Start server (auto-reload enabled)
./start_server.sh
```

### Production Setup
```bash
cd backend

# Create production config
cp .env.production.example .env.production
nano .env.production  # Configure: SECRET_KEY, DB_NAME, admin credentials

# Point .env to production config
ln -sf .env.production .env

# Initialize database with Alembic (production-like)
python scripts/init_database.py --use-alembic

# Start server (no auto-reload)
./start_server.sh
```

## Environment Configuration

The active `.env` file controls everything. Switch environments by changing the symlink:

```bash
cd backend

# Development
ln -sf .env.development .env

# Production  
ln -sf .env.production .env
```

**Key Variables:**
- `DB_NAME` - Database file (devel.db or ama-impact.db)
- `INITIAL_ADMIN_EMAIL` - Admin user email
- `INITIAL_ADMIN_PASSWORD` - Admin initial password
- `INITIAL_ADMIN_NAME` - Admin display name
- `DEBUG` - Enables auto-reload (True/False)
- `SECRET_KEY` - JWT signing key (⚠️ generate new for production!)

## Scripts

### `init_database.py`
Initializes or resets database from scratch.

**Usage:**
```bash
python scripts/init_database.py                    # Dev: Direct table creation
python scripts/init_database.py --use-alembic      # Use existing Alembic migrations
python scripts/init_database.py --reset-alembic    # Reset Alembic + create fresh migration
```

**What it does:**
- Deletes existing database file (+ WAL files)
- Creates schema: Direct (dev) OR via Alembic migrations (production-like)
- Optionally resets Alembic migration history (`--reset-alembic`)
- Creates initial admin user from `.env` variables

**Modes:**
- **Default (dev):** Fast, direct SQLAlchemy table creation
- **--use-alembic:** Production-like, uses existing migrations
- **--reset-alembic:** Dev tool, clears migration history and creates fresh one

**⚠️ Warning:** Deletes ALL existing data!

---

### `load_fixtures.sh`
Loads basic test data (development only).

**What it does:**
- Shell wrapper: loads `.env`, exports `DB_NAME`, calls Python
- Python script: creates contracts, departments, users, visa types
- Includes production database safety check

**⚠️ Do NOT use in production!**

---

### `load_assess_fixture.sh`
Loads comprehensive ASSESS contract data with real employee visa cases (development only).

**What it does:**
- Creates ASSESS contract with full NASA Ames organizational structure (13 departments)
- **NASA Ames Structure:**
  - **TS (Entry Systems and Technology Division)** - Dave Cornelius / PM (Manager)
    - TSM (Thermal Protection Materials Branch) - Arnaud Borner
    - TSA (Aerothermodynamics Branch) - Bhaskaran Rathakrishnan
    - TSF (Thermo-Physics Facilities Branch) - No manager
    - TSS (Entry Systems and Vehicle Development Branch) - Blake Hannah
  - **TN (NASA Advanced Supercomputing Division)** - Parent department
    - TNA (Computational Aerosciences Branch) - Gerrit-Daniel Stich
    - TNP (Computational Physics Branch) - Patricia Ventura Diaz
  - **A (Aeronautics Directorate)** - Parent department
    - AV (Aeromechanics Office) - Gerrit-Daniel Stich (dual role)
    - AA (Systems Analysis Office) - Blake Hannah (dual role)
  - **Y (Aeroflightdynamics Directorate - US Army)** - Parent department
    - YA (Computational Aeromechanics Tech Area) - Shirzad Hoseinverdy
- Creates PM user and 6 branch managers
- Beneficiaries, case groups, and visa applications are seeded separately (see below)

**Test Accounts:**
- `pm.assess@ama-impact.com` - Project Manager (Dave Cornelius) - manages TS division
- `bhaskaran.rathakrishnan@ama-inc.com` - TSA Manager
- `arnaud.borner@ama-inc.com` - TSM Manager
- `blake.Hannah@ama-inc.com` - TSS & AA Manager (dual role)
- `patricia.ventura@ama-inc.com` - TNP Manager
- `gerrit-daniel.stich@ama-inc.com` - TNA & AV Manager (dual role)
- `shirzad.hoseinverdy@ama-inc.com` - YA Manager (Army)

All passwords: `TempPassword123!`

**⚠️ CRITICAL:** This is the COMPLETE NASA Ames organizational structure. DO NOT SIMPLIFY.

**⚠️ Do NOT use in production!**

---

### `start_server.sh`
Starts API server on port 8000.

**Auto-detects mode:**
- DEBUG=True → auto-reload enabled
- DEBUG=False → no auto-reload

---

## File Structure

```
scripts/
├── init_database.py              # Initialize database (dev or Alembic)
├── setup_dev_environment.py      # One-command dev setup (DB + all fixtures)
├── start_server.sh               # Start API server
└── fixtures/
    ├── README.md                 # Fixtures documentation
    ├── seed_visa_types.py        # Reference data: Visa types
    ├── seed_contracts.py         # ASSESS & RSES contracts
    ├── seed_law_firms.py         # Immigration law firms
    └── seed_development_data.py  # Realistic test data (users, visas, case groups, todos)
```

## Database Connection Flow

```
.env → Shell exports DB_NAME → Python reads from environment
    → Pydantic Settings → SQLAlchemy connects to sqlite:///./[DB_NAME]
```

## Admin Credentials

Set in your active `.env` file:

**Development (`.env.development`):**
- Email: `admin@ama-impact.com`
- Password: `Admin123!`

**Production (`.env.production`):**
- Configure `INITIAL_ADMIN_EMAIL`
- Configure `INITIAL_ADMIN_PASSWORD`

⚠️ Admin must change password on first login.

## Common Tasks

**Complete development setup (recommended):**
```bash
cd backend
python scripts/setup_dev_environment.py
```

**Reset development database only:**
```bash
cd backend
python scripts/init_database.py
```

**Reset development database WITH Alembic (production-like):**
```bash
cd backend
python scripts/init_database.py --reset-alembic
```

**Load fixtures individually:**
```bash
cd backend
python scripts/fixtures/seed_visa_types.py
python scripts/fixtures/seed_contracts.py
python scripts/fixtures/seed_law_firms.py
python scripts/fixtures/seed_development_data.py
```

**Switch to production:**
```bash
cd backend
ln -sf .env.production .env
python scripts/init_database.py --use-alembic
./scripts/start_server.sh
```

**Check active environment:**
```bash
cd backend
ls -la .env
cat .env | grep DB_NAME
```

## Troubleshooting

**"No environment file found"**
→ Create `.env` file or symlink: `ln -sf .env.development .env`

**Fixtures fail with "Admin not found"**
→ Run `python scripts/init_database.py` first

**"No module named app"**
→ Don't run Python scripts directly, use shell wrappers

**Wrong database**
→ Check `.env` symlink points to correct config file
