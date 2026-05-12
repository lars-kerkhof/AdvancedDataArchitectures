import os

import requests
import uvicorn
from fastapi import Depends, FastAPI, HTTPException

from auth import require_user
from agent import CoordinatorAgent
from service_token import auth_header, get_service_token
from tools import call_matching_agent, update_candidate_enrolled

ENROLLMENT_SERVICE_URL = os.getenv("ENROLLMENT_SERVICE_URL", "")

app = FastAPI(title="Coordinator Agent", version="0.1.0")

coordinator = CoordinatorAgent()


@app.get("/health")
def health():
    return {"status": "ok", "service": "coordinator-agent"}


def create_enrollment(best_match: dict) -> dict:
    if not ENROLLMENT_SERVICE_URL:
        raise HTTPException(
            status_code=500,
            detail="ENROLLMENT_SERVICE_URL environment variable is not set",
        )

    enrollment_payload = {
        "candidate_id": best_match["candidate_id"],
        "trial_id": best_match["trial_id"],
        "match_score": best_match["match_score"],
        "match_reason": "; ".join(best_match.get("match_reasons", [])),
        "status": "matched",
    }

    url = f"{ENROLLMENT_SERVICE_URL}/enrollments"

    response = requests.post(
        url,
        json=enrollment_payload,
        headers=auth_header(),
        timeout=15,
    )

    if response.status_code == 401:
        get_service_token(force_refresh=True)
        response = requests.post(
            url,
            json=enrollment_payload,
            headers=auth_header(),
            timeout=15,
        )

    response.raise_for_status()
    return response.json()


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

    enrollment_result = None

    if decision["enrolled"]:
        selected_match = decision["selected_match"]
        enrollment_result = create_enrollment(selected_match)

    return {
        "goal": "coordinate_candidate_matching",
        "candidate_id": candidate_id,
        "agent": coordinator.name,
        "matching_agent_called": True,
        "decision": decision,
        "candidate_update": candidate_update,
        "enrollment_created": decision["enrolled"],
        "enrollment": enrollment_result,
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
