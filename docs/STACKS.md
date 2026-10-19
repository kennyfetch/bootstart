# Choosing a stack

Used by the `init-project` workflow. Pick the most boring stack that fits the project well:
mature tooling, large community, good AI-agent familiarity. Record the choice in ADR 0001.

## By project nature

| Project nature | Default choice | Consider instead when… |
|---|---|---|
| Web front-end, SPA | TypeScript + Vite + React | SvelteKit for a smaller, simpler UI |
| Full-stack web app (SSR, SEO) | TypeScript + Next.js | Python + Django when the app is mostly admin/forms/CRUD |
| REST / HTTP API | Python + FastAPI | TypeScript + Hono/Fastify to share types with a TS front-end; Go for high throughput and low ops |
| Data processing, ML, automation scripts | Python | — |
| CLI tool | Python + Typer | Go or Rust when a single static binary matters |
| Library / SDK | The target ecosystem's language | — |
| Desktop app | Tauri (TypeScript UI + Rust core) | Electron for heavy Node integrations; .NET (WinUI) for Windows-only |
| Mobile app | React Native + Expo (TypeScript) | Flutter (Dart); native Kotlin/Swift for deep platform features |
| Game | Godot (GDScript or C#) | Unity (C#) |
| Systems, embedded, performance-critical | Rust | C/C++ when the platform requires it |

Questions that move the choice: who maintains it later and what they know; where it runs (browser,
server, device, desktop); whether front-end and back-end should share code; deployment and hosting
constraints; performance or footprint requirements.

## Packs shipped in `stacks/`

| Pack | Package manager | Format + lint | Types | Tests |
|---|---|---|---|---|
| `python` | uv | Ruff | Pyright (strict) | pytest + pytest-cov |
| `typescript` | pnpm | Biome | tsc (strict) | Vitest + V8 coverage |

A framework (FastAPI, React, …) is added on top of a pack during `init-project`, not shipped in it.

## Two stacks in one repository

For example a Python API with a TypeScript front-end. Keep each stack self-contained and the
commands identical from the root:

- **Folders:** one per stack (`backend/`, `frontend/`), each a full pack with its own `justfile`,
  config, `src/`, `tests/` and lockfile.
- **Root `justfile`:** every standard recipe runs the same recipe in each folder, the way the
  template's `selftest` recipe does:
  `{{ just_executable() }} --justfile backend/justfile --working-directory backend check`.
  `dev` usually needs both running: document it in the README, or start each one in its own terminal.
- **CI:** one job per folder in `ci.yml`, modeled on `template-selftest.yml`
  (`defaults.run.working-directory`, toolchain files pointing into the folder). Keep a final job
  named `check` so the required status check does not change. It must fail when any job fails —
  GitHub counts a skipped required check as passing:

  ```yaml
  check:
    needs: [backend, frontend]
    if: always()
    runs-on: ubuntu-latest
    steps:
      - if: contains(needs.*.result, 'failure') || contains(needs.*.result, 'cancelled')
        run: exit 1
  ```

- **Dependabot:** one entry per folder.
- **AGENTS.md:** the "Layout" line names both folders.

## Stack contract

Any stack — shipped or created for a project — must provide:

1. A root `justfile` with the recipes `setup`, `dev`, `format`, `fix`, `lint`, `typecheck`, `test`,
   `check` (`check` = `lint` + `typecheck` + `test`; `format` only formats, so the edit hook never
   deletes code; `dev` starts the app locally, or prints why there is nothing to run, e.g. a library).
2. A strict formatter, linter, type checker (or the language's compiler) and test runner, with
   coverage enforced at 80 %.
3. A committed lockfile.
4. Toolchain setup steps in `.github/workflows/ci.yml`, triggered by a file at the repository root.
5. An ecosystem entry in `.github/dependabot.yml`.
6. Its ignore patterns in `.gitignore`.
7. An example source file and test that demonstrate `docs/CONVENTIONS.md`.
