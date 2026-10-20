# Bootstart

A reusable starting point for AI-assisted software projects. It provides conventions, step-by-step
workflows, tests, CI and GitHub settings that work with Claude Code, Codex and Qwen Code, and stay
easy to read for the humans who maintain the code.

## What's inside

```
AGENTS.md              Instructions for every AI agent (short: loaded in each session)
CLAUDE.md              Imports AGENTS.md, adds Claude Code specifics
justfile               One command interface: setup, dev, format, fix, lint, typecheck, test, check
docs/
  CONVENTIONS.md       Naming, comments, structure, errors, tests, git, review checklist
  ARCHITECTURE.md      One-page system overview (filled per project)
  HANDOFF.md           Current state and next steps, for resuming work
  STACKS.md            Stack choice by project nature + the stack contract
  SCOPE.md             First version: users, main journey, priorities, success criteria
  DATA.md              Personal data, roles and permissions, GDPR checklist
  THIRD_PARTY.md       License policy and register of third-party assets
  decisions/           Architecture Decision Records (ADRs)
.claude/
  settings.json        Permissions, read exclusions, auto-format hook
  skills/              Workflows: init-project, feature, test, review, ship, handoff, adr
  agents/reviewer.md   Independent reviewer subagent
.github/               CI, template self-test, Dependabot, PR and issue templates, CODEOWNERS
scripts/setup-github.sh  Repository settings + branch protection (solo or team)
stacks/                Stack packs (python, typescript), each with a dev container; removed by init-project
```

## Prerequisites

[git](https://git-scm.com), [GitHub CLI](https://cli.github.com), [just](https://just.systems), and the
tools of the stack you pick. On Windows:

```powershell
winget install --id GitHub.cli -e
winget install --id Casey.Just -e
winget install --id astral-sh.uv -e            # Python stack
winget install --id OpenJS.NodeJS.LTS -e       # TypeScript stack
winget install --id pnpm.pnpm -e               # TypeScript stack
```

## Start a new project

1. Create a repository from this template — on GitHub with **Use this template**, or:
   `gh repo create my-app --template kennyfetch/bootstart --public --clone`
   (`--private` works too, but on GitHub Free a private repository gets no branch protection)
2. Open it in Claude Code and run `/init-project`. With another agent, ask it to follow
   `.claude/skills/init-project/SKILL.md`.
3. It interviews you, proposes a stack suited to the project, installs it, fills the placeholders,
   checks that everything passes, then commits and applies the GitHub settings with your approval.

## Daily workflow

| Step | Claude Code | Other agents |
|---|---|---|
| Implement, tests first | `/feature <task>` | "Run the feature workflow for <task>" |
| Add tests to existing code | `/test <target>` | "Run the test workflow on <target>" |
| Review the diff (optional: `ship` runs it) | `/review` | "Run the review workflow" |
| Commit, push, open a PR | `/ship` | "Run the ship workflow" |
| Record a decision | `/adr <decision>` | "Run the adr workflow" |
| End the session | `/handoff` | "Run the handoff workflow" |

`AGENTS.md` maps each workflow name to its file, so any agent can find and follow it.

## Working with several AI agents

- **Claude Code** reads `CLAUDE.md`, which imports `AGENTS.md`. Workflows are slash commands, code is
  formatted after each edit, and reviews run in a separate `reviewer` subagent.
- **Codex** reads `AGENTS.md` natively.
- **Qwen Code** reads `AGENTS.md` in recent versions. In older ones, set `"context": {"fileName":
  "AGENTS.md"}` in `.qwen/settings.json`. Local models have small context windows, which is one more
  reason `AGENTS.md` stays short.
- Agents hand work to each other through the `handoff` workflow (`docs/HANDOFF.md`, or the PR
  description in team mode) and git, never through chat history.

## Saving tokens

- `AGENTS.md` stays under ~100 lines and points to `docs/` instead of copying it.
- Skills cost almost nothing until used: only their one-line description is loaded.
- Tools enforce style (formatter, linter, type checker), so no rule needs repeating in prompts.
- Dependencies, build output, coverage and lockfiles are excluded from AI reads (`.claude/settings.json`).
  These exclusions block Claude's file reading, not shell commands such as `cat`: rule 7 of
  `AGENTS.md` covers secrets for every agent.
- One task per session; `/handoff` then `/clear` keeps the context small.
- Small files and functions mean less to read for every change.

## Dev containers

`/init-project` offers to keep the pack's dev container (`.devcontainer/`): an Ubuntu container
with the stack's tools, `gh` and Claude Code, where `just setup` runs on creation and every `just`
command works as on the host and in CI.

- **Why:** the same environment for everyone, no Windows quirks, and AI agents that can work
  autonomously while seeing only the project, not the rest of the machine.
- **How:** VS Code with the Dev Containers extension ("Reopen in Container"), GitHub Codespaces, or
  the CLI (`npx @devcontainers/cli up --workspace-folder .`). Claude Code's desktop app runs commands
  on the host: to use the container, run `claude` in the container's terminal. Its login persists
  in a volume across rebuilds.
- **Windows:** Docker Desktop (or Podman Desktop) with WSL 2. Clone projects inside WSL rather than
  on a Windows drive: file access is much faster. `.venv/` and `node_modules/` already live on
  container volumes.
- **Not for:** mobile apps with an emulator, desktop GUI apps, games.
- The container limits what an agent can reach on disk; it does not filter the network. For
  stricter isolation, see Anthropic's reference dev container, which adds a firewall.

## Solo, then team

- **Solo:** `bash scripts/setup-github.sh solo`. Pull requests and green CI are required, no approval
  (GitHub does not let you approve your own pull request).
- **Team:** needs at least one other collaborator with write access — alone, nobody could approve
  your PRs, so the script refuses. List the team in `.github/CODEOWNERS` (reviewers requested
  automatically), then `bash scripts/setup-github.sh team`: every PR needs one approval from any
  collaborator with write access. Mandatory code-owner approval is off by default, because a single
  owner could never get their own PRs approved; to turn it on, list at least two owners and run
  `REQUIRE_CODE_OWNER_REVIEW=true bash scripts/setup-github.sh team`. The `handoff` workflow then
  writes its notes in each branch's PR description instead of `docs/HANDOFF.md`, which parallel PRs
  would all conflict on.
- Branch rulesets need a public repository, or GitHub Pro/Team for a private one.
- On Windows, run the script from Git Bash: in PowerShell, `bash` may start WSL instead.

## Maintaining this template

- `just selftest` runs setup and every check of each stack pack locally; the `Template self-test`
  workflow does the same in CI.
- The template's own `check` job has nothing to check, so its branch protection also requires the
  pack jobs, their dev containers and the license check:
  `bash scripts/setup-github.sh solo "stack (python)" "stack (typescript)" "devcontainer (python)" "devcontainer (typescript)" dependency-review`.
- To add a stack pack: create `stacks/<name>/` following the stack contract in `docs/STACKS.md`,
  then add it to the `selftest` recipe, the self-test workflow matrix, `.github/dependabot.yml`,
  the table in `docs/STACKS.md` and the required checks above.
- Mark the GitHub repository as a template: `gh repo edit --template`.
