---
name: how
description: Explain how a subsystem works, trace a runtime flow, or settle a placement question. Use for "how does X work", "walk me through what happens when a user does Y", a code walkthrough before changing something, onboarding onto an unfamiliar area, and package-ownership or layering questions such as "where should this live", "which package owns this", "is this the right layer", "do these need their own tsconfig", "should this be its own entrypoint or its own package". Can also critique a subsystem's architecture when asked for problems or improvements. Use the why skill for motivation and history.
---

# How

Answer "how does X work?" at the level of a senior engineer onboarding onto a subsystem. Produce a working mental model, not annotated source code.

Pick the mode from the question. Do not ask the user which one they want.

- **Explain** (default). Explore, then explain.
- **Placement.** Where should this live, which package owns it, is this the right layer.
- **Critique.** Explain first, then fan out lens-specific critics.

## Explain mode

### Step 1. Parse the question, then triage

Identify the target and its scope: a subsystem ("how does the rate limiter work"), a feature flow, an architectural overview, or a runtime trace ("what happens when a user submits a form"). If the target is ambiguous, state your best-guess interpretation in one line and proceed. Do not ask; let the user redirect.

**Triage is the cost control. Do not skip it.**

- **Simple.** A single module, a small utility, anything you could answer confidently after reading three or four files. No fan-out. Go to Step 2b.
- **Complex.** A subsystem spanning multiple files, packages, or services; a cross-cutting feature; a full architectural overview. Fan out. Go to Step 2a.

When in doubt, lean simple. You can always fan out if the single pass hits a wall. A small question must not spawn a fleet.

### Step 2a. Explore in parallel (complex only)

Decompose into **2 to 4** angles, each a distinct slice so explorers do not duplicate work. For a rate limiter that might be: data model and state; request path and enforcement; configuration and metrics. The right split depends on the question. Narrow question, 2 explorers. Broad subsystem, 4 at most.

Spawn all of them in a single message:

- `subagent_type`: `Explore`
- Prompt: [references/explorer-prompt.md](references/explorer-prompt.md) plus the angle naming that explorer's slice.

`Explore` is read-only and biased toward excerpts, so tell each explorer to read implementations rather than skim and to trace one call chain end to end. Overlap between explorers is fine; the explainer reconciles it. Go to Step 3.

### Step 2b. Direct explain (simple only)

One subagent explores and explains in a single pass. `subagent_type`: `general-purpose`, prompted with [references/explainer-prompt.md](references/explainer-prompt.md) adapted for no explorer findings. Instruct it not to write files. Go to Step 4.

### Step 3. Synthesize (complex only)

One subagent reconciles all explorer findings into a single explanation. `subagent_type`: `general-purpose`, prompted with [references/explainer-prompt.md](references/explainer-prompt.md) and every explorer's output. It merges overlaps and resolves contradictions by checking the code itself. Instruct it not to write files.

### Step 4. Present

Present the explainer's output. Light edits for clarity or conversational context are fine; do not substantially rewrite it. The explainer's communication is the product, and it owns the output structure.

## Placement mode

Triggered by ownership, layering, and boundary questions: where should this live, which package owns this, is this the right layer, does this need its own tsconfig or entrypoint, should this be extracted, why is this import pulling in half the monorepo.

A generic subsystem walkthrough answers these badly. Read [references/placement-questions.md](references/placement-questions.md) first and follow the evidence order it sets out: read the workspace, build, and tsconfig files before reasoning about where anything belongs.

Triage the same way. A "which of these two packages" question needs no subagents. A "how should we split this package" question warrants 2 to 3 explorers, one per candidate boundary.

## Critique mode

Triggered when the user asks for architectural issues, problems, or improvements rather than understanding.

**Step 1.** Run the full explain flow. You must understand the architecture before critiquing it.

**Step 2.** Fan out critics, each assigned **one lens** from [references/critique-rubric.md](references/critique-rubric.md). The assigned narrowness is what makes parallel critics find different things; a critic told to look at everything returns the same generic complaints every time.

Pick the **2 to 4 lenses the subsystem actually implicates**, matched to what the explanation surfaced. Optional fields crossing boundaries points at Data Model and Boundary Discipline. Interfaces with one implementation each points at Abstraction Fit and Complexity vs. Value. Do not spawn all six by default.

Spawn them in a single message. `subagent_type`: `general-purpose`, prompted with [references/critic-prompt.md](references/critic-prompt.md), the Step 1 explanation, the relevant file paths, and only that critic's lens. Instruct each not to write files.

**Step 3.** Judge as a pragmatic lead, not an aggregator. Categorize every finding as **act on** (worth fixing now), **consider** (real, unclear cost/benefit), **noted** (valid, low priority), or **dismissed** (wrong, missing context, or style preference — say which). Dismissing findings is part of the job, and a critic that returns nothing is a valid result.

Present the explanation first, then the verdict below it. The explanation must stand on its own so someone who only wants to understand the system does not have to wade through critique.
