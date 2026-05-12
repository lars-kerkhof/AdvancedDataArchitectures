from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TrialStatusEnum(str, Enum):
    draft = "draft"
    recruiting = "recruiting"
    paused = "paused"
    closed = "closed"


class TrialReq(BaseModel):
    """Payload for creating or updating a trial."""
    title: str
    status: TrialStatusEnum = TrialStatusEnum.draft
    inclusion_criteria_text: str
    exclusion_criteria_text: str = ""
    min_age: int = Field(ge=0, le=120)
    max_age: int = Field(ge=0, le=120)
    condition: str
    country: Optional[str] = None
    sponsor: Optional[str] = None
