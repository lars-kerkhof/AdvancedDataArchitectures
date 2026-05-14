import os
import requests
from datetime import date

from service_token import auth_header, get_service_token


CANDIDATE_SERVICE_URL = os.environ.get("CANDIDATE_SERVICE_URL")
TRIAL_SERVICE_URL = os.environ.get("TRIAL_SERVICE_URL")


def _get_with_service_token(url: str) -> requests.Response:
    response = requests.get(url, headers=auth_header(), timeout=30)
    if response.status_code == 401:
        # Token may be stale (clock skew / IAM restart). Force-refresh once.
        get_service_token(force_refresh=True)
        response = requests.get(url, headers=auth_header(), timeout=30)
    response.raise_for_status()
    return response


def get_candidate_profile(candidate_id: str) -> dict:
    return _get_with_service_token(
        f"{CANDIDATE_SERVICE_URL}/candidates/{candidate_id}"
    ).json()


def get_trial_catalog() -> list[dict]:
    return _get_with_service_token(f"{TRIAL_SERVICE_URL}/trials").json()


def calculate_age(date_of_birth: str) -> int | None:
    if not date_of_birth:
        return None

    birth_date = date.fromisoformat(date_of_birth)
    today = date.today()

    return (
        today.year
        - birth_date.year
        - ((today.month, today.day) < (birth_date.month, birth_date.day))
    )


def calculate_match_score(candidate: dict, trial: dict) -> dict:
    score = 0
    reasons = []

    candidate_conditions = [c.lower() for c in candidate.get("conditions", [])]
    trial_condition = trial.get("condition", "").lower()

    if trial_condition and any(trial_condition in c or c in trial_condition for c in candidate_conditions):
        score += 50
        reasons.append(f"Condition match: {trial_condition}")

    if candidate.get("country") and trial.get("country"):
        if candidate.get("country") == trial.get("country"):
            score += 20
            reasons.append("Same country/site region")

    age = calculate_age(candidate.get("date_of_birth"))
    if age is not None and trial.get("min_age") is not None and trial.get("max_age") is not None:
        if trial["min_age"] <= age <= trial["max_age"]:
            score += 30
            reasons.append("Age fits trial criteria")

    return {
        "candidate_id": candidate.get("id"),
        "trial_id": trial.get("id"),
        "match_score": score,
        "match_reasons": reasons,
    }
