from google.adk.agents import Agent
from tools import get_candidate_profile, get_trial_catalog, calculate_match_score
from dotenv import load_dotenv


matching_agent = Agent(
    name="matching_agent",
    model="gemini-1.5-flash",
    description="Matches clinical trial candidates to suitable trials.",
    instruction="""
    You are the Matching Agent in a clinical trial recruitment platform.
    Your task is to match a candidate to suitable trials.

    Use the available tools to:
    1. Retrieve the candidate profile.
    2. Retrieve available trial metadata.
    3. Compare candidate attributes to trial criteria.
    4. Return ranked trial matches with reasons.

    Do not enroll candidates. Do not make final eligibility decisions.
    Only return candidate-trial match suggestions.
    """,
    tools=[
        get_candidate_profile,
        get_trial_catalog,
        calculate_match_score
    ]
)