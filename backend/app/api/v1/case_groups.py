"""
Case Group API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.case_group import CaseGroup, CaseType
from app.models.user import User, UserRole
from app.schemas.case_group import (
    CaseGroupCreate,
    CaseGroupUpdate,
    CaseGroupResponse,
    CaseGroupWithApplications,
)

router = APIRouter()


@router.post("/", response_model=CaseGroupResponse, status_code=status.HTTP_201_CREATED)
def create_case_group(
    *,
    db: Session = Depends(get_db),
    case_group_in: CaseGroupCreate,
    current_user: User = Depends(get_current_active_user),
) -> CaseGroup:
    """
    Create a new case group.
    
    Permissions:
    - ADMIN, HR: Can create case groups for any beneficiary
    - PM, MANAGER: Can create case groups for beneficiaries in their organization
    - BENEFICIARY: Cannot create case groups
    """
    if current_user.role == UserRole.BENEFICIARY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Beneficiaries cannot create case groups",
        )
    
    # If user is PM/MANAGER, verify beneficiary is in same organization
    if current_user.role in [UserRole.PM, UserRole.MANAGER]:
        from app.models.beneficiary import Beneficiary
        beneficiary = db.query(Beneficiary).filter(
            Beneficiary.id == case_group_in.beneficiary_id
        ).first()
        if not beneficiary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Beneficiary not found",
            )
        if beneficiary.user.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot create case groups for beneficiaries outside your organization",
            )
    
    case_group = CaseGroup(**case_group_in.dict())
    db.add(case_group)
    db.commit()
    db.refresh(case_group)
    return case_group


@router.get("/", response_model=List[CaseGroupResponse])
def list_case_groups(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    beneficiary_id: Optional[str] = None,
    case_type: Optional[CaseType] = None,
    status: Optional[str] = None,
    responsible_party_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[CaseGroup]:
    """
    List case groups with optional filters.
    
    Permissions:
    - ADMIN, HR: Can view all case groups
    - PM, MANAGER: Can view case groups for beneficiaries in their organization
    - BENEFICIARY: Can only view their own case groups
    """
    query = db.query(CaseGroup)
    
    # Apply role-based filtering
    if current_user.role == UserRole.BENEFICIARY:
        # Beneficiaries can only see their own case groups
        from app.models.beneficiary import Beneficiary
        beneficiary = db.query(Beneficiary).filter(
            Beneficiary.user_id == current_user.id
        ).first()
        if not beneficiary:
            return []
        query = query.filter(CaseGroup.beneficiary_id == beneficiary.id)
    
    elif current_user.role in [UserRole.PM, UserRole.MANAGER]:
        # PM/Manager can see case groups for beneficiaries in their organization
        from app.models.beneficiary import Beneficiary
        beneficiary_ids = db.query(Beneficiary.id).join(User).filter(
            User.organization_id == current_user.organization_id
        ).all()
        beneficiary_ids = [b_id for (b_id,) in beneficiary_ids]
        query = query.filter(CaseGroup.beneficiary_id.in_(beneficiary_ids))
    
    # Apply optional filters
    if beneficiary_id:
        query = query.filter(CaseGroup.beneficiary_id == beneficiary_id)
    if case_type:
        query = query.filter(CaseGroup.case_type == case_type)
    if status:
        query = query.filter(CaseGroup.status == status)
    if responsible_party_id:
        query = query.filter(CaseGroup.responsible_party_id == responsible_party_id)
    
    case_groups = query.offset(skip).limit(limit).all()
    return case_groups


@router.get("/{case_group_id}", response_model=CaseGroupWithApplications)
def get_case_group(
    *,
    db: Session = Depends(get_db),
    case_group_id: str,
    current_user: User = Depends(get_current_active_user),
) -> CaseGroup:
    """
    Get a specific case group with all its applications.
    
    Permissions:
    - ADMIN, HR: Can view any case group
    - PM, MANAGER: Can view case groups for beneficiaries in their organization
    - BENEFICIARY: Can only view their own case groups
    """
    case_group = (
        db.query(CaseGroup)
        .options(joinedload(CaseGroup.applications))
        .filter(CaseGroup.id == case_group_id)
        .first()
    )
    
    if not case_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case group not found",
        )
    
    # Check permissions
    if current_user.role == UserRole.BENEFICIARY:
        from app.models.beneficiary import Beneficiary
        beneficiary = db.query(Beneficiary).filter(
            Beneficiary.user_id == current_user.id
        ).first()
        if not beneficiary or case_group.beneficiary_id != beneficiary.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this case group",
            )
    
    elif current_user.role in [UserRole.PM, UserRole.MANAGER]:
        # Verify beneficiary is in same organization
        if case_group.beneficiary.user.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this case group",
            )
    
    return case_group


@router.patch("/{case_group_id}", response_model=CaseGroupResponse)
def update_case_group(
    *,
    db: Session = Depends(get_db),
    case_group_id: str,
    case_group_in: CaseGroupUpdate,
    current_user: User = Depends(get_current_active_user),
) -> CaseGroup:
    """
    Update a case group.
    
    Permissions:
    - ADMIN, HR: Can update any case group
    - PM, MANAGER: Can update case groups for beneficiaries in their organization
    - BENEFICIARY: Cannot update case groups
    """
    if current_user.role == UserRole.BENEFICIARY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Beneficiaries cannot update case groups",
        )
    
    case_group = db.query(CaseGroup).filter(CaseGroup.id == case_group_id).first()
    
    if not case_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case group not found",
        )
    
    # Check permissions for PM/Manager
    if current_user.role in [UserRole.PM, UserRole.MANAGER]:
        if case_group.beneficiary.user.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this case group",
            )
    
    # Update only provided fields
    update_data = case_group_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(case_group, field, value)
    
    db.commit()
    db.refresh(case_group)
    return case_group


@router.delete("/{case_group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_case_group(
    *,
    db: Session = Depends(get_db),
    case_group_id: str,
    current_user: User = Depends(get_current_active_user),
) -> None:
    """
    Delete a case group.
    
    Note: This is a soft delete (sets is_deleted=True).
    Applications in the case group are not deleted, but are unlinked (case_group_id set to NULL).
    
    Permissions:
    - ADMIN, HR: Can delete any case group
    - PM, MANAGER: Can delete case groups for beneficiaries in their organization
    - BENEFICIARY: Cannot delete case groups
    """
    if current_user.role == UserRole.BENEFICIARY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Beneficiaries cannot delete case groups",
        )
    
    case_group = db.query(CaseGroup).filter(CaseGroup.id == case_group_id).first()
    
    if not case_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case group not found",
        )
    
    # Check permissions for PM/Manager
    if current_user.role in [UserRole.PM, UserRole.MANAGER]:
        if case_group.beneficiary.user.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this case group",
            )
    
    # Soft delete
    case_group.is_deleted = True
    
    # Unlink applications from this case group
    for app in case_group.applications:
        app.case_group_id = None
    
    db.commit()
    return None
