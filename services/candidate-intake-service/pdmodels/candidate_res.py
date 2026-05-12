from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from pdmodels.candidate_req import OutreachStateEnum, RecruitmentStatusEnum, SexEnum


class CandidateRes(BaseModel):
    """Full candidate response."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    full_name: str
    email: str
    phone: Optional[str]
    date_of_birth: date
    sex: SexEnum
    country: str
    conditions: List[str]
    medications: List[str]
    allergies: List[str]
    contact_email_opt_in: bool
    contact_phone_opt_in: bool
    preferred_language: str
    outreach_state: OutreachStateEnum
    recruitment_status: RecruitmentStatusEnum
    enrolled: bool
    intake_submitted_at: datetime
    last_intake_update_at: datetime
    created_at: datetime
    updated_at: datetime


class RecruitmentStatusRes(BaseModel):
    """Lightweight response for GET /candidates/{id}/recruitment-status."""
    id: str
    recruitment_status: RecruitmentStatusEnum
    updated_at: datetime
