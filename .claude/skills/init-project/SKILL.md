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

Skip what the input already gives. "Not decided yet" is a valid answer: it becomes an open question
in the matching document.

1. **Project:** name and one-sentence purpose.
2. **First version** (`docs/SCOPE.md`): target users; the main journey, from opening the app to the
   result they came for; the three most important features; what waits for later; what would make
   the first version a success.
3. **Nature:** web front-end, full-stack web, API, CLI, data/automation, library, desktop, mobile,
   game, other. Where it runs, and any hard constraint: platform, performance, offline, hosting,
   existing code.
4. **Use and licenses** (`docs/THIRD_PARTY.md`): commercial use planned? Distributed how —
   internal tool, online service, distributed app or package, open source? Project license:
   MIT, Apache-2.0, a copyleft license, or none (proprietary).
5. **Data and access** (`docs/DATA.md`): public or internal? User accounts, and which roles? Personal
   data collected (which), and any sensitive data (health, children, …)? How long it is kept?
   Hosting region and third-party services that would receive data (email, analytics, payment…)?
6. **Team and repository:** solo or team? Team means at least one other person with write access
   who reviews PRs; alone, choose solo (switch later with `scripts/setup-github.sh team`). Public
   or private repository? On GitHub Free, a private repository gets no branch protection and no
   automatic license check.
7. **Dev container:** work inside a container that holds every tool? Recommended for a team (same
   environment for everyone) or to let AI agents work autonomously, isolated from the rest of the
   machine. Not suited to mobile apps with an emulator, desktop GUI apps or games. Needs Docker
   (Docker Desktop or Podman) locally, or GitHub Codespaces.

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
   which `just setup` regenerates: `Project Name` → display name,
   `project-name` → kebab-case, `project_name` → snake_case, `Project description.` → purpose.
   Rename `src/project_name/` accordingly (Python).
3. Keep the example module (`pricing`) and its tests: they show the conventions while the first
   feature is written. Their deletion goes in the next steps of `docs/HANDOFF.md` (step 4).

**Two stacks** (e.g. API + front-end): install each pack in its own folder and follow
"Two stacks in one repository" in `docs/STACKS.md`.

**Without a pack:** build the equivalent by following the stack contract in `docs/STACKS.md`, using
the closest pack as a model for structure. Use the current stable version of each tool, strict
settings, and the language's official style guide.

**Dev container** (block 7): each pack ships a `.devcontainer/`. No dev container: delete it.
Two stacks: merge the packs' dev containers into a single `.devcontainer/` at the root — one
Dockerfile with both toolchains, and both packs' features and mounts.

**Then, before anything else:** delete `stacks/` — its nested tool configs (a second `biome.json`,
for example) make the formatter refuse to run — and run `just setup`, so the edit hook and the
`just` recipes work for the rest of init.

**Framework:** if the stack includes one (FastAPI, React, Typer…), add it with its official
tooling and make sure the `justfile` recipes still cover all the code. If the app needs an entry
point to run, create the smallest one the framework allows — a CLI that only shows `--help`, an
API with only a health route, an empty page — with one smoke test, and make `just dev` start it.
Real behavior comes with the first `feature`. If nothing can run yet (a library, for example),
leave `dev` printing its hint. React with Vitest: set `environment: "jsdom"` and a setup file that
calls Testing Library's `cleanup` after each test (`afterEach(cleanup)`) — the pack does not enable
Vitest globals, so it does not happen on its own.

Then:

- `.github/workflows/ci.yml`: keep only the toolchain setup steps this project needs, and the
  `UV_LOCKED` variable only with a Python stack; add the setup action for any other toolchain.
- `.github/dependabot.yml`: replace the `stacks/*` entries and their header comment with one entry
  per stack directory — `directory: /` for a single stack, one per folder for two stacks — with the
  stack's ecosystem (`uv`, `npm`, `cargo`, `gomod`…), the same schedule and grouping, and the
  `ignore` rules of the replaced entry with the same ecosystem.
- `.gitignore`: make sure the stack's patterns are present.

## 4. Documents

- `AGENTS.md`, section "Project": name, purpose, stack.
- `README.md`: replace with `.claude/skills/init-project/README.project.md`, filled in. Without a
  dev container, drop its "Dev container" section.
- `docs/decisions/0001-stack-choice.md`: ADR from the interview and step 2 (use the `adr` workflow).
  It also records where the project comes from, so template fixes can be traced to it later:
  - a line `Created from <template>@<commit> on <date>`. With a GitHub remote:
    `gh repo view --json templateRepository,createdAt` gives the template and the creation date;
    the template commit at that date is
    `gh api "repos/<template>/commits?sha=main&until=<createdAt>&per_page=1" --jq '.[0].sha'`.
    Cloned from the template itself: `git rev-parse HEAD` before the initial commit. Otherwise:
    `unknown`;
  - the init options: stack, dev container, solo or team, repository visibility, project license, commercial use
    and distribution, personal data (yes or no).
- `docs/ARCHITECTURE.md`: fill "Purpose", "Context" and "Constraints" from the interview, and
  "Module map" with the folders just created.
- `docs/SCOPE.md`: from interview block 2.
- `docs/THIRD_PARTY.md`: fill "Policy" from block 4. For a copyleft project license, move the
  matching copyleft licenses to "Allowed", in the table and in the `allow-licenses` list of
  `.github/workflows/dependency-review.yml`. Add a row for any asset already used (font, icon…).
- `docs/DATA.md`: from block 5. No accounts and no personal data: keep the file short and say so,
  so that any later change starts by updating it. Sensitive data: list the impact assessment
  (DPIA) in the open questions of `docs/SCOPE.md`.
- License:
  - MIT, Apache-2.0 or a copyleft license: create `LICENSE` with the standard text, current year, holder from
    `git config user.name`; in the README's "License" section, name the license and link `LICENSE`.
  - None: create no `LICENSE` file; the README's "License" section reads
    `Proprietary. All rights reserved.` with no link.
- `.github/CODEOWNERS`: in team mode, uncomment the default rule with the team members' GitHub
  handles. They are requested as reviewers automatically; any collaborator with write access can
  give the required approval (see `scripts/setup-github.sh`).
- `docs/HANDOFF.md`: replace the "not initialized" content, here, before the initial commit:
  afterwards `main` is protected and the `handoff` workflow only runs on development branches.
  - Solo: the state after init and the next steps — the first feature, then deleting the
    `pricing` example once real code is tested.
  - Team: this file is never updated per PR, so write content that stays true. "Current state"
    says the live state is in the open PRs (`gh pr list`) and their `## Handoff` sections; keep
    only durable pitfalls and open questions. The first steps (first feature, deleting the
    `pricing` example) go in an issue, opened in step 7.

## 5. Clean up

1. Delete `.github/workflows/template-selftest.yml` and this skill's folder
   `.claude/skills/init-project/` (`stacks/` is already gone, step 3).
2. Remove what referred to them:
   - `AGENTS.md`: the `init-project` row of the workflow table and the HTML comment in "Project";
   - `CLAUDE.md`: `/init-project` in the command list;
   - `docs/STACKS.md`: the "Packs shipped in `stacks/`" section.
3. Search the repository (excluding `.git`, `node_modules`, `.venv`) for `init-project`, `stacks/`
   and `selftest`: nothing may remain.

## 6. Verify

Run `just setup`, then `just check`. Fix until it passes.

With a dev container and Docker running, also check it from the host with the dev container CLI:
`npx @devcontainers/cli up --workspace-folder .`, then
`npx @devcontainers/cli exec --workspace-folder . just check`. No Docker here: say so, and leave
this check to the first opening of the container.

## 7. Git and GitHub

Show the user the commands below, adapted to the project, and ask for a single confirmation.

1. No repository yet: `git init -b main`.
2. Commit everything on `main` as `chore: initialize project from Bootstart` — the only commit made
   directly on `main`.
3. No `origin` remote yet: `gh repo create <kebab-name> --private|--public --source . --push`.
   Otherwise: `git push`.
4. Apply repository settings and branch protection: `bash scripts/setup-github.sh solo` (or `team`).
   Public repository: also require the license check — `bash scripts/setup-github.sh solo dependency-review`.
   On Windows, run it with Git Bash — Claude Code's Bash tool, or
   `& "$env:ProgramFiles\Git\bin\bash.exe" scripts/setup-github.sh solo` from PowerShell — never
   `bash` from PowerShell, which may start WSL. A private repository on GitHub Free cannot have
   rulesets: skip this step and say so.
5. Close any Dependabot PR opened on `stacks/` before init (`gh pr list --author app/dependabot`,
   then `gh pr close <number>`): it no longer applies.
6. Team mode: open an issue with the first steps (`gh issue create`), as noted in
   `docs/HANDOFF.md`.

## 8. Report

What was set up, how to run it, and the suggested first step: `/feature <first feature>`.
Do not run the `handoff` workflow here: `docs/HANDOFF.md` was written in step 4 and committed.
