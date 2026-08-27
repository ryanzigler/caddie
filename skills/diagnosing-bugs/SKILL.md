---
name: diagnosing-bugs
description: Diagnosis loop for bugs, test failures, crashes, broken CI, and performance regressions. Use whenever the user pastes a stack trace, failing test output, CI log, or error message, or names a failing workflow, job, build, or check without pasting its output, or says "I'm seeing this", "this is failing", "why is this broken", "fix this bug", "debug this", "diagnose this", or reports something throwing, hanging, returning the wrong value, or getting slower — and before proposing any fix. This is the debugging process skill: use it instead of any other, including a retired one you remember.
---

# Diagnosing Bugs

Build a feedback loop that goes red on the bug, minimise it, rank hypotheses, then probe. Work
the phases in order; skip one only with an explicit, stated reason.

## Redact first

This skill has you show commands, outputs, and captured artifacts. Replace every secret with
`<REDACTED>` before showing it. Drive loops from environment variables so credentials stay in
the environment rather than in what you print. Captured artifacts carry auth headers, so quote
only the lines that carry signal. If the redacted output is not enough to diagnose the bug, say
so and ask the user.

## Phase 1: Build a feedback loop

**This is the skill.** Everything else is mechanical. Given a tight pass/fail signal that goes
red on _this_ bug, you will find the cause: bisection, hypothesis-testing, and instrumentation
all just consume it. Without one, no amount of reading code will save you.

Spend disproportionate effort here. Be aggressive, be creative, refuse to give up.
[references/feedback-loops.md](references/feedback-loops.md) has ten ways to construct a loop,
how to tighten one, and how to handle bugs that only reproduce sometimes.

### The gate is an artifact, not a mental state

Phase 1 is done when you can name **one command** that you have **already run at least once**,
showing the invocation and its redacted output, and that is:

- [ ] **Red-capable**: it drives the actual bug code path and asserts the user's exact symptom,
      so it goes red on this bug and green once fixed. Not "runs without erroring" — it must be
      able to catch _this_ bug.
- [ ] **Deterministic**: same verdict every run. For flaky bugs, a pinned and high reproduction
      rate.
- [ ] **Fast**: seconds, not minutes.
- [ ] **Agent-runnable**: you can run it unattended, with a human in the loop only through the
      template in `references/hitl-loop.template.sh`.

If you catch yourself reading code to build a theory before that command exists, **stop:
jumping straight to a hypothesis is the exact failure this skill prevents.** No red-capable
command, no Phase 2.

If you genuinely cannot build a loop, stop and say so. List what you tried, then ask for one
of: access to an environment that reproduces it, a redacted captured artifact (HAR file, log
dump, core dump, screen recording with timestamps), or permission to add temporary production
instrumentation. Do not proceed to hypothesise without a loop.

## Phase 2: Reproduce and minimise

Run the loop. Watch it go red as the bug appears.

- [ ] The failure is the one the **user** described, not a different failure that happens to sit
      nearby. Wrong bug, wrong fix.
- [ ] It reproduces across multiple runs, or for flaky bugs at a high enough rate to debug
      against.
- [ ] You have captured the exact symptom — error text, wrong value, slow timing — so later
      phases can verify the fix addresses it.

### Minimise

Once it is red, shrink the repro to the smallest scenario that still goes red. Cut inputs,
callers, config, data, and steps **one at a time**, re-running the loop after each cut.

Done when every remaining element is load-bearing: removing any one of them turns the loop
green. A minimal repro shrinks the hypothesis space in Phase 3, because there are fewer moving
parts left to suspect, and it becomes the clean regression test in Phase 5.

Do not proceed until you have reproduced **and** minimised.

## Phase 3: Rank hypotheses before probing

Generate **3–5 ranked hypotheses** before testing any of them. Generating one anchors you on
the first plausible idea, which is how a confident fix turns out not to fix anything.

Each hypothesis must be **falsifiable**. State the prediction it makes:

> If X is the cause, then changing Y makes the bug disappear, or changing Z makes it worse.

If you cannot state the prediction, the hypothesis is a vibe: sharpen it or discard it.

**Show the ranked list to the user before you probe.** Domain knowledge re-ranks it instantly
("we just deployed a change to #3"), and they may have already ruled some out. Cheap
checkpoint, large saving. Do not block on it: proceed with your own ranking if the user is
away.

## Phase 4: Instrument

Every probe maps to a specific prediction from Phase 3. Change one variable at a time.

1. **Debugger or REPL inspection** wherever the environment supports it. One breakpoint beats
   ten logs.
2. **Targeted logs** at the boundaries that distinguish the hypotheses.
3. Never "log everything and grep".

Tag every debug log with a unique prefix, such as `[DEBUG-a4f2]`, so cleanup is a single grep.
Untagged logs survive; tagged logs die.

**Performance regressions**: logs are usually the wrong instrument. Establish a baseline
measurement first — timing harness, `performance.now()`, profiler, query plan — then bisect
against it. Measure first, fix second.

## Phase 5: Fix and regression test

Write the regression test **before** the fix, but only where a **correct seam** exists: one
where the test exercises the real bug pattern as it occurs at the call site. A seam too shallow
to replicate what triggered the bug (a single-caller test for a bug that needs several callers,
a unit test that cannot reproduce the chain) gives false confidence.

**If no correct seam exists, that is itself the finding.** Say so plainly: the architecture is
preventing the bug from being locked down.

Where a correct seam exists:

1. Turn the minimised repro into a failing test at that seam.
2. Watch it fail.
3. Apply the fix.
4. Watch it pass.
5. Re-run the Phase 1 loop against the original, un-minimised scenario.

## Three strikes: question the architecture

Count your fix attempts. A failed fix is any attempt that left the Phase 1 loop red, or turned
it green while breaking something else.

On the **third** failed fix, stop generating hypotheses. Three failures is evidence about the
design, not an invitation to try a fourth idea. Instead:

- Say explicitly that you are at three strikes.
- Name what all three attempts assumed in common. That shared assumption is the real suspect.
- Widen the frame one level: wrong layer, wrong module boundary, duplicated state, two sources
  of truth, an abstraction that cannot express the correct behaviour.
- Bring the user in with all three attempts, the prediction each made, and what actually
  happened. Propose the structural change rather than applying it unannounced.

## Phase 6: Cleanup

Required before declaring done:

- [ ] Original repro no longer reproduces (re-run the Phase 1 loop)
- [ ] Regression test passes, or the absence of a correct seam is written down
- [ ] All `[DEBUG-...]` instrumentation removed (grep the prefix)
- [ ] Throwaway harnesses deleted, or moved to a clearly marked debug location
- [ ] The hypothesis that turned out correct is stated in the commit or PR message, so the next
      person to debug this area learns from it
