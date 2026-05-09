# Coordinator Agent

The Coordinator Agent receives goal-oriented requests and delegates them to specialist agents.

## Current scope

For now, it only coordinates the Matching Agent.

## Endpoints

### Health check

GET /health

### Coordinate matching

POST /coordinate/match/{candidate_id}

## Environment variables

MATCHING_AGENT_URL=https://matching-agent-xxxxx.run.app