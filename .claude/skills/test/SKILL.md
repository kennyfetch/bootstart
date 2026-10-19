---
name: test
description: Add or improve tests for existing code without changing its behavior. Use when asked to test, cover or harden a module or function.
argument-hint: <file, module or function to test>
---

# Test

Target: $ARGUMENTS

1. **Branch.** Work on the current task branch. On `main`, create `test/<short-slug>` first.
2. Read the target code and its existing tests (`tests/` mirrors `src/`).
3. List the behaviors to cover, in this order: main path, edge cases (empty, zero, limits, unicode,
   large input), error cases. Skip what is already tested.
4. Write the tests following `docs/CONVENTIONS.md` §6: one behavior per test, Arrange / Act / Assert,
   names that read as sentences, no real network, clock or shared state.
   Prefer table-driven tests (`pytest.mark.parametrize`, `it.each`) for input/output variations.
5. Run `just test`. A new test that passes immediately must still be able to fail: check that it
   would break if the code were wrong (for example by temporarily inverting a condition).
6. Do **not** change production code. If a test reveals a bug, stop and report it with the failing
   test, then:
   - bug in this branch's own unmerged work: it is fixed on this same branch (`feature`), and the
     test stays as it is;
   - bug in code already on `main`: the fix is a separate `fix/…` branch. Here, mark the test as an
     expected failure that names the bug (`pytest.mark.xfail(strict=True, reason="…")`,
     `it.fails(…)`) so `just check` stays green; it turns red once the bug is fixed, as a reminder
     to remove the marker.
7. Run `just check`, then report: behaviors covered, coverage change, bugs found.
