import os
import requests
from fastapi import Depends, FastAPI, HTTPException

from auth import require_user
from service_token import auth_header, get_service_token
from tools import call_matching_agent

ENROLLMENT_SERVICE_URL = os.environ.get("ENROLLMENT_SERVICE_URL", "")

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok", "service": "coordinator-agent"}


def create_enrollment(best_match: dict) -> dict:
    if not ENROLLMENT_SERVICE_URL:
        raise HTTPException(
            status_code=500,
            detail="ENROLLMENT_SERVICE_URL environment variable is not set"
        )

    enrollment_payload = {
        "candidate_id": best_match["candidate_id"],
        "trial_id": best_match["trial_id"],
        "match_score": best_match["match_score"],
        "match_reason": "; ".join(best_match.get("match_reasons", [])),
        "status": "matched"
    }

    url = f"{ENROLLMENT_SERVICE_URL}/enrollments"
    response = requests.post(url, json=enrollment_payload, headers=auth_header(), timeout=15)
    if response.status_code == 401:
        get_service_token(force_refresh=True)
        response = requests.post(url, json=enrollment_payload, headers=auth_header(), timeout=15)
    response.raise_for_status()

    return response.json()


@app.post("/coordinate/match/{candidate_id}")
def coordinate_match(candidate_id: str, _user=Depends(require_user)):
    matching_result = call_matching_agent(candidate_id)

    matches = matching_result.get("matches", [])

    if not matches:
        raise HTTPException(
            status_code=404,
            detail=f"No trial matches found for candidate {candidate_id}"
        )

    # Minimum 50 — that's the score the matching agent gives for a condition
    # match, which is the only signal that the trial is actually relevant to
    # the candidate. Country and age alone (20+30) shouldn't trigger enrollment.
    MIN_MATCH_SCORE = 50

    best_match = matches[0]
    if best_match.get("match_score", 0) < MIN_MATCH_SCORE:
        raise HTTPException(
            status_code=404,
            detail=f"No suitable trial match for candidate {candidate_id}"
        )

    enrollment_result = create_enrollment(best_match)

    return {
        "goal": "find_trial_matches_and_create_enrollment",
        "candidate_id": candidate_id,
        "agent_used": "matching-agent",
        "selected_match": best_match,
        "enrollment": enrollment_result
    }
