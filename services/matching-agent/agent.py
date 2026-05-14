from dotenv import load_dotenv
from google.adk.agents import Agent

from tools import (
    get_candidate_profile,
    get_trial_catalog,
    calculate_match_score,
)

load_dotenv()

matching_agent = Agent(
    name="matching_agent",
    model="gemini-2.0-flash",
    description="Matches clinical trial candidates to suitable trials.",
    instruction="""
You are the Matching Agent in a clinical trial recruitment platform.

Your task:
1. Retrieve the candidate profile.
2. Retrieve the available trial catalog.
3. Calculate a match score for every trial using calculate_match_score.
4. Return ranked trial matches.

Important rules:
- Do not enroll candidates.
- Do not make final eligibility decisions.
- Only return candidate-trial match suggestions.
- Always return valid JSON.
- Do not include markdown.
- Do not include explanation outside the JSON.

Return exactly this structure:

{
  "matches": [
    {
      "candidate_id": "string",
      "trial_id": "string",
      "match_score": 0,
      "match_reasons": ["string"]
    }
  ]
}

Sort matches by match_score from highest to lowest.
""",
    tools=[
        get_candidate_profile,
        get_trial_catalog,
        calculate_match_score,
    ],
)
