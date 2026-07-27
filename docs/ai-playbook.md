\# My AI Playbook



\## When I reach for AI first

\- Drafting boilerplate I already know how to write by hand (CI YAML syntax, Dockerfile structure, README sections) — AI saves time on the "shape" of the file, but I still need to check the specifics against my actual repo.

\- Getting a second set of eyes on a file I already understand well, to catch things I might have missed — treating AI review as a checklist prompt, not a verdict.

\- Explaining unfamiliar tooling quickly (e.g. what a Docker multi-stage build actually does) before I commit to using it.



\## When I do not reach for AI first

\- Anything involving the actual business logic of my app (the Done status-transition rule, the null-validation fix) — I write and test that myself, because I'm the one who has to explain it if asked.

\- Anything touching real credentials, `.env` values, or personal data — never goes into a prompt, period.

\- Situations where I don't yet understand the risk well enough to judge whether AI's answer is even reasonable (e.g. security findings) — I check the actual code first, then evaluate the AI's claim against it, not the other way around.



\## My non-negotiables

\- No real secrets, tokens, or personal/customer data in any prompt or repo file.

\- Every AI suggestion gets tested or read against the actual code before I accept it — "it sounds right" is not verification.

\- I don't accept an AI claim about my own code without checking the relevant file myself first.

\- Business rules that look like bugs get confirmed against documentation or tests before I "fix" them.



\## My review rules

\- I read the diff or file myself before I read the AI's comments on it, so I'm not anchored to its framing.

\- I grade every AI code or security comment as Useful, Noise, or Wrong (or Valid/False Positive/Noise for security) with a one-line reason — no ungraded feedback makes it into my decisions.

\- If an AI claim can be checked with one command (running a test, reading a model file), I run that command before deciding, instead of trusting the claim on its own.

\- I don't let an AI "security finding" become a real action item until I've confirmed it's actually reachable in my code, not just plausible-sounding.



\## What I am still figuring out

\- Where the line is between "acceptable AI-drafted boilerplate" and "I should really understand this well enough to write it myself" — CI YAML and Dockerfiles are still a bit of a gray area for me.

\- How much weight to give an AI security review when the finding is valid but genuinely out of scope (like no-auth on a course project) — documenting it feels right, but I'm not fully sure that's the correct instinct in every context.

\- Team norms: I've only worked on this project solo, so I don't yet have a tested sense of how AI-review grading should work when more than one person is involved.



\## Decision Card

| Situation | What I do |

|---|---|

| New feature request | Reach for AI to draft, but I write the tests myself first so I know what "correct" means before I look at AI output. |

| Code review | Read the diff myself first, then run AI review, then grade every comment before acting on any of it. |

| Debugging | Try to reproduce and understand the bug myself first; use AI to brainstorm causes only after I already have the failing behavior in front of me. |

| Infrastructure (CI/Docker) | Let AI draft the structure, but verify every command against the actual project (does this Python version match, does this port match, does this path exist). |

| One rule | If I can't explain why a line of AI-suggested code is there, it doesn't go into my repo. |

