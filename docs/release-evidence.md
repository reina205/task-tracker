\# Release Evidence



\## Baseline

\- Branch: final-project

\- Date: 2026-07-27

\- Local app run command: `uvicorn app.main:app --reload`

\- /health result: `{"status":"ok","timestamp":"2026-07-24T07:02:26.042831+00:00"}`

\- Frontend check: Kanban board loaded at frontend/index.html; created a test task, confirmed the "Done cannot move back to ToDo/InProgress" business rule is still correctly enforced

\- Test command: `pytest`

\- Test result: 51 passed, 3 warnings, in 0.84s



\## CI evidence

\- Workflow file: .github/workflows/ci.yml

\- Latest run link or note: CI #1, commit ad4eacf, ran successfully on final-project branch (https://github.com/reina205/task-tracker/actions)

\- Test command used by CI: `pytest`

\- Shortcut check: no `continue-on-error`, no `|| true`, pytest is not skipped, Python version pinned to 3.12 explicitly



\## Docker evidence

\- Build command: `docker build -t task-tracker .`

\- Run command: `docker run -p 8000:8000 task-tracker`

\- /health check: `{"status":"ok","timestamp":"2026-07-27T09:15:07.270739+00:00"}`

\- Non-root check, if implemented: Yes — Dockerfile creates and switches to a non-root user (`appuser`) before running the app

\- No-baked-secrets check: Yes — `.dockerignore` excludes `.env`, `.env.example`, `.git`, `venv`, tests, and docs from the build context; Dockerfile only copies `requirements.txt` and `app/`



\## Documentation claim-vs-reality log

| Claim checked | Evidence used | Result | Change made, if any |

|---|---|---|---|

| README backend run command (`uvicorn app.main:app --reload`) starts the API correctly | Ran the command locally, confirmed server started on port 8000 | Confirmed accurate | None |

| `/health` endpoint returns HTTP 200 with status "ok" | Ran `curl http://127.0.0.1:8000/health` locally and inside the Docker container | Confirmed accurate in both environments | None |

| Task in Done status cannot move back to ToDo or InProgress (business rule) | Created a test task, moved it to Done, attempted to move it back via UI | Confirmed accurate — app correctly rejected the transition with an error message | None |

