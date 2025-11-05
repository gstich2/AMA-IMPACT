"""Pydantic schemas for Dependent model."""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class DependentBase(BaseModel):
    """Base schema for dependent - family members of beneficiaries."""
    beneficiary_id: str
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    relationship_type: str  # spouse, child, other
    country_of_citizenship: Optional[str] = Field(None, max_length=100)
    country_of_birth: Optional[str] = Field(None, max_length=100)
    current_visa_type: Optional[str] = Field(None, max_length=50)
    visa_expiration: Optional[date] = None
    i94_expiration: Optional[date] = None
    passport_number: Optional[str] = Field(None, max_length=50)
    passport_country: Optional[str] = Field(None, max_length=100)
    passport_expiration: Optional[date] = None


class DependentCreate(DependentBase):
    """Schema for creating a dependent."""
    pass


class DependentUpdate(BaseModel):
    """Schema for updating a dependent."""
    beneficiary_id: Optional[str] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    relationship_type: Optional[str] = None
    country_of_citizenship: Optional[str] = Field(None, max_length=100)
    country_of_birth: Optional[str] = Field(None, max_length=100)
    current_visa_type: Optional[str] = Field(None, max_length=50)
    visa_expiration: Optional[date] = None
    i94_expiration: Optional[date] = None
    passport_number: Optional[str] = Field(None, max_length=50)
    passport_country: Optional[str] = Field(None, max_length=100)
    passport_expiration: Optional[date] = None


class DependentResponse(DependentBase):
    """Schema for dependent response."""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
