from typing import Optional

import uvicorn
from fastapi import FastAPI

from db import Base, engine
from pdmodels.trial_req import TrialReq, TrialStatusEnum
from resources.trial import Trial

app = FastAPI(title="Trial Catalog Service", version="0.1.0")
Base.metadata.create_all(engine)


@app.post("/trials")
def create_trial(t_req: TrialReq):
    return Trial.create(t_req)


@app.get("/trials/{t_id}")
def get_trial(t_id: str):
    return Trial.get(t_id)


@app.get("/trials")
def list_trials(status: Optional[TrialStatusEnum] = None):
    return Trial.list(status_filter=status)


@app.put("/trials/{t_id}")
def update_trial(t_id: str, t_req: TrialReq):
    return Trial.update(t_id, t_req)


@app.delete("/trials/{t_id}")
def delete_trial(t_id: str):
    return Trial.delete(t_id)


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
