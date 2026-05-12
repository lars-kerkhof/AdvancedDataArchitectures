# app.py

import os

import uvicorn
from fastapi import Depends, FastAPI

from auth import require_user
from agent import CoordinatorAgent
from tools import call_matching_agent, update_candidate_enrolled

app = FastAPI(title="Coordinator Agent", version="0.1.0")

coordinator = CoordinatorAgent()


@app.get("/health")
def health():
    return {"status": "ok", "service": "coordinator-agent"}


@app.post("/coordinate/match/{candidate_id}")
def coordinate_match(candidate_id: str, _user=Depends(require_user)):
    matching_result = call_matching_agent(candidate_id)
    matches = matching_result.get("matches", [])

    decision = coordinator.decide_enrollment(
        candidate_id=candidate_id,
        matches=matches,
    )

    candidate_update = update_candidate_enrolled(
        candidate_id=candidate_id,
        enrolled=decision["enrolled"],
    )

    return {
        "goal": "coordinate_candidate_matching",
        "candidate_id": candidate_id,
        "agent": coordinator.name,
        "matching_agent_called": True,
        "decision": decision,
        "candidate_update": candidate_update,
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
