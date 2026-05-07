from pydantic import BaseModel

from pdmodels.candidate_req import RecruitmentStatusEnum


class RecruitmentStatusReq(BaseModel):
    recruitment_status: RecruitmentStatusEnum
