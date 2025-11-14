"""
Petition Pipeline Configuration

Defines milestone pipelines for each petition type.
Each pipeline contains ordered stages with weights for progress calculation.

CRITICAL DESIGN PRINCIPLE:
- Pipeline milestone types MUST exactly match MilestoneType enum values in the database
- Progress calculation does: `if milestone_type in completed_milestone_types`
- This is an EXACT enum comparison, not string matching
- Example: Pipeline must use MilestoneType.I140_APPROVED (not MilestoneType.APPROVED)
  to match database milestone with type I140_APPROVED

Government visa processes are standardized by law, so these are hardcoded.
Future: Can be moved to database for per-contract customization if needed.

See MILESTONE_PROGRESS_SYSTEM.md for full documentation.
"""

from typing import Dict, Any, List, Optional
from app.models.petition import PetitionType
from app.models.milestone import MilestoneType


def get_pipeline_for_petition_type(petition_type: PetitionType) -> Dict[str, Any]:
    """Get the milestone pipeline for a specific petition type."""
    # Map petition types to their specific pipelines
    pipeline_map = {
        PetitionType.I140: I140_PIPELINE,
        PetitionType.I485: I485_PIPELINE,
        PetitionType.I129: I129_PIPELINE,
        PetitionType.PERM: PERM_PIPELINE,
        PetitionType.TN_APPLICATION: TN_PIPELINE,
    }
    
    return pipeline_map.get(petition_type, DEFAULT_PIPELINE)


def get_next_milestone(petition_type: PetitionType, completed_milestone_types: List[str]) -> Optional[Dict[str, Any]]:
    """Get the next incomplete milestone in the pipeline."""
    pipeline = get_pipeline_for_petition_type(petition_type)
    completed_set = set(completed_milestone_types)
    
    for stage in pipeline["stages"]:
        milestone_type_str = stage["milestone_type"].value if hasattr(stage["milestone_type"], 'value') else str(stage["milestone_type"])
        if milestone_type_str not in completed_set:
            if not stage["required"]:
                continue
            return stage
    return None


def get_all_visa_pipelines() -> List[Dict[str, Any]]:
    """Get metadata for all available visa pipelines."""
    return [
        {
            "petition_type": "DEFAULT",
            "name": DEFAULT_PIPELINE["name"],
            "description": DEFAULT_PIPELINE["description"],
            "total_stages": len(DEFAULT_PIPELINE["stages"]),
            "required_stages": len([s for s in DEFAULT_PIPELINE["stages"] if s["required"]])
        }
    ]


# ==============================================================================
# PETITION-SPECIFIC PIPELINES
# ==============================================================================

# I-140: Immigrant Petition for Alien Worker (EB-2, EB-3 categories)
I140_PIPELINE = {
    "name": "I-140 Immigrant Petition",
    "description": "Employment-based immigrant petition workflow",
    "stages": [
        {
            "order": 1,
            "milestone_type": MilestoneType.CASE_OPENED,
            "label": "Case Opened",
            "description": "I-140 petition case initiated",
            "weight": 10,
            "required": False,
        },
        {
            "order": 2,
            "milestone_type": MilestoneType.DOCUMENTS_REQUESTED,
            "label": "Documents Requested",
            "description": "Required documentation checklist provided",
            "weight": 20,
            "required": False,
        },
        {
            "order": 3,
            "milestone_type": MilestoneType.DOCUMENTS_SUBMITTED,
            "label": "Documents Submitted",
            "description": "All required documents collected",
            "weight": 40,
            "required": False,
        },
        {
            "order": 4,
            "milestone_type": MilestoneType.I140_FILED,
            "label": "I-140 Filed",
            "description": "I-140 petition filed with USCIS",
            "weight": 60,
            "required": True,
        },
        {
            "order": 5,
            "milestone_type": MilestoneType.RFE_RECEIVED,
            "label": "RFE Received",
            "description": "Request for Evidence received",
            "weight": 70,
            "required": False,
        },
        {
            "order": 6,
            "milestone_type": MilestoneType.RFE_RESPONDED,
            "label": "RFE Responded",
            "description": "Response to RFE submitted",
            "weight": 80,
            "required": False,
        },
        {
            "order": 7,
            "milestone_type": MilestoneType.I140_APPROVED,
            "label": "I-140 Approved",
            "description": "USCIS approved the I-140 petition",
            "weight": 100,
            "required": True,
            "terminal": True,
        },
        {
            "order": 8,
            "milestone_type": MilestoneType.I140_DENIED,
            "label": "I-140 Denied",
            "description": "USCIS denied the I-140 petition",
            "weight": 100,
            "required": False,
            "terminal": True,
        },
    ]
}

# I-485: Adjustment of Status (Green Card application)
I485_PIPELINE = {
    "name": "I-485 Adjustment of Status",
    "description": "Application to adjust status to permanent resident",
    "stages": [
        {
            "order": 1,
            "milestone_type": MilestoneType.CASE_OPENED,
            "label": "Case Opened",
            "description": "I-485 case initiated",
            "weight": 10,
            "required": False,
        },
        {
            "order": 2,
            "milestone_type": MilestoneType.DOCUMENTS_REQUESTED,
            "label": "Documents Requested",
            "description": "Required documentation checklist provided",
            "weight": 20,
            "required": False,
        },
        {
            "order": 3,
            "milestone_type": MilestoneType.DOCUMENTS_SUBMITTED,
            "label": "Documents Submitted",
            "description": "All required documents collected",
            "weight": 30,
            "required": False,
        },
        {
            "order": 4,
            "milestone_type": MilestoneType.I485_FILED,
            "label": "I-485 Filed",
            "description": "I-485 application filed with USCIS",
            "weight": 45,
            "required": True,
        },
        {
            "order": 5,
            "milestone_type": MilestoneType.BIOMETRICS_SCHEDULED,
            "label": "Biometrics Scheduled",
            "description": "Biometrics appointment scheduled",
            "weight": 55,
            "required": False,
        },
        {
            "order": 6,
            "milestone_type": MilestoneType.BIOMETRICS_COMPLETED,
            "label": "Biometrics Completed",
            "description": "Biometrics appointment completed",
            "weight": 65,
            "required": False,
        },
        {
            "order": 7,
            "milestone_type": MilestoneType.INTERVIEW_SCHEDULED,
            "label": "Interview Scheduled",
            "description": "USCIS interview scheduled",
            "weight": 75,
            "required": False,
        },
        {
            "order": 8,
            "milestone_type": MilestoneType.INTERVIEW_COMPLETED,
            "label": "Interview Completed",
            "description": "USCIS interview completed",
            "weight": 85,
            "required": False,
        },
        {
            "order": 9,
            "milestone_type": MilestoneType.I485_APPROVED,
            "label": "I-485 Approved",
            "description": "I-485 approved, Green Card will be issued",
            "weight": 95,
            "required": True,
        },
        {
            "order": 10,
            "milestone_type": MilestoneType.GREEN_CARD_RECEIVED,
            "label": "Green Card Received",
            "description": "Physical Green Card received",
            "weight": 100,
            "required": True,
            "terminal": True,
        },
    ]
}

# I-129: Petition for Nonimmigrant Worker (H-1B, L-1, etc.)
I129_PIPELINE = {
    "name": "I-129 Nonimmigrant Worker",
    "description": "Petition for nonimmigrant worker (H-1B, L-1, etc.)",
    "stages": [
        {
            "order": 1,
            "milestone_type": MilestoneType.CASE_OPENED,
            "label": "Case Opened",
            "description": "I-129 petition case initiated",
            "weight": 10,
            "required": False,
        },
        {
            "order": 2,
            "milestone_type": MilestoneType.LCA_FILED,
            "label": "LCA Filed",
            "description": "Labor Condition Application filed with DOL",
            "weight": 30,
            "required": False,
        },
        {
            "order": 3,
            "milestone_type": MilestoneType.LCA_APPROVED,
            "label": "LCA Approved",
            "description": "DOL approved the LCA",
            "weight": 50,
            "required": False,
        },
        {
            "order": 4,
            "milestone_type": MilestoneType.H1B_FILED,
            "label": "H-1B Filed",
            "description": "H-1B petition filed with USCIS",
            "weight": 70,
            "required": True,
        },
        {
            "order": 5,
            "milestone_type": MilestoneType.RFE_RECEIVED,
            "label": "RFE Received",
            "description": "Request for Evidence received",
            "weight": 80,
            "required": False,
        },
        {
            "order": 6,
            "milestone_type": MilestoneType.RFE_RESPONDED,
            "label": "RFE Responded",
            "description": "Response to RFE submitted",
            "weight": 90,
            "required": False,
        },
        {
            "order": 7,
            "milestone_type": MilestoneType.H1B_APPROVED,
            "label": "H-1B Approved",
            "description": "USCIS approved the H-1B petition",
            "weight": 100,
            "required": True,
            "terminal": True,
        },
    ]
}

# PERM: Labor Certification
PERM_PIPELINE = {
    "name": "PERM Labor Certification",
    "description": "Permanent labor certification process",
    "stages": [
        {
            "order": 1,
            "milestone_type": MilestoneType.PWD_FILED,
            "label": "PWD Filed",
            "description": "Prevailing Wage Determination filed with DOL",
            "weight": 15,
            "required": True,
        },
        {
            "order": 2,
            "milestone_type": MilestoneType.PWD_APPROVED,
            "label": "PWD Approved",
            "description": "Prevailing Wage Determination approved",
            "weight": 30,
            "required": True,
        },
        {
            "order": 3,
            "milestone_type": MilestoneType.RECRUITMENT_STARTED,
            "label": "Recruitment Started",
            "description": "Required recruitment process started",
            "weight": 45,
            "required": True,
        },
        {
            "order": 4,
            "milestone_type": MilestoneType.RECRUITMENT_COMPLETED,
            "label": "Recruitment Completed",
            "description": "Recruitment process completed",
            "weight": 60,
            "required": True,
        },
        {
            "order": 5,
            "milestone_type": MilestoneType.PERM_FILED,
            "label": "PERM Filed",
            "description": "PERM application filed with DOL",
            "weight": 75,
            "required": True,
        },
        {
            "order": 6,
            "milestone_type": MilestoneType.PERM_AUDIT,
            "label": "PERM Audit",
            "description": "PERM application selected for audit",
            "weight": 85,
            "required": False,
        },
        {
            "order": 7,
            "milestone_type": MilestoneType.PERM_APPROVED,
            "label": "PERM Approved",
            "description": "DOL approved the PERM labor certification",
            "weight": 100,
            "required": True,
            "terminal": True,
        },
    ]
}

# TN: NAFTA Professional
TN_PIPELINE = {
    "name": "TN NAFTA Professional",
    "description": "TN visa for Canadian/Mexican professionals",
    "stages": [
        {
            "order": 1,
            "milestone_type": MilestoneType.CASE_OPENED,
            "label": "Case Opened",
            "description": "TN application case initiated",
            "weight": 20,
            "required": False,
        },
        {
            "order": 2,
            "milestone_type": MilestoneType.DOCUMENTS_REQUESTED,
            "label": "Documents Requested",
            "description": "Required documentation checklist provided",
            "weight": 40,
            "required": False,
        },
        {
            "order": 3,
            "milestone_type": MilestoneType.DOCUMENTS_SUBMITTED,
            "label": "Documents Submitted",
            "description": "All required documents collected",
            "weight": 60,
            "required": False,
        },
        {
            "order": 4,
            "milestone_type": MilestoneType.TN_BORDER_APPOINTMENT,
            "label": "Border/Consulate Appointment",
            "description": "TN application submitted at port of entry or consulate",
            "weight": 80,
            "required": True,
        },
        {
            "order": 5,
            "milestone_type": MilestoneType.TN_APPROVED,
            "label": "TN Approved",
            "description": "TN status granted",
            "weight": 100,
            "required": True,
            "terminal": True,
        },
    ]
}

# Default pipeline for petition types without specific definitions
DEFAULT_PIPELINE = {
    "name": "Standard Immigration Process",
    "description": "Generic immigration case workflow",
    "stages": [
        {
            "order": 1,
            "milestone_type": MilestoneType.CASE_OPENED,
            "label": "Case Opened",
            "description": "Case initiated and under review",
            "weight": 15,
            "required": True,
        },
        {
            "order": 2,
            "milestone_type": MilestoneType.DOCUMENTS_REQUESTED,
            "label": "Documents Requested",
            "description": "Required documentation checklist provided",
            "weight": 30,
            "required": True,
        },
        {
            "order": 3,
            "milestone_type": MilestoneType.DOCUMENTS_SUBMITTED,
            "label": "Documents Submitted",
            "description": "All required documents collected",
            "weight": 50,
            "required": True,
        },
        {
            "order": 4,
            "milestone_type": MilestoneType.FILED_WITH_USCIS,
            "label": "Filed with USCIS",
            "description": "Petition/application filed with USCIS",
            "weight": 75,
            "required": True,
        },
        {
            "order": 5,
            "milestone_type": MilestoneType.APPROVED,
            "label": "Approved",
            "description": "Case approved by adjudicating authority",
            "weight": 100,
            "required": True,
            "terminal": True,
        },
    ]
}
