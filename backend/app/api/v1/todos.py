"""
Todo API endpoints
Provides task tracking and management functionality
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, func
from typing import List, Optional
from datetime import datetime, timezone

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User, UserRole
from app.models.todo import Todo, TodoStatus, TodoPriority
from app.models.visa import VisaApplication
from app.models.case_group import CaseGroup
from app.models.beneficiary import Beneficiary
from app.schemas.todo import TodoCreate, TodoUpdate, TodoResponse, TodoStats

router = APIRouter()


def compute_todo_metrics(todo: Todo) -> dict:
    """
    Compute metrics for a todo item.
    Returns dict with: is_overdue, days_overdue, days_to_complete, completed_on_time
    """
    now = datetime.now(timezone.utc)
    metrics = {
        'is_overdue': None,
        'days_overdue': None,
        'days_to_complete': None,
        'completed_on_time': None
    }
    
    # Is overdue? (only if not completed/cancelled and past due date)
    if todo.due_date and todo.status not in [TodoStatus.COMPLETED, TodoStatus.CANCELLED]:
        # Make due_date timezone-aware if it isn't
        due_date_aware = todo.due_date if todo.due_date.tzinfo else todo.due_date.replace(tzinfo=timezone.utc)
        if now > due_date_aware:
            metrics['is_overdue'] = True
            metrics['days_overdue'] = (now - due_date_aware).days
        else:
            metrics['is_overdue'] = False
    
    # Days to complete (if completed)
    if todo.completed_at and todo.created_at:
        completed_aware = todo.completed_at if todo.completed_at.tzinfo else todo.completed_at.replace(tzinfo=timezone.utc)
        created_aware = todo.created_at if todo.created_at.tzinfo else todo.created_at.replace(tzinfo=timezone.utc)
        metrics['days_to_complete'] = (completed_aware - created_aware).days
    
    # Completed on time? (if completed and had due date)
    if todo.completed_at and todo.due_date:
        completed_aware = todo.completed_at if todo.completed_at.tzinfo else todo.completed_at.replace(tzinfo=timezone.utc)
        due_date_aware = todo.due_date if todo.due_date.tzinfo else todo.due_date.replace(tzinfo=timezone.utc)
        metrics['completed_on_time'] = completed_aware <= due_date_aware
    
    return metrics


def enrich_todo_response(todo: Todo) -> TodoResponse:
    """Convert Todo model to TodoResponse with computed metrics."""
    metrics = compute_todo_metrics(todo)
    todo_dict = {
        'id': todo.id,
        'title': todo.title,
        'description': todo.description,
        'assigned_to_user_id': todo.assigned_to_user_id,
        'created_by_user_id': todo.created_by_user_id,
        'visa_application_id': todo.visa_application_id,
        'case_group_id': todo.case_group_id,
        'beneficiary_id': todo.beneficiary_id,
        'status': todo.status,
        'priority': todo.priority,
        'due_date': todo.due_date,
        'completed_at': todo.completed_at,
        'created_at': todo.created_at,
        'updated_at': todo.updated_at,
        **metrics
    }
    return TodoResponse(**todo_dict)


def auto_populate_hierarchy(
    db: Session,
    visa_application_id: Optional[str],
    case_group_id: Optional[str],
    beneficiary_id: Optional[str]
) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Auto-populate the hierarchy based on what's provided.
    If visa_application_id is given, populate case_group_id and beneficiary_id.
    If case_group_id is given, populate beneficiary_id.
    
    Returns: (visa_application_id, case_group_id, beneficiary_id)
    """
    if visa_application_id:
        visa_app = db.query(VisaApplication).filter(VisaApplication.id == visa_application_id).first()
        if not visa_app:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Visa application not found"
            )
        return visa_application_id, visa_app.case_group_id, visa_app.beneficiary_id
    
    elif case_group_id:
        case_group = db.query(CaseGroup).filter(CaseGroup.id == case_group_id).first()
        if not case_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case group not found"
            )
        return None, case_group_id, case_group.beneficiary_id
    
    elif beneficiary_id:
        beneficiary = db.query(Beneficiary).filter(Beneficiary.id == beneficiary_id).first()
        if not beneficiary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Beneficiary not found"
            )
        return None, None, beneficiary_id
    
    # All None - general todo not tied to any case
    return None, None, None


def get_user_hierarchy_ids(db: Session, user: User) -> List[str]:
    """Get list of user IDs in the reporting hierarchy (user + all subordinates)."""
    user_ids = [user.id]
    
    # Recursive query to get all subordinates
    def get_subordinates(manager_id: str):
        subordinates = db.query(User).filter(User.reports_to_id == manager_id).all()
        for subordinate in subordinates:
            user_ids.append(subordinate.id)
            get_subordinates(subordinate.id)
    
    get_subordinates(user.id)
    return user_ids


@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo_in: TodoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new todo.
    
    Auto-populates hierarchy:
    - If visa_application_id provided → auto-fills case_group_id and beneficiary_id
    - If case_group_id provided → auto-fills beneficiary_id
    """
    # Auto-populate hierarchy
    visa_app_id, case_group_id, beneficiary_id = auto_populate_hierarchy(
        db,
        todo_in.visa_application_id,
        todo_in.case_group_id,
        todo_in.beneficiary_id
    )
    
    # Verify assigned user exists
    assigned_user = db.query(User).filter(User.id == todo_in.assigned_to_user_id).first()
    if not assigned_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found"
        )
    
    # Create todo
    todo = Todo(
        title=todo_in.title,
        description=todo_in.description,
        assigned_to_user_id=todo_in.assigned_to_user_id,
        created_by_user_id=current_user.id,
        visa_application_id=visa_app_id,
        case_group_id=case_group_id,
        beneficiary_id=beneficiary_id,
        status=todo_in.status,
        priority=todo_in.priority,
        due_date=todo_in.due_date
    )
    
    db.add(todo)
    db.commit()
    db.refresh(todo)
    
    return enrich_todo_response(todo)


@router.get("/my-todos", response_model=List[TodoResponse])
async def get_my_todos(
    status_filter: Optional[TodoStatus] = Query(None, description="Filter by status"),
    priority_filter: Optional[TodoPriority] = Query(None, description="Filter by priority"),
    include_completed: bool = Query(False, description="Include completed todos"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get todos assigned to the current user.
    Dashboard endpoint for "My Todos".
    """
    query = db.query(Todo).filter(Todo.assigned_to_user_id == current_user.id)
    
    # Apply filters
    if not include_completed:
        query = query.filter(Todo.status != TodoStatus.COMPLETED)
    
    if status_filter:
        query = query.filter(Todo.status == status_filter)
    
    if priority_filter:
        query = query.filter(Todo.priority == priority_filter)
    
    # Order by priority (urgent first) then due date
    query = query.order_by(
        Todo.priority.desc(),
        Todo.due_date.asc().nullslast(),
        Todo.created_at.desc()
    )
    
    todos = query.all()
    return [enrich_todo_response(todo) for todo in todos]


@router.get("/team-todos", response_model=List[TodoResponse])
async def get_team_todos(
    status_filter: Optional[TodoStatus] = Query(None, description="Filter by status"),
    priority_filter: Optional[TodoPriority] = Query(None, description="Filter by priority"),
    include_completed: bool = Query(False, description="Include completed todos"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get todos for the current user's entire reporting hierarchy.
    Dashboard endpoint for managers to see all team todos.
    
    - BENEFICIARY: Only their own todos
    - MANAGER: Their todos + all subordinates' todos
    - PM/HR/ADMIN: All todos in their contract/organization
    """
    if current_user.role == UserRole.BENEFICIARY:
        # Beneficiaries only see their own todos
        query = db.query(Todo).filter(Todo.assigned_to_user_id == current_user.id)
    
    elif current_user.role == UserRole.MANAGER:
        # Managers see their hierarchy
        user_ids = get_user_hierarchy_ids(db, current_user)
        query = db.query(Todo).filter(Todo.assigned_to_user_id.in_(user_ids))
    
    else:  # PM, HR, ADMIN
        # See all todos (can add contract filtering if needed)
        query = db.query(Todo)
    
    # Apply filters
    if not include_completed:
        query = query.filter(Todo.status != TodoStatus.COMPLETED)
    
    if status_filter:
        query = query.filter(Todo.status == status_filter)
    
    if priority_filter:
        query = query.filter(Todo.priority == priority_filter)
    
    # Order by priority then due date
    query = query.order_by(
        Todo.priority.desc(),
        Todo.due_date.asc().nullslast(),
        Todo.created_at.desc()
    )
    
    todos = query.all()
    return [enrich_todo_response(todo) for todo in todos]


@router.get("/stats", response_model=TodoStats)
async def get_my_todo_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get todo statistics for the current user's dashboard.
    Shows counts by status and priority.
    """
    base_query = db.query(Todo).filter(Todo.assigned_to_user_id == current_user.id)
    
    total = base_query.count()
    todo = base_query.filter(Todo.status == TodoStatus.TODO).count()
    in_progress = base_query.filter(Todo.status == TodoStatus.IN_PROGRESS).count()
    blocked = base_query.filter(Todo.status == TodoStatus.BLOCKED).count()
    completed = base_query.filter(Todo.status == TodoStatus.COMPLETED).count()
    cancelled = base_query.filter(Todo.status == TodoStatus.CANCELLED).count()
    
    # Overdue todos (not completed and past due date)
    overdue = base_query.filter(
        and_(
            Todo.status.notin_([TodoStatus.COMPLETED, TodoStatus.CANCELLED]),
            Todo.due_date < datetime.utcnow()
        )
    ).count()
    
    # Priority counts (not completed)
    urgent = base_query.filter(
        and_(
            Todo.status != TodoStatus.COMPLETED,
            Todo.priority == TodoPriority.URGENT
        )
    ).count()
    
    high_priority = base_query.filter(
        and_(
            Todo.status != TodoStatus.COMPLETED,
            Todo.priority == TodoPriority.HIGH
        )
    ).count()
    
    return TodoStats(
        total=total,
        todo=todo,
        in_progress=in_progress,
        blocked=blocked,
        completed=completed,
        cancelled=cancelled,
        overdue=overdue,
        urgent=urgent,
        high_priority=high_priority
    )


@router.get("/beneficiary/{beneficiary_id}", response_model=List[TodoResponse])
async def get_beneficiary_todos(
    beneficiary_id: str,
    status_filter: Optional[TodoStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all todos related to a specific beneficiary.
    Includes todos at visa, case group, and beneficiary level.
    """
    # Permission check
    if current_user.role == UserRole.BENEFICIARY:
        # Beneficiaries can only see their own todos
        beneficiary = db.query(Beneficiary).filter(Beneficiary.id == beneficiary_id).first()
        if not beneficiary or beneficiary.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own todos"
            )
    
    query = db.query(Todo).filter(Todo.beneficiary_id == beneficiary_id)
    
    if status_filter:
        query = query.filter(Todo.status == status_filter)
    
    query = query.order_by(Todo.priority.desc(), Todo.due_date.asc().nullslast())
    
    todos = query.all()
    return [enrich_todo_response(todo) for todo in todos]


@router.get("/visa-application/{visa_application_id}", response_model=List[TodoResponse])
async def get_visa_application_todos(
    visa_application_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all todos for a specific visa application."""
    visa_app = db.query(VisaApplication).filter(VisaApplication.id == visa_application_id).first()
    if not visa_app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visa application not found"
        )
    
    # Permission check for beneficiaries
    if current_user.role == UserRole.BENEFICIARY:
        beneficiary = db.query(Beneficiary).filter(
            Beneficiary.id == visa_app.beneficiary_id,
            Beneficiary.user_id == current_user.id
        ).first()
        if not beneficiary:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view todos for your own visa applications"
            )
    
    todos = db.query(Todo).filter(
        Todo.visa_application_id == visa_application_id
    ).order_by(Todo.priority.desc(), Todo.due_date.asc().nullslast()).all()
    
    return [enrich_todo_response(todo) for todo in todos]


@router.get("/case-group/{case_group_id}", response_model=List[TodoResponse])
async def get_case_group_todos(
    case_group_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all todos for a specific case group."""
    case_group = db.query(CaseGroup).filter(CaseGroup.id == case_group_id).first()
    if not case_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case group not found"
        )
    
    # Permission check for beneficiaries
    if current_user.role == UserRole.BENEFICIARY:
        beneficiary = db.query(Beneficiary).filter(
            Beneficiary.id == case_group.beneficiary_id,
            Beneficiary.user_id == current_user.id
        ).first()
        if not beneficiary:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view todos for your own case groups"
            )
    
    todos = db.query(Todo).filter(
        Todo.case_group_id == case_group_id
    ).order_by(Todo.priority.desc(), Todo.due_date.asc().nullslast()).all()
    
    return [enrich_todo_response(todo) for todo in todos]


@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(
    todo_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific todo by ID."""
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    
    # Permission check for beneficiaries
    if current_user.role == UserRole.BENEFICIARY:
        if todo.assigned_to_user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own todos"
            )
    
    return enrich_todo_response(todo)


@router.patch("/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: str,
    todo_update: TodoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a todo.
    
    - Assigned user can update status, notes
    - PM/HR/ADMIN can update everything
    - Auto-sets completed_at when status changes to COMPLETED
    """
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    
    # Permission check
    can_update_all = current_user.role in [UserRole.ADMIN, UserRole.HR, UserRole.PM]
    is_assigned = todo.assigned_to_user_id == current_user.id
    
    if not (can_update_all or is_assigned):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own todos"
        )
    
    # Update fields
    update_data = todo_update.model_dump(exclude_unset=True)
    
    # If reassigning or changing hierarchy, re-populate
    if any(k in update_data for k in ['visa_application_id', 'case_group_id', 'beneficiary_id']):
        visa_app_id, case_group_id, beneficiary_id = auto_populate_hierarchy(
            db,
            update_data.get('visa_application_id', todo.visa_application_id),
            update_data.get('case_group_id', todo.case_group_id),
            update_data.get('beneficiary_id', todo.beneficiary_id)
        )
        update_data['visa_application_id'] = visa_app_id
        update_data['case_group_id'] = case_group_id
        update_data['beneficiary_id'] = beneficiary_id
    
    # Auto-set completed_at when completing
    if 'status' in update_data and update_data['status'] == TodoStatus.COMPLETED:
        update_data['completed_at'] = datetime.utcnow()
    elif 'status' in update_data and update_data['status'] != TodoStatus.COMPLETED:
        update_data['completed_at'] = None
    
    for field, value in update_data.items():
        setattr(todo, field, value)
    
    db.commit()
    db.refresh(todo)
    
    return enrich_todo_response(todo)


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a todo.
    Only PM/HR/ADMIN or the creator can delete.
    """
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    
    # Permission check
    can_delete = (
        current_user.role in [UserRole.ADMIN, UserRole.HR, UserRole.PM] or
        todo.created_by_user_id == current_user.id
    )
    
    if not can_delete:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete todos you created"
        )
    
    db.delete(todo)
    db.commit()
    
    return None
