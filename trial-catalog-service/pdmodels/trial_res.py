from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from pdmodels.trial_req import TrialStatusEnum


class TrialRes(BaseModel):
    """What the API returns when a trial is fetched."""
    model_config = ConfigDict(from_attributes=True)  # lets Pydantic read SQLAlchemy ORM objects directly

    id: str
    title: str
    status: TrialStatusEnum
    inclusion_criteria_text: str
    exclusion_criteria_text: str
    min_age: int
    max_age: int
    condition: str
    sponsor: Optional[str] = None
    created_at: datetime
    updated_at: datetime
