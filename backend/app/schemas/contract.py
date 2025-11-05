from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date, datetime
from app.models.contract import ContractStatus


class ContractBase(BaseModel):
    """Base contract schema."""
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    start_date: date
    end_date: Optional[date] = None
    status: ContractStatus = ContractStatus.ACTIVE
    
    # Management
    manager_user_id: Optional[str] = None
    
    # Client information
    client_name: Optional[str] = Field(None, max_length=255)
    client_contact_name: Optional[str] = Field(None, max_length=255)
    client_contact_email: Optional[str] = Field(None, max_length=255)
    client_contact_phone: Optional[str] = Field(None, max_length=50)
    
    # Billing information
    billing_rate: Optional[float] = None
    billing_frequency: Optional[str] = Field(None, max_length=50)
    billing_contact_name: Optional[str] = Field(None, max_length=255)
    billing_contact_email: Optional[str] = Field(None, max_length=255)
    
    # Additional details
    description: Optional[str] = None
    notes: Optional[str] = None


class ContractCreate(ContractBase):
    """Schema for creating a contract."""
    pass


class ContractUpdate(BaseModel):
    """Schema for updating a contract."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[ContractStatus] = None
    
    # Management
    manager_user_id: Optional[str] = None
    
    # Client information
    client_name: Optional[str] = Field(None, max_length=255)
    client_contact_name: Optional[str] = Field(None, max_length=255)
    client_contact_email: Optional[str] = Field(None, max_length=255)
    client_contact_phone: Optional[str] = Field(None, max_length=50)
    
    # Billing information
    billing_rate: Optional[float] = None
    billing_frequency: Optional[str] = Field(None, max_length=50)
    billing_contact_name: Optional[str] = Field(None, max_length=255)
    billing_contact_email: Optional[str] = Field(None, max_length=255)
    
    # Additional details
    description: Optional[str] = None
    notes: Optional[str] = None


class Contract(ContractBase):
    """Public contract schema."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    created_at: datetime
    updated_at: datetime
