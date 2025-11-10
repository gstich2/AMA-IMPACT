"""Pydantic schemas for CaseGroup model."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any
from datetime import date, datetime

from app.models.case_group import CaseType, CaseStatus, ApprovalStatus
from app.models.visa import VisaPriority


class CaseGroupBase(BaseModel):
    """Base schema for CaseGroup."""
    case_type: CaseType = Field(..., description="Type of visa case")
    case_number: Optional[str] = Field(None, max_length=50, description="Internal tracking number")
    status: CaseStatus = Field(CaseStatus.PLANNING, description="Overall case status")
    priority: VisaPriority = Field(VisaPriority.MEDIUM, description="Case priority")
    case_started_date: Optional[date] = Field(None, description="When case work began")
    target_completion_date: Optional[date] = Field(None, description="Target completion date")
    case_completed_date: Optional[date] = Field(None, description="When case was completed")
    responsible_party_id: Optional[str] = Field(None, description="PM/HR managing this case")
    notes: Optional[str] = Field(None, description="Case notes")
    attorney_portal_link: Optional[str] = Field(None, max_length=500, description="Link to law firm's document portal")


class CaseGroupCreate(CaseGroupBase):
    """Schema for creating a new CaseGroup."""
    beneficiary_id: str = Field(..., description="ID of the beneficiary")


class CaseGroupUpdate(BaseModel):
    """Schema for updating a CaseGroup."""
    case_type: Optional[CaseType] = None
    case_number: Optional[str] = Field(None, max_length=50)
    status: Optional[CaseStatus] = None
    priority: Optional[VisaPriority] = None
    case_started_date: Optional[date] = None
    target_completion_date: Optional[date] = None
    case_completed_date: Optional[date] = None
    responsible_party_id: Optional[str] = None
    notes: Optional[str] = None
    attorney_portal_link: Optional[str] = Field(None, max_length=500)


class CaseGroupResponse(CaseGroupBase):
    """Schema for CaseGroup response."""
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    
    id: str
    beneficiary_id: str
    law_firm_id: Optional[str] = None
    approval_status: ApprovalStatus
    created_by_manager_id: Optional[str] = None
    approved_by_pm_id: Optional[str] = None
    pm_approval_date: Optional[datetime] = None
    pm_approval_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class CaseGroupWithApplications(CaseGroupResponse):
    """Schema for CaseGroup with related visa applications."""
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    
    applications: List[Any] = []  # List of VisaApplication objects


class CaseGroupSubmitForApproval(BaseModel):
    """Schema for submitting a case group for PM approval."""
    notes: Optional[str] = Field(None, description="Additional notes for the PM")


class CaseGroupApprove(BaseModel):
    """Schema for PM approving a case group."""
    approval_notes: Optional[str] = Field(None, description="PM's approval comments")
    assigned_hr_user_id: str = Field(..., description="HR user assigned to handle this case")
    law_firm_id: str = Field(..., description="Law firm assigned for this case")


class CaseGroupReject(BaseModel):
    """Schema for PM rejecting a case group."""
    rejection_reason: str = Field(..., description="Reason for rejection (required)")
