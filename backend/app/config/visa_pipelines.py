"""
Visa Pipeline Configuration

Defines milestone pipelines for each visa type.
Each pipeline contains ordered stages with weights for progress calculation.

Government visa processes are standardized by law, so these are hardcoded.
Future: Can be moved to database for per-contract customization if needed.
"""

from typing import Dict, Any, List, Optional
from app.models.visa import VisaTypeEnum
from app.models.milestone import MilestoneType


def get_pipeline_for_visa_type(visa_type: VisaTypeEnum) -> Dict[str, Any]:
    """
    Get the milestone pipeline for a specific visa type.
    
    Args:
        visa_type: The visa type enum value
        
    Returns:
        Dictionary containing pipeline name, description, and ordered stages
    """
    return VISA_PIPELINES.get(visa_type, DEFAULT_PIPELINE)


def get_next_milestone(visa_type: VisaTypeEnum, completed_milestone_types: List[str]) -> Optional[Dict[str, Any]]:
    """
    Get the next incomplete milestone in the pipeline.
    
    Args:
        visa_type: The visa type enum value
        completed_milestone_types: List of milestone_type values that are completed
        
    Returns:
        The next stage dictionary, or None if all milestones completed
    """
    pipeline = get_pipeline_for_visa_type(visa_type)
    completed_set = set(completed_milestone_types)
    
    for stage in pipeline["stages"]:
        milestone_type_str = stage["milestone_type"].value if hasattr(stage["milestone_type"], 'value') else str(stage["milestone_type"])
        if milestone_type_str not in completed_set:
            # Skip optional stages if not in sequence
            if not stage["required"]:
                continue
            return stage
    
    return None  # All required milestones completed


def get_all_visa_pipelines() -> List[Dict[str, Any]]:
    """
    Get metadata for all available visa pipelines.
    Useful for admin interfaces.
    
    Returns:
        List of pipeline metadata dictionaries
    """
    return [
        {
            "visa_type": visa_type.value,
            "name": config["name"],
            "description": config["description"],
            "total_stages": len(config["stages"]),
            "required_stages": len([s for s in config["stages"] if s["required"]])
        }
        for visa_type, config in VISA_PIPELINES.items()
    ]


# ==============================================================================
# VISA PIPELINE DEFINITIONS
# ==============================================================================

VISA_PIPELINES = {
    # H1B Visa Pipeline
    # Employer-sponsored temporary work visa
    VisaTypeEnum.H1B: {
        "name": "H-1B Specialty Occupation",
        "description": "Employer-sponsored temporary work visa for specialty occupations",
        "stages": [
            {
                "order": 1,
                "milestone_type": MilestoneType.CASE_OPENED,
                "label": "Case Opened",
                "description": "Initial consultation and eligibility assessment completed",
                "weight": 10,
                "required": True,
            },
            {
                "order": 2,
                "milestone_type": MilestoneType.DOCUMENTS_REQUESTED,
                "label": "Documents Requested",
                "description": "Document checklist provided to beneficiary and employer",
                "weight": 25,
                "required": True,
            },
            {
                "order": 3,
                "milestone_type": MilestoneType.DOCUMENTS_SUBMITTED,
                "label": "Documents Submitted",
                "description": "All required documents collected and reviewed",
                "weight": 40,
                "required": True,
            },
            {
                "order": 4,
                "milestone_type": MilestoneType.LCA_FILED,
                "label": "LCA Filed with DOL",
                "description": "Labor Condition Application submitted to Department of Labor",
                "weight": 55,
                "required": True,
            },
            {
                "order": 5,
                "milestone_type": MilestoneType.LCA_APPROVED,
                "label": "LCA Approved",
                "description": "Department of Labor approved the Labor Condition Application",
                "weight": 70,
                "required": True,
            },
            {
                "order": 6,
                "milestone_type": MilestoneType.H1B_FILED,
                "label": "H-1B Petition Filed",
                "description": "Employer filed H-1B petition with USCIS (Form I-129)",
                "weight": 85,
                "required": True,
            },
            {
                "order": 7,
                "milestone_type": MilestoneType.RFE_RECEIVED,
                "label": "RFE Received",
                "description": "Request for Evidence received from USCIS",
                "weight": 87,
                "required": False,  # Optional - only if USCIS requests
            },
            {
                "order": 8,
                "milestone_type": MilestoneType.RFE_RESPONDED,
                "label": "RFE Response Submitted",
                "description": "Response to Request for Evidence submitted to USCIS",
                "weight": 92,
                "required": False,  # Optional - only if RFE received
            },
            {
                "order": 9,
                "milestone_type": MilestoneType.APPROVED,
                "label": "H-1B Approved",
                "description": "USCIS approved the H-1B petition",
                "weight": 100,
                "required": True,
                "terminal": True,
            },
        ]
    },
    
    # EB-2 NIW (National Interest Waiver) Pipeline
    # Employment-based second preference with waiver
    VisaTypeEnum.EB2NIW: {
        "name": "EB-2 National Interest Waiver",
        "description": "Employment-based second preference immigrant visa with National Interest Waiver",
        "stages": [
            {
                "order": 1,
                "milestone_type": MilestoneType.CASE_OPENED,
                "label": "Case Opened",
                "description": "Initial assessment of NIW eligibility and qualifications",
                "weight": 10,
                "required": True,
            },
            {
                "order": 2,
                "milestone_type": MilestoneType.DOCUMENTS_REQUESTED,
                "label": "Documents Requested",
                "description": "Evidence checklist for NIW petition provided",
                "weight": 20,
                "required": True,
            },
            {
                "order": 3,
                "milestone_type": MilestoneType.DOCUMENTS_SUBMITTED,
                "label": "Documents Submitted",
                "description": "All supporting evidence and documentation collected",
                "weight": 35,
                "required": True,
            },
            {
                "order": 4,
                "milestone_type": MilestoneType.I140_FILED,
                "label": "I-140 Filed with USCIS",
                "description": "I-140 Immigrant Petition filed with USCIS",
                "weight": 60,
                "required": True,
            },
            {
                "order": 5,
                "milestone_type": MilestoneType.RFE_RECEIVED,
                "label": "RFE Received",
                "description": "Request for Evidence received from USCIS",
                "weight": 65,
                "required": False,
            },
            {
                "order": 6,
                "milestone_type": MilestoneType.RFE_RESPONDED,
                "label": "RFE Response Submitted",
                "description": "Response to Request for Evidence submitted",
                "weight": 75,
                "required": False,
            },
            {
                "order": 7,
                "milestone_type": MilestoneType.I140_APPROVED,
                "label": "I-140 Approved",
                "description": "USCIS approved the I-140 petition",
                "weight": 90,
                "required": True,
            },
            {
                "order": 8,
                "milestone_type": MilestoneType.CASE_CLOSED,
                "label": "Case Closed",
                "description": "EB-2 NIW petition completed successfully",
                "weight": 100,
                "required": True,
                "terminal": True,
            },
        ]
    },
    
    # TN (NAFTA Professional) Pipeline
    # Canadian/Mexican professional temporary work authorization
    VisaTypeEnum.TN: {
        "name": "TN NAFTA Professional",
        "description": "Canadian/Mexican professional work authorization under NAFTA/USMCA",
        "stages": [
            {
                "order": 1,
                "milestone_type": MilestoneType.CASE_OPENED,
                "label": "Case Opened",
                "description": "Initial assessment of TN eligibility",
                "weight": 15,
                "required": True,
            },
            {
                "order": 2,
                "milestone_type": MilestoneType.DOCUMENTS_REQUESTED,
                "label": "Documents Requested",
                "description": "Document checklist for TN application provided",
                "weight": 35,
                "required": True,
            },
            {
                "order": 3,
                "milestone_type": MilestoneType.DOCUMENTS_SUBMITTED,
                "label": "Documents Submitted",
                "description": "All required documents prepared for border/consulate",
                "weight": 60,
                "required": True,
            },
            {
                "order": 4,
                "milestone_type": MilestoneType.TN_BORDER_APPOINTMENT,
                "label": "Border Appointment / Consulate Visit",
                "description": "TN application submitted at border port of entry or consulate",
                "weight": 85,
                "required": True,
            },
            {
                "order": 5,
                "milestone_type": MilestoneType.APPROVED,
                "label": "TN Approved",
                "description": "TN status granted by CBP or consular officer",
                "weight": 100,
                "required": True,
                "terminal": True,
            },
        ]
    },
    
    # I-485 / Green Card (Adjustment of Status) Pipeline
    # For beneficiaries already in the US adjusting status to permanent resident
    VisaTypeEnum.GREEN_CARD: {
        "name": "I-485 Adjustment of Status",
        "description": "Application to adjust status to Lawful Permanent Resident (Green Card)",
        "stages": [
            {
                "order": 1,
                "milestone_type": MilestoneType.CASE_OPENED,
                "label": "Case Opened",
                "description": "I-485 case initiated, priority date current",
                "weight": 10,
                "required": True,
            },
            {
                "order": 2,
                "milestone_type": MilestoneType.DOCUMENTS_REQUESTED,
                "label": "Documents Requested",
                "description": "I-485 document checklist provided",
                "weight": 20,
                "required": True,
            },
            {
                "order": 3,
                "milestone_type": MilestoneType.DOCUMENTS_SUBMITTED,
                "label": "Documents Submitted",
                "description": "All I-485 supporting documents collected",
                "weight": 30,
                "required": True,
            },
            {
                "order": 4,
                "milestone_type": MilestoneType.I485_FILED,
                "label": "I-485 Filed with USCIS",
                "description": "I-485 Application to Adjust Status filed",
                "weight": 50,
                "required": True,
            },
            {
                "order": 5,
                "milestone_type": MilestoneType.BIOMETRICS_COMPLETED,
                "label": "Biometrics Completed",
                "description": "Biometrics appointment completed at USCIS Application Support Center",
                "weight": 65,
                "required": True,
            },
            {
                "order": 6,
                "milestone_type": MilestoneType.RFE_RECEIVED,
                "label": "RFE Received",
                "description": "Request for Evidence received from USCIS",
                "weight": 70,
                "required": False,
            },
            {
                "order": 7,
                "milestone_type": MilestoneType.RFE_RESPONDED,
                "label": "RFE Response Submitted",
                "description": "Response to Request for Evidence submitted",
                "weight": 75,
                "required": False,
            },
            {
                "order": 8,
                "milestone_type": MilestoneType.INTERVIEW_SCHEDULED,
                "label": "Interview Scheduled",
                "description": "USCIS interview appointment scheduled",
                "weight": 80,
                "required": False,  # Not always required
            },
            {
                "order": 9,
                "milestone_type": MilestoneType.INTERVIEW_COMPLETED,
                "label": "Interview Completed",
                "description": "USCIS interview completed",
                "weight": 85,
                "required": False,
            },
            {
                "order": 10,
                "milestone_type": MilestoneType.APPROVED,
                "label": "Green Card Approved",
                "description": "I-485 approved, Green Card will be issued",
                "weight": 100,
                "required": True,
                "terminal": True,
            },
        ]
    },
    
    # EB-2 (with Labor Certification / PERM) Pipeline
    # Standard EB-2 requiring labor certification
    VisaTypeEnum.EB2: {
        "name": "EB-2 with Labor Certification",
        "description": "Employment-based second preference immigrant visa with PERM labor certification",
        "stages": [
            {
                "order": 1,
                "milestone_type": MilestoneType.CASE_OPENED,
                "label": "Case Opened",
                "description": "Initial EB-2 case assessment",
                "weight": 8,
                "required": True,
            },
            {
                "order": 2,
                "milestone_type": MilestoneType.PWD_FILED,
                "label": "PWD Filed",
                "description": "Prevailing Wage Determination filed with DOL",
                "weight": 15,
                "required": True,
            },
            {
                "order": 3,
                "milestone_type": MilestoneType.PWD_APPROVED,
                "label": "PWD Approved",
                "description": "Prevailing Wage Determination approved by DOL",
                "weight": 25,
                "required": True,
            },
            {
                "order": 4,
                "milestone_type": MilestoneType.PERM_FILED,
                "label": "PERM Filed",
                "description": "PERM Labor Certification filed with DOL",
                "weight": 40,
                "required": True,
            },
            {
                "order": 5,
                "milestone_type": MilestoneType.PERM_APPROVED,
                "label": "PERM Approved",
                "description": "PERM Labor Certification approved by DOL",
                "weight": 55,
                "required": True,
            },
            {
                "order": 6,
                "milestone_type": MilestoneType.I140_FILED,
                "label": "I-140 Filed",
                "description": "I-140 Immigrant Petition filed with USCIS",
                "weight": 70,
                "required": True,
            },
            {
                "order": 7,
                "milestone_type": MilestoneType.RFE_RECEIVED,
                "label": "RFE Received",
                "description": "Request for Evidence received from USCIS",
                "weight": 75,
                "required": False,
            },
            {
                "order": 8,
                "milestone_type": MilestoneType.RFE_RESPONDED,
                "label": "RFE Response Submitted",
                "description": "Response to Request for Evidence submitted",
                "weight": 82,
                "required": False,
            },
            {
                "order": 9,
                "milestone_type": MilestoneType.I140_APPROVED,
                "label": "I-140 Approved",
                "description": "USCIS approved the I-140 petition",
                "weight": 90,
                "required": True,
            },
            {
                "order": 10,
                "milestone_type": MilestoneType.CASE_CLOSED,
                "label": "Case Closed",
                "description": "EB-2 petition completed successfully",
                "weight": 100,
                "required": True,
                "terminal": True,
            },
        ]
    },
}


# Default pipeline for visa types without specific definitions
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
