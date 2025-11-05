from pydantic import BaseModel, Field
from typing import Optional, TYPE_CHECKING
from datetime import date, datetime

if TYPE_CHECKING:
    from app.schemas.user import User
    from app.schemas.dependent import DependentResponse


class BeneficiaryBase(BaseModel):
    """Base schema for Beneficiary - foreign national with visa case(s)"""
    first_name: str = Field(..., max_length=100, description="Legal first name")
    last_name: str = Field(..., max_length=100, description="Legal last name")
    country_of_citizenship: str = Field(..., max_length=100, description="Country of citizenship for USCIS")
    country_of_birth: str = Field(..., max_length=100, description="Country of birth for USCIS")
    passport_country: Optional[str] = Field(None, max_length=100, description="Passport issuing country (for dual citizens)")
    passport_expiration: Optional[date] = Field(None, description="Passport expiration date (for renewal warnings)")
    current_visa_type: Optional[str] = Field(None, max_length=50, description="Current visa status (e.g., H1B, F1)")
    current_visa_expiration: Optional[date] = Field(None, description="Current visa expiration date")
    i94_expiration: Optional[date] = Field(None, description="I-94 expiration date")
    job_title: Optional[str] = Field(None, max_length=200, description="Job title for USCIS documents")
    employment_start_date: Optional[date] = Field(None, description="Employment start date")


class BeneficiaryCreate(BeneficiaryBase):
    """Schema for creating a new Beneficiary"""
    user_id: Optional[str] = Field(None, description="Optional: Link to User account (for current employees)")


class BeneficiaryUpdate(BaseModel):
    """Schema for updating a Beneficiary"""
    user_id: Optional[str] = Field(None, description="Link to User account")
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    country_of_citizenship: Optional[str] = Field(None, max_length=100)
    country_of_birth: Optional[str] = Field(None, max_length=100)
    passport_country: Optional[str] = Field(None, max_length=100)
    passport_expiration: Optional[date] = None
    current_visa_type: Optional[str] = Field(None, max_length=50)
    current_visa_expiration: Optional[date] = None
    i94_expiration: Optional[date] = None
    job_title: Optional[str] = Field(None, max_length=200)
    employment_start_date: Optional[date] = None


class BeneficiaryResponse(BeneficiaryBase):
    """Schema for Beneficiary response"""
    id: str
    user_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BeneficiaryWithRelations(BeneficiaryResponse):
    """Schema for Beneficiary with related data"""
    user: Optional["User"] = None
    dependents: list["DependentResponse"] = []

    class Config:
        from_attributes = True
