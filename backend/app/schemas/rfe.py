"""Pydantic schemas for RFETracking model."""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class RFETrackingBase(BaseModel):
    """Base schema for RFE tracking."""
    visa_application_id: str
    rfe_type: str  # initial_evidence, additional_evidence, intent_to_deny, etc.
    status: str  # received, in_progress, responded, resolved
    rfe_received_date: date
    rfe_deadline: date
    response_submitted_date: Optional[date] = None
    resolution_date: Optional[date] = None
    rfe_subject: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    response_summary: Optional[str] = None
    notes: Optional[str] = None


class RFETrackingCreate(RFETrackingBase):
    """Schema for creating RFE tracking."""
    pass


class RFETrackingUpdate(BaseModel):
    """Schema for updating RFE tracking."""
    rfe_type: Optional[str] = None
    status: Optional[str] = None
    rfe_received_date: Optional[date] = None
    rfe_deadline: Optional[date] = None
    response_submitted_date: Optional[date] = None
    resolution_date: Optional[date] = None
    rfe_subject: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    response_summary: Optional[str] = None
    notes: Optional[str] = None


class RFETrackingResponse(RFETrackingBase):
    """Schema for RFE tracking response."""
    id: str
    created_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
