\# AGENTS.md



\## Project stack

\- Backend: FastAPI (Python), Pydantic v2 models, in-memory storage

\- Frontend: vanilla HTML/CSS/JS (Kanban board UI), no build step

\- Tests: pytest, TestClient with an autouse fixture that resets storage between tests



\## Setup and run commands

\- Create venv: `python -m venv venv`

\- Activate venv: `venv\\Scripts\\activate`

\- Install deps: `pip install -r requirements.txt`

\- Run backend: `uvicorn app.main:app --reload`

\- Run frontend: open `frontend/index.html` directly in a browser

\- Run tests: `pytest`

\- Health check: `curl http://127.0.0.1:8000/health`



\## Guardrails for AI tools working in this repo

1\. \*\*Read first, docs-first.\*\* Before proposing any change, read the relevant file(s) and any related docs in `docs/`. Do not assume behavior — verify against the actual code.

2\. \*\*No new product features.\*\* Do not add comments, authentication, a production database, notifications, or unrelated UI changes. This repo is in hardening/documentation mode only.

3\. \*\*Protect `app/` and `frontend/`.\*\* Only touch these folders for a small bug fix, a security fix, or a documentation-supported correction. Any such change must be explained in `docs/final-ai-review.md`.

4\. \*\*No secrets.\*\* Never write real credentials, `.env` values, tokens, production logs, or real personal/customer data into the repo or into AI prompts.

5\. \*\*Every suggestion must be reviewed and tested before acceptance.\*\* AI output is a draft, not a merge-ready change. Human review, test runs, and manual verification always happen before anything is accepted.

6\. \*\*State the existing business rules, don't "fix" them without confirmation.\*\* For example, tasks in `Done` cannot move back to `To Do` or `In Progress` — this is an intentional rule, not a bug, unless documentation says otherwise.



\## Known business rules (do not treat as bugs)

\- A task in `Done` cannot transition back to `To Do` or `In Progress`.

\- Task `title`, `status`, and `priority` must be non-null on update (explicit `null` is rejected with HTTP 422).



\## Security notes

\- No authentication layer exists; this is an intentional scope boundary for a course project, not an oversight to silently patch.

\- Storage is in-memory only; no persistent database or migrations.

