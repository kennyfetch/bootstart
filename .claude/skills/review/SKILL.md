---
name: review
description: Review the current changes against the project conventions and report problems ranked by severity. Use before shipping or when asked to review code.
argument-hint: "[base branch, default main]"
---

# Review

Base branch: $ARGUMENTS (use `main` if empty).

1. Collect every change since the base, including files that were never committed:
   - committed: `git diff <base>...HEAD`;
   - uncommitted: `git diff HEAD`;
   - new files: `git ls-files --others --exclude-standard` — read each one in full, since no diff
     shows them.

   If the change is large, review file by file instead of loading everything at once.

   **Delta review** — when a full review already ran in this session and only fixes or a small
   follow-up came after: review only what changed since (diff against the state that was reviewed,
   plus any new untracked file), checking that each earlier finding is resolved. In Claude Code,
   continue the same `reviewer` subagent (SendMessage) instead of starting a new one: it already
   has the context, which roughly halves the cost.
2. In Claude Code, delegate to the `reviewer` subagent so the review runs in a fresh context, then
   relay its findings. If the change touches untrusted input (network, uploaded or external files),
   authentication, secrets, or shell/SQL execution, also run `/security-review`.
   Other agents: do the review yourself with the steps below.
3. Check the changes against the checklist in `docs/CONVENTIONS.md` §9. Do not comment on formatting.
4. Report findings ranked **blocking → should fix → nit**, each as
   `path:line — problem — suggested fix`. Say plainly when nothing blocks.
5. Do not modify files unless asked to apply the fixes.
