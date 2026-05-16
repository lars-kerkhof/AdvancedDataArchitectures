from pydantic import BaseModel, field_validator
from typing import Union, List

class EnrollmentReq(BaseModel):
    candidate_id: str
    trial_id: str
    match_score: int
    match_reasons: Union[str, List[str]] 

    @field_validator('match_reasons', mode='after')
    @classmethod
    def ensure_string_list(cls, v):
        # If it arrives as a single string, wrap it in a list so the downstream code works perfectly
        if isinstance(v, str):
            return [v]
        return v
