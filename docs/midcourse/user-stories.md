# User Stories — Mid-Course Project

## Feature 1: Due dates + overdue filter

**Story 1.** As a user, I want to set an optional due date when creating a task, so I can track when it needs to be done.
- Acceptance criteria:
  - `due_date` is optional on task creation.
  - If provided, it must be a valid ISO date (`YYYY-MM-DD`); invalid formats return `422`.
  - Omitting it entirely leaves the task with no due date.

**Story 2.** As a user, I want to update the due date of an existing task, so I can adjust my plans.
- Acceptance criteria:
  - `PATCH /tasks/{id}` accepts a `due_date` field.
  - An invalid date format returns `422`.
  - Omitting `due_date` from a PATCH request leaves the existing due date unchanged.

**Story 3.** As a user, I want to see which tasks are overdue, so I know what needs urgent attention.
- Acceptance criteria:
  - A task is "overdue" if its `due_date` is before today **and** its status is not `Done`.
  - A `Done` task is never overdue, even with a past due date.
  - Overdue status is computed at read time, not stored, so it stays accurate over time.

**Story 4.** As a user, I want to filter my task list to show only overdue tasks, so I can focus on what's late.
- Acceptance criteria:
  - `GET /tasks?overdue=true` returns only overdue tasks.
  - `GET /tasks?overdue=false` returns only non-overdue tasks.
  - No matches returns `200` with an empty list, not an error.

**Story 5.** As a user, I want to see a due date or overdue indicator on task cards in the UI, so I don't have to open each task to check.
- Acceptance criteria:
  - Cards with a due date show a pill with the date.
  - Overdue cards show a visually distinct (red) pill instead of the default (gray) one.
  - Cards with no due date show no pill.

**AI assumption corrected:** the initial draft assumed overdue status should be *computed in the frontend* using the browser's current date. We corrected this to compute it in the **backend** instead, so the value is consistent regardless of which client calls the API, and so it can be tested directly with pytest rather than relying on JavaScript date logic.

---

## Feature 2: Tags / labels

**Story 6.** As a user, I want to add tags to a task, so I can categorize it (e.g. "backend", "urgent").
- Acceptance criteria:
  - `tags` accepts a list of strings on creation; defaults to an empty list if omitted.
  - Each tag is trimmed of leading/trailing whitespace.
  - A blank or whitespace-only tag is rejected with `422`.

**Story 7.** As a user, I want duplicate or excessive tags to be handled sensibly, so my task list stays clean.
- Acceptance criteria:
  - Duplicate tags in the same request are silently de-duplicated (not an error).
  - A task may have at most 10 tags; exceeding this returns `422`.
  - A single tag may be at most 30 characters; exceeding this returns `422`.

**Story 8.** As a user, I want to update a task's tags, so I can re-categorize it later.
- Acceptance criteria:
  - `PATCH /tasks/{id}` with a `tags` field **replaces** the existing tag list entirely.
  - Omitting `tags` from a PATCH request leaves existing tags unchanged.
  - Sending `tags: []` explicitly clears all tags.

**Story 9.** As a user, I want to filter tasks by tag, so I can quickly find related work.
- Acceptance criteria:
  - `GET /tasks?tag=backend` returns only tasks containing that tag.
  - No matches returns `200` with an empty list.

**Story 10.** As a user, I want to see and edit tags directly in the task board UI, so tagging doesn't require using the API directly.
- Acceptance criteria:
  - Tags render as chips on each card.
  - The task modal has a comma-separated tags input, pre-filled with existing tags on edit.
  - A "Filter by tag" box in the toolbar filters the visible board live as you type.

**AI assumption corrected:** the initial draft considered storing tags as a single comma-separated string field (simpler to display) rather than a proper list. We corrected this to use a **list of strings**, since it validates more cleanly (each tag checked independently), and filtering/deduplication logic is simpler and less error-prone than parsing a raw string on every request.
