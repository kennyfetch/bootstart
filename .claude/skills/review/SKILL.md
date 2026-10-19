---
name: review
description: Review the current changes against the project conventions and report problems ranked by severity. Use before shipping or when asked to review code.
argument-hint: "[base branch, default main]"
---

# Review

Base branch: $ARGUMENTS (use `main` if empty).

1. Get the diff: `git diff <base>...HEAD` plus uncommitted changes (`git diff HEAD`).
   If it is large, review file by file instead of loading everything at once.
2. In Claude Code, delegate to the `reviewer` subagent so the review runs in a fresh context, then
   relay its findings. For a security-sensitive change (auth, input parsing, file or network access,
   secrets), also run `/security-review`. Other agents: do the review yourself with the steps below.
3. Check the diff against the checklist in `docs/CONVENTIONS.md` §9. Do not comment on formatting.
4. Report findings ranked **blocking → should fix → nit**, each as
   `path:line — problem — suggested fix`. Say plainly when nothing blocks.
5. Do not modify files unless asked to apply the fixes.
