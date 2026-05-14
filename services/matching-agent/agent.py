from dotenv import load_dotenv
from google.adk.agents.llm_agent import LlmAgent
from google.genai import types

from tools import (
    get_candidate_profile,
    get_trial_catalog,
    calculate_match_score,
)

load_dotenv()

matching_agent = LlmAgent(
    name="matching_agent",
    model="gemini-2.5-flash",
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
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2,
        max_output_tokens=1000,
        safety_settings=[
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.BLOCK_NONE,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=types.HarmBlockThreshold.BLOCK_NONE,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=types.HarmBlockThreshold.BLOCK_NONE,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=types.HarmBlockThreshold.BLOCK_NONE,
            ),
        ],
        http_options=types.HttpOptions(
            retry_options=types.HttpRetryOptions(
                initial_delay=1.0,
                attempts=3,
                http_status_codes=[408, 429, 500, 502, 503, 504],
            ),
            timeout=120 * 1000,
        ),
    ),
    tools=[
        get_candidate_profile,
        get_trial_catalog,
        calculate_match_score,
    ],
)
