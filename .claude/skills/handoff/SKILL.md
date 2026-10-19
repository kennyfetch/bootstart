---
name: handoff
description: Save the current state so another person or AI can resume the work — in docs/HANDOFF.md when solo, in the branch's PR description in team mode. Use at the end of a session, before /clear, or when asked to hand off.
---

# Handoff

If nothing changed since the last handoff in this session (for example `ship` just ran it), say so
and stop.

Where the notes go depends on the mode and the branch:

- **Solo** (no active rule in `.github/CODEOWNERS`): rewrite `docs/HANDOFF.md` — overwrite it,
  do not append, keep its section headings. The file reaches `main` with the PR, so write it as
  the state `main` will have once the branch is merged; transient status (PR open, CI pending,
  review comments) belongs in the PR, not here. Then commit only that file on the branch
  (`docs: update handoff`) and push if the branch has a remote, so the note never stays behind
  uncommitted.
- **Team** (an owner is set in `.github/CODEOWNERS`): never touch `docs/HANDOFF.md`, since
  parallel branches would all conflict on it. Write the notes in a `## Handoff` section of the
  current branch's PR description, at the end of the body. The section runs from `## Handoff` to
  the next `## ` heading or the end of the body; use `###` sub-headings inside it. Read the body
  (`gh pr view --json body --jq .body`), replace any previous `## Handoff` section, write it back
  with `gh pr edit --body-file <file>`, the file
  being outside the repository (system temp folder). No PR yet: ask the user, then push the branch
  and open a draft (`gh pr create --draft`). The next session reads the notes with
  `gh pr view --json body`.
- **On `main`** (either mode): handoff notes belong to a development branch — `main` is protected
  and a PR from `main` to `main` is impossible. Unfinished work: create its branch first
  (`<type>/<short-slug>`), then continue as above. Nothing in progress: say there is nothing to hand
  off, and stop.

1. Gather facts, not memories: `git status`, `git log --oneline -10`, current branch, open PRs
   (`gh pr list --author @me`, if `gh` is available), and what was done in this session.
2. Fill each section briefly:
   - **Last updated:** today's date and the branch (no commit SHA: the note is written before the
     commit that contains it, and git history already has it).
   - **Current state:** what works now, in 2–5 bullets.
   - **In progress:** unfinished work, with file paths and the exact point where it stopped.
   - **Next steps:** ordered, each one actionable on its own.
   - **Pitfalls:** traps discovered (flaky test, odd API behavior, setup quirk).
   - **Open questions:** decisions waiting on the user.
3. Remove anything stale or already done. Do not duplicate git history, the README or ADRs —
   link to them instead.
4. Stay under ~60 lines. Write for a reader with zero context, in plain sentences.
