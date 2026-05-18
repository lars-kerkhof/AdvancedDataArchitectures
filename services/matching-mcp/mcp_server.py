"""FastMCP server exposing matching tools over HTTP for the matching-agent LlmAgent."""
import os

from fastmcp import FastMCP

from tools import find_matches_for_candidate

mcp = FastMCP(name="matching-mcp")


@mcp.tool
def match_candidate(candidate_id: str) -> dict:
    """Score every trial in the catalog against the given candidate.

    Args:
        candidate_id: The candidate's unique identifier (e.g. "cand_abc123...").

    Returns:
        dict with a "matches" array of {candidate_id, trial_id, match_score, match_reasons}, sorted by score descending.
    """
    return find_matches_for_candidate(candidate_id)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    mcp.run(transport="http", host="0.0.0.0", port=port)
