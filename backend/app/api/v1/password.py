"""
Password management endpoints
Handles user invitation, password reset, and password changes
"""
from datetime import datetime, timedelta
from typing import Optional
import secrets
import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, get_current_user
from app.models.user import User, UserRole
from app.schemas.password import (
    InviteUserRequest,
    InviteUserResponse,
    AcceptInvitationRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    ChangePasswordRequest,
    PasswordResetResponse,
    ResetPasswordLimitRequest,
    PasswordChangeStatus
)

router = APIRouter()


def generate_token() -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(32)


def parse_password_change_count(count_str: str) -> tuple[int, Optional[datetime]]:
    """
    Parse password change count string format: "count|timestamp"
    Returns (count, timestamp)
    """
    if not count_str or count_str == "0":
        return 0, None
    
    parts = count_str.split("|")
    count = int(parts[0])
    timestamp = datetime.fromisoformat(parts[1]) if len(parts) > 1 and parts[1] else None
    return count, timestamp


def format_password_change_count(count: int, timestamp: Optional[datetime] = None) -> str:
    """
    Format password change count as "count|timestamp"
    """
    if timestamp:
        return f"{count}|{timestamp.isoformat()}"
    return f"{count}|"


def can_change_password(user: User) -> tuple[bool, str, int]:
    """
    Check if user can change password (max 2 changes per 24 hours)
    Returns (can_change, message, changes_remaining)
    """
    count, timestamp = parse_password_change_count(user.password_change_count)
    
    # If no timestamp or more than 24 hours ago, reset the count
    if not timestamp or datetime.utcnow() - timestamp > timedelta(hours=24):
        return True, "You can change your password", 2
    
    # Check if under limit
    if count < 2:
        return True, f"You can change your password ({2 - count} changes remaining in 24h period)", 2 - count
    
    # Limit exceeded
    time_until_reset = timestamp + timedelta(hours=24) - datetime.utcnow()
    hours = int(time_until_reset.total_seconds() // 3600)
    minutes = int((time_until_reset.total_seconds() % 3600) // 60)
    return False, f"Password change limit exceeded. Try again in {hours}h {minutes}m", 0


@router.post("/invite-user", response_model=InviteUserResponse)
async def invite_user(
    invite_data: InviteUserRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Invite a new user (Admin or HR only)
    Generates invitation token and sends email
    """
    # Check permissions
    if current_user.role not in [UserRole.ADMIN, UserRole.HR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and HR can invite users"
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == invite_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Validate role and contract requirements
    role = UserRole(invite_data.role)
    if role in [UserRole.STAFF, UserRole.TECH_LEAD, UserRole.PROGRAM_MANAGER] and not invite_data.contract_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Contract ID is required for {role.value} role"
        )
    
    # Generate invitation token
    invitation_token = generate_token()
    invitation_expires = datetime.utcnow() + timedelta(days=7)  # Token valid for 7 days
    
    # Create user with temporary password (will be forced to change)
    temp_password = secrets.token_urlsafe(16)
    new_user = User(
        email=invite_data.email,
        hashed_password=get_password_hash(temp_password),
        full_name=invite_data.full_name,
        phone=invite_data.phone,
        role=role,
        contract_id=invite_data.contract_id,
        reports_to_id=invite_data.reports_to_id,
        invitation_token=invitation_token,
        invitation_token_expires=invitation_expires,
        invitation_accepted=False,
        force_password_change=True,
        password_change_count="0|"
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # TODO: Send email with invitation link
    # For now, return the token in response for testing
    invitation_link = f"http://localhost:3000/accept-invitation?token={invitation_token}"
    
    return InviteUserResponse(
        message="Invitation sent successfully",
        user_id=str(new_user.id),
        email=new_user.email,
        invitation_sent=True,
        invitation_link=invitation_link
    )


@router.post("/accept-invitation", response_model=PasswordResetResponse)
async def accept_invitation(
    accept_data: AcceptInvitationRequest,
    db: Session = Depends(get_db)
):
    """
    Accept invitation and set initial password
    """
    # Find user by invitation token
    user = db.query(User).filter(
        User.invitation_token == accept_data.token,
        User.invitation_accepted == False
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or already used invitation token"
        )
    
    # Check if token expired
    if user.invitation_token_expires and datetime.utcnow() > user.invitation_token_expires:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation token has expired"
        )
    
    # Set password and mark invitation as accepted
    user.hashed_password = get_password_hash(accept_data.password)
    user.invitation_accepted = True
    user.invitation_token = None
    user.invitation_token_expires = None
    user.force_password_change = False
    user.password_changed_at = datetime.utcnow()
    user.password_change_count = "0|"
    
    db.commit()
    
    return PasswordResetResponse(
        message="Password set successfully. You can now log in.",
        success=True
    )


@router.post("/reset-password-request", response_model=PasswordResetResponse)
async def request_password_reset(
    reset_data: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Request password reset - sends email with reset token
    Rate limited to 2 requests per 24 hours
    """
    user = db.query(User).filter(User.email == reset_data.email).first()
    
    if not user:
        # Don't reveal if user exists
        return PasswordResetResponse(
            message="If the email exists, a password reset link has been sent.",
            success=True
        )
    
    # Check rate limit
    can_change, message, remaining = can_change_password(user)
    if not can_change:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=message
        )
    
    # Generate reset token
    reset_token = generate_token()
    reset_expires = datetime.utcnow() + timedelta(hours=1)  # Token valid for 1 hour
    
    user.password_reset_token = reset_token
    user.password_reset_token_expires = reset_expires
    
    # Increment counter
    count, timestamp = parse_password_change_count(user.password_change_count)
    if not timestamp or datetime.utcnow() - timestamp > timedelta(hours=24):
        # Reset counter if 24h passed
        user.password_change_count = format_password_change_count(1, datetime.utcnow())
    else:
        # Increment existing counter
        user.password_change_count = format_password_change_count(count + 1, timestamp)
    
    db.commit()
    
    # TODO: Send email with reset link
    # For now, log the token (in production, only send via email)
    reset_link = f"http://localhost:3000/reset-password?token={reset_token}"
    print(f"Password reset link for {user.email}: {reset_link}")
    
    return PasswordResetResponse(
        message="If the email exists, a password reset link has been sent.",
        success=True
    )


@router.post("/reset-password", response_model=PasswordResetResponse)
async def reset_password(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    Reset password using token from email
    """
    user = db.query(User).filter(
        User.password_reset_token == reset_data.token
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Check if token expired
    if user.password_reset_token_expires and datetime.utcnow() > user.password_reset_token_expires:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired"
        )
    
    # Set new password
    user.hashed_password = get_password_hash(reset_data.new_password)
    user.password_reset_token = None
    user.password_reset_token_expires = None
    user.password_changed_at = datetime.utcnow()
    user.force_password_change = False
    
    db.commit()
    
    return PasswordResetResponse(
        message="Password reset successfully",
        success=True
    )


@router.post("/change-password", response_model=PasswordResetResponse)
async def change_password(
    change_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change password for authenticated user
    Rate limited to 2 changes per 24 hours
    """
    # Verify current password
    if not verify_password(change_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Check rate limit
    can_change, message, remaining = can_change_password(current_user)
    if not can_change:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=message
        )
    
    # Set new password
    current_user.hashed_password = get_password_hash(change_data.new_password)
    current_user.password_changed_at = datetime.utcnow()
    current_user.force_password_change = False
    
    # Increment counter
    count, timestamp = parse_password_change_count(current_user.password_change_count)
    if not timestamp or datetime.utcnow() - timestamp > timedelta(hours=24):
        # Reset counter if 24h passed
        current_user.password_change_count = format_password_change_count(1, datetime.utcnow())
    else:
        # Increment existing counter
        current_user.password_change_count = format_password_change_count(count + 1, timestamp)
    
    db.commit()
    
    return PasswordResetResponse(
        message=f"Password changed successfully. {remaining - 1} changes remaining in 24h period.",
        success=True
    )


@router.get("/password-change-status", response_model=PasswordChangeStatus)
async def get_password_change_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current password change status for authenticated user
    """
    can_change, message, remaining = can_change_password(current_user)
    
    count, timestamp = parse_password_change_count(current_user.password_change_count)
    reset_time = None
    if timestamp and count >= 2:
        reset_time = timestamp + timedelta(hours=24)
    
    return PasswordChangeStatus(
        can_change_password=can_change,
        changes_remaining=remaining,
        reset_time=reset_time,
        message=message
    )


@router.post("/admin/reset-password-limit", response_model=PasswordResetResponse)
async def admin_reset_password_limit(
    reset_data: ResetPasswordLimitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Admin endpoint to reset user's password change limit
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can reset password limits"
        )
    
    user = db.query(User).filter(User.id == reset_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Reset the counter
    user.password_change_count = "0|"
    db.commit()
    
    return PasswordResetResponse(
        message=f"Password change limit reset for user {user.email}",
        success=True
    )
