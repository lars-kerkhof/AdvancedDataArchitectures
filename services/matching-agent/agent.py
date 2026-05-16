from dotenv import load_dotenv
from google.adk.agents import Agent

# Import the single, consolidated tool instead of the 3 separate ones
from tools import find_matches_for_candidate

load_dotenv()

matching_agent = Agent(
    name="matching_agent",
    model="gemini-2.5-flash",
    description="Matches clinical trial candidates to suitable trials.",
    instruction="""
You are the Matching Agent in a clinical trial recruitment platform.

Your task:
1. Call find_matches_for_candidate using the provided candidate ID.
2. Return the exact JSON structure provided by the tool.

Important rules:
- Do not enroll candidates.
- Do not make final eligibility decisions.
- Only return candidate-trial match suggestions.
- Always return valid JSON.
- Do not include markdown.
- Do not include explanation outside the JSON.
""",
    tools=[
        find_matches_for_candidate,
    ],
)
