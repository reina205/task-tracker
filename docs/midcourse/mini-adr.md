# Mini-ADR — Mid-Course Project

## Feature 1: Due dates + overdue filter

**Decision:** Store `due_date` as an optional `date` field on the task. Compute "overdue" as a derived, read-time property (`is_overdue`) rather than a stored field, based on comparing `due_date` to the current date and checking the task is not `Done`.

**Alternatives considered and rejected:**
- **Computing overdue status in the frontend** (comparing `due_date` to `new Date()` in JavaScript) — rejected because it duplicates logic across every client, isn't directly testable with pytest, and could drift out of sync with backend business rules (e.g. the Done exception).
- **Storing `is_overdue` as a persisted boolean field, updated on a schedule** — rejected as unnecessary complexity for an in-memory, single-process app with no background job runner. Computing it at read time is simpler and always accurate.

**Risk to revisit if the project grew:** if this became a multi-user or persistent-database app, computing overdue status on every read could become a performance concern at scale (e.g. thousands of tasks), and might warrant a scheduled job to pre-compute and index it instead.

---

## Feature 2: Tags / labels

**Decision:** Store `tags` as a `list[str]` on the task, validated to trim whitespace, reject blank tags, de-duplicate, and cap at 10 tags of 30 characters each. `PATCH` semantics: providing `tags` **replaces** the full list (not merges); omitting it leaves tags unchanged; providing an empty list clears all tags.

**Alternatives considered and rejected:**
- **Storing tags as a single comma-separated string** (e.g. `"backend,urgent"`) — rejected because it pushes parsing and validation logic to every consumer of the field, makes duplicate/empty-tag detection error-prone (e.g. `"backend,,urgent"`), and complicates the `tag=` query filter (`in` checks against a substring rather than a list).
- **Merging tags on PATCH instead of replacing** (i.e. `PATCH` adds new tags without removing old ones) — rejected as the replace-list model, which matches how the frontend's tag input naturally works (a full comma-separated field, not an add/remove control), and is simpler to reason about and test.

**Risk to revisit if the project grew:** the current design allows any string as a tag with no normalization for case (e.g. "Backend" and "backend" are treated as different tags). If tag-based reporting or a tag-management UI were added later, case-insensitive normalization would likely be needed.
