"""API endpoints for Dependents."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.dependent import Dependent
from app.schemas.dependent import DependentResponse, DependentCreate, DependentUpdate

router = APIRouter()


@router.get("/", response_model=List[DependentResponse])
async def list_dependents(
    user_id: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all dependents, optionally filtered by user."""
    query = db.query(Dependent)
    
    if user_id:
        query = query.filter(Dependent.user_id == user_id)
    
    dependents = query.offset(skip).limit(limit).all()
    return dependents


@router.get("/{dependent_id}", response_model=DependentResponse)
async def get_dependent(
    dependent_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get dependent by ID."""
    dependent = db.query(Dependent).filter(Dependent.id == dependent_id).first()
    if not dependent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dependent not found"
        )
    
    return dependent


@router.post("/", response_model=DependentResponse, status_code=status.HTTP_201_CREATED)
async def create_dependent(
    dependent_in: DependentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new dependent."""
    # Verify user exists
    user = db.query(User).filter(User.id == dependent_in.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    dependent = Dependent(**dependent_in.model_dump())
    db.add(dependent)
    db.commit()
    db.refresh(dependent)
    return dependent


@router.patch("/{dependent_id}", response_model=DependentResponse)
async def update_dependent(
    dependent_id: str,
    dependent_in: DependentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update dependent information."""
    dependent = db.query(Dependent).filter(Dependent.id == dependent_id).first()
    if not dependent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dependent not found"
        )
    
    update_data = dependent_in.model_dump(exclude_unset=True)
    
    # If changing user, verify user exists
    if "user_id" in update_data:
        user = db.query(User).filter(User.id == update_data["user_id"]).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    
    for field, value in update_data.items():
        setattr(dependent, field, value)
    
    db.commit()
    db.refresh(dependent)
    return dependent


@router.delete("/{dependent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dependent(
    dependent_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete dependent."""
    dependent = db.query(Dependent).filter(Dependent.id == dependent_id).first()
    if not dependent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dependent not found"
        )
    
    db.delete(dependent)
    db.commit()
