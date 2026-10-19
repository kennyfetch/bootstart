---
name: handoff
description: Update docs/HANDOFF.md with the current state so another person or AI can resume the work. Use at the end of a session, before /clear, or when asked to hand off.
---

# Handoff

Rewrite `docs/HANDOFF.md` — overwrite it, do not append. Keep the existing section headings.

1. Gather facts, not memories: `git status`, `git log --oneline -10`, current branch, open PRs
   (`gh pr list --author @me`, if `gh` is available), and what was done in this session.
2. Fill each section briefly:
   - **Last updated:** today's date, branch, short commit SHA.
   - **Current state:** what works now, in 2–5 bullets.
   - **In progress:** unfinished work, with file paths and the exact point where it stopped.
   - **Next steps:** ordered, each one actionable on its own.
   - **Pitfalls:** traps discovered (flaky test, odd API behavior, setup quirk).
   - **Open questions:** decisions waiting on the user.
3. Remove anything stale or already done. Do not duplicate git history, the README or ADRs —
   link to them instead.
4. Stay under ~60 lines. Write for a reader with zero context, in plain sentences.
