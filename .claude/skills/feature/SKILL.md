---
name: feature
description: Implement a feature or bug fix end to end, tests first. Use when asked to add, change or fix behavior in the code.
argument-hint: <what to build or fix>
---

# Feature

Task: $ARGUMENTS

1. **Context.** Read `docs/HANDOFF.md` (team mode: also the branch's PR description, if a PR
   exists). Read `docs/ARCHITECTURE.md` only if the task spans modules.
   Locate the relevant code by searching; open only the files you need.
2. **Clarify.** Restate the expected behavior as 2–5 acceptance criteria. If anything is ambiguous,
   ask before writing code. List any assumption you make.
3. **Branch.** From an up-to-date `main`: `git switch -c <type>/<short-slug>` (`feat/…`, `fix/…`).
   Skip if already on a dedicated branch for this task.
4. **Plan.** For anything beyond a few lines, write a plan of at most ~10 lines: files to touch,
   new functions and their names, tests to add. Keep it in the conversation, not in a file.
5. **Tests first.** Write tests for each acceptance criterion, following `docs/CONVENTIONS.md` §6.
   For a bug, first write a test that reproduces it. Run `just test` and confirm they fail for the
   right reason.
6. **Implement** the smallest change that makes them pass. Follow `docs/CONVENTIONS.md`.
   Do not refactor unrelated code; note it in the handoff instead.
7. **Verify.** `just check` must pass. Fix the cause of any failure; never weaken or skip a test
   to get green.
8. **Docs.** Update `docs/ARCHITECTURE.md` if the structure changed, `.env.example` if a setting was
   added. If a significant choice was made, run the `adr` workflow.
9. **Report** in a few lines: what changed, how it is tested, anything left undone. Suggest `ship`.
