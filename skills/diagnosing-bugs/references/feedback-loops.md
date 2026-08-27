# Building a feedback loop

Depth for Phase 1 of [`diagnosing-bugs`](../SKILL.md). Build the right feedback loop and the
bug is 90% fixed.

## Ways to construct one, in roughly this order

1. **Failing test** at whatever seam reaches the bug: unit, integration, e2e.
2. **Curl or HTTP script** against a running dev server.
3. **CLI invocation** with a fixture input, diffing stdout against a known-good snapshot.
4. **Headless browser script** (Playwright, Puppeteer) that drives the UI and asserts on DOM,
   console, or network.
5. **Replay a captured trace.** Save a real network request, payload, or event log to disk and
   replay it through the code path in isolation.
6. **Throwaway harness.** Stand up a minimal subset of the system — one service, mocked
   dependencies — that reaches the bug code path in a single function call.
7. **Property or fuzz loop.** For "sometimes wrong output", run 1000 random inputs and look for
   the failure mode.
8. **Bisection harness.** If the bug appeared between two known states (commit, dataset,
   version), automate "boot at state X, check, repeat" so `git bisect run` can drive it.
9. **Differential loop.** Run the same input through old versus new version, or two configs,
   and diff the outputs.
10. **Human-in-the-loop bash script.** Last resort, when a human must click. Copy
    `hitl-loop.template.sh`, edit its steps, and run it so the loop is still structured and its
    captured output feeds back to you.

## Tighten the loop

Treat the loop as a product. Once you have _a_ loop, tighten it:

- **Faster?** Cache setup, skip unrelated init, narrow the test scope.
- **Sharper signal?** Assert on the specific symptom, not "didn't crash".
- **More deterministic?** Pin time, seed the RNG, isolate the filesystem, freeze the network.

A 30-second flaky loop is barely better than no loop. A 2-second deterministic one is a
debugging superpower.

## Non-deterministic bugs

The goal is not a clean repro but a **higher reproduction rate**. Loop the trigger 100 times,
parallelise it, add stress, narrow timing windows, inject sleeps. A 50% flake is debuggable and
a 1% flake is not, so keep raising the rate until it is debuggable, then pin whatever you
changed to hold it there.
