import os
import requests
from datetime import date


CANDIDATE_SERVICE_URL = os.environ.get("CANDIDATE_SERVICE_URL")
TRIAL_SERVICE_URL = os.environ.get("TRIAL_SERVICE_URL")


def get_candidate_profile(candidate_id: str) -> dict:
    response = requests.get(f"{CANDIDATE_SERVICE_URL}/candidates/{candidate_id}")
    response.raise_for_status()
    return response.json()


def get_trial_catalog() -> list[dict]:
    response = requests.get(f"{TRIAL_SERVICE_URL}/trials")
    response.raise_for_status()
    return response.json()


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

    # Map internal IDs → external contract
    candidate_id = candidate.get("id")
    trial_id = trial.get("id")

    candidate_conditions = candidate.get("conditions", [])
    trial_condition = trial.get("condition")

    # Simplified condition match
    if trial_condition and trial_condition in candidate_conditions:
        score += 50
        reasons.append(f"Condition match: {trial_condition}")

    # Optional country match (only if trial has country field)
    if candidate.get("country") and trial.get("country"):
        if candidate.get("country") == trial.get("country"):
            score += 20
            reasons.append("Same country/site region")

    # Age from date_of_birth
    age = calculate_age(candidate.get("date_of_birth"))

    if age is not None and trial.get("min_age") is not None and trial.get("max_age") is not None:
        if trial["min_age"] <= age <= trial["max_age"]:
            score += 30
            reasons.append("Age fits trial criteria")

    return {
        "candidate_id": candidate_id,
        "trial_id": trial_id,
        "match_score": score,
        "match_reasons": reasons,
    }
