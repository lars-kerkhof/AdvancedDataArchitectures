# agent.py

import os


class CoordinatorAgent:
    def __init__(self):
        self.name = "coordinator-agent"
        self.min_match_score = int(os.getenv("MIN_MATCH_SCORE", "50"))

    def decide_enrollment(self, candidate_id: str, matches: list[dict]) -> dict:
        if not matches:
            return {
                "candidate_id": candidate_id,
                "action": "set_enrolled_false",
                "enrolled": False,
                "reason": "No trial matches found",
            }

        best_match = sorted(
            matches,
            key=lambda match: match.get("match_score", 0),
            reverse=True,
        )[0]

        score = best_match.get("match_score", 0)

        if score >= self.min_match_score:
            return {
                "candidate_id": candidate_id,
                "action": "set_enrolled_true",
                "enrolled": True,
                "reason": f"Best match score {score} is above threshold {self.min_match_score}",
                "selected_match": best_match,
            }

        return {
            "candidate_id": candidate_id,
            "action": "set_enrolled_false",
            "enrolled": False,
            "reason": f"Best match score {score} is below threshold {self.min_match_score}",
            "selected_match": best_match,
        }
