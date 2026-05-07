import uvicorn
from fastapi import FastAPI
import os

from db import Base, engine
from pdmodels.enrollment_req import EnrollmentReq
from pdmodels.status_req import StatusModel
from resources.enrollment import Enrollment
from resources.status import Status

app = FastAPI()
Base.metadata.create_all(engine)


@app.post("/enrollments")
def create_enrollment(e_req: EnrollmentReq):
    return Enrollment.create(e_req)


@app.get("/enrollments/{e_id}")
def get_enrollment(e_id: int):
    return Enrollment.get(e_id)


@app.put("/enrollments/{e_id}/status")
def update_enrollment_status(e_id: int, new_status: StatusModel):
    return Status.update(e_id, new_status.status)


@app.delete("/enrollments/{e_id}")
def delete_enrollment(e_id: int):
    return Enrollment.delete(e_id)


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
