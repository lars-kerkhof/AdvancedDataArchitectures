# Schema not yet finalized with Ralf — fields below are working assumptions.
# Likely review points: medical fields structure, recruitment_status enum values,
# whether to split demographics from medical history.

from datetime import date
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class SexEnum(str, Enum):
    male = "male"
    female = "female"
    other = "other"
    prefer_not_to_say = "prefer_not_to_say"


class OutreachStateEnum(str, Enum):
    not_contacted = "not_contacted"
    contacted = "contacted"
    responded = "responded"
    unreachable = "unreachable"


class RecruitmentStatusEnum(str, Enum):
    submitted = "submitted"
    under_review = "under_review"
    matched = "matched"
    enrolled = "enrolled"
    rejected = "rejected"
    withdrawn = "withdrawn"


class CandidateReq(BaseModel):
    """Payload for creating a candidate (initial intake submission)."""
    # Demographics
    full_name: str
    email: str
    phone: Optional[str] = None
    date_of_birth: date
    sex: SexEnum
    country: str = Field(min_length=2, max_length=2, description="ISO 3166 alpha-2 code, e.g., NL")

    # Medical (lists serialized as JSON strings in storage)
    conditions: List[str] = []
    medications: List[str] = []
    allergies: List[str] = []

    # Contact preferences
    contact_email_opt_in: bool = True
    contact_phone_opt_in: bool = False
    preferred_language: str = "en"
