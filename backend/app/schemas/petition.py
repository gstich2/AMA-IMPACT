from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date, datetime
from app.models.petition import PetitionType, PetitionStatus, PetitionPriority, CaseStatus


class PetitionBase(BaseModel):
    """Base petition schema."""
    petition_type: PetitionType
    status: PetitionStatus = PetitionStatus.DRAFT
    case_status: CaseStatus = CaseStatus.ACTIVE
    priority: PetitionPriority = PetitionPriority.MEDIUM
    
    # Case group (for multi-step visa cases like EB2)
    case_group_id: Optional[str] = None
    
    # Dates
    filing_date: Optional[date] = None
    approval_date: Optional[date] = None
    expiration_date: Optional[date] = None
    i94_expiration_date: Optional[date] = None
    next_action_date: Optional[date] = None
    
    # USCIS tracking
    receipt_number: Optional[str] = Field(None, max_length=50)
    company_case_id: Optional[str] = Field(None, max_length=50)
    current_stage: Optional[str] = Field(None, max_length=100)
    
    # Law firm and attorney
    law_firm_id: Optional[str] = None
    attorney_name: Optional[str] = Field(None, max_length=255, description="Attorney full name")
    attorney_email: Optional[str] = Field(None, max_length=255, description="Attorney email")
    attorney_phone: Optional[str] = Field(None, max_length=50, description="Attorney phone")
    responsible_party_id: Optional[str] = None
    
    # RFE tracking
    rfe_received: bool = False
    rfe_received_date: Optional[date] = None
    rfe_response_date: Optional[date] = None
    rfe_notes: Optional[str] = None
    
    # Cost tracking
    filing_fee: Optional[str] = Field(None, max_length=20)
    attorney_fee: Optional[str] = Field(None, max_length=20)
    premium_processing: bool = False
    premium_processing_fee: Optional[str] = Field(None, max_length=20)
    total_cost: Optional[str] = Field(None, max_length=20)
    
    notes: Optional[str] = None


class PetitionCreate(PetitionBase):
    """Schema for creating a visa application."""
    beneficiary_id: str


class PetitionUpdate(BaseModel):
    """Schema for updating a visa application."""
    petition_type: Optional[PetitionType] = None
    status: Optional[PetitionStatus] = None
    case_status: Optional[CaseStatus] = None
    priority: Optional[PetitionPriority] = None
    
    # Case group (for multi-step visa cases like EB2)
    case_group_id: Optional[str] = None
    
    # Dates
    filing_date: Optional[date] = None
    approval_date: Optional[date] = None
    expiration_date: Optional[date] = None
    i94_expiration_date: Optional[date] = None
    next_action_date: Optional[date] = None
    
    # USCIS tracking
    receipt_number: Optional[str] = Field(None, max_length=50)
    company_case_id: Optional[str] = Field(None, max_length=50)
    current_stage: Optional[str] = Field(None, max_length=100)
    
    # Law firm and attorney
    law_firm_id: Optional[str] = None
    attorney_name: Optional[str] = Field(None, max_length=255)
    attorney_email: Optional[str] = Field(None, max_length=255)
    attorney_phone: Optional[str] = Field(None, max_length=50)
    responsible_party_id: Optional[str] = None
    
    # RFE tracking
    rfe_received: Optional[bool] = None
    rfe_received_date: Optional[date] = None
    rfe_response_date: Optional[date] = None
    rfe_notes: Optional[str] = None
    
    # Cost tracking
    filing_fee: Optional[str] = Field(None, max_length=20)
    attorney_fee: Optional[str] = Field(None, max_length=20)
    premium_processing: Optional[bool] = None
    premium_processing_fee: Optional[str] = Field(None, max_length=20)
    total_cost: Optional[str] = Field(None, max_length=20)
    
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class Petition(PetitionBase):
    """Public visa application schema."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    beneficiary_id: str
    case_group_id: Optional[str]
    created_by: str
    case_status: CaseStatus
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
