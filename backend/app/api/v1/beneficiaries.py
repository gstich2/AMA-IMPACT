"""API endpoints for Beneficiary management."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.beneficiary import Beneficiary
from app.schemas.beneficiary import (
    BeneficiaryCreate, BeneficiaryUpdate, BeneficiaryResponse
)

router = APIRouter()


@router.post("/", response_model=BeneficiaryResponse, status_code=status.HTTP_201_CREATED)
def create_beneficiary(
    beneficiary_in: BeneficiaryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new beneficiary (foreign national with visa case).
    Requires: ADMIN, HR, PM, or MANAGER role.
    """
    # Check permissions
    if current_user.role.value not in ["ADMIN", "HR", "PM", "MANAGER"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only ADMIN, HR, PM, or MANAGER can create beneficiaries"
        )
    
    # If user_id provided, verify it exists and not already linked
    if beneficiary_in.user_id:
        existing_user = db.query(User).filter(User.id == beneficiary_in.user_id).first()
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {beneficiary_in.user_id} not found"
            )
        
        # Check if user already has a beneficiary record
        existing_beneficiary = db.query(Beneficiary).filter(Beneficiary.user_id == beneficiary_in.user_id).first()
        if existing_beneficiary:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User {beneficiary_in.user_id} already has a beneficiary record"
            )
    
    # Create beneficiary
    beneficiary = Beneficiary(**beneficiary_in.model_dump())
    db.add(beneficiary)
    db.commit()
    db.refresh(beneficiary)
    
    return beneficiary


@router.get("/", response_model=List[BeneficiaryResponse])
def list_beneficiaries(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List all beneficiaries.
    - ADMIN, HR, PM, MANAGER: See all beneficiaries
    - BENEFICIARY: See only their own record
    """
    if current_user.role.value in ["ADMIN", "HR", "PM", "MANAGER"]:
        # See all beneficiaries
        beneficiaries = db.query(Beneficiary).offset(skip).limit(limit).all()
    else:
        # BENEFICIARY role: see only their own record
        beneficiaries = db.query(Beneficiary).filter(Beneficiary.user_id == current_user.id).all()
    
    return beneficiaries


@router.get("/{beneficiary_id}", response_model=BeneficiaryResponse)
def get_beneficiary(
    beneficiary_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific beneficiary.
    - ADMIN, HR, PM, MANAGER: Can view any beneficiary
    - BENEFICIARY: Can only view their own record
    """
    beneficiary = db.query(Beneficiary).filter(Beneficiary.id == beneficiary_id).first()
    
    if not beneficiary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Beneficiary with id {beneficiary_id} not found"
        )
    
    # Check permissions
    if current_user.role.value == "BENEFICIARY" and beneficiary.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own beneficiary record"
        )
    
    return beneficiary


@router.patch("/{beneficiary_id}", response_model=BeneficiaryResponse)
def update_beneficiary(
    beneficiary_id: str,
    beneficiary_in: BeneficiaryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a beneficiary's information.
    - ADMIN, HR, PM, MANAGER: Can update any beneficiary
    - BENEFICIARY: Can only update their own record
    """
    beneficiary = db.query(Beneficiary).filter(Beneficiary.id == beneficiary_id).first()
    
    if not beneficiary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Beneficiary with id {beneficiary_id} not found"
        )
    
    # Check permissions
    if current_user.role.value == "BENEFICIARY" and beneficiary.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own beneficiary record"
        )
    
    # Update fields
    update_data = beneficiary_in.model_dump(exclude_unset=True)
    
    # If changing user_id, verify new user exists and not already linked
    if "user_id" in update_data and update_data["user_id"] != beneficiary.user_id:
        if update_data["user_id"]:
            existing_user = db.query(User).filter(User.id == update_data["user_id"]).first()
            if not existing_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with id {update_data['user_id']} not found"
                )
            
            existing_beneficiary = db.query(Beneficiary).filter(
                Beneficiary.user_id == update_data["user_id"],
                Beneficiary.id != beneficiary_id
            ).first()
            if existing_beneficiary:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User {update_data['user_id']} already has a beneficiary record"
                )
    
    for field, value in update_data.items():
        setattr(beneficiary, field, value)
    
    db.commit()
    db.refresh(beneficiary)
    
    return beneficiary


@router.delete("/{beneficiary_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_beneficiary(
    beneficiary_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a beneficiary.
    Requires: ADMIN role only.
    """
    # Check permissions
    if current_user.role.value != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only ADMIN can delete beneficiaries"
        )
    
    beneficiary = db.query(Beneficiary).filter(Beneficiary.id == beneficiary_id).first()
    
    if not beneficiary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Beneficiary with id {beneficiary_id} not found"
        )
    
    db.delete(beneficiary)
    db.commit()
    
    return None
