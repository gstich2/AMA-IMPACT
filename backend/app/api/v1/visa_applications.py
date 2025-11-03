from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.visa import VisaApplication
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List visa applications (filtered by permissions)."""
    # TODO: Implement hierarchical filtering
    # Staff: only their own
    # Tech Lead: their reports
    # PM: entire contract
    # HR: assigned contracts
    # Admin: all
    
    applications = db.query(VisaApplication).offset(skip).limit(limit).all()
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
