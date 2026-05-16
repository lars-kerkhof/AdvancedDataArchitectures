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

app = FastAPI(title="Matching Agent", version="0.2.0")

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


def _extract_text(event) -> str | None:
    if not event.content or not event.content.parts:
        return None
    chunks = [getattr(p, "text", None) for p in event.content.parts]
    chunks = [c for c in chunks if c]
    return "".join(chunks) if chunks else None


def _parse_matches_json(raw: str) -> dict:
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if not m:
            raise
        return json.loads(m.group(0))


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
        parts=[types.Part(text=f"Match candidate {candidate_id} to suitable clinical trials.")],
    )

    final_response = None
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session_id,
        new_message=message,
    ):
        if event.is_final_response():
            text = _extract_text(event)
            if text:
                final_response = text

    if not final_response:
        raise HTTPException(status_code=500, detail="Matching agent produced no response")

    try:
        parsed = _parse_matches_json(final_response)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail={"error": "Matching agent did not return valid JSON", "raw_response": final_response},
        )

    if not isinstance(parsed, dict):
        raise HTTPException(status_code=500, detail={"error": "Top-level JSON not an object", "raw_response": final_response})

    matches = parsed.get("matches", []) or []
    matches.sort(key=lambda m: m.get("match_score", 0), reverse=True)

    return {
        "candidate_id": candidate_id,
        "agent": "matching_agent",
        "matches": matches,
        "match_score": matches[0].get("match_score", 0) if matches else 0,
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
