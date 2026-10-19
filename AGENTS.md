# AGENTS.md

Instructions for AI coding agents (Claude Code, Codex, Qwen Code, …). Humans start with `README.md`.
Keep this file short: it is loaded in every session. Details live in `docs/`.

## Project

<!-- Filled by /init-project. -->
- **Name:** _not initialized — run the `init-project` workflow_
- **Purpose:** _one sentence_
- **Stack:** _see `docs/decisions/0001-*.md`_

## Start here

1. Read `docs/HANDOFF.md`: current state, work in progress, next steps. Team mode (owner set in
   `.github/CODEOWNERS`): also read the handoff notes in the branch's PR (`gh pr view --json body`).
2. Read `docs/CONVENTIONS.md` before writing or reviewing code.
3. Read `docs/ARCHITECTURE.md` only when the task touches structure or several modules.

## Commands

Every task goes through `just` — the same commands run locally, in hooks and in CI.

| Command | Effect |
|---|---|
| `just setup` | Install dependencies |
| `just dev` | Run the app locally |
| `just format` | Format code in place |
| `just fix` | Format + apply safe lint fixes |
| `just lint` | Check formatting and lint rules (no changes) |
| `just typecheck` | Static type checking |
| `just test [args]` | Run tests with coverage |
| `just check` | Everything CI runs — must pass before any commit |

## Layout

`src/` code · `tests/` tests mirroring `src/` · `docs/` documentation · `docs/decisions/` ADRs · `.claude/skills/` workflows

## Rules

1. English for code, identifiers, comments, docs and commits.
2. Tests first: write or update a failing test, then the code. A bug fix starts with a regression test.
3. Small, focused changes: one concern per commit and per PR.
4. Never commit to `main`. Branch as `<type>/<short-slug>` (e.g. `feat/user-login`).
5. Commit messages follow Conventional Commits (`feat: …`, `fix: …`).
6. No new dependency without a stated reason; a significant one gets an ADR.
7. Never read, print or commit secrets. `.env` and `.env.*` files are off-limits, except
   `.env.example`, which documents every variable.
8. Never edit lockfiles or generated files by hand.
9. When requirements are ambiguous, ask. When you assume, say so.
10. Run `just format` after editing code; never hand-format. Claude Code does it automatically.

## Workflows

Step-by-step procedures live in `.claude/skills/<name>/SKILL.md`.
Claude Code runs them as `/<name>`. Other agents: read the file and follow it.

| Workflow | Use it to |
|---|---|
| `init-project` | Turn this template into a real project (once) |
| `feature` | Implement a feature or fix, tests first |
| `test` | Add or improve tests for existing code |
| `review` | Review the current diff against the conventions |
| `ship` | Check, commit, push and open a pull request |
| `handoff` | Save the current state for the next session before ending one |
| `adr` | Record an architecture decision |

## Definition of done

- `just check` passes.
- New behavior is covered by tests.
- `docs/ARCHITECTURE.md` or an ADR is updated when structure or a key choice changed.
- The `handoff` workflow has run at the end of the session.

## Saving tokens

- Read only what the task needs; search (`grep`, glob) before opening whole files.
- Never read `node_modules/`, `.venv/`, build output, coverage reports or lockfiles.
- Do not paste file contents back in answers; reference `path:line` instead.
- Keep answers short. Report results, not process.
