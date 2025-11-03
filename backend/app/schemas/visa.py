from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date, datetime
from app.models.visa import VisaTypeEnum, VisaStatus, VisaPriority, VisaCaseStatus


class VisaApplicationBase(BaseModel):
    """Base visa application schema."""
    visa_type: VisaTypeEnum
    status: VisaStatus = VisaStatus.DRAFT
    case_status: VisaCaseStatus = VisaCaseStatus.ACTIVE
    priority: VisaPriority = VisaPriority.MEDIUM
    filing_date: Optional[date] = None
    approval_date: Optional[date] = None
    expiration_date: Optional[date] = None
    i94_expiration_date: Optional[date] = None
    notes: Optional[str] = None


class VisaApplicationCreate(VisaApplicationBase):
    """Schema for creating a visa application."""
    user_id: str
    visa_type_id: str


class VisaApplicationUpdate(BaseModel):
    """Schema for updating a visa application."""
    visa_type: Optional[VisaTypeEnum] = None
    status: Optional[VisaStatus] = None
    case_status: Optional[VisaCaseStatus] = None
    priority: Optional[VisaPriority] = None
    filing_date: Optional[date] = None
    approval_date: Optional[date] = None
    expiration_date: Optional[date] = None
    i94_expiration_date: Optional[date] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class VisaApplication(VisaApplicationBase):
    """Public visa application schema."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    user_id: str
    visa_type_id: str
    created_by: str
    case_status: VisaCaseStatus
    is_active: bool
    created_at: datetime
    updated_at: datetime


class VisaTypeBase(BaseModel):
    """Base visa type schema."""
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    default_renewal_lead_days: str = "180"


class VisaTypeCreate(VisaTypeBase):
    """Schema for creating a visa type."""
    pass


class VisaType(VisaTypeBase):
    """Public visa type schema."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    is_active: bool
    created_at: datetime
