import os
import requests


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


def calculate_match_score(candidate: dict, trial: dict) -> dict:
    score = 0
    reasons = []

    candidate_conditions = candidate.get("conditions", [])
    trial_conditions = trial.get("target_conditions", [])

    overlap = set(candidate_conditions).intersection(set(trial_conditions))

    if overlap:
        score += 50
        reasons.append(f"Condition overlap: {', '.join(overlap)}")

    if candidate.get("country") == trial.get("country"):
        score += 20
        reasons.append("Same country/site region")

    if candidate.get("age") and trial.get("min_age") and trial.get("max_age"):
        age = candidate["age"]
        if trial["min_age"] <= age <= trial["max_age"]:
            score += 30
            reasons.append("Age fits trial criteria")

    return {
        "trial_id": trial.get("trial_id"),
        "score": score,
        "reasons": reasons
    }