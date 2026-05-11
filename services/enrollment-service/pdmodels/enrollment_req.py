from pydantic import BaseModel


class EnrollmentReq(BaseModel):
    candidate_id: str
    trial_id: str
    match_score: int
    match_reason: str
