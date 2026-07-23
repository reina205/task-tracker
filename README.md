# Task Tracker

A simple Kanban-style task board: FastAPI backend (in-memory storage) + a
vanilla HTML/CSS/JS frontend with native drag-and-drop.

## Scope (Module 1 ADR)

- Create, view, update, delete tasks.
- Filter by status and priority.
- Fields: id, title, description, status, priority, assignee.
- Status transitions: a task in **Done** cannot move back to ToDo or InProgress.
- No authentication, no database, no real-time sync (in-memory only, single process).

## Running the backend

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- Health check: `curl http://localhost:8000/health`

## Running the frontend

The frontend is static — no build step. With the backend running on port 8000:

```bash
cd frontend
python -m http.server 5500
```

Then open http://localhost:5500 in your browser.

(Opening `index.html` directly by double-clicking also works in most
browsers, since the frontend talks to the backend via CORS-enabled `fetch`.)

## Running tests

```bash
pytest -v
```

51 tests cover: task creation and validation, listing and filtering,
get-by-id, partial updates, the Done status-transition rule, delete
(including 404/422 edge cases), due dates and the overdue filter, tags
and tag filtering, and a dedicated regression suite (`TestUpdateRejectsExplicitNull`)
confirming that PATCH rejects explicit `null` for `title`/`status`/`priority`/`tags`
while still allowing those fields to be omitted, and still allowing explicit
`null` for the genuinely optional fields (`description`, `assignee`, `due_date`).

## Project structure

```
app/
  main.py              FastAPI app + /health
  models/task.py       Pydantic v2 models (TaskCreate, TaskUpdate, TaskResponse)
  storage/memory.py     In-memory task storage
  api/routes/tasks.py   CRUD endpoints + status-transition business rule
frontend/
  index.html, style.css, app.js   Kanban board UI
tests/
  conftest.py           TestClient + autouse storage reset fixture
  test_tasks.py          CRUD + business rule test suite
  test_health.py        Health check test
docs/midcourse/          Mid-course project documentation (added later)
```
