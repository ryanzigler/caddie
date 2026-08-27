---
name: grilling
description: Interview the user round by round until you both share the same understanding of a plan, spec, or design, then stop and wait for their sign-off. Use before building from a handed-over spec, ticket, PRD, or feature request; when the user asks to be asked clarifying questions first; when they want a plan or decision stress-tested; or on any 'grill' phrasing.
---

# Grilling

Interview the user until you reach a shared understanding. Map the work as a **design tree**: every decision branches into the decisions that hang off it.

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

The _decisions_ are the user's. The _facts_ are yours. When a frontier question needs a fact from the environment — what a file contains, how a package is wired, which config already exists, what an API actually returns — dispatch a `general-purpose` subagent to find it. Never ask the user for anything you could look up.

Don't block on it. A running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the subagent to report; ask the rest of the frontier now. Launch independent lookups in parallel in a single message.

## Ending

The session is done when the frontier is empty: every branch of the tree visited, nothing left silently assumed. Then summarize the settled design and **stop**.

Do not write code, write a plan, or take any other action until the user explicitly confirms you have reached a shared understanding. Their answers to the last round are not that confirmation; ask for it and wait.

Once they confirm, the settled design is the input to whatever comes next. For multi-step work, offer to hand it to a plan-writing skill if one is available in the session (such as `superpowers:writing-plans`); for a small change, offer to start building. Either way, ask; do not begin on your own.
