import json
import os
import re
import uuid

import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from auth import require_user
from agent import matching_agent

app = FastAPI(title="Matching Agent", version="0.1.0")

APP_NAME = os.getenv("APP_NAME", "clinical_trial_matching")
USER_ID = os.getenv("AGENT_USER_ID", "api_user")

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
async def match(candidate_id: str, _user=Depends(require_user)):
    session_id = f"match-{candidate_id}-{uuid.uuid4().hex[:8]}"

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
                    "Return only valid JSON with a matches array."
                )
            )
        ],
    )

    final_response = None

    try:
        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=session_id,
            new_message=message,
        ):
            if not event.is_final_response():
                continue
            if not event.content or not event.content.parts:
                continue
            for part in event.content.parts:
                if getattr(part, "text", None):
                    final_response = part.text
                    break
            if final_response:
                break
    finally:
        try:
            await session_service.delete_session(
                app_name=APP_NAME,
                user_id=USER_ID,
                session_id=session_id,
            )
        except Exception:
            pass

    # VERANDERING 1: Geen 500-error meer als de agent geen tekst teruggeeft (bijv. bij een kale function_call)
    if not final_response:
        print(f"Waarschuwing: Geen final_response ontvangen voor {candidate_id}.")
        parsed_response = {"matches": []}
    else:
        cleaned_json = final_response.strip()
        cleaned_json = re.sub(r"^
http://googleusercontent.com/immersive_entry_chip/0
