---
name: tdd
description: Build behavior in test-first vertical slices. Use when the user requests TDD, red-green-refactor, or test-first implementation, or an implementation plan selects that approach.
---

# Test-driven development

Choose the public interface where the behavior can be observed. Use the requirements
and existing test conventions to select meaningful cases; clarify a disputed contract
before encoding it. A test should survive refactoring that preserves behavior.

Work one behavior at a time:

1. Write a test with expected results from the requirements or an independently worked
   example. Test through the caller's interface rather than private implementation.
2. Run it and confirm failure for the missing or incorrect behavior. Fix unrelated
   import, fixture, or environment failures before treating the result as red.
3. Implement enough behavior to pass, then run the test and relevant existing checks.
4. Refactor while green when it improves the changed code; rerun affected checks.

Avoid writing all tests against an imagined implementation before building any slice.
Mock external boundaries only where necessary for control or isolation; a mock of
internal calls is usually testing the implementation rather than its outcome. Prefer
observable outputs, state transitions, and failures over call-count assertions.

For a bug, use the actual failing scenario at a seam that can reproduce it. If the
architecture prevents a meaningful regression test, explain that limitation rather
than substitute a test that cannot catch the bug. For prose and simple configuration
edits, use appropriate validation instead of manufacturing a unit test.
