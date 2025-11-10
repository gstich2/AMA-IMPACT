from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User, UserRole
from app.models.department import Department
from app.models.contract import Contract
from app.schemas.department import (
    Department as DepartmentSchema,
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentTree,
    DepartmentSimple
)

router = APIRouter()


@router.get("/", response_model=List[DepartmentSimple])
async def list_departments(
    contract_id: Optional[str] = Query(None, description="Filter by contract ID"),
    include_inactive: bool = Query(False, description="Include inactive departments"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List all departments.
    
    **Filters:**
    - contract_id: Filter departments by contract
    - include_inactive: Include inactive departments (default: False)
    
    **Permissions:**
    - ADMIN: Can see all departments
    - PM: Can see departments in their contracts
    - MANAGER/HR/BENEFICIARY: Can see departments in their contract
    """
    query = db.query(Department)
    
    # Filter by active status
    if not include_inactive:
        query = query.filter(Department.is_active == True)
    
    # Filter by contract
    if contract_id:
        query = query.filter(Department.contract_id == contract_id)
    elif current_user.role != UserRole.ADMIN and current_user.contract_id:
        # Non-admin users can only see departments in their contract
        query = query.filter(Department.contract_id == current_user.contract_id)
    
    departments = query.order_by(Department.code).offset(skip).limit(limit).all()
    return departments


@router.get("/tree", response_model=List[DepartmentTree])
async def get_department_tree(
    contract_id: Optional[str] = Query(None, description="Filter by contract ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get department hierarchy as a tree structure.
    
    Returns departments with their children nested, suitable for tree UI components.
    Only returns top-level departments (no parent) with nested children.
    
    **Filters:**
    - contract_id: Filter departments by contract
    """
    query = db.query(Department).filter(Department.is_active == True)
    
    # Filter by contract
    if contract_id:
        query = query.filter(Department.contract_id == contract_id)
    elif current_user.role != UserRole.ADMIN and current_user.contract_id:
        query = query.filter(Department.contract_id == current_user.contract_id)
    
    # Get all departments
    all_departments = query.all()
    
    # Build tree structure
    dept_dict = {dept.id: dept for dept in all_departments}
    tree = []
    
    # Clear any existing children arrays (in case of cached objects)
    for dept in all_departments:
        dept.children = []
    
    # Build parent-child relationships
    for dept in all_departments:
        if dept.parent_id is None:
            # Top-level department
            tree.append(dept)
        else:
            # Add as child to parent
            parent = dept_dict.get(dept.parent_id)
            if parent:
                parent.children.append(dept)
    
    return tree


@router.get("/{department_id}", response_model=DepartmentSchema)
async def get_department(
    department_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get department by ID with full details.
    
    Includes:
    - Parent department info
    - Manager info
    - User counts (direct and total with sub-departments)
    """
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    # Check permissions
    if current_user.role != UserRole.ADMIN and current_user.contract_id != department.contract_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this department"
        )
    
    # Get user count
    user_count = db.query(func.count(User.id)).filter(
        User.department_id == department_id,
        User.is_active == True
    ).scalar()
    
    # Attach counts
    department.user_count = user_count
    
    return department


@router.post("/", response_model=DepartmentSchema, status_code=status.HTTP_201_CREATED)
async def create_department(
    department_in: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new department.
    
    **Permissions:** ADMIN or PM only
    
    **Validations:**
    - Department code must be unique within contract
    - Parent department (if specified) must exist in same contract
    - Manager (if specified) must exist and be in the same contract
    """
    # Check permissions
    if current_user.role not in [UserRole.ADMIN, UserRole.PM]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only ADMIN and PM can create departments"
        )
    
    # Verify contract exists
    contract = db.query(Contract).filter(Contract.id == department_in.contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    # Check if code already exists in this contract
    existing = db.query(Department).filter(
        Department.code == department_in.code,
        Department.contract_id == department_in.contract_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Department code '{department_in.code}' already exists in this contract"
        )
    
    # Validate parent department if specified
    if department_in.parent_id:
        parent = db.query(Department).filter(Department.id == department_in.parent_id).first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent department not found"
            )
        if parent.contract_id != department_in.contract_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent department must be in the same contract"
            )
    
    # Validate manager if specified
    if department_in.manager_id:
        manager = db.query(User).filter(User.id == department_in.manager_id).first()
        if not manager:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Manager user not found"
            )
        if manager.contract_id != department_in.contract_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Manager must be in the same contract"
            )
    
    # Create department
    department = Department(**department_in.model_dump())
    db.add(department)
    db.commit()
    db.refresh(department)
    
    return department


@router.patch("/{department_id}", response_model=DepartmentSchema)
async def update_department(
    department_id: str,
    department_update: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update department information.
    
    **Permissions:** ADMIN or PM only
    
    **Updatable fields:**
    - name, code, description
    - parent_id (change hierarchy)
    - manager_id (assign new manager)
    - is_active (activate/deactivate)
    """
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    # Check permissions
    if current_user.role not in [UserRole.ADMIN, UserRole.PM]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only ADMIN and PM can update departments"
        )
    
    if current_user.role == UserRole.PM and current_user.contract_id != department.contract_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="PM can only update departments in their contract"
        )
    
    # Validate code uniqueness if being changed
    update_data = department_update.model_dump(exclude_unset=True)
    if 'code' in update_data and update_data['code'] != department.code:
        existing = db.query(Department).filter(
            Department.code == update_data['code'],
            Department.contract_id == department.contract_id,
            Department.id != department_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Department code '{update_data['code']}' already exists in this contract"
            )
    
    # Validate parent_id if being changed
    if 'parent_id' in update_data and update_data['parent_id']:
        parent = db.query(Department).filter(Department.id == update_data['parent_id']).first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent department not found"
            )
        if parent.contract_id != department.contract_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent department must be in the same contract"
            )
        # Prevent circular references
        if update_data['parent_id'] == department_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Department cannot be its own parent"
            )
    
    # Validate manager_id if being changed
    if 'manager_id' in update_data and update_data['manager_id']:
        manager = db.query(User).filter(User.id == update_data['manager_id']).first()
        if not manager:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Manager user not found"
            )
        if manager.contract_id != department.contract_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Manager must be in the same contract"
            )
    
    # Apply updates
    for field, value in update_data.items():
        setattr(department, field, value)
    
    db.commit()
    db.refresh(department)
    
    return department


@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    department_id: str,
    force: bool = Query(False, description="Force delete even if department has users"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a department (soft delete by default).
    
    **Permissions:** ADMIN only
    
    **Safety checks:**
    - Cannot delete if department has active users (unless force=true)
    - Cannot delete if department has child departments
    
    **Behavior:**
    - Soft delete: Sets is_active = False
    - Force delete: Removes department record (use with caution)
    """
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    # Check permissions
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only ADMIN can delete departments"
        )
    
    # Check for child departments
    children = db.query(Department).filter(
        Department.parent_id == department_id,
        Department.is_active == True
    ).count()
    if children > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete department with {children} active child department(s). Delete or reassign children first."
        )
    
    # Check for users
    user_count = db.query(User).filter(
        User.department_id == department_id,
        User.is_active == True
    ).count()
    if user_count > 0 and not force:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete department with {user_count} active user(s). Reassign users or use force=true."
        )
    
    if force:
        # Hard delete
        db.delete(department)
    else:
        # Soft delete
        department.is_active = False
    
    db.commit()
    return None


@router.get("/contract/{contract_id}/summary")
async def get_contract_department_summary(
    contract_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get department summary for a contract.
    
    Returns:
    - Total departments
    - Top-level departments
    - Total users across all departments
    - Average users per department
    """
    # Verify contract exists
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    # Check permissions
    if current_user.role != UserRole.ADMIN and current_user.contract_id != contract_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this contract"
        )
    
    # Get counts
    total_depts = db.query(func.count(Department.id)).filter(
        Department.contract_id == contract_id,
        Department.is_active == True
    ).scalar()
    
    top_level_depts = db.query(func.count(Department.id)).filter(
        Department.contract_id == contract_id,
        Department.parent_id == None,
        Department.is_active == True
    ).scalar()
    
    total_users = db.query(func.count(User.id)).filter(
        User.contract_id == contract_id,
        User.is_active == True
    ).scalar()
    
    return {
        "contract_id": contract_id,
        "contract_code": contract.code,
        "contract_name": contract.name,
        "total_departments": total_depts,
        "top_level_departments": top_level_depts,
        "total_users": total_users,
        "average_users_per_department": round(total_users / total_depts, 2) if total_depts > 0 else 0
    }
