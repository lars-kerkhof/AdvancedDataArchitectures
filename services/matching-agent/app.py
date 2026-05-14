import json
import os
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
    from google.genai.errors import ServerError
    import asyncio as _asyncio

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
    last_error = None

    for attempt in range(3):
        session_id = f"match-{candidate_id}-{attempt}"
        await session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=session_id,
        )

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
        except ServerError as e:
            last_error = e
            if attempt < 2:
                await _asyncio.sleep(2 * (attempt + 1))  # 2s, 4s
                continue
            raise HTTPException(
                status_code=503,
                detail=f"Gemini unavailable after retries: {e}",
            )

    if not final_response:
        raise HTTPException(
            status_code=500,
            detail="Matching agent produced no response",
        )

    try:
        cleaned_json = final_response.strip()
        if cleaned_json.startswith("```json"):
            cleaned_json = cleaned_json.replace("```json", "", 1)
        if cleaned_json.endswith("```"):
            cleaned_json = cleaned_json.rsplit("```", 1)[0]
        parsed_response = json.loads(cleaned_json.strip())
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Matching agent did not return valid JSON",
                "raw_response": final_response,
            },
        )

    matches = parsed_response.get("matches", [])
    matches = sorted(matches, key=lambda m: m.get("match_score", 0), reverse=True)

    return {
        "candidate_id": candidate_id,
        "agent": "matching_agent",
        "matches": matches,
        "match_score": matches[0].get("match_score", 0) if matches else 0,
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
