# Verification — Mid-Course Project

## Baseline check (before any changes)

Ran on the `mid-course-project` branch immediately after checkout, before touching any code:

```
23 passed, 3 warnings in 0.36s
```

All 23 existing tests (health check + full CRUD/status-transition suite from Modules 1–3) passed cleanly. This confirmed a clean starting point before feature work began.

## Backend test results (after both features, before the resubmission fix)

Full suite run at the point of original submission:

```
42 passed, 3 warnings in 0.24s
```

Breakdown:
- 23 original tests (Module 1–3 foundation) — still passing, confirming no regressions.
- 8 new tests for Feature 1 (due dates + overdue filter).
- 11 new tests for Feature 2 (tags/labels).

## Backend test results (final, after the resubmission fix below)

```
51 passed, 3 warnings in 0.24s
```

The additional 9 tests are the `TestUpdateRejectsExplicitNull` regression suite added in response to facilitator feedback (see below).

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

## Bug found during facilitator review: explicit `null` on PATCH

Facilitator review of the mid-course submission found that `PATCH /tasks/{id}` accepted an explicit `null` for `title`, `status`, or `priority` and returned `200`, silently corrupting the task (e.g. a task ending up with `title: null`). Root cause: the `title` validator explicitly let `None` pass through (treating it the same as "field omitted"), and `status`/`priority`/`tags` had no validator protecting them from `None` at all.

**Fix:** `TaskUpdate` validators now explicitly reject `None` for `title`, `status`, `priority`, and `tags` (these have no valid "empty" state on an existing task), while still allowing those fields to be **omitted** (meaning "leave unchanged" — Pydantic v2 does not run field validators on fields that are absent from the request body, only on fields that are present, so omission and explicit-null are distinguishable). Fields where `null` is a genuinely valid value — `description`, `assignee`, `due_date` — still accept explicit `null` to mean "clear this field."

## Break Test evidence — real defect / fix / defect cycle against the test suite

Per facilitator feedback, this replaces the earlier "valid input against already-correct code" evidence with a genuine break-fix-verify cycle, run against the actual pytest suite rather than a standalone script.

**Step 1 — reintroduced the original defect** (reverted the `title` validator to let `None` pass through unchanged) and ran the new regression tests:

```
$ python -m pytest tests/test_tasks.py::TestUpdateRejectsExplicitNull -v
...
FAILED tests/test_tasks.py::TestUpdateRejectsExplicitNull::test_explicit_null_title_returns_422
FAILED tests/test_tasks.py::TestUpdateRejectsExplicitNull::test_null_rejection_does_not_corrupt_existing_task
    AssertionError: assert None == 'Write tests'
==================== 2 failed, 7 passed, 1 warning in 0.08s ====================
```

This confirms the tests actually detect the bug — they fail when the defect is present, and the failure message shows exactly the corruption described in the facilitator feedback (`title` becoming `None`).

**Step 2 — restored the fix** and re-ran the full suite:

```
$ python -m pytest -v
======================== 51 passed, 3 warnings in 0.32s ========================
```

All 51 tests pass, confirming the fix resolves the defect without breaking anything else.

## Behavior contract (before/after a focused refactor)

After confirming the fix, a small refactor was made: the three near-identical "reject explicit null" checks in `status_not_null`, `priority_not_null`, and `tags_valid` (and `title_not_blank`) were duplicating the same `if v is None: raise ValueError(...)` pattern, so this was extracted into a single shared `_reject_explicit_none()` helper function.

**Before refactor:**
```
======================== 51 passed, 3 warnings in 0.24s ========================
```

**After refactor:**
```
======================== 51 passed, 3 warnings in 0.24s ========================
```

Identical result (51 passed, same warnings) before and after, confirming the refactor changed only internal structure, not behavior.

## Break Test evidence — malformed input (Feature 1 & 2, from original submission)

**Break Test — Due dates (malformed `due_date` input):**
```
Empty string:              422
Wrong format (13/01/2030): 422
Number instead of string:  422
Explicit null:             201 (correctly treated as "no due date" — due_date IS a
                                 genuinely optional field, unlike title/status/priority)
```

**Break Test — Tags (malformed `tags` input on create):**
```
Tag as a number instead of a string: 422
Tags as a string instead of a list:  422
Tag exceeding 30-character limit:    422
Explicit null on create:             422
```
On `TaskCreate`, `tags` is typed as `list[str]` (not optional), so explicit `null` fails validation there already — the correct way to represent "no tags" is an empty list `[]`. The facilitator-reported bug was specifically about `TaskUpdate` (PATCH), where this same protection was missing for `tags` (and `title`/`status`/`priority`) until the fix above.
