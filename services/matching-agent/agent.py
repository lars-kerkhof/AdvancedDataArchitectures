from dotenv import load_dotenv
from google.adk.agents import Agent
from google.genai import types

from tools import (
    get_candidate_profile,
    get_trial_catalog,
    score_trials,
)

load_dotenv()

_SAFETY_OFF = [
    types.SafetySetting(category=c, threshold="BLOCK_NONE")
    for c in [
        "HARM_CATEGORY_HARASSMENT",
        "HARM_CATEGORY_HATE_SPEECH",
        "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "HARM_CATEGORY_DANGEROUS_CONTENT",
    ]
]

_GENERATE_CONFIG = types.GenerateContentConfig(
    temperature=0.2,
    response_mime_type="application/json",
    safety_settings=_SAFETY_OFF,
    http_options=types.HttpOptions(
        retry_options=types.HttpRetryOptions(
            attempts=3,
            http_status_codes=[408, 429, 500, 502, 503, 504],
        ),
    ),
)

matching_agent = Agent(
    name="matching_agent",
    model="gemini-2.5-flash",
    description="Matches clinical trial candidates to suitable trials.",
    generate_content_config=_GENERATE_CONFIG,
    instruction="""
You are the Matching Agent in a clinical trial recruitment platform.

You MUST follow this exact three-step process:
1. Call get_candidate_profile with the provided candidate_id.
2. Call get_trial_catalog with no arguments.
3. Call score_trials, passing the candidate dict from step 1 and the trials list from step 2.

Then return ONLY this JSON object (no markdown, no commentary):

{
  "matches": <the list returned by score_trials>
}

If score_trials returns an empty list, return {"matches": []}.
Do not invent scores. Do not skip any step.
""",
    tools=[
        get_candidate_profile,
        get_trial_catalog,
        score_trials,
    ],
)
