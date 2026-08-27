---
name: why
description: Reconstruct the motivation and history behind code, cited and confidence-calibrated. Use for "why does X work this way", "why did we pick Y over Z", design rationale, rejected alternatives, "when did this regress and what changed", postmortem archaeology, and "where did this number come from". Discovers which evidence sources are actually connected in this environment (source control, issue tracker, long-form docs, team chat, infrastructure observability, error tracking, product analytics), runs one investigator per connected category in parallel, and returns a cited answer with an explicit coverage map of what was searched, what came back empty, and what could not be searched at all. Use the how skill for runtime behavior, and diagnosing-bugs for a failure that is happening now: this skill reconstructs history, it does not debug.
---

# Why

Investigate the motivation and intent behind code. Why was it built this way? What edge cases were considered? What product, business, or operational constraint shaped it? What alternatives were rejected, and why?

Companion to the `how` skill. `how` answers what the code does. `why` answers what forces led to its shape.

The target is in `$ARGUMENTS` when provided. Otherwise infer it from the conversation: files recently read or edited, the change just discussed, the error just pasted.

Historical context spreads across seven evidence categories, and you cannot tell from the question alone which one holds the answer. So discover which categories are actually reachable here, query each in parallel, and synthesize with explicit confidence calibration. A null result from a category you searched is first-class evidence about how the decision was made; report it alongside the positive findings.

## Operating posture

Work like a careful investigator assembling a historical case from fragmentary records, not like an author writing a satisfying story.

- **Evidence before narrative.** Collect the pieces, then see what story they support. Never pick a story and recruit evidence for it.
- **Precision over polish.** An exact quote with a precise citation beats a smooth paraphrase. A reader should be able to verify any claim in a minute.
- **Consider what you haven't seen.** What you found is a sample. Ask what you would expect to see if an alternative explanation were true, and whether you looked for it.
- **Name the gaps.** A cold thread, an unauthenticated source, an unanswerable question: document it rather than papering over it.
- **Hedge on purpose.** When evidence is indirect the language must signal it. Confidence-matching phrasing is the product, not a style choice anyone may override.
- **No shortcut by code-reading.** Code tells you what it does, almost never why it exists.

[references/epistemics.md](references/epistemics.md) has the confidence tiers, the phrasing guide, and the failure modes. The synthesizer must follow it in full.

## Step 1. Understand the target and the question

The **target** is a chunk of code, a pattern, a feature, or a named decision. The **question** is usually design rationale, tradeoffs and rejected alternatives, what edge cases motivated a defense, what external constraint forced it, why dead-looking code still exists, or a broad archaeological sweep.

If the target is vague, guess from context and state your interpretation in one line so the user can redirect. Then proceed. If the question embeds a hypothesis ("I assume this is for performance?"), treat it as one candidate among several rather than something to confirm.

## Step 2. Establish the code anchor

Build this inline with `git` and `gh` before spawning anything. It is cheap, and every investigator needs it. Commands are in [references/sources/code-archaeology.md](references/sources/code-archaeology.md). The anchor must contain:

- File paths and line ranges, and the key symbols
- The last several commits touching the target, with hashes and dates
- PR numbers from merge-commit subjects (pattern `(#1234)`), and any ticket IDs in those commits or PR bodies
- Whether the target looks **defensive** (null check, retry, timeout, rate limit, feature flag, guard clause, fallback). This flag decides whether investigators also get the incident playbook.

Pass the anchor to every investigator so none of them rediscovers it.

## Step 3. Discover which sources are connected

Do not assume. Determine what is actually reachable before deciding what to spawn.

1. **Scan your own tool surface.** Any tool named `mcp__<server>__<tool>` is a connected MCP server. Deferred MCP tools appear by name in system-reminders without schemas; that still tells you the server exists. Investigators load their own schemas with `ToolSearch`, so do not load them here.
2. **Run `claude mcp list`.** It prints every configured server as `Connected` or `Needs authentication`. This distinction is load-bearing: `Connected` means searchable, `Needs authentication` means the category is a **gap** and the coverage map should say so and mention that `/mcp` authenticates it.
3. **Check CLI-backed sources**, since not every category arrives as an MCP. `command -v` for `git` and `gh` (source control, expected present), `sentry-cli` (error tracking), `bq` (product analytics), and whatever deploy tooling the repo uses (infrastructure observability). A working CLI counts as connected.
4. **Map each connected source to exactly one category**, classifying from its name, instructions, and tool names. Ambiguous cases get noted in the coverage map. Two sources in one category means one investigator owns both.

The seven categories: source control history, issue / ticket tracker, long-form documents, real-time team chat, infrastructure observability, error / exception tracking, product analytics.

[references/evidence-categories.md](references/evidence-categories.md) covers what each contains, what it is strongest at, and how to word a gap. [references/source-playbook.md](references/source-playbook.md) maps each category to its playbook.

## Step 4. Spawn investigators

**Investigator budget.** Each investigator is a subagent plus a round of external queries, so the count scales to the question rather than defaulting to the maximum.

- **Always spawn** the source control investigator. It is the only guaranteed source.
- **One investigator per remaining category that has a connected source.** Never two for one category; each source has its own query vocabulary and result shape, and pooling them dilutes specialization.
- **Never spawn for a category with no connected source.** There is nothing to search. Write the gap line instead.
- **Ceiling is 7 investigators plus 1 synthesizer.** A typical run is 3 to 6 subagents total.
- **Narrow run.** When the user asks for something quick, or the target is a single line whose seed PR body already contains an explicit answer, run source control plus the one or two categories the target's character points at. Every unrun category then gets a `not searched (budget)` line worded so the user knows a full sweep is available. This is a budget decision the user can see and reverse, never a silent drop.
- **No category goes unrun for any other reason.** "Docs probably don't have this" and "it's feature code, error tracking won't have anything" are the exact failure this design prevents. The only legal reasons: no connected source, an explicit narrow run, or provably irrelevant with a written justification ("error tracking skipped, the target is a build-time script with no runtime path"). "Probably irrelevant" does not qualify.

Whatever runs, **the coverage map always has exactly seven lines, one per category.**

Launch all investigators in a single message. `subagent_type`: `general-purpose` — they need MCP tools and Bash, and they need to read whole PRs and threads rather than excerpts. Instruct each one not to write files, commit, or modify external state; that is a posture, not a sandbox.

Each prompt is: [references/investigator-prompt.md](references/investigator-prompt.md), plus the one playbook matching its assigned source, plus [references/sources/incident-postmortem.md](references/sources/incident-postmortem.md) only if the target looked defensive, plus the code anchor and the user's original question.

## Step 5. Synthesize

One synthesizer, `subagent_type`: `general-purpose`. It needs MCP and codebase access to spot-verify citations. Instruct it not to write files or modify external state.

It gets all investigator findings including null results, the list of unrun categories and why, the code anchor, the original question, the contents of [references/epistemics.md](references/epistemics.md), and [references/synthesizer-prompt.md](references/synthesizer-prompt.md).

Run this step even when only source control ran. The confidence tiers and the seven-line coverage map still apply.

## Step 6. Present

Present the synthesizer's output. Light edits for clarity or conversational context are fine. **Do not rewrite the confidence language.** Dropping hedges to sound more authoritative is the exact failure mode this skill exists to prevent. Two more, at this step specifically:

- **Skipping a connected category by anticipation.** A null result is a data point; a skipped search is a blind spot.
- **Reading "needs authentication" as "nothing there."** An unauthenticated source is an unsearched source.

Output sections, defined in full in [references/synthesizer-prompt.md](references/synthesizer-prompt.md): the question; the code in question; what we found; what we can reasonably infer; competing hypotheses; what we don't know; sources consulted; confidence summary.

If the question is a precursor to actually changing this code, append a Preserve / Change / Avoid / Risk constraint set derived from the findings, so the lineage feeds the plan.
