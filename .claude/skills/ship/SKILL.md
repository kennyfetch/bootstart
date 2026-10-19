---
name: ship
description: Verify, commit, push and open a pull request for the current work. Run only when the user asks to ship, commit or open a PR.
disable-model-invocation: true
argument-hint: "[optional PR title]"
---

# Ship

1. **Branch.** If on `main`, create a branch first (`<type>/<short-slug>`); never push to `main`.
2. **Check.** Run `just check`. Stop and report if it fails.
3. **Review.** Run the `review` workflow. Stop on any blocking finding and report it.
4. **Handoff.** Solo: run the `handoff` workflow so `docs/HANDOFF.md` ships with the change.
   Team mode: run it after step 7 instead, once the PR exists to hold the notes.
5. **Commit.** Stage only files related to the task (`git status` first; never `git add -A` blindly,
   never stage `.env` or local settings). Message in Conventional Commits format:
   `<type>(<optional scope>): <imperative summary, ≤ 72 chars>`, with a short body for the why.
   Split into several commits only if the change has clearly separate steps.
6. **Push.** `git push -u origin HEAD`.
7. **Pull request.** Title: $ARGUMENTS if given, otherwise the commit subject. Body: fill every
   section of `.github/pull_request_template.md`; link the issue with `Closes #N` when there is one.
   GitHub allows one open PR per branch, so check first: `gh pr view --json number,isDraft,body`.
   - **A PR exists** (earlier `ship`, or a draft opened by `handoff`): update it with
     `gh pr edit --title "…" --body-file <file>`, keeping its `## Handoff` section if it has one.
     If it is a draft, mark it ready for review: `gh pr ready`.
   - **No PR:** `gh pr create --title "…" --body-file <file>`.
8. **Report** the PR URL and the CI status (`gh pr checks`). Do not merge: merging is the human's call.
