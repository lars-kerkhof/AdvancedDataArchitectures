"""
Coordinator Agent.

For now, this agent coordinates only the Matching Agent.
Later, Screening Agent and Verification Agent can be added here.
"""


class CoordinatorAgent:
    def __init__(self):
        self.name = "coordinator-agent"

    def describe_goal(self, candidate_id: str):
        return {
            "goal": "find_trial_matches",
            "candidate_id": candidate_id,
            "next_agent": "matching-agent"
        }