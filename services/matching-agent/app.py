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

    if not final_response:
        raise HTTPException(
            status_code=500,
            detail="Matching agent produced no response (possibly safety-filtered or empty)",
        )

    cleaned_json = final_response.strip()
    cleaned_json = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned_json, flags=re.MULTILINE)
    match_obj = re.search(r"\{.*\}", cleaned_json, flags=re.DOTALL)
    if match_obj:
        cleaned_json = match_obj.group(0)

    try:
        parsed_response = json.loads(cleaned_json)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Matching agent did not return valid JSON",
                "raw_response": final_response,
            },
        )

    if not isinstance(parsed_response, dict):
        matches = []
    else:
        matches = parsed_response.get("matches", [])

    matches = sorted(
        matches,
        key=lambda m: m.get("match_score", 0),
        reverse=True,
    )

    return {
        "candidate_id": candidate_id,
        "agent": "matching_agent",
        "matches": matches,
        "match_score": matches[0].get("match_score", 0) if matches else 0,
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
