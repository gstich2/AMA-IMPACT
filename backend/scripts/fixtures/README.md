# Test Fixtures

Test data files that can be loaded into the database.

## `development_data.py`

Creates comprehensive test data for development.

**Contains:**
- 2 Contracts (ASSESS-2025, RESESS-2025)
- 5 Departments with hierarchy (TS → TSM/TSA, TNA, AV)
- 5 Test Users (HR, PM, Tech Lead, 2 Staff)
- 12 Visa Types (H1B, L1, O1, TN, EB-types, PERM, OPT, EAD, Green Card)

**Usage:**
```bash
cd backend/scripts
./load_fixtures.sh  # Wrapper script that calls this
```

**Don't run directly** - the wrapper script sets up the environment correctly.

## Database Connection

The script connects to the database specified by `DB_NAME` in your active `.env` file:

```
.env file → Shell exports DB_NAME → Python imports config
    → SQLAlchemy connects to sqlite:///./[DB_NAME]
```

## Adding Test Data

To add more fixtures:

1. Open `development_data.py`
2. Add data in `seed_database()` function
3. Use SQLAlchemy models

Example:
```python
new_contract = Contract(
    name='New Program',
    code='NEW-2025',
    start_date=date(2025, 1, 1),
    status=ContractStatus.ACTIVE
)
db.add(new_contract)
db.commit()
```

## Production

**Never** load fixtures in production! Only the admin user is created by `init_database.sh`.
