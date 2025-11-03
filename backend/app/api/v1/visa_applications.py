from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.visa import VisaApplication, VisaCaseStatus
from app.schemas.visa import (
    VisaApplication as VisaApplicationSchema,
    VisaApplicationCreate,
    VisaApplicationUpdate
)

router = APIRouter()


@router.get("/", response_model=List[VisaApplicationSchema])
async def list_visa_applications(
    skip: int = 0,
    limit: int = 100,
    case_status: Optional[str] = Query(None, description="Filter by case status: UPCOMING, ACTIVE, or FINALIZED"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List visa applications (filtered by permissions and case status).
    
    Case Status:
    - UPCOMING: Cases that are planned but not yet active
    - ACTIVE: Cases currently being worked on
    - FINALIZED: Completed or closed cases
    """
    # TODO: Implement hierarchical filtering
    # Staff: only their own
    # Tech Lead: their reports
    # PM: entire contract
    # HR: assigned contracts
    # Admin: all
    
    query = db.query(VisaApplication)
    
    # Filter by case status if provided
    if case_status:
        try:
            status_enum = VisaCaseStatus(case_status.upper())
            query = query.filter(VisaApplication.case_status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid case status. Must be one of: UPCOMING, ACTIVE, FINALIZED"
            )
    
    applications = query.offset(skip).limit(limit).all()
    return applications


@router.get("/{application_id}", response_model=VisaApplicationSchema)
async def get_visa_application(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get visa application by ID."""
    application = db.query(VisaApplication).filter(
        VisaApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visa application not found"
        )
    
    # TODO: Check if current_user has permission to view this application
    
    return application


@router.post("/", response_model=VisaApplicationSchema, status_code=status.HTTP_201_CREATED)
async def create_visa_application(
    application_in: VisaApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new visa application."""
    # TODO: Check if current_user has permission to create for this user
    
    application = VisaApplication(
        **application_in.model_dump(),
        created_by=current_user.id
    )
    
    db.add(application)
    db.commit()
    db.refresh(application)
    
    return application


@router.patch("/{application_id}", response_model=VisaApplicationSchema)
async def update_visa_application(
    application_id: str,
    application_update: VisaApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update visa application."""
    application = db.query(VisaApplication).filter(
        VisaApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visa application not found"
        )
    
    # TODO: Check if current_user has permission to update this application
    
    update_data = application_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(application, field, value)
    
    db.commit()
    db.refresh(application)
    
    return application


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_visa_application(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete visa application (admin only)."""
    application = db.query(VisaApplication).filter(
        VisaApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visa application not found"
        )
    
    # TODO: Check if current_user is admin
    
    db.delete(application)
    db.commit()
    
    return None
