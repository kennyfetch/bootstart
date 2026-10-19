---
name: test
description: Add or improve tests for existing code without changing its behavior. Use when asked to test, cover or harden a module or function.
argument-hint: <file, module or function to test>
---

# Test

Target: $ARGUMENTS

1. Read the target code and its existing tests (`tests/` mirrors `src/`).
2. List the behaviors to cover, in this order: main path, edge cases (empty, zero, limits, unicode,
   large input), error cases. Skip what is already tested.
3. Write the tests following `docs/CONVENTIONS.md` §6: one behavior per test, Arrange / Act / Assert,
   names that read as sentences, no real network, clock or shared state.
   Prefer table-driven tests (`pytest.mark.parametrize`, `it.each`) for input/output variations.
4. Run `just test`. A new test that passes immediately must still be able to fail: check that it
   would break if the code were wrong (for example by temporarily inverting a condition).
5. Do **not** change production code. If a test reveals a bug, stop and report it with the failing
   test — fixing it is a separate `feature` task.
6. Run `just check`, then report: behaviors covered, coverage change, bugs found.
