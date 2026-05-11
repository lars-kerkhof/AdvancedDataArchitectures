import os
import requests
from fastapi import FastAPI, HTTPException
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

    response = requests.post(
        f"{ENROLLMENT_SERVICE_URL}/enrollments",
        json=enrollment_payload
    )
    response.raise_for_status()

    return response.json()


@app.post("/coordinate/match/{candidate_id}")
def coordinate_match(candidate_id: str):
    matching_result = call_matching_agent(candidate_id)

    matches = matching_result.get("matches", [])

    if not matches:
        raise HTTPException(
            status_code=404,
            detail=f"No trial matches found for candidate {candidate_id}"
        )

    best_match = matches[0]
    enrollment_result = create_enrollment(best_match)

    return {
        "goal": "find_trial_matches_and_create_enrollment",
        "candidate_id": candidate_id,
        "agent_used": "matching-agent",
        "selected_match": best_match,
        "enrollment": enrollment_result
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
