"""API endpoints for Law Firms."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.law_firm import LawFirm
from app.schemas.law_firm import (
    LawFirmResponse, LawFirmCreate, LawFirmUpdate
)

router = APIRouter()


# ============================================================
# LAW FIRM ENDPOINTS
# ============================================================

@router.get("/", response_model=List[LawFirmResponse])
async def list_law_firms(
    skip: int = 0,
    limit: int = 100,
    is_active: bool = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all law firms."""
    query = db.query(LawFirm)
    
    if is_active is not None:
        query = query.filter(LawFirm.is_active == is_active)
    
    law_firms = query.offset(skip).limit(limit).all()
    return law_firms


@router.get("/{law_firm_id}", response_model=LawFirmResponse)
async def get_law_firm(
    law_firm_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get law firm by ID."""
    law_firm = db.query(LawFirm).filter(LawFirm.id == law_firm_id).first()
    if not law_firm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Law firm not found"
        )
    
    return law_firm


@router.post("/", response_model=LawFirmResponse, status_code=status.HTTP_201_CREATED)
async def create_law_firm(
    law_firm_in: LawFirmCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new law firm (admin/manager only)."""
    law_firm = LawFirm(**law_firm_in.model_dump())
    db.add(law_firm)
    db.commit()
    db.refresh(law_firm)
    return law_firm


@router.patch("/{law_firm_id}", response_model=LawFirmResponse)
async def update_law_firm(
    law_firm_id: str,
    law_firm_in: LawFirmUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update law firm information."""
    law_firm = db.query(LawFirm).filter(LawFirm.id == law_firm_id).first()
    if not law_firm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Law firm not found"
        )
    
    update_data = law_firm_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(law_firm, field, value)
    
    db.commit()
    db.refresh(law_firm)
    return law_firm


@router.delete("/{law_firm_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_law_firm(
    law_firm_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Soft delete law firm (set is_active=False)."""
    law_firm = db.query(LawFirm).filter(LawFirm.id == law_firm_id).first()
    if not law_firm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Law firm not found"
        )
    
    law_firm.is_active = False
    db.commit()
