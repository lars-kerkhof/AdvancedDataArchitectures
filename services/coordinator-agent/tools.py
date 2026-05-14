import os
import requests

from service_token import auth_header, get_service_token

MATCHING_AGENT_URL = os.environ.get("MATCHING_AGENT_URL", "")
CANDIDATE_SERVICE_URL = os.environ.get("CANDIDATE_SERVICE_URL", "")


def call_matching_agent(candidate_id: str):
    if not MATCHING_AGENT_URL:
        return {
            "error": "MATCHING_AGENT_URL environment variable is not set"
        }

    url = f"{MATCHING_AGENT_URL}/match/{candidate_id}"
    response = requests.post(url, headers=auth_header(), timeout=60)
    if response.status_code == 401:
        get_service_token(force_refresh=True)
        response = requests.post(url, headers=auth_header(), timeout=60)
    response.raise_for_status()

    return response.json()


def update_candidate_enrolled(candidate_id: str, enrolled: bool):
    if not CANDIDATE_SERVICE_URL:
        return {
            "error": "CANDIDATE_SERVICE_URL environment variable is not set"
        }

    url = f"{CANDIDATE_SERVICE_URL}/candidates/{candidate_id}/recruitment-status"
    payload = {"recruitment_status": "enrolled" if enrolled else "rejected"}

    response = requests.put(url, json=payload, headers=auth_header(), timeout=30)

    if response.status_code == 401:
        get_service_token(force_refresh=True)
        response = requests.put(url, json=payload, headers=auth_header(), timeout=30)

    response.raise_for_status()
    return response.json()
