"""Pydantic schemas for ApplicationMilestone model."""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class ApplicationMilestoneBase(BaseModel):
    """Base schema for application milestone."""
    visa_application_id: str
    milestone_type: str  # case_opened, filed, rfe_received, approved, etc.
    milestone_date: date
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None


class ApplicationMilestoneCreate(ApplicationMilestoneBase):
    """Schema for creating a milestone."""
    pass


class ApplicationMilestoneUpdate(BaseModel):
    """Schema for updating a milestone."""
    milestone_type: Optional[str] = None
    milestone_date: Optional[date] = None
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None


class ApplicationMilestoneResponse(ApplicationMilestoneBase):
    """Schema for milestone response."""
    id: str
    created_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
