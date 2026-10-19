@AGENTS.md

## Claude Code specifics

- The workflows above are slash commands: `/feature`, `/test`, `/review`, `/ship`, `/handoff`, `/adr`, `/init-project`.
- `just format` runs automatically after each file edit (hook in `.claude/settings.json`).
- Delegate broad code searches and independent reviews to subagents (`reviewer` in `.claude/agents/`) to keep this context small.
- One task per session. Run `/handoff` before `/clear` or before ending the session.
