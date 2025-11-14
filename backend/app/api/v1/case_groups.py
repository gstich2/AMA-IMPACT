"""
Case Group API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from datetime import datetime, timezone

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.case_group import CaseGroup, PathwayType
from app.models.user import User, UserRole
from app.models.beneficiary import Beneficiary
from app.models.department import Department
from app.models.audit import AuditLog, AuditAction
from app.schemas.case_group import (
    CaseGroupCreate,
    CaseGroupUpdate,
    CaseGroupResponse,
    CaseGroupWithApplications,
    CaseGroupSubmitForApproval,
    CaseGroupApprove,
    CaseGroupReject,
)
from app.schemas.timeline import TimelineResponse, TimelineEvent, TimelineEventType

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
    
    # Create audit log
    audit_log = AuditLog(
        user_id=current_user.id,
        action=AuditAction.CREATE,
        resource_type="case_group",
        resource_id=case_group.id,
        new_value={
            "case_type": case_group.case_type.value,
            "beneficiary_id": case_group.beneficiary_id,
            "status": case_group.status.value,
            "priority": case_group.priority.value,
            "approval_status": case_group.approval_status.value,
        }
    )
    db.add(audit_log)
    db.commit()
    
    return case_group


@router.get("/", response_model=List[CaseGroupResponse])
def list_case_groups(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    beneficiary_id: Optional[str] = None,
    case_type: Optional[PathwayType] = None,
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
    # Eagerly load relationships for list view
    query = db.query(CaseGroup).options(
        joinedload(CaseGroup.beneficiary).joinedload(Beneficiary.user).joinedload(User.department),
        joinedload(CaseGroup.responsible_party),
        joinedload(CaseGroup.created_by_manager),
    )
    
    # Apply role-based filtering
    if current_user.role == UserRole.BENEFICIARY:
        # Beneficiaries can only see their own case groups
        beneficiary = db.query(Beneficiary).filter(
            Beneficiary.user_id == current_user.id
        ).first()
        if not beneficiary:
            return []
        query = query.filter(CaseGroup.beneficiary_id == beneficiary.id)
    
    elif current_user.role in [UserRole.PM, UserRole.MANAGER]:
        # PM/Manager can see case groups for beneficiaries in their contract
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
        .options(
            joinedload(CaseGroup.petitions),
            joinedload(CaseGroup.beneficiary).joinedload(Beneficiary.user).joinedload(User.department),
            joinedload(CaseGroup.beneficiary).joinedload(Beneficiary.user).joinedload(User.reports_to),
            joinedload(CaseGroup.responsible_party).joinedload(User.department),
            joinedload(CaseGroup.created_by_manager).joinedload(User.department),
            joinedload(CaseGroup.approved_by_pm).joinedload(User.department),
            joinedload(CaseGroup.law_firm),
        )
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
    
    # Capture old values for audit
    old_values = {}
    update_data = case_group_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        old_values[field] = getattr(case_group, field).value if hasattr(getattr(case_group, field), 'value') else getattr(case_group, field)
        setattr(case_group, field, value)
    
    db.commit()
    db.refresh(case_group)
    
    # Create audit log if there were actual changes
    if update_data:
        new_values = {}
        for field in update_data.keys():
            new_values[field] = getattr(case_group, field).value if hasattr(getattr(case_group, field), 'value') else getattr(case_group, field)
        
        audit_log = AuditLog(
            user_id=current_user.id,
            action=AuditAction.UPDATE,
            resource_type="case_group",
            resource_id=case_group.id,
            old_value=old_values,
            new_value=new_values
        )
        db.add(audit_log)
        db.commit()
    
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
    for app in case_group.petitions:
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
    old_status = case_group.approval_status.value
    case_group.approval_status = ApprovalStatus.PENDING_PM_APPROVAL
    if submit_data.notes:
        case_group.notes = (case_group.notes or "") + f"\n[Manager submission notes]: {submit_data.notes}"
    
    # Get the contract's PM to notify
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
    
    # Create audit log
    audit_log = AuditLog(
        user_id=current_user.id,
        action=AuditAction.STATUS_CHANGED,
        resource_type="case_group",
        resource_id=case_group.id,
        old_value={"approval_status": old_status},
        new_value={"approval_status": ApprovalStatus.PENDING_PM_APPROVAL.value}
    )
    db.add(audit_log)
    db.commit()
    
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
    
    # Create audit log
    audit_log = AuditLog(
        user_id=current_user.id,
        action=AuditAction.STATUS_CHANGED,
        resource_type="case_group",
        resource_id=case_group.id,
        old_value={"approval_status": "PENDING_PM_APPROVAL"},
        new_value={
            "approval_status": ApprovalStatus.PM_APPROVED.value,
            "approved_by_pm_id": current_user.id,
            "pm_approval_date": approval_date.isoformat(),
            "assigned_hr_user_id": hr_user.id,
            "law_firm_id": law_firm.id,
        }
    )
    db.add(audit_log)
    db.commit()
    
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
    rejection_date = datetime.now(timezone.utc)
    case_group.approval_status = ApprovalStatus.PM_REJECTED
    case_group.approved_by_pm_id = current_user.id
    case_group.pm_approval_date = rejection_date
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
    
    # Create audit log
    audit_log = AuditLog(
        user_id=current_user.id,
        action=AuditAction.STATUS_CHANGED,
        resource_type="case_group",
        resource_id=case_group.id,
        old_value={"approval_status": "PENDING_PM_APPROVAL"},
        new_value={
            "approval_status": ApprovalStatus.PM_REJECTED.value,
            "approved_by_pm_id": current_user.id,
            "pm_approval_date": rejection_date.isoformat(),
            "rejection_reason": rejection_data.rejection_reason,
        }
    )
    db.add(audit_log)
    db.commit()
    
    return case_group


@router.get("/{case_group_id}/timeline", response_model=TimelineResponse)
def get_case_group_timeline(
    *,
    db: Session = Depends(get_db),
    case_group_id: str,
    current_user: User = Depends(get_current_active_user),
) -> TimelineResponse:
    """
    Get unified timeline for a case group.
    
    Combines:
    - Audit logs (case creation, updates, approvals)
    - Milestones from all visa applications
    - Completed todos
    
    Returns events sorted by timestamp (most recent first).
    """
    from app.models.audit import AuditLog
    from app.models.milestone import Milestone
    from app.models.todo import Todo
    from app.models.petition import Petition
    
    # Verify case group exists and user has access
    case_group = db.query(CaseGroup).filter(CaseGroup.id == case_group_id).first()
    if not case_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case group not found",
        )
    
    # Check permissions (same as get_case_group)
    if current_user.role == UserRole.BENEFICIARY:
        beneficiary = db.query(Beneficiary).filter(
            Beneficiary.user_id == current_user.id
        ).first()
        if not beneficiary or case_group.beneficiary_id != beneficiary.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this timeline",
            )
    elif current_user.role in [UserRole.PM, UserRole.MANAGER]:
        if case_group.beneficiary.user.contract_id != current_user.contract_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this timeline",
            )
    
    events = []
    
    # 1. Get audit logs for this case group
    audit_logs = (
        db.query(AuditLog)
        .filter(
            AuditLog.resource_type == "case_group",
            AuditLog.resource_id == case_group_id
        )
        .all()
    )
    
    for log in audit_logs:
        # Determine event type from action and new values
        event_type = TimelineEventType.CASE_UPDATED
        title = "Case Updated"
        description = None
        
        if log.action.value == "create":
            event_type = TimelineEventType.CASE_CREATED
            title = "Case Created"
            beneficiary_name = "Beneficiary"
            if case_group.beneficiary:
                beneficiary_name = f"{case_group.beneficiary.first_name or ''} {case_group.beneficiary.last_name or ''}".strip() or "Beneficiary"
            description = f"Case group created for {beneficiary_name}"
        elif log.action.value == "status_changed":
            if log.new_value and "approval_status" in log.new_value:
                approval_status = log.new_value["approval_status"]
                if approval_status == "PENDING_PM_APPROVAL":
                    event_type = TimelineEventType.SUBMITTED_FOR_APPROVAL
                    title = "Submitted for PM Approval"
                    description = "Case submitted to PM for review"
                elif approval_status == "PM_APPROVED":
                    event_type = TimelineEventType.APPROVED
                    title = "PM Approved Case"
                    hr_user_id = log.new_value.get("assigned_hr_user_id")
                    law_firm_id = log.new_value.get("law_firm_id")
                    if hr_user_id:
                        hr_user = db.query(User).filter(User.id == hr_user_id).first()
                        description = f"Case approved and assigned to {hr_user.full_name if hr_user else 'HR'}"
                elif approval_status == "PM_REJECTED":
                    event_type = TimelineEventType.REJECTED
                    title = "PM Rejected Case"
                    reason = log.new_value.get("rejection_reason", "No reason provided")
                    description = f"Reason: {reason}"
            else:
                event_type = TimelineEventType.STATUS_CHANGED
                title = "Status Changed"
        
        events.append(TimelineEvent(
            id=log.id,
            event_type=event_type,
            timestamp=log.created_at,
            user_id=log.user_id,
            user_name=log.user.full_name if log.user else None,
            user_email=log.user.email if log.user else None,
            title=title,
            description=description,
            old_values=log.old_value,
            new_values=log.new_value,
        ))
    
    # 2. Get milestones from all visa applications in this case group
    petition_app_ids = [app.id for app in case_group.petitions]
    if petition_app_ids:
        milestones = (
            db.query(Milestone)
            .filter(Milestone.petition_id.in_(petition_app_ids))
            .all()
        )
        
        for milestone in milestones:
            # Get visa application to show which application this milestone belongs to
            petition_app = db.query(Petition).filter(Petition.id == milestone.petition_id).first()
            
            # Skip milestones without a completed_date
            if not milestone.completed_date:
                continue
            
            events.append(TimelineEvent(
                id=milestone.id,
                event_type=TimelineEventType.MILESTONE,
                timestamp=datetime.combine(milestone.completed_date, datetime.min.time()),
                user_id=milestone.created_by,
                user_name=milestone.creator.full_name if milestone.creator else None,
                user_email=milestone.creator.email if milestone.creator else None,
                title=f"Milestone: {milestone.milestone_type.value.replace('_', ' ').title()}",
                description=milestone.description or (milestone.title if milestone.title else None),
                milestone_type=milestone.milestone_type.value,
                milestone_date=milestone.completed_date,
                details={
                    "petition_type": petition_app.petition_type.value if petition_app else None,
                }
            ))
    
    # 3. Get completed todos for this case group
    todos = (
        db.query(Todo)
        .filter(
            Todo.case_group_id == case_group_id,
            Todo.status == "DONE"  # Only completed todos
        )
        .all()
    )
    
    for todo in todos:
        events.append(TimelineEvent(
            id=todo.id,
            event_type=TimelineEventType.TODO_COMPLETED,
            timestamp=todo.completed_at if todo.completed_at else todo.updated_at,
            user_id=todo.assigned_to_user_id,
            user_name=todo.assigned_to_user.full_name if todo.assigned_to_user else None,
            user_email=todo.assigned_to_user.email if todo.assigned_to_user else None,
            title=f"Completed: {todo.title}",
            description=todo.description,
            todo_title=todo.title,
            todo_status=todo.status.value,
        ))
    
    # Sort all events by timestamp (most recent first)
    events.sort(key=lambda x: x.timestamp, reverse=True)
    
    return TimelineResponse(
        case_group_id=case_group_id,
        total_events=len(events),
        events=events
    )


@router.get("/{case_group_id}/progress")
def get_case_group_progress(
    *,
    db: Session = Depends(get_db),
    case_group_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """
    Calculate progress for ALL visa applications in a case group.
    
    Each visa application has its own pipeline based on petition_type.
    Case group progress is the aggregate of all visa application progresses.
    
    Returns:
    - overall_percentage: Overall case group progress (weighted average of all petitions)
    - overall_stage: Description of overall case status
    - petitions: Array of visa apps with individual progress and pipelines
    
    Permissions:
    - BENEFICIARY: Can view their own case group progress
    - PM/HR/MANAGER: Can view case groups in their contract
    - ADMIN: Can view any case group progress
    """
    from app.config.petition_pipelines import get_pipeline_for_petition_type
    from app.models.milestone import Milestone
    
    # Get case group and check permissions
    case_group = db.query(CaseGroup).filter(CaseGroup.id == case_group_id).first()
    
    if not case_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case group not found",
        )
    
    # Permission checks (same as get_case_group)
    if current_user.role == UserRole.BENEFICIARY:
        # Beneficiaries can only view their own cases
        beneficiary = db.query(Beneficiary).filter(
            Beneficiary.user_id == current_user.id
        ).first()
        if not beneficiary or case_group.beneficiary_id != beneficiary.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own case progress",
            )
    elif current_user.role in [UserRole.PM, UserRole.HR, UserRole.MANAGER]:
        # PM/HR/MANAGER can only view cases in their contract
        beneficiary = db.query(Beneficiary).filter(
            Beneficiary.id == case_group.beneficiary_id
        ).first()
        if not beneficiary or beneficiary.user.contract_id != current_user.contract_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view case groups in your contract",
            )
    # ADMIN can view all
    
    if not case_group.petitions:
        return {
            "case_group_id": case_group_id,
            "overall_percentage": 0,
            "overall_stage": "No visa applications",
            "petitions": []
        }
    
    visa_progress_list = []
    total_progress = 0
    
    # Calculate progress for EACH visa application
    for petition_app in case_group.petitions:
        # Get pipeline config for THIS visa type
        pipeline_config = get_pipeline_for_petition_type(petition_app.petition_type)
        
        # Get milestones for THIS visa application only
        milestones = db.query(Milestone).filter(
            Milestone.petition_id == petition_app.id
        ).all()
        
        # Build set of completed milestone types
        completed_milestone_types = {m.milestone_type for m in milestones}
        
        # Calculate progress for this visa
        max_weight = 0
        current_stage_label = "Not Started"
        next_stage = None
        pipeline_with_status = []
        
        for stage in pipeline_config["stages"]:
            milestone_type = stage["milestone_type"]
            is_completed = milestone_type in completed_milestone_types
            
            if is_completed and stage["weight"] > max_weight:
                max_weight = stage["weight"]
                current_stage_label = stage["label"]
            
            # Find completion date
            completion_date = None
            if is_completed:
                for m in milestones:
                    if m.milestone_type == milestone_type:
                        completion_date = m.completed_date.isoformat() if m.completed_date else None
                        break
            
            pipeline_with_status.append({
                "order": stage["order"],
                "milestone_type": milestone_type.value,
                "label": stage["label"],
                "description": stage.get("description"),
                "weight": stage["weight"],
                "required": stage["required"],
                "terminal": stage.get("terminal", False),
                "completed": is_completed,
                "completion_date": completion_date,
            })
            
            # Track next incomplete required stage
            if not is_completed and stage["required"] and next_stage is None:
                next_stage = stage["label"]
        
        visa_progress_list.append({
            "petition_id": petition_app.id,
            "petition_type": petition_app.petition_type.value,
            "visa_status": petition_app.status.value if petition_app.status else None,
            "case_status": petition_app.case_status.value if petition_app.case_status else None,
            "percentage": max_weight,
            "current_stage": current_stage_label,
            "next_stage": next_stage,
            "pipeline_name": pipeline_config["name"],
            "pipeline": pipeline_with_status,
        })
        
        total_progress += max_weight
    
    # Overall case group progress = average of all visa apps
    overall_percentage = total_progress // len(case_group.petitions) if case_group.petitions else 0
    
    # Determine overall stage description
    if overall_percentage == 100:
        overall_stage = "Complete"
    elif overall_percentage >= 80:
        overall_stage = "Nearing Completion"
    elif overall_percentage >= 50:
        overall_stage = "In Progress"
    elif overall_percentage >= 25:
        overall_stage = "Early Stage"
    else:
        overall_stage = "Getting Started"
    
    return {
        "case_group_id": case_group_id,
        "overall_percentage": overall_percentage,
        "overall_stage": overall_stage,
        "petitions": visa_progress_list,
    }
