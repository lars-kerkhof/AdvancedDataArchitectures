# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Project Overview

Clinical Trial Recruitment Platform on Google Cloud Platform.
GCP project: `extended-optics-495508-r1` (region `us-central1`).

The system matches candidates to clinical trials using an LLM-powered agent and
orchestrates the end-to-end flow with Google Workflows.

## Architecture

Microservices on Cloud Run, fronted by a KrakenD API gateway, orchestrated by a
Google Workflow, with BigQuery as the data layer.

Workflow (clinical-trial-flow.yaml)
└── api-gateway (KrakenD)
├── iam-service -> users/jwt (BQ: iam_db)
├── candidate-intake-service -> candidates (BQ: candidate_intake_db)
├── trial-catalog-service -> trials (BQ: trial_catalog_db)
├── matching-agent (Vertex AI / Gemini ADK LlmAgent)
├── coordinator-agent (plain Python, decides enrollment)
└── enrollment-service -> enrollments (BQ: enrollment_db


Auth is JWT-based: services verify tokens by calling `iam-service /verify`.
Agent-to-service calls use a service token (see `service_token.py` in agents).

## Repo Layout

- `clinical-trial-flow.yaml` — Google Workflow definition (end-to-end happy path)
- `services/`
  - `iam-service/` — login, JWT issue/verify
  - `candidate-intake-service/` — candidate CRUD + `/recruitment-status` (admin-only)
  - `trial-catalog-service/` — trial CRUD
  - `matching-agent/` — Google ADK `LlmAgent` (Gemini 2.5 Flash on Vertex AI)
  - `coordinator-agent/` — plain Python; decides enrollment based on `MIN_MATCH_SCORE`
  - `enrollment-service/` — creates enrollment records
  - `cloud_build.yaml` — CI deploy for all six services
- `infrastructure/api-gateway/` — KrakenD config (`krakend.json`) + Dockerfile
- `tests/` — sample candidate/trial JSON payloads
- `Assumptions.md` — design assumptions

## Conventions

### Branches
- Feature work goes on `claude/...` branches (e.g. `claude/summarize-project-structure-ReOyb`).
- Never push to `main` without explicit user confirmation.

### Environment variables (services expect these)
- `IAM_URL` — base URL of iam-service (every service that requires auth needs it)
- `CANDIDATE_SERVICE_URL`, `TRIAL_SERVICE_URL`, `ENROLLMENT_SERVICE_URL` — for agents
- `MATCHING_AGENT_URL` — coordinator → matching
- `MIN_MATCH_SCORE` (coordinator-agent, default 50)
- Matching-agent (Vertex AI mode):
  - `GOOGLE_GENAI_USE_VERTEXAI=1`
  - `GOOGLE_CLOUD_PROJECT=extended-optics-495508-r1`
  - `GOOGLE_CLOUD_LOCATION=us-central1`
- `APP_NAME`, `AGENT_USER_ID` (agents — ADK session identifiers)

### Deploy

CI: `services/cloud_build.yaml` deploys all six services. Uses `--update-env-vars`
(not `--set-env-vars`) so existing env vars are preserved on each deploy.

Manual one-off deploys from PowerShell — note the `^|^` separator trick because
PowerShell mangles commas in gcloud arg lists:
```powershell
gcloud run services update matching-agent --region=us-central1 `
  --update-env-vars="^|^GOOGLE_GENAI_USE_VERTEXAI=1|GOOGLE_CLOUD_PROJECT=extended-optics-495508-r1|GOOGLE_CLOUD_LOCATION=us-central1"

  Workflows (clinical-trial-flow.yaml)
Uses hardcoded demo admin credentials (demo@example.com / demopass123) for now.
The final success message ("successfully matched and enrolled") prints
unconditionally on a successful HTTP from coordinator — it does NOT reflect
decision.enrolled. Inspect the JSON body, not the string.
return: ${e} shim in the except block exists for debugging. Remove for prod.
