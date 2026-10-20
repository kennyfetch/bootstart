# Project Name

Project description.

## Requirements

- [just](https://just.systems) — task runner used for every command
- The stack tools listed in [ADR 0001](docs/decisions/0001-stack-choice.md)

## Getting started

```bash
just setup   # install dependencies
just check   # lint, type-check and test — what CI runs
```

### Dev container

Every tool is preinstalled in the dev container (`.devcontainer/`), and `just setup` runs when it
is created. Open the folder in VS Code with the Dev Containers extension ("Reopen in Container"),
or in GitHub Codespaces. Run AI agents inside it — `claude` in the container's terminal — so they
only see the project. On Windows, clone the project inside WSL rather than on a Windows drive: file
access is much faster.

## Development

| Command | Effect |
|---|---|
| `just dev` | Run the app locally |
| `just format` | Format code |
| `just fix` | Format and apply safe lint fixes |
| `just lint` | Check formatting and lint rules |
| `just typecheck` | Static type checking |
| `just test` | Run tests with coverage |
| `just check` | All of the above, as in CI |

Workflow: branch from `main` → write tests first → `just check` → pull request (squash merge).
Details in [docs/CONVENTIONS.md](docs/CONVENTIONS.md).

## Documentation

- [Architecture](docs/ARCHITECTURE.md) — how the system is organized
- [Conventions](docs/CONVENTIONS.md) — naming, comments, tests, git
- [Scope](docs/SCOPE.md) — what the first version does, and what waits
- [Data and access](docs/DATA.md) — personal data, roles, GDPR
- [Third-party licenses](docs/THIRD_PARTY.md) — license policy and assets
- [Decisions](docs/decisions/) — why things are the way they are
- [Handoff](docs/HANDOFF.md) — current state and next steps
- [AGENTS.md](AGENTS.md) — instructions for AI coding agents

## License

_Filled by init-project: the license name and a link to `LICENSE`, or "Proprietary. All rights reserved."_
