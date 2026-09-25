---
name: grilling
description: Interview the user to resolve a plan, design, or decision. Use when asked to grill, interview, or stress-test their thinking, or when material requirements need clarification. Route engineering interviews that should capture terminology and decisions to grill-with-docs.
---

# Grilling

Interview the user until you reach a shared understanding. Map the work as a **design tree**: every decision branches into the decisions that hang off it.

## Choose the questions for the work

For engineering work, establish users, observable behavior, scope, constraints, failure
cases, and acceptance criteria. Then probe ownership, interfaces, compatibility,
migration, and testability where relevant. Inspect the code to answer factual questions.
When the interview should maintain a glossary and ADRs, use
[grill-with-docs](../grill-with-docs/SKILL.md); it adds documentation to this process.

For non-engineering work, probe the goal, audience, incentives, resources, constraints,
tradeoffs, and evidence of success. Use the domain's own language; avoid imposing code
architecture, test plans, or ADRs on a career, writing, or business decision.

For mixed work, settle the outcome first, then separate product or business decisions
from technical choices. Ask only questions that can change the decision or the result;
a straightforward authorized edit does not need a design interview.

## Rounds

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask the whole frontier in one round. Number each question and give your recommended answer. Then wait for the user's answers before the next round.

Format a round like this:

```
❓ **Q1** - **<question title>**: <question body, may be several paragraphs, may offer choices>

➡️ <your recommended answer>

---

❓ **Q2** - **<question title>**: <question body, may be several paragraphs, may offer choices>

➡️ <your recommended answer>
```

Every recommended answer is mandatory. A question with no recommendation attached is you offloading the thinking; take a position and let the user overrule it.

Each round of answers reshapes the tree: settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

## Finding facts is your job, never the user's

The _decisions_ are the user's. The _facts_ are yours. Read the relevant files and
inspect the environment before asking a factual question. For substantial independent
lookups, delegate when tools are available; otherwise investigate directly. Never ask
the user for information you can look up.

A running exploration is an unsettled prerequisite, so only the questions downstream
of it wait for its result; ask the rest of the frontier now.

## Ending

The interview is done when every material decision is settled or explicitly deferred
with its consequence recorded. Summarize the agreement and any remaining assumptions.
For an interview-only request, ask whether this captures the user's intent and wait;
confirmation of understanding alone does not authorize implementation.

When implementation was already requested, preserve that authorization. Continue with
[writing-plans](../writing-plans/SKILL.md) for substantial work or directly with a small
change once the blocking decisions are answered. Ask for a new decision only when the
answers materially change the authorized scope.
