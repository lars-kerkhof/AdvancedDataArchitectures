import os

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

load_dotenv()

MATCHING_MCP_URL = os.environ["MATCHING_MCP_URL"]

mcp_tools = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=f"{MATCHING_MCP_URL}/mcp",
        timeout=120.0,
    ),
)

matching_agent = Agent(
    name="matching_agent",
    model="gemini-2.5-flash",
    description="Matches clinical trial candidates to suitable trials.",
    instruction="""
You are the Matching Agent in a clinical trial recruitment platform.

Your task:
1. Call the match_candidate tool with the provided candidate ID.
2. Return the exact JSON structure returned by the tool, in this shape:

{
  "matches": <the matches array returned by match_candidate>
}

Important rules:
- Do not enroll candidates.
- Do not make final eligibility decisions.
- Only return candidate-trial match suggestions.
- Always return valid JSON.
- Do not include markdown fences.
- Do not include explanation outside the JSON.
""",
    tools=[mcp_tools],
)
