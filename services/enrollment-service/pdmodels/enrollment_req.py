from pydantic import BaseModel


class EnrollmentReq(BaseModel):
    candidate_id: str
    trial_id: str
    screening_result_id: str