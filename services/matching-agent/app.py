# app.py
from fastapi import FastAPI, HTTPException
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agent import matching_agent

app = FastAPI()

APP_NAME = "clinical_trial_matching"
USER_ID = "api_user"

session_service = InMemorySessionService()
runner = Runner(
    agent=matching_agent,
    app_name=APP_NAME,
    session_service=session_service,
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "matching-agent"}


@app.post("/match/{candidate_id}")
async def match(candidate_id: str):
    session_id = f"match-{candidate_id}"

    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id,
    )

    message = types.Content(
        role="user",
        parts=[
            types.Part(
                text=(
                    f"Match candidate {candidate_id} to suitable clinical trials. "
                    "Use the available tools and return ranked matches with reasons."
                )
            )
        ],
    )

    final_response = None

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session_id,
        new_message=message,
    ):
        if event.is_final_response():
            final_response = event.content.parts[0].text

    if final_response is None:
        raise HTTPException(status_code=500, detail="Matching agent produced no response")

    return {
        "candidate_id": candidate_id,
        "agent": "matching_agent",
        "result": final_response,
    }
