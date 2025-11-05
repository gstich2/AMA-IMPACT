"""Pydantic schemas for API request/response validation."""

from app.schemas.user import (
    UserBase, UserCreate, UserUpdate, UserInDB, User, UserLogin, Token, TokenData
)
from app.schemas.beneficiary import (
    BeneficiaryBase, BeneficiaryCreate, BeneficiaryUpdate, BeneficiaryResponse, BeneficiaryWithRelations
)
from app.schemas.contract import ContractBase, ContractCreate, ContractUpdate, Contract
from app.schemas.visa import (
    VisaApplicationBase, VisaApplicationCreate, VisaApplicationUpdate, VisaApplication,
    VisaTypeBase, VisaTypeCreate, VisaType
)
from app.schemas.case_group import (
    CaseGroupBase, CaseGroupCreate, CaseGroupUpdate, CaseGroupResponse, CaseGroupWithApplications
)
from app.schemas.law_firm import (
    LawFirmBase, LawFirmCreate, LawFirmUpdate, LawFirmResponse
)
from app.schemas.dependent import DependentBase, DependentCreate, DependentUpdate, DependentResponse
from app.schemas.milestone import (
    ApplicationMilestoneBase, ApplicationMilestoneCreate, ApplicationMilestoneUpdate, ApplicationMilestoneResponse
)
from app.schemas.rfe import RFETrackingBase, RFETrackingCreate, RFETrackingUpdate, RFETrackingResponse

__all__ = [
    # User schemas
    "UserBase", "UserCreate", "UserUpdate", "UserInDB", "User", "UserLogin", "Token", "TokenData",
    # Beneficiary schemas
    "BeneficiaryBase", "BeneficiaryCreate", "BeneficiaryUpdate", "BeneficiaryResponse", "BeneficiaryWithRelations",
    # Contract schemas
    "ContractBase", "ContractCreate", "ContractUpdate", "Contract",
    # Visa schemas
    "VisaApplicationBase", "VisaApplicationCreate", "VisaApplicationUpdate", "VisaApplication",
    "VisaTypeBase", "VisaTypeCreate", "VisaType",
    # Case group schemas
    "CaseGroupBase", "CaseGroupCreate", "CaseGroupUpdate", "CaseGroupResponse", "CaseGroupWithApplications",
    # Law firm schemas
    "LawFirmBase", "LawFirmCreate", "LawFirmUpdate", "LawFirmResponse",
    # Dependent schemas
    "DependentBase", "DependentCreate", "DependentUpdate", "DependentResponse",
    # Milestone schemas
    "ApplicationMilestoneBase", "ApplicationMilestoneCreate", "ApplicationMilestoneUpdate", "ApplicationMilestoneResponse",
    # RFE schemas
    "RFETrackingBase", "RFETrackingCreate", "RFETrackingUpdate", "RFETrackingResponse",
]