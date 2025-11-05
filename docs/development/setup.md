# Development Guide

Complete guide for developing and contributing to AMA-IMPACT.

## Table of Contents

- [Environment Setup](#environment-setup)
- [Database Management](#database-management)
- [Fixture System](#fixture-system)
- [Testing](#testing)
- [Code Standards](#code-standards)
- [Common Tasks](#common-tasks)

---

## Environment Setup

### Prerequisites

- Python 3.12+
- Node.js 18+
- Git
- Virtual environment tool (venv)

### Backend Setup

```bash
# Clone repository
git clone https://github.com/gstich2/AMA-IMPACT.git
cd AMA-IMPACT

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies
cd backend
pip install -r requirements.txt

# Setup database
python scripts/setup_dev_environment.py

# Start server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install

# Create environment file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local

# Start development server
npm run dev
```

---

## Database Management

### Database Location

SQLite database: `backend/devel.db`

### Database Schema

The database uses SQLAlchemy ORM with the following models:

- **User** - System users with roles and hierarchy
- **Beneficiary** - Foreign nationals with visa cases
- **VisaApplication** - Individual visa petitions
- **CaseGroup** - Collections of related visa applications
- **Todo** - Task tracking with hierarchical relationships
- **Contract** - Project/contract organization
- **Department** - Organizational units
- **Dependent** - Family members of beneficiaries
- **LawFirm** - Law firms handling cases
- And more...

See [Data Models](../architecture/data-models.md) for complete documentation.

### Database Initialization

```bash
cd backend
python scripts/init_database.py
```

This creates all tables based on SQLAlchemy models.

### Resetting Database

```bash
# Delete database
rm backend/devel.db

# Recreate with fixtures
python scripts/setup_dev_environment.py
```

### Manual Database Access

```bash
cd backend
sqlite3 devel.db

# Useful queries
SELECT email, role FROM users;
SELECT first_name, last_name, current_visa_type FROM beneficiaries;
SELECT title, status, priority FROM todos;
SELECT name, case_type, status FROM case_groups;
```

---

## Fixture System

### Overview

The fixture system provides modular, composable test data. Each fixture is responsible for one entity type.

### Fixture Files

Located in `backend/scripts/fixtures/`:

- `seed_users.py` - Create system users
- `seed_contracts.py` - Create contracts
- `seed_departments.py` - Create departments
- `seed_beneficiaries.py` - Create beneficiaries
- `seed_visa_applications.py` - Create visa applications
- `seed_case_groups.py` - Create case groups
- `seed_dependents.py` - Create dependents
- `seed_law_firms.py` - Create law firms
- `seed_development_data.py` - Create sample todos and additional data

### Running Fixtures

**All fixtures:**
```bash
python scripts/setup_dev_environment.py
```

**Individual fixture:**
```bash
cd backend
python -c "
from app.core.database import SessionLocal
from scripts.fixtures.seed_users import seed_users

db = SessionLocal()
try:
    seed_users(db)
    db.commit()
finally:
    db.close()
"
```

### Creating New Fixtures

Example: `seed_my_entity.py`

```python
"""
Seed script for MyEntity
"""
from sqlalchemy.orm import Session
from app.models.my_entity import MyEntity

def seed_my_entities(db: Session):
    """Seed MyEntity data"""
    
    entities = [
        MyEntity(
            name="Entity 1",
            description="Description 1",
        ),
        MyEntity(
            name="Entity 2",
            description="Description 2",
        ),
    ]
    
    for entity in entities:
        db.add(entity)
    
    print(f"✅ Created {len(entities)} my_entities")
    
    return entities

if __name__ == "__main__":
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    try:
        seed_my_entities(db)
        db.commit()
        print("✅ MyEntity seeding completed")
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()
```

### Fixture Best Practices

1. **Idempotent**: Should be safe to run multiple times
2. **Self-contained**: Include all necessary data
3. **Realistic**: Use representative sample data
4. **Documented**: Add comments explaining relationships
5. **Modular**: One fixture per entity type

---

## Testing

### Running Tests

```bash
cd backend

# Run all tests
pytest

# Run specific test file
pytest tests/test_todos.py

# Run with coverage
pytest --cov=app --cov-report=html

# Run with verbose output
pytest -v
```

### Test Structure

```
backend/tests/
├── conftest.py           # Shared fixtures
├── test_auth.py          # Authentication tests
├── test_users.py         # User API tests
├── test_beneficiaries.py # Beneficiary tests
├── test_visa_apps.py     # Visa application tests
├── test_case_groups.py   # Case group tests
└── test_todos.py         # Todo tests
```

### Writing Tests

Example test:

```python
def test_create_todo(client, auth_headers):
    """Test creating a todo"""
    response = client.post(
        "/api/v1/todos",
        json={
            "title": "Test Todo",
            "assigned_to_user_id": "user-uuid",
            "priority": "HIGH",
            "status": "TODO"
        },
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Todo"
    assert data["priority"] == "HIGH"
```

---

## Code Standards

### Python (Backend)

**Style Guide:**
- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use docstrings for functions and classes

**Example:**
```python
from typing import List, Optional
from sqlalchemy.orm import Session

def get_todos(
    db: Session,
    user_id: str,
    status: Optional[str] = None,
    limit: int = 20
) -> List[Todo]:
    """
    Retrieve todos for a user.
    
    Args:
        db: Database session
        user_id: UUID of the user
        status: Optional status filter
        limit: Maximum number of results
        
    Returns:
        List of Todo objects
    """
    query = db.query(Todo).filter(Todo.assigned_to_user_id == user_id)
    
    if status:
        query = query.filter(Todo.status == status)
    
    return query.limit(limit).all()
```

### TypeScript (Frontend)

**Style Guide:**
- Use TypeScript strict mode
- Prefer functional components
- Use proper typing for props and state

**Example:**
```typescript
interface TodoItemProps {
  todo: Todo;
  onUpdate: (id: string, updates: Partial<Todo>) => void;
}

export function TodoItem({ todo, onUpdate }: TodoItemProps) {
  const handleComplete = () => {
    onUpdate(todo.id, { status: 'COMPLETED' });
  };
  
  return (
    <div className="todo-item">
      <h3>{todo.title}</h3>
      <button onClick={handleComplete}>Complete</button>
    </div>
  );
}
```

### File Naming

**Backend:**
- Models: `snake_case.py` (e.g., `case_group.py`)
- API routes: `snake_case.py` (e.g., `visa_applications.py`)
- Schemas: `snake_case.py` (e.g., `todo.py`)

**Frontend:**
- Components: `PascalCase.tsx` (e.g., `TodoList.tsx`)
- Utilities: `camelCase.ts` (e.g., `apiClient.ts`)
- Pages: `kebab-case/` (e.g., `visa-applications/`)

---

## Common Tasks

### Adding a New Model

1. **Create model** in `app/models/my_model.py`:
```python
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.mixins import UUIDMixin, TimestampMixin

class MyModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "my_models"
    
    name = Column(String, nullable=False)
    user_id = Column(String, ForeignKey("users.id"))
    
    user = relationship("User", back_populates="my_models")
```

2. **Create schema** in `app/schemas/my_model.py`:
```python
from pydantic import BaseModel
from datetime import datetime

class MyModelBase(BaseModel):
    name: str
    user_id: str

class MyModelCreate(MyModelBase):
    pass

class MyModelResponse(MyModelBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

3. **Create API** in `app/api/v1/my_models.py`:
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.schemas.my_model import MyModelCreate, MyModelResponse

router = APIRouter()

@router.post("/", response_model=MyModelResponse)
async def create_my_model(
    data: MyModelCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    model = MyModel(**data.dict())
    db.add(model)
    db.commit()
    db.refresh(model)
    return model
```

4. **Register router** in `app/main.py`:
```python
from app.api.v1 import my_models

app.include_router(
    my_models.router,
    prefix="/api/v1/my-models",
    tags=["My Models"]
)
```

5. **Update exports** in `app/models/__init__.py`:
```python
from app.models.my_model import MyModel
```

6. **Create fixture** in `scripts/fixtures/seed_my_models.py`

7. **Add to setup script** in `scripts/setup_dev_environment.py`

### Adding a New API Endpoint

1. Find relevant router in `app/api/v1/`
2. Add endpoint function with proper decorators
3. Add authentication/authorization checks
4. Implement business logic
5. Add documentation docstring
6. Test in Swagger UI

### Database Migration (Future)

Currently using direct SQLAlchemy schema creation. For production:

```bash
# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Add my_model table"

# Apply migration
alembic upgrade head
```

---

## Development Workflow

### Daily Development

1. **Pull latest changes**
```bash
git pull origin main
```

2. **Activate virtual environment**
```bash
source .venv/bin/activate
```

3. **Start backend**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

4. **Start frontend** (in new terminal)
```bash
cd frontend
npm run dev
```

5. **Make changes and test**

6. **Run tests before committing**
```bash
cd backend
pytest
```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes and commit
git add .
git commit -m "Add: My feature description"

# Push to remote
git push origin feature/my-feature

# Create pull request on GitHub
```

### Commit Message Format

```
Type: Brief description

- Detailed point 1
- Detailed point 2

Types: Add, Update, Fix, Remove, Refactor, Docs, Test
```

Example:
```
Add: Todo computed metrics

- Implemented is_overdue calculation
- Added days_overdue, days_to_complete metrics
- Updated all todo endpoints to return enriched responses
```

---

## Troubleshooting

### Backend Issues

**Import Errors:**
```bash
# Ensure you're in backend directory
cd backend

# Activate virtual environment
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**Database Locked:**
```bash
# Stop all servers
pkill -f uvicorn

# Remove lock files
rm devel.db-shm devel.db-wal

# Restart server
uvicorn app.main:app --reload --port 8000
```

**Port Already in Use:**
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn app.main:app --reload --port 8001
```

### Frontend Issues

**Module Not Found:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Port Already in Use:**
```bash
lsof -ti:3000 | xargs kill -9
npm run dev -- -p 3001
```

---

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Next.js Documentation](https://nextjs.org/docs)
- [React Query Documentation](https://tanstack.com/query/latest)

---

## Getting Help

- **API Issues**: Check `http://localhost:8000/docs`
- **Database Schema**: See [Data Models](../architecture/data-models.md)
- **API Endpoints**: See [API Reference](../api/overview.md)
- **Contact**: dev-team@ama-inc.com
