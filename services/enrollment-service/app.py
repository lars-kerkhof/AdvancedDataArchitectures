import os

import uvicorn
from fastapi import Depends, FastAPI

from auth import require_admin, require_user
from pdmodels.enrollment_req import EnrollmentReq
from pdmodels.status_req import StatusModel
from resources.enrollment import Enrollment
from resources.status import Status

app = FastAPI(title="Enrollment Service", version="0.1.0")

# BigQuery tables are managed externally.
# Do not run Base.metadata.create_all(engine) on Cloud Run.

@app.post("/enrollments")
def create_enrollment(e_req: EnrollmentReq, _user=Depends(require_user)):
    # THE FIX: Intercept the data before handing it to the database layer.
    # Gemini sends 'match_reasons' as a list, but BigQuery expects a single string.
    
    # 1. Handle the plural array mapping
    if hasattr(e_req, "match_reasons") and isinstance(e_req.match_reasons, list):
        joined_str = ", ".join(e_req.match_reasons)
        e_req.match_reasons = joined_str
        # Inject singular attribute just in case the DAO explicitly calls e_req.match_reason
        setattr(e_req, "match_reason", joined_str)
        
    # 2. Handle if it mapped to the singular name but still arrived as a list
    elif hasattr(e_req, "match_reason") and isinstance(e_req.match_reason, list):
        e_req.match_reason = ", ".join(e_req.match_reason)

    return Enrollment.create(e_req)


@app.get("/enrollments/{e_id}")
def get_enrollment(e_id: str, _user=Depends(require_user)):
    return Enrollment.get(e_id)


@app.put("/enrollments/{e_id}/status")
def update_enrollment_status(e_id: str, new_status: StatusModel, _user=Depends(require_user)):
    return Status.update(e_id, new_status.status)


@app.delete("/enrollments/{e_id}")
def delete_enrollment(e_id: str, _admin=Depends(require_admin)):
    return Enrollment.delete(e_id)


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
