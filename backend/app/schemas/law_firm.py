"""Pydantic schemas for Law Firm model."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# ============================================================
# LawFirm Schemas
# ============================================================

class LawFirmBase(BaseModel):
    """Base schema for law firm - simplified for basic tracking."""
    name: str = Field(..., min_length=1, max_length=255)
    contact_person: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    website: Optional[str] = Field(None, max_length=255)
    is_preferred_vendor: bool = False
    performance_rating: Optional[str] = Field(None, max_length=10)
    is_active: bool = True


class LawFirmCreate(LawFirmBase):
    """Schema for creating a law firm."""
    pass


class LawFirmUpdate(BaseModel):
    """Schema for updating a law firm."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    contact_person: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    website: Optional[str] = Field(None, max_length=255)
    is_preferred_vendor: Optional[bool] = None
    performance_rating: Optional[str] = Field(None, max_length=10)
    is_active: Optional[bool] = None


class LawFirmResponse(LawFirmBase):
    """Schema for law firm response."""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
