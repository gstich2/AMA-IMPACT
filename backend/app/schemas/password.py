"""
Password management schemas for user invitation and password reset
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
import re


class InviteUserRequest(BaseModel):
    """Request to invite a new user"""
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    role: str = Field(..., description="User role: STAFF, TECH_LEAD, PROGRAM_MANAGER, HR, ADMIN")
    contract_id: Optional[str] = Field(None, description="Contract ID (required for non-admin/HR roles)")
    reports_to_id: Optional[str] = Field(None, description="Manager user ID")


class InviteUserResponse(BaseModel):
    """Response after inviting a user"""
    message: str
    user_id: str
    email: str
    invitation_sent: bool
    invitation_link: Optional[str] = None  # For development/testing


class AcceptInvitationRequest(BaseModel):
    """Request to accept invitation and set initial password"""
    token: str = Field(..., min_length=1)
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password meets security requirements"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v


class PasswordResetRequest(BaseModel):
    """Request to reset password"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Confirm password reset with token"""
    token: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate password meets security requirements"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v


class ChangePasswordRequest(BaseModel):
    """Change password for authenticated user"""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate password meets security requirements"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v


class PasswordResetResponse(BaseModel):
    """Response for password reset operations"""
    message: str
    success: bool


class ResetPasswordLimitRequest(BaseModel):
    """Admin request to reset user's password change limit"""
    user_id: str = Field(..., description="User ID to reset limit for")
    reason: Optional[str] = Field(None, description="Reason for resetting limit")


class PasswordChangeStatus(BaseModel):
    """Status of user's password change capability"""
    can_change_password: bool
    changes_remaining: int
    reset_time: Optional[datetime] = None
    message: str
