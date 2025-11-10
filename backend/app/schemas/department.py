"""
Department/Organizational Unit schemas
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class DepartmentBase(BaseModel):
    """Base department schema"""
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    parent_id: Optional[str] = Field(None, description="Parent department ID for hierarchy")
    manager_id: Optional[str] = Field(None, description="User ID of department manager/lead")
    level: int = Field(1, ge=1, description="Hierarchy level (1=top, 2=sub, etc.)")


class DepartmentCreate(DepartmentBase):
    """Schema for creating a department"""
    contract_id: str = Field(..., description="Contract ID this department belongs to")


class DepartmentUpdate(BaseModel):
    """Schema for updating a department"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    parent_id: Optional[str] = None
    manager_id: Optional[str] = None
    level: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None


class DepartmentSimple(BaseModel):
    """Simplified department schema (no nested relationships)"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    name: str
    code: str
    description: Optional[str]
    contract_id: str
    parent_id: Optional[str]
    manager_id: Optional[str]
    level: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class Department(DepartmentSimple):
    """Full department schema with nested data"""
    model_config = ConfigDict(from_attributes=True)
    
    # Add computed fields
    full_path: Optional[str] = Field(None, description="Full hierarchical path")
    user_count: Optional[int] = Field(None, description="Number of users in this department")
    total_user_count: Optional[int] = Field(None, description="Total users including sub-departments")


class DepartmentTree(DepartmentSimple):
    """Department with children for tree view"""
    model_config = ConfigDict(from_attributes=True)
    
    children: List['DepartmentTree'] = []
    user_count: Optional[int] = None


class DepartmentStats(BaseModel):
    """Department statistics for visa tracking"""
    department_id: Optional[str] = Field(None, description="Department ID (null if contract-wide)")
    department_name: Optional[str] = Field(None, description="Department name")
    department_code: Optional[str] = Field(None, description="Department code")
    contract_id: str = Field(..., description="Contract ID")
    contract_code: str = Field(..., description="Contract code")
    
    # Beneficiary counts (foreign nationals with visa cases)
    beneficiaries_direct: int = Field(..., description="Beneficiaries in this department only")
    beneficiaries_total: int = Field(..., description="Total including sub-departments")
    beneficiaries_active: int = Field(..., description="Active beneficiaries")
    beneficiaries_inactive: int = Field(..., description="Inactive beneficiaries")
    
    # Visa application counts
    visa_applications_total: int = Field(..., description="Total visa applications")
    visa_applications_active: int = Field(..., description="Active visa applications")
    visa_applications_by_status: dict = Field(default_factory=dict, description="Applications by status")
    visa_applications_by_type: dict = Field(default_factory=dict, description="Applications by visa type")
    
    # Expirations (actionable alerts)
    expiring_next_30_days: int = Field(..., description="Visas expiring in 30 days")
    expiring_next_90_days: int = Field(..., description="Visas expiring in 90 days")
    expired: int = Field(..., description="Expired visas")
    
    # Metadata
    generated_at: datetime = Field(..., description="Timestamp of generation")
    include_subdepartments: bool = Field(..., description="Whether sub-departments are included")


# For recursive model
DepartmentTree.model_rebuild()
