---
name: init-project
description: Turn the Bootstart template into a real project — interview, stack choice, stack pack install, placeholders, first commit. Run once, right after creating a repository from the template.
disable-model-invocation: true
argument-hint: "[project name and one-line description]"
---

# Init project

Input: $ARGUMENTS

Ask everything in step 1 at once, wait for the answers and the stack confirmation (step 2), then run
the remaining steps without interrupting the user unless something fails or a step below says to ask.

## 1. Interview

1. Project name and one-sentence purpose (skip what the input already gives).
2. Nature: web front-end, full-stack web, API, CLI, data/automation, library, desktop, mobile, game, other.
3. Where it runs, and any hard constraint: platform, performance, offline, hosting, existing code.
4. Solo or team? Public or private repository? License: MIT, Apache-2.0, or none (proprietary).

## 2. Stack

Propose a stack from `docs/STACKS.md`: the choice, 2–3 lines of rationale tied to the answers, and
one credible alternative. Wait for confirmation.

## 3. Install the stack

Derive three names: display name (`My Tool`), `kebab-case` (`my-tool`), `snake_case` (`my_tool`).

**With a pack** in `stacks/<pack>/`:

1. Copy the pack's tracked files (`git ls-files stacks/<pack>`), dotfiles included, to the
   repository root — never local `node_modules/`, `.venv/` or caches. Its `justfile` replaces the
   root one.
2. Replace the placeholders in every copied file except lockfiles (`uv.lock`, `pnpm-lock.yaml`),
   which `just setup` regenerates in step 6: `Project Name` → display name,
   `project-name` → kebab-case, `project_name` → snake_case, `Project description.` → purpose.
   Rename `src/project_name/` accordingly (Python).
3. Keep the example module (`pricing`) and its tests: they show the conventions while the first
   feature is written. Their deletion goes in the next steps of `docs/HANDOFF.md` (step 4).

**Two stacks** (e.g. API + front-end): install each pack in its own folder and follow
"Two stacks in one repository" in `docs/STACKS.md`.

**Without a pack:** build the equivalent by following the stack contract in `docs/STACKS.md`, using
the closest pack as a model for structure. Use the current stable version of each tool, strict
settings, and the language's official style guide.

**Framework:** if the stack includes one (FastAPI, React, Next.js…), add it with its official
tooling, then make sure the `justfile` recipes still cover all the code, and make `just dev` start
the app (dev server or entry point).

Then:

- `.github/workflows/ci.yml`: keep only the toolchain setup steps this project needs; add the
  setup action for any other toolchain.
- `.github/dependabot.yml`: replace the `stacks/*` entries with one entry per stack directory —
  `directory: /` for a single stack, one per folder for two stacks — with the stack's ecosystem
  (`uv`, `npm`, `cargo`, `gomod`…), the same schedule and grouping, and the replaced entries'
  `ignore` rules.
- `.gitignore`: make sure the stack's patterns are present.

## 4. Documents

- `AGENTS.md`, section "Project": name, purpose, stack.
- `README.md`: replace with `.claude/skills/init-project/README.project.md`, filled in.
- `docs/decisions/0001-stack-choice.md`: ADR from the interview and step 2 (use the `adr` workflow).
- `docs/ARCHITECTURE.md`: fill "Purpose", "Context" and "Constraints" from the interview.
- License:
  - MIT or Apache-2.0: create `LICENSE` with the standard text, current year, holder from
    `git config user.name`; in the README's "License" section, name the license and link `LICENSE`.
  - None: create no `LICENSE` file; the README's "License" section reads
    `Proprietary. All rights reserved.` with no link.
- `.github/CODEOWNERS`: in team mode, uncomment the default rule with the owner's GitHub handle.
- `docs/HANDOFF.md`: replace the "not initialized" content with the state after init and the next
  steps — the first feature, then deleting the `pricing` example once real code is tested. This is
  done here, before the initial commit, in both modes: afterwards `main` is protected, and the
  `handoff` workflow only runs on development branches.

## 5. Clean up

Delete `stacks/`, `.github/workflows/template-selftest.yml` and this skill's folder
`.claude/skills/init-project/`. Remove the `init-project` row from the table in `AGENTS.md` and
from the command list in `CLAUDE.md`.

## 6. Verify

Run `just setup`, then `just check`. Fix until it passes.

## 7. Git and GitHub — confirm with the user before each command

1. No repository yet: `git init -b main`.
2. Commit everything on `main` as `chore: initialize project from Bootstart` — the only commit made
   directly on `main`.
3. No `origin` remote yet: `gh repo create <kebab-name> --private|--public --source . --push`.
   Otherwise: `git push`.
4. Apply repository settings and branch protection: `bash scripts/setup-github.sh solo` (or `team`).

## 8. Report

What was set up, how to run it, and the suggested first step: `/feature <first feature>`.
Do not run the `handoff` workflow here: `docs/HANDOFF.md` was written in step 4 and committed.
