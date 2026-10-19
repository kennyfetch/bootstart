# Conventions

Shared rules for humans and AI agents. Anything a tool can enforce (formatting, import order, most lint
rules) is enforced by `just lint` and CI, not described here.

## 1. Language

English everywhere: identifiers, comments, docs, commit messages, PR descriptions.

## 2. Naming

A name says **what** a thing is or does, so the reader never has to open it to find out.

| Kind | Rule | Good | Avoid |
|---|---|---|---|
| Function / method | Verb + object | `compute_invoice_total`, `sendWelcomeEmail` | `invoice`, `process`, `handle` |
| Boolean | `is` / `has` / `can` / `should` prefix | `is_expired`, `hasAccess` | `expired`, `flag`, `status` |
| Collection | Plural noun | `users`, `pendingOrders` | `user_list`, `data` |
| Map / dict | `<value>_by_<key>` | `price_by_sku`, `userById` | `prices_map` |
| Quantity with a unit | Unit as suffix | `timeout_ms`, `sizeBytes`, `price_cents` | `timeout`, `size` |
| Constant | Upper snake case | `MAX_RETRY_COUNT` | `maxRetry`, magic numbers |
| Class / type | Noun, PascalCase | `InvoiceRepository` | `InvoiceManager`, `InvoiceHelper` |

- No abbreviations except universally known ones: `id`, `url`, `db`, `api`, `io`, `html`.
- Banned as standalone names: `data`, `info`, `item`, `obj`, `tmp`, `manager`, `helper`, `utils`, `misc`.
- Name length grows with scope: `i` in a 3-line loop is fine; a module-level name is never one letter.
- Same concept, same word, everywhere: do not mix `fetch`/`get`/`load` or `customer`/`client`.

### Casing by language

| | Python | TypeScript / JavaScript |
|---|---|---|
| Variables, functions | `snake_case` | `camelCase` |
| Classes, types | `PascalCase` | `PascalCase` |
| Constants | `UPPER_SNAKE_CASE` | `UPPER_SNAKE_CASE` |
| Files, modules | `snake_case.py` | `kebab-case.ts` |
| Private | `_leading_underscore` | not exported (or `#private`) |

Other languages: follow the official style guide of the language and record it in an ADR.

## 3. Comments and docs

- A comment explains **why**: a constraint, a non-obvious choice, a workaround, a link to an issue or ADR.
  It never paraphrases **what** the code does — rename or extract a function instead.
- Docstrings / JSDoc on public functions, classes and modules only: purpose, parameters with units,
  return value, errors raised. One line is often enough.
- `TODO(#42): …` always references an issue. No anonymous TODOs.
- No commented-out code (git remembers it) and no change history in comments (git log does that).

## 4. Structure

- A function does one thing. Past ~40 lines, it is probably doing two.
- A file has one responsibility. Past ~300 lines, consider splitting.
  Small files are also cheaper for AI agents to read.
- Organize by feature (`billing/`, `auth/`) rather than by technical type (`models/`, `services/`)
  once the project has more than a handful of files.
- Dependencies point inward: business logic never imports a web framework, a database driver or the UI.
  Side effects (I/O, network, clock, randomness) are pushed to the edges and injected.

## 5. Errors and configuration

- Fail fast and loudly. Never swallow an exception silently; catch only what you can handle.
- Validate input at system boundaries (HTTP, CLI, files, env); trust it inside.
- Prefer specific error types over generic ones; error messages say what failed and with which value.
- Configuration comes from environment variables, listed with safe defaults in `.env.example`.
- Never log secrets, tokens or personal data.

## 6. Tests

- Pyramid: many fast unit tests, some integration tests, few end-to-end tests.
- One behavior per test. Structure: **Arrange / Act / Assert**, separated by a blank line.
- Test names read as sentences: `test_returns_zero_when_cart_is_empty`, `it("rejects an expired token")`.
- Tests are deterministic: no real network, no real clock, no shared state between tests.
  Inject a fake clock or client instead of mocking deep internals.
- Test behavior through the public interface, not implementation details.
- `tests/` mirrors `src/`: `src/billing/invoice.py` → `tests/billing/test_invoice.py`.
- Coverage is a safety net, not a goal: CI enforces 80 % overall; aim higher on business logic.
- Every bug fix starts with a test that reproduces the bug.

## 7. Git and pull requests

- Branches: `<type>/<short-slug>` — `feat/csv-export`, `fix/login-timeout`, `chore/bump-deps`.
- Commits: [Conventional Commits](https://www.conventionalcommits.org/).
  Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`, `ci`, `build`.
  Subject in imperative mood, ≤ 72 characters: `fix: handle empty cart in checkout`.
  Breaking change: `feat!: …` plus a `BREAKING CHANGE:` footer.
- Pull requests stay small (under ~400 changed lines) and do one thing.
- Merge with **squash**: one commit per PR on `main`, so `git log` reads as a changelog.
- Required before merge: green CI. In team mode, also one approving review (see README).

## 8. Dependencies

- Prefer the standard library, then well-maintained, widely used packages.
- Every new dependency is justified in the PR description; a framework-level one gets an ADR.
- Versions are locked by the lockfile, which is committed and never edited by hand.

## 9. Review checklist

Used by humans and by the `review` workflow. Style is not reviewed: tools handle it.

- [ ] Does the change do what the PR says, and only that?
- [ ] Are the new behaviors and edge cases tested? Would the tests fail if the code were wrong?
- [ ] Are names clear without reading the implementation?
- [ ] Are errors handled at the right level, without silent failures?
- [ ] Any secret, credential, personal data or debug leftover?
- [ ] Any input from outside the system used without validation?
- [ ] Is anything duplicated that already exists in the codebase?
- [ ] Are docs, ADRs and `.env.example` updated if needed?
