import os
from typing import Optional

import uvicorn
from fastapi import Depends, FastAPI

from auth import require_admin, require_user
from db import Base, engine
from pdmodels.candidate_req import CandidateReq, RecruitmentStatusEnum
from pdmodels.intake_details_req import IntakeDetailsReq
from pdmodels.recruitment_status_req import RecruitmentStatusReq
from resources.candidate import Candidate

app = FastAPI(title="Candidate Intake Service", version="0.1.0")
Base.metadata.create_all(engine)


@app.post("/candidates")
def create_candidate(c_req: CandidateReq, _user=Depends(require_user)):
    return Candidate.create(c_req)


@app.get("/candidates/{c_id}")
def get_candidate(c_id: str, _user=Depends(require_user)):
    return Candidate.get(c_id)


@app.get("/candidates")
def list_candidates(
    recruitment_status: Optional[RecruitmentStatusEnum] = None,
    _user=Depends(require_user),
):
    return Candidate.list(recruitment_status=recruitment_status)


@app.put("/candidates/{c_id}")
def update_candidate(c_id: str, c_req: CandidateReq, _user=Depends(require_user)):
    return Candidate.update(c_id, c_req)


@app.put("/candidates/{c_id}/intake-details")
def submit_intake_details(
    c_id: str, details: IntakeDetailsReq, _user=Depends(require_user)
):
    return Candidate.submit_intake_details(c_id, details)


@app.get("/candidates/{c_id}/recruitment-status")
def get_recruitment_status(c_id: str, _user=Depends(require_user)):
    return Candidate.get_recruitment_status(c_id)


@app.put("/candidates/{c_id}/recruitment-status")
def update_recruitment_status(
    c_id: str, status_req: RecruitmentStatusReq, _admin=Depends(require_admin)
):
    return Candidate.update_recruitment_status(c_id, status_req)


@app.delete("/candidates/{c_id}")
def delete_candidate(c_id: str, _admin=Depends(require_admin)):
    return Candidate.delete(c_id)


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
