import os
from fastapi import Depends, FastAPI
from auth import require_user
from mcp_server import match_candidate

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok", "service": "matching-agent"}


@app.post("/match/{candidate_id}")
def match(candidate_id: str, _user=Depends(require_user)):
    return match_candidate(candidate_id)
