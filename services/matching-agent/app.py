import os
from fastapi import FastAPI
from mcp_server import match_candidate

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok", "service": "matching-agent"}


@app.post("/match/{candidate_id}")
def match(candidate_id: str):
    return match_candidate(candidate_id)