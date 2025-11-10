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
    CaseGroupSubmitForApproval,
    CaseGroupApprove,
    CaseGroupReject,
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
        if beneficiary.user.contract_id != current_user.contract_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot create case groups for beneficiaries outside your contract",
            )
    
    case_group = CaseGroup(**case_group_in.dict())
    # Set the creator (manager who created this case group)
    case_group.created_by_manager_id = current_user.id
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
    approval_status: Optional[str] = None,
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
        # PM/Manager can see case groups for beneficiaries in their contract
        from app.models.beneficiary import Beneficiary
        beneficiary_ids = db.query(Beneficiary.id).join(User).filter(
            User.contract_id == current_user.contract_id
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
    if approval_status:
        query = query.filter(CaseGroup.approval_status == approval_status)
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
        # Verify beneficiary is in same contract
        if case_group.beneficiary.user.contract_id != current_user.contract_id:
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
        if case_group.beneficiary.user.contract_id != current_user.contract_id:
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
        if case_group.beneficiary.user.contract_id != current_user.contract_id:
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


@router.post("/{case_group_id}/submit-for-approval", response_model=CaseGroupResponse)
def submit_case_group_for_approval(
    *,
    db: Session = Depends(get_db),
    case_group_id: str,
    submit_data: CaseGroupSubmitForApproval,
    current_user: User = Depends(get_current_active_user),
) -> CaseGroup:
    """
    Submit a case group for PM approval.
    
    Permissions:
    - MANAGER: Can submit their own draft case groups
    - ADMIN, HR, PM: Cannot submit (they don't create drafts)
    - BENEFICIARY: Cannot submit
    
    Workflow:
    - Case group must be in DRAFT status
    - Changes approval_status to PENDING_PM_APPROVAL
    - Notifies the contract's PM
    """
    from app.models.case_group import ApprovalStatus
    from app.models.contract import Contract
    from app.models.notification import Notification, NotificationType
    
    if current_user.role not in [UserRole.MANAGER, UserRole.ADMIN, UserRole.HR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can submit case groups for approval",
        )
    
    case_group = db.query(CaseGroup).filter(CaseGroup.id == case_group_id).first()
    
    if not case_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case group not found",
        )
    
    # Verify the manager created this case group
    if case_group.created_by_manager_id != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.HR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only submit case groups you created",
        )
    
    # Check if case group is in DRAFT status
    if case_group.approval_status != ApprovalStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Case group is already {case_group.approval_status.value}, cannot submit again",
        )
    
    # Update approval status
    case_group.approval_status = ApprovalStatus.PENDING_PM_APPROVAL
    if submit_data.notes:
        case_group.notes = (case_group.notes or "") + f"\n[Manager submission notes]: {submit_data.notes}"
    
    # Get the contract's PM to notify
    from app.models.beneficiary import Beneficiary
    beneficiary = db.query(Beneficiary).filter(Beneficiary.id == case_group.beneficiary_id).first()
    if beneficiary and beneficiary.user.contract_id:
        contract = db.query(Contract).filter(Contract.id == beneficiary.user.contract_id).first()
        if contract and contract.manager_user_id:
            # Create notification for PM
            notification = Notification(
                user_id=contract.manager_user_id,
                type=NotificationType.STATUS_CHANGED,
                title="New Case Group Pending Approval",
                message=f"Case group for {beneficiary.user.full_name} ({case_group.case_type.value}) submitted by {current_user.full_name}",
                link=f"/cases/{case_group.id}",
            )
            db.add(notification)
    
    db.commit()
    db.refresh(case_group)
    return case_group


@router.post("/{case_group_id}/approve", response_model=CaseGroupResponse)
def approve_case_group(
    *,
    db: Session = Depends(get_db),
    case_group_id: str,
    approval_data: CaseGroupApprove,
    current_user: User = Depends(get_current_active_user),
) -> CaseGroup:
    """
    PM approves a case group.
    
    Permissions:
    - PM: Can approve case groups in their contract
    - ADMIN: Can approve any case group
    - Others: Cannot approve
    
    Workflow:
    - Case group must be in PENDING_PM_APPROVAL status
    - PM must select an HR user and law firm during approval
    - Changes approval_status to PM_APPROVED
    - Sets approved_by_pm_id and pm_approval_date
    - Assigns case to selected HR user (responsible_party_id)
    - Assigns selected law firm (law_firm_id)
    - Auto-creates 2 HR action items (todos):
      1. Schedule Pre-Filing Meeting (HR + Manager + Beneficiary) - due 7 days after approval
      2. Schedule Law Firm Consultation - due 14 days after approval
    """
    from app.models.case_group import ApprovalStatus
    from app.models.todo import Todo, TodoStatus, TodoPriority
    from app.models.contract import Contract
    from app.models.notification import Notification, NotificationType
    from datetime import datetime, timezone
    
    if current_user.role not in [UserRole.PM, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only PMs can approve case groups",
        )
    
    case_group = db.query(CaseGroup).filter(CaseGroup.id == case_group_id).first()
    
    if not case_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case group not found",
        )
    
    # Verify PM is managing the correct contract
    if current_user.role == UserRole.PM:
        from app.models.beneficiary import Beneficiary
        beneficiary = db.query(Beneficiary).filter(Beneficiary.id == case_group.beneficiary_id).first()
        if not beneficiary or beneficiary.user.contract_id != current_user.contract_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only approve case groups in your contract",
            )
    
    # Check if case group is in PENDING_PM_APPROVAL status
    if case_group.approval_status != ApprovalStatus.PENDING_PM_APPROVAL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Case group is {case_group.approval_status.value}, cannot approve",
        )
    
    # Verify assigned HR user exists and is in the same contract
    from app.models.law_firm import LawFirm
    hr_user = db.query(User).filter(
        User.id == approval_data.assigned_hr_user_id,
        User.role == UserRole.HR,
        User.is_active == True
    ).first()
    
    if not hr_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned HR user not found or not an active HR user",
        )
    
    # Verify HR user is in the same contract
    if current_user.role == UserRole.PM and hr_user.contract_id != current_user.contract_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot assign HR user from a different contract",
        )
    
    # Verify law firm exists
    law_firm = db.query(LawFirm).filter(LawFirm.id == approval_data.law_firm_id).first()
    if not law_firm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Selected law firm not found",
        )
    
    # Update approval fields
    approval_date = datetime.now(timezone.utc)
    case_group.approval_status = ApprovalStatus.PM_APPROVED
    case_group.approved_by_pm_id = current_user.id
    case_group.pm_approval_date = approval_date
    case_group.pm_approval_notes = approval_data.approval_notes
    case_group.responsible_party_id = hr_user.id  # Assign case to HR user
    case_group.law_firm_id = law_firm.id  # Assign law firm to case
    
    # Create 2 specific HR action items with fixed due dates
    from datetime import timedelta
    
    # Todo 1: Pre-filing meeting - due 7 days after approval
    todo_1_due_date = approval_date + timedelta(days=7)
    todo_1 = Todo(
        title="Schedule Pre-Filing Meeting",
        description=f"Schedule pre-filing meeting with HR, Manager ({case_group.created_by_manager.full_name if case_group.created_by_manager else 'Manager'}), and Beneficiary ({case_group.beneficiary.user.full_name}) for {case_group.case_type.value} case. Discuss case requirements, timeline, and required documents.",
        assigned_to_user_id=hr_user.id,
        created_by_user_id=current_user.id,
        case_group_id=case_group.id,
        beneficiary_id=case_group.beneficiary_id,
        priority=TodoPriority.HIGH,
        status=TodoStatus.TODO,
        due_date=todo_1_due_date,
    )
    
    # Todo 2: Law firm consultation - due 14 days after approval
    todo_2_due_date = approval_date + timedelta(days=14)
    todo_2 = Todo(
        title="Schedule Law Firm Consultation",
        description=f"Schedule consultation meeting with {law_firm.name} for {case_group.beneficiary.user.full_name} - {case_group.case_type.value} case. Coordinate document submission and case filing timeline.\n\nLaw Firm Contact: {law_firm.contact_person or 'N/A'}\nLaw Firm Email: {law_firm.email or 'N/A'}\nLaw Firm Phone: {law_firm.phone or 'N/A'}",
        assigned_to_user_id=hr_user.id,
        created_by_user_id=current_user.id,
        case_group_id=case_group.id,
        beneficiary_id=case_group.beneficiary_id,
        priority=TodoPriority.HIGH,
        status=TodoStatus.TODO,
        due_date=todo_2_due_date,
    )
    
    db.add_all([todo_1, todo_2])
    
    # Notify HR user
    notification = Notification(
        user_id=hr_user.id,
        type=NotificationType.STATUS_CHANGED,
        title="Case Group Approved - Action Required",
        message=f"Case group for {case_group.beneficiary.user.full_name} approved. 2 action items assigned to you.",
        link=f"/cases/{case_group.id}",
    )
    db.add(notification)
    
    # Notify the manager who created it
    if case_group.created_by_manager_id:
        manager_notification = Notification(
            user_id=case_group.created_by_manager_id,
            type=NotificationType.STATUS_CHANGED,
            title="Your Case Group Was Approved",
            message=f"Case group for {case_group.beneficiary.user.full_name} ({case_group.case_type.value}) has been approved by PM.",
            link=f"/cases/{case_group.id}",
        )
        db.add(manager_notification)
    
    db.commit()
    db.refresh(case_group)
    return case_group


@router.post("/{case_group_id}/reject", response_model=CaseGroupResponse)
def reject_case_group(
    *,
    db: Session = Depends(get_db),
    case_group_id: str,
    rejection_data: CaseGroupReject,
    current_user: User = Depends(get_current_active_user),
) -> CaseGroup:
    """
    PM rejects a case group.
    
    Permissions:
    - PM: Can reject case groups in their contract
    - ADMIN: Can reject any case group
    - Others: Cannot reject
    
    Workflow:
    - Case group must be in PENDING_PM_APPROVAL status
    - Changes approval_status to PM_REJECTED
    - Sets approved_by_pm_id and pm_approval_date
    - Records rejection reason in pm_approval_notes
    - Notifies the manager who created it
    - Case is closed, manager must create new case group if needed
    """
    from app.models.case_group import ApprovalStatus
    from app.models.notification import Notification, NotificationType
    from datetime import datetime, timezone
    
    if current_user.role not in [UserRole.PM, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only PMs can reject case groups",
        )
    
    case_group = db.query(CaseGroup).filter(CaseGroup.id == case_group_id).first()
    
    if not case_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case group not found",
        )
    
    # Verify PM is managing the correct contract
    if current_user.role == UserRole.PM:
        from app.models.beneficiary import Beneficiary
        beneficiary = db.query(Beneficiary).filter(Beneficiary.id == case_group.beneficiary_id).first()
        if not beneficiary or beneficiary.user.contract_id != current_user.contract_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only reject case groups in your contract",
            )
    
    # Check if case group is in PENDING_PM_APPROVAL status
    if case_group.approval_status != ApprovalStatus.PENDING_PM_APPROVAL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Case group is {case_group.approval_status.value}, cannot reject",
        )
    
    # Update approval fields
    case_group.approval_status = ApprovalStatus.PM_REJECTED
    case_group.approved_by_pm_id = current_user.id
    case_group.pm_approval_date = datetime.now(timezone.utc)
    case_group.pm_approval_notes = f"REJECTED: {rejection_data.rejection_reason}"
    
    # Notify the manager who created it
    if case_group.created_by_manager_id:
        notification = Notification(
            user_id=case_group.created_by_manager_id,
            type=NotificationType.STATUS_CHANGED,
            title="Case Group Rejected",
            message=f"Your case group for {case_group.beneficiary.user.full_name} was rejected. Reason: {rejection_data.rejection_reason}",
            link=f"/cases/{case_group.id}",
        )
        db.add(notification)
    
    db.commit()
    db.refresh(case_group)
    return case_group
