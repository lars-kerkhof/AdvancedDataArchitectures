import os
import traceback

import uvicorn
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from auth import require_admin, require_user
from pdmodels.enrollment_req import EnrollmentReq
from pdmodels.status_req import StatusModel
from resources.enrollment import Enrollment
from resources.status import Status

app = FastAPI(title="Enrollment Service", version="0.1.0")

# THE SMUGGLER: Catch code crashes and disguise them as a 200 OK
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=200,  # <-- Trick KrakenD into letting the body through
        content={
            "debug_error_message": str(exc),
            "debug_traceback": traceback.format_exc().splitlines()
        }
    )

# THE SMUGGLER PART 2: Catch Pydantic schema mismatches
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=200,  # <-- Trick KrakenD
        content={
            "debug_error_message": "Pydantic Validation Error",
            "debug_details": exc.errors()
        }
    )

@app.post("/enrollments")
def create_enrollment(e_req: EnrollmentReq, _user=Depends(require_user)):
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
