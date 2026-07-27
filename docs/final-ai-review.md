\# Final AI Review and Ownership Evidence



\## AGENTS.md guardrails

\- Repo-specific stack and commands included: yes

\- Docs-first/read-first guardrail included: yes

\- Unexpected app/frontend edits rule included: yes



\## AI code review mini-log

File reviewed: app/api/routes/tasks.py



| AI comment | Grade | Reason | Verification or decision |

|---|---|---|---|

| "The `tag in t.tags` filter in `list\_tasks` could raise an AttributeError if `tags` is ever None." | Wrong | Checked `TaskResponse` in app/models/task.py: `tags` uses `Field(default\_factory=list)`, so it is never None, always at least an empty list. | No change needed. |

| "Task IDs from `new\_task\_id()` might be sequential or guessable, allowing enumeration." | Wrong | Checked `new\_task\_id()`: it returns `str(uuid.uuid4())`, a cryptographically random UUID, not sequential or practically guessable. | No change needed. |

| "`\_get\_or\_404` is called on every read/update; consider caching the lookup." | Noise | Style preference only; no functional or performance issue at this scale (in-memory storage, course project). | No change made. |

| "There is no pagination on `list\_tasks`; a large result set could be unbounded." | Noise | Technically accurate in general, but irrelevant given in-memory storage and course-project scale. Not a real risk here. | No change made. |



\## AI security mini-review

Scope checked: app/api/routes/tasks.py, app/models/task.py



| Finding | File evidence | Grade | Reason | Next action |

|---|---|---|---|---|

| No authentication or authorization on any endpoint; anyone reaching the API can create, read, update, or delete any task. | app/api/routes/tasks.py — all routes have no auth dependency | Valid | Confirmed true by reading every route in the file. This is a real gap by security-checklist standards. | Documented as an intentional, out-of-scope boundary for this course project in AGENTS.md; not fixed, since adding auth would be a new feature outside the final project's allowed scope. |

| No rate limiting on any endpoint. | Same file, no throttling middleware present | Valid | Confirmed true. Same category as above — real, but out of scope for a course project. | Documented as an accepted, out-of-scope limitation. |

| `extra="forbid"` correctly rejects unexpected fields with 422 on all request models. | app/models/task.py, ConfigDict(extra="forbid") on TaskCreate and TaskUpdate | Valid (positive finding) | Confirmed by reading the model config; this is good practice already in place, not a gap. | No action needed; noted as an existing strength. |



\## Manual security check

I manually re-verified the null-validation fix from the mid-course-project resubmission: sent a PATCH request with explicit `null` for `title`, `status`, and `priority` and confirmed each is rejected with HTTP 422, while `description`, `assignee`, and `due\_date` still correctly accept explicit `null` to mean "clear this field." This confirms the original facilitator-flagged bug remains fixed on the final-project branch, rather than assuming the AI review would have caught a regression.



\## One AI output I rejected or corrected

The AI's code review flagged `tag in t.tags` as a potential AttributeError risk and flagged task IDs as guessable. Both were plausible-sounding but wrong once checked against the actual model code: `tags` always defaults to an empty list, and IDs are generated with `uuid.uuid4()`, not a sequential counter. I rejected both comments rather than acting on them, since the underlying code already handles what the AI assumed was missing.



\## Three AI usage rules

1\. Never paste real secrets, `.env` values, or personal/customer data into any AI tool or prompt.

2\. Always verify AI claims about the code against the actual file before accepting them as true.

3\. Record every AI finding with a grade and a reason, so decisions are traceable rather than just "AI said so."



\## Ownership statement

I reviewed this repository's business logic, tests, CI, and Docker setup personally and verified each piece by running it myself rather than trusting AI output at face value. Two of the four AI code review comments turned out to be wrong once checked against the actual model code, which is exactly why I treat AI review as a starting point for investigation, not a final answer. The security findings that were valid (no auth, no rate limiting) reflect real, intentional scope boundaries of a course project rather than oversights, and I documented them rather than silently accepting or hiding them. I'm comfortable submitting this repository as my own work because every claim in this document is backed by a command I ran or a file I read myself.

