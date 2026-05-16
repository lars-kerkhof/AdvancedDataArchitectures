from pydantic import BaseModel
from typing import List

class EnrollmentReq(BaseModel):
    candidate_id: str
    trial_id: str
    match_score: int
    match_reasons: List[str]
