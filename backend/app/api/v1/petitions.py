from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, text
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.petition import Petition, CaseStatus, PetitionStatus, PetitionPriority, PetitionType
from app.models.beneficiary import Beneficiary
from app.models.department import Department
from app.services.rbac_service import RBACService
from app.schemas.petition import (
    Petition as PetitionSchema,
    PetitionCreate,
    PetitionUpdate
)

router = APIRouter()


@router.get("/", response_model=List[PetitionSchema])
async def list_petitions(
    # Pagination
    page: int = Query(1, description="Page number (1-based)", ge=1),
    limit: int = Query(20, description="Items per page", ge=1, le=100),
    
    # Status Filters
    status: Optional[PetitionStatus] = Query(None, description="Filter by petition status"),
    case_status: Optional[CaseStatus] = Query(None, description="Filter by case status"),
    priority: Optional[PetitionPriority] = Query(None, description="Filter by priority level"),
    
    # Type Filters
    petition_type: Optional[PetitionType] = Query(None, description="Filter by petition type"),
    
    # Date Filters
    expiring_within_days: Optional[int] = Query(None, description="Show visas expiring within N days", ge=1, le=1095),
    filed_after: Optional[str] = Query(None, description="Show petitions filed after date (YYYY-MM-DD)"),
    filed_before: Optional[str] = Query(None, description="Show petitions filed before date (YYYY-MM-DD)"),
    
    # Assignment Filters
    responsible_party_id: Optional[str] = Query(None, description="Filter by responsible party ID"),
    law_firm_id: Optional[str] = Query(None, description="Filter by law firm ID"),
    
    # Search
    search: Optional[str] = Query(None, description="Search in beneficiary name, case ID, receipt number, or notes"),
    
    # Sorting
    sort_by: str = Query("created_at", description="Sort field: created_at, expiration_date, filing_date, priority"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order: asc or desc"),
    
    # Flags
    overdue_only: bool = Query(False, description="Show only overdue/expired petitions"),
    premium_processing_only: bool = Query(False, description="Show only premium processing cases"),
    
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List petitions with comprehensive filtering, searching, and sorting.
    
    **Filtering Options:**
    - **Status Filters**: status, case_status, priority
    - **Type Filters**: petition_type  
    - **Date Filters**: expiring_within_days, filed_after, filed_before
    - **Assignment**: responsible_party_id, law_firm_id
    - **Search**: Full-text search across names, IDs, notes
    - **Flags**: overdue_only, premium_processing_only
    
    **Sorting**: Sort by created_at, expiration_date, filing_date, or priority
    
    **Pagination**: Use page/limit for efficient data loading
    
    **Role-Based Access**: Results filtered by user permissions
    - BENEFICIARY: Only their own applications
    - MANAGER: Their team's applications  
    - PM: Contract-wide applications
    - HR/ADMIN: Multi-contract access
    """
    
    # Build base query with eager loading for performance
    query = db.query(Petition).options(
        joinedload(Petition.beneficiary),
        joinedload(Petition.case_group)
    )
    
    # =============================================================
    # FILTERING
    # =============================================================
    
    # Status Filters
    if status:
        query = query.filter(Petition.status == status)
    
    if case_status:
        query = query.filter(Petition.case_status == case_status)
        
    if priority:
        query = query.filter(Petition.priority == priority)
    
    # Type Filters
    if petition_type:
        query = query.filter(Petition.petition_type == petition_type)
    
    # Date Filters
    if expiring_within_days:
        today = datetime.utcnow().date()
        future_date = today + timedelta(days=expiring_within_days)
        query = query.filter(
            and_(
                Petition.expiration_date.isnot(None),
                Petition.expiration_date <= future_date,
                Petition.expiration_date >= today  # Exclude already expired
            )
        )
    
    if filed_after:
        try:
            filed_after_date = datetime.strptime(filed_after, "%Y-%m-%d").date()
            query = query.filter(Petition.filing_date >= filed_after_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid filed_after date format. Use YYYY-MM-DD"
            )
    
    if filed_before:
        try:
            filed_before_date = datetime.strptime(filed_before, "%Y-%m-%d").date()
            query = query.filter(Petition.filing_date <= filed_before_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid filed_before date format. Use YYYY-MM-DD"
            )
    
    # Assignment Filters
    if responsible_party_id:
        query = query.filter(Petition.responsible_party_id == responsible_party_id)
        
    if law_firm_id:
        query = query.filter(Petition.law_firm_id == law_firm_id)
    
    # Search (across multiple fields)
    if search:
        search_term = f"%{search.lower()}%"
        query = query.join(Beneficiary).filter(
            or_(
                func.lower(Beneficiary.first_name).like(search_term),
                func.lower(Beneficiary.last_name).like(search_term),
                func.lower(Petition.company_case_id).like(search_term),
                func.lower(Petition.receipt_number).like(search_term),
                func.lower(Petition.notes).like(search_term)
            )
        )
    
    # Special Flags
    if overdue_only:
        today = datetime.utcnow().date()
        query = query.filter(
            and_(
                Petition.expiration_date.isnot(None),
                Petition.expiration_date < today
            )
        )
    
    if premium_processing_only:
        query = query.filter(Petition.premium_processing == True)
    
    # =============================================================
    # ROLE-BASED ACCESS CONTROL
    # =============================================================
    
    # Apply hierarchical role-based filtering
    rbac = RBACService(db, current_user)
    query = rbac.apply_petition_filters(query)
    
    # =============================================================
    # SORTING
    # =============================================================
    
    # Validate and apply sorting
    valid_sort_fields = {
        "created_at": Petition.created_at,
        "expiration_date": Petition.expiration_date,
        "filing_date": Petition.filing_date,
        "priority": Petition.priority
    }
    
    if sort_by not in valid_sort_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sort_by field. Must be one of: {', '.join(valid_sort_fields.keys())}"
        )
    
    sort_column = valid_sort_fields[sort_by]
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    # Secondary sort by created_at for consistency
    if sort_by != "created_at":
        query = query.order_by(Petition.created_at.desc())
    
    # =============================================================
    # PAGINATION
    # =============================================================
    
    # Calculate offset
    skip = (page - 1) * limit
    
    # Get total count for pagination metadata (optional for frontend)
    # total_count = query.count()  # Uncomment if you want to return pagination metadata
    
    # Apply pagination and execute query
    applications = query.offset(skip).limit(limit).all()
    
    return applications


@router.get("/expiring", response_model=List[PetitionSchema])
async def get_expiring_petitions(
    days: int = Query(30, description="Number of days to look ahead for expiring visas", ge=1, le=365),
    include_overdue: bool = Query(False, description="Include visas that are already expired"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get petitions that are expiring within the specified number of days.
    
    This is a critical endpoint for preventing visa lapses.
    
    Query Parameters:
    - days: Number of days to look ahead (default: 30, max: 365)
    - include_overdue: Whether to include already expired visas (default: false)
    
    Returns:
    - List of petitions expiring within the timeframe
    - Ordered by expiration date (soonest first)
    - Role-filtered based on user permissions
    """
    today = datetime.utcnow().date()
    future_date = today + timedelta(days=days)
    
    # Base query for active visas
    active_statuses = [PetitionStatus.APPROVED, PetitionStatus.IN_PROGRESS, PetitionStatus.SUBMITTED]
    query = db.query(Petition).filter(
        and_(
            Petition.status.in_(active_statuses),
            Petition.expiration_date.isnot(None)
        )
    )
    
    # Build date filter
    if include_overdue:
        # Include expired visas AND upcoming expirations
        date_filter = Petition.expiration_date <= future_date
    else:
        # Only upcoming expirations (not expired)
        date_filter = and_(
            Petition.expiration_date >= today,
            Petition.expiration_date <= future_date
        )
    
    query = query.filter(date_filter)
    
    # Apply role-based filtering
    rbac = RBACService(db, current_user)
    query = rbac.apply_petition_filters(query)
    
    # Order by expiration date (soonest first)
    applications = query.order_by(Petition.expiration_date.asc()).all()
    
    return applications


@router.get("/{application_id}", response_model=PetitionSchema)
async def get_petition(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get petition by ID with role-based access control."""
    
    # Build query with role-based filtering
    query = db.query(Petition).filter(Petition.id == application_id)
    
    # Apply RBAC filtering
    rbac = RBACService(db, current_user)
    query = rbac.apply_petition_filters(query)
    
    application = query.first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Petition not found or access denied"
        )
    
    return application


@router.post("/", response_model=PetitionSchema, status_code=status.HTTP_201_CREATED)
async def create_petition(
    application_in: PetitionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new petition with role-based access control."""
    
    # Check permissions
    rbac = RBACService(db, current_user)
    
    if not rbac.can_modify_data():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create petitions"
        )
    
    # If creating for a specific beneficiary, check if user has access to that beneficiary
    if hasattr(application_in, 'beneficiary_id') and application_in.beneficiary_id:
        if not rbac.can_access_beneficiary(application_in.beneficiary_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot create petition for this beneficiary"
            )
    
    application = Petition(
        **application_in.model_dump(),
        created_by=current_user.id
    )
    
    db.add(application)
    db.commit()
    db.refresh(application)
    
    return application


@router.patch("/{application_id}", response_model=PetitionSchema)
async def update_petition(
    application_id: str,
    application_update: PetitionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update petition with role-based access control."""
    
    # Check permissions
    rbac = RBACService(db, current_user)
    
    if not rbac.can_modify_data():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update petitions"
        )
    
    # Build query with role-based filtering
    query = db.query(Petition).filter(Petition.id == application_id)
    query = rbac.apply_petition_filters(query)
    
    application = query.first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Petition not found or access denied"
        )
    
    update_data = application_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(application, field, value)
    
    db.commit()
    db.refresh(application)
    
    return application


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_petition(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete petition (admin only) with role-based access control."""
    
    # Check permissions - only admins can delete
    rbac = RBACService(db, current_user)
    
    if not rbac.can_delete_data():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete petitions"
        )
    
    # Build query with role-based filtering (admin sees all, so this is just safety)
    query = db.query(Petition).filter(Petition.id == application_id)
    query = rbac.apply_petition_filters(query)
    
    application = query.first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Petition not found"
        )
    
    db.delete(application)
    db.commit()
    
    return None


@router.get("/{application_id}/available-milestones")
async def get_available_milestones(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get available milestone types for this petition based on its visa type.
    Returns the full pipeline with status (completed/incomplete).
    
    This endpoint helps users know which milestones are valid for this specific visa type.
    For example, an H1B will show LCA-related milestones, while an EB-2 NIW will show I-140 milestones.
    
    Permissions:
    - BENEFICIARY: Can view milestones for their own petitions
    - PM/HR/MANAGER: Can view milestones for applications in their contract
    - ADMIN: Can view milestones for any application
    """
    from app.config.petition_pipelines import get_pipeline_for_petition_type
    from app.models.milestone import Milestone
    
    # Build query with role-based filtering
    rbac = RBACService(db, current_user)
    query = db.query(Petition).filter(Petition.id == application_id)
    query = rbac.apply_petition_filters(query)
    
    petition = query.first()
    
    if not petition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Petition not found or access denied"
        )
    
    # Get pipeline for this visa type
    pipeline_config = get_pipeline_for_petition_type(petition.petition_type)
    
    # Get completed milestones
    milestones = db.query(Milestone).filter(
        Milestone.petition_id == application_id
    ).all()
    completed_types = {m.milestone_type for m in milestones}
    
    # Return pipeline with completion status
    available_milestones = []
    for stage in pipeline_config["stages"]:
        milestone_type = stage["milestone_type"]
        is_completed = milestone_type in completed_types
        
        # Find completion date if completed
        completion_date = None
        if is_completed:
            for m in milestones:
                if m.milestone_type == milestone_type:
                    completion_date = m.milestone_date.isoformat()
                    break
        
        available_milestones.append({
            "milestone_type": milestone_type.value,
            "label": stage["label"],
            "description": stage.get("description"),
            "required": stage["required"],
            "weight": stage["weight"],
            "completed": is_completed,
            "completion_date": completion_date,
        })
    
    return {
        "petition_id": application_id,
        "petition_type": petition.petition_type.value,
        "petition_type": petition.petition_type,
        "pipeline_name": pipeline_config["name"],
        "pipeline_description": pipeline_config["description"],
        "milestones": available_milestones,
    }
