import os
import requests

from service_token import auth_header, get_service_token

MATCHING_AGENT_URL = os.environ.get("MATCHING_AGENT_URL", "")


def call_matching_agent(candidate_id: str):
    if not MATCHING_AGENT_URL:
        return {
            "error": "MATCHING_AGENT_URL environment variable is not set"
        }

    url = f"{MATCHING_AGENT_URL}/match/{candidate_id}"
    response = requests.post(url, headers=auth_header(), timeout=30)
    if response.status_code == 401:
        get_service_token(force_refresh=True)
        response = requests.post(url, headers=auth_header(), timeout=30)
    response.raise_for_status()

    return response.json()
