from dotenv import load_dotenv
from google.adk.agents import Agent
from google.genai import types

from tools import find_matches_for_candidate

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

Your task:
1. Call find_matches_for_candidate with the provided candidate_id (a string).
2. Return the tool's response as JSON, in exactly this shape:

{
  "matches": <the "matches" array returned by the tool>
}

Rules:
- Only call find_matches_for_candidate. Do not call any other tool.
- Do not invent scores or trials. Use exactly what the tool returns.
- Do not include markdown fences or commentary.
- If the tool returns an empty matches array, return {"matches": []}.
""",
    tools=[find_matches_for_candidate],
)
