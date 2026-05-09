import os
import requests

MATCHING_AGENT_URL = os.environ.get("MATCHING_AGENT_URL", "")


def call_matching_agent(candidate_id: str):
    if not MATCHING_AGENT_URL:
        return {
            "error": "MATCHING_AGENT_URL environment variable is not set"
        }

    response = requests.post(f"{MATCHING_AGENT_URL}/match/{candidate_id}")
    response.raise_for_status()

    return response.json()