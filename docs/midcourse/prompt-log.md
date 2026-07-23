# Prompt Log — Mid-Course Project

This log covers the prompts used with Claude (Anthropic) to implement both features. For each prompt, the AI's output was reviewed, then run against the pytest suite and manually verified in the browser before being accepted.

## Feature 1: Due dates + overdue filter

**Prompt 1 (initial ask):**
> "Draft user stories for a due-dates and overdue-filter feature added to an existing FastAPI Task Tracker with in-memory storage. Include acceptance criteria."

- **What AI returned:** 5 user stories, including one that implicitly assumed overdue status would be computed however was most convenient — it didn't commit to backend vs. frontend.
- **What I accepted/edited/rejected:** Accepted the story structure, but explicitly forced the design decision (backend-computed) rather than leaving it ambiguous, since the assignment requires a deliberate, documented decision.

**Prompt 2 (weak → strong rewrite):**
- **Weak version:** "add due dates to the task model"
- **Stronger version used:** "Add an optional `due_date: date` field to `TaskCreate`, `TaskUpdate`, and `TaskResponse` Pydantic v2 models. Add a computed `is_overdue` property on `TaskResponse` that returns `True` only if `due_date` is in the past and `status != Done`. Do not store `is_overdue`; compute it at read time."
- **What AI returned:** Full working model code, including the `@computed_field` decorator usage, matching the exact business rule.
- **What I accepted/edited/rejected:** Accepted as-is after reviewing the Pydantic v2 `computed_field` behavior (confirmed it recomputes per serialization, not once at creation, so "today" is always current).

**Prompt 3:**
> "Add pytest tests for: valid due date creation, invalid date format returns 422, a task with a past due date is overdue, a Done task with a past due date is NOT overdue, updating due date, and filtering by `overdue=true` returns only overdue tasks."

- **What AI returned:** 8 test functions covering each case.
- **What I accepted/edited/rejected:** Accepted all 8 after running them and confirming they passed against the real implementation, not just in isolation.

---

## Feature 2: Tags / labels

**Prompt 1:**
> "Add a `tags` field to the Task model as a list of strings. Validate: trim whitespace, reject blank tags, de-duplicate, cap at 10 tags of 30 characters each. On PATCH, tags should replace the existing list entirely; omitting the field should leave tags unchanged; an explicit empty list should clear all tags."

- **What AI returned:** A shared `_validate_tags` helper function used by both `TaskCreate` and `TaskUpdate` validators, plus the field additions.
- **What I accepted/edited/rejected:** Accepted the shared-validator approach as good practice (avoids duplicating validation logic between Create and Update models).

**Prompt 2 (weak → strong rewrite):**
- **Weak version:** "let users filter by tag"
- **Stronger version used:** "Add an optional `tag: str` query parameter to `GET /tasks` that returns only tasks where the tag is present in their `tags` list. No matches should return 200 with an empty list, not an error."
- **What AI returned:** The filter implementation using a simple `in` check against each task's tag list.
- **What I accepted/edited/rejected:** Accepted as-is; simple and matches the "good tests" guidance in the assignment brief exactly.

**Prompt 3:**
> "Write a Break Test: feed the tags field a number instead of a string, a string instead of a list, an oversized tag, and explicit null on create. Confirm each is rejected."

- **What AI returned:** A short script hitting the API with each malformed input.
- **What I accepted/edited/rejected:** Ran it myself and confirmed all four cases returned 422 as expected — this was the evidence used in `verification.md`.

---

## Resubmission fix: explicit-null validation bug (facilitator feedback)

**Prompt 1:**
> "Facilitator feedback says sending an explicit `null` for `title`, `status`, or `priority` on a task update is accepted with 200 instead of rejected with 422. Reproduce this bug against the actual API first, then explain the root cause before fixing anything."

- **What AI returned:** A reproduction script confirming `PATCH {"title": null}` returns 200 and sets `title` to `null`, plus an explanation that the `title` validator explicitly returned `None` unchanged, and `status`/`priority` had no validator at all.
- **What I accepted/edited/rejected:** Accepted the diagnosis, asked for confirmation the fix wouldn't also break legitimate omission (leaving a field unchanged) before applying it.

**Prompt 2:**
> "Fix this so explicit null is rejected for title, status, priority, and tags, but omitting those fields still works as before, and explicit null is still valid for description, assignee, and due_date. Verify with a script that checks all of these cases, not just the broken one."

- **What AI returned:** Updated validators, plus a verification script covering: explicit nulls that should be rejected, an omitted-field partial update that should still succeed, and explicit nulls that should still be accepted for the genuinely-optional fields.
- **What I accepted/edited/rejected:** Ran it and reviewed each printed status code against what I expected before accepting the fix as correct — this was to make sure the fix didn't overcorrect and break legitimate partial updates.

**Prompt 3 (real Break Test, not just valid-input-vs-broken-code):**
> "The facilitator specifically said Break Test evidence needs to show a test failing after a deliberate defect is introduced, then passing again after the fix is restored, not just valid input against already-correct code. Do that using the actual pytest suite: temporarily reintroduce the original bug, run the new regression tests to show them fail, then restore the fix and run the full suite."
- **What AI returned:** Reintroduced the exact original defect, ran `pytest`, showed 2 tests failing with the same symptom described in the feedback (`title` becoming `None`), then restored the fix and reran the full suite (51 passed).
- **What I accepted/edited/rejected:** This became the evidence in `verification.md` directly, since it's actual pytest output rather than a paraphrase.

## General note on AI-assisted workflow

Across both features, most of my edits to AI output were about being **more specific up front** rather than fixing broken code after the fact — for example, explicitly stating "replace, don't merge" for tag updates, and explicitly forcing the overdue computation into the backend rather than letting the AI pick. Every piece of generated code was run through the existing pytest suite plus new tests, and manually verified in the browser (creating tasks, checking pills/chips render correctly, testing filters) before being committed.
