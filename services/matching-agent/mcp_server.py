from mcp.server.fastmcp import FastMCP
from tools import get_candidate_profile, get_trial_catalog, calculate_match_score

mcp = FastMCP("matching-agent-mcp")


@mcp.tool()
def match_candidate(candidate_id: str) -> dict:
    candidate = get_candidate_profile(candidate_id)
    trials = get_trial_catalog()

    matches = []
    for trial in trials:
        result = calculate_match_score(candidate, trial)
        matches.append(result)

    # FIX: use match_score instead of score
    matches = sorted(matches, key=lambda x: x["match_score"], reverse=True)

    return {
        "candidate_id": candidate_id,
        "matches": matches[:5]
    }


if __name__ == "__main__":
    mcp.run()
