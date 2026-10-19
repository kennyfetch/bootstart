---
name: ship
description: Verify, commit, push and open or update the pull request for the current work. Run only when the user asks to ship, commit or open a PR.
disable-model-invocation: true
argument-hint: "[optional PR title]"
---

# Ship

1. **Branch.** If on `main`, create a branch first (`<type>/<short-slug>`); never push to `main`.
2. **Check.** Run `just check`. Stop and report if it fails.
3. **Review.** Run the `review` workflow — in full the first time; afterwards only as needed:
   - nothing changed since the last review in this session: skip it;
   - only fixes for its findings or a small follow-up since: review just that delta (see `review`).

   Stop on any blocking finding and report it.
4. **Handoff.** Solo: run the `handoff` workflow so `docs/HANDOFF.md` ships with the change.
   Team mode: run it after step 7 instead, once the PR exists to hold the notes.
5. **Commit.** Stage only files related to the task (`git status` first; never `git add -A` blindly,
   never stage `.env` or local settings). Message in Conventional Commits format:
   `<type>(<optional scope>): <imperative summary, ≤ 72 chars>`, with a short body for the why.
   One commit per clearly separate step; the PR as a whole stays a single concern.
6. **Push.** `git push -u origin HEAD`.
7. **Pull request.** Its title becomes the squash commit on `main`, so it describes the whole PR, in
   Conventional Commits format. The body fills every section of `.github/pull_request_template.md`
   (`Closes #N` when there is an issue) and covers all the branch's commits (`git log main..HEAD`),
   not just the last one. Write it to a file outside the repository (the system temp folder) so it
   is never committed. GitHub allows one open PR per branch, so check first:
   `gh pr view --json number,title,isDraft,body`.
   - **A PR exists** (earlier `ship`, or a draft opened by `handoff`): keep its title unless
     $ARGUMENTS gives one or the PR's scope changed. Update the body with
     `gh pr edit --body-file <file>`, keeping its `## Handoff` section if it has one. If it is a
     draft, mark it ready for review: `gh pr ready`.
   - **No PR:** title = $ARGUMENTS if given, otherwise a summary of the whole branch (the commit
     subject when there is a single commit). `gh pr create --title "…" --body-file <file>`.
8. **Report** the PR URL and the CI status with `gh pr checks` — exit code 8 means checks are still
   running, not failing; wait with `gh pr checks --watch` when the result is needed now.
   Do not merge: merging is the human's call.
