import os
from fastapi import FastAPI
from tools import call_matching_agent

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok", "service": "coordinator-agent"}


@app.post("/coordinate/match/{candidate_id}")
def coordinate_match(candidate_id: str):
    result = call_matching_agent(candidate_id)

    return {
        "goal": "find_trial_matches",
        "candidate_id": candidate_id,
        "agent_used": "matching-agent",
        "result": result
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("app:app", host="0.0.0.0", port=port)