---
name: adr
description: Record an architecture decision as a short ADR in docs/decisions/. Use when a significant technical choice is made (stack, framework, storage, structure, major dependency, trade-off).
argument-hint: <decision in a few words>
---

# ADR

Decision: $ARGUMENTS

1. Find the next number: highest `NNNN` in `docs/decisions/` plus one, zero-padded to 4 digits.
2. Create `docs/decisions/NNNN-<kebab-case-title>.md` from `docs/decisions/0000-adr-template.md`.
3. Fill it from what was actually discussed: context, the options really considered, the decision,
   its consequences. If the reasons are unclear, ask rather than invent them. Status: `Accepted`
   unless the user says otherwise. Fit on one screen.
4. If it replaces an earlier ADR, set the old one's status to `Superseded by [NNNN](…)`.
5. If it changes the system's structure, add a link under "Key decisions" in `docs/ARCHITECTURE.md`.
