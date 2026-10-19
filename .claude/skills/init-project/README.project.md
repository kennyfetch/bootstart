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
- [Decisions](docs/decisions/) — why things are the way they are
- [Handoff](docs/HANDOFF.md) — current state and next steps
- [AGENTS.md](AGENTS.md) — instructions for AI coding agents

## License

_Filled by init-project: the license name and a link to `LICENSE`, or "Proprietary. All rights reserved."_
