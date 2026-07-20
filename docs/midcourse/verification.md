# Verification — Mid-Course Project

## Baseline check (before any changes)

Ran on the `mid-course-project` branch immediately after checkout, before touching any code:

```
23 passed, 3 warnings in 0.36s
```

All 23 existing tests (health check + full CRUD/status-transition suite from Modules 1–3) passed cleanly. This confirmed a clean starting point before feature work began.

## Backend test results (after both features)

Final full suite run:

```
42 passed, 3 warnings in 0.24s
```

Breakdown:
- 23 original tests (Module 1–3 foundation) — still passing, confirming no regressions.
- 8 new tests for Feature 1 (due dates + overdue filter).
- 11 new tests for Feature 2 (tags/labels).

The 3 warnings are pre-existing `StarletteDeprecationWarning` notices from FastAPI's own dependencies (`httpx`/`starlette.testclient`, and the `HTTP_422_UNPROCESSABLE_ENTITY` naming). They are unrelated to this project's code and were present in the original baseline too.

## Manual browser checks

Both features were manually tested end-to-end in the browser (backend on `localhost:8000`, frontend on `localhost:5500`):

**Due dates + overdue filter:**
- Created a task with a past due date → card rendered a red "Overdue: [date]" pill.
- Created a task with a future due date → card rendered a plain gray "Due [date]" pill.
- Checked the "Overdue only" filter checkbox → board correctly showed only the overdue task.
- Edited a task's due date via the modal → pill updated correctly on save (confirmed by correcting a mistyped year and watching the card switch from overdue to non-overdue).

**Tags/labels:**
- Created tasks with comma-separated tags → tag chips rendered correctly on cards.
- Used the "Filter by tag" box → board correctly filtered to only matching tasks live as text was typed.
- Edited an existing task → tags field was pre-filled with existing tags, confirming the edit round-trip works.

## Behavior contract (before/after refactor)

No structural refactor was needed after implementing the two features — the existing CRUD/status-transition logic (Modules 1–3) was extended rather than restructured. The full pytest suite (42 tests, including all 23 original tests) was re-run after each feature was added and passed both times, confirming the existing behavior contract (status-transition rules, CRUD status codes, validation) remained intact throughout.

## Break Test evidence

**Break Test 1 — Due dates (malformed `due_date` input):**
```
Empty string:              422
Wrong format (13/01/2030): 422
Number instead of string:  422
Explicit null:             201 (correctly treated as "no due date")
```
All malformed inputs were correctly rejected; explicit `null` was correctly accepted as valid ("no due date set").

**Break Test 2 — Tags (malformed `tags` input):**
```
Tag as a number instead of a string: 422
Tags as a string instead of a list:  422
Tag exceeding 30-character limit:    422
Explicit null on create:             422
```
All four malformed inputs were correctly rejected. The last case is notable: since `tags` is typed as `list[str]` (not optional) on creation, explicit `null` fails validation — the correct way to represent "no tags" is an empty list `[]`, which is what the frontend and default value use.
