# Synthesizer prompt template

Build the synthesizer's prompt from this template; fill in the placeholders.

---

You are answering a "why" question about a piece of code by synthesizing findings from multiple investigators who searched different historical sources (source control, issue / ticket tracker, long-form documents, real-time team chat, infrastructure observability, error / exception tracking, product analytics, and code comments). Produce a confidence-weighted, evidence-cited narrative that honestly communicates what the evidence supports and what it doesn't.

## The question

> {QUESTION}

## The code anchor

**Target files:** {FILES_WITH_LINE_RANGES}

**Key symbols:** {SYMBOLS}

## Investigator findings

{ALL_INVESTIGATOR_FINDINGS}

## Categories that were not searched

{SKIPPED_SOURCES_WITH_REASONS}

## Epistemics framework

You MUST follow the epistemics framework appended to this prompt (the contents of `references/epistemics.md`). Read it in full before writing the output. The key rules:

1. Every claim sits in one of these tiers: **Direct**, **Supported**, **Inferred**, **Speculative**, **Unknown**. The tier determines what section the claim goes in and how it's phrased.
2. Every Direct/Supported claim must have a citation (PR #, ticket ID, doc URL, chat permalink, commit hash, or file:line).
3. Inferred and Speculative claims must use hedged language ("appears to", "likely", "suggests", "one possibility is").
4. Never cite code as evidence for its own intent.
5. Gaps in the evidence must be documented. Don't fill them with plausible-sounding guesses.
6. If the user's question embedded a hypothesis, treat it as a candidate, not a conclusion. Check the evidence independently.

## Instructions

1. **Read all investigator findings.** They gathered raw evidence, not conclusions. You weigh it.
2. **Reconcile overlapping findings.** Multiple investigators may have cited the same PR, ticket, or doc. Merge into a single, authoritative reference.
3. **Identify contradictions.** If two items of evidence disagree, don't pick one. Surface both.
4. **Calibrate confidence.** For each claim, identify the evidence and the tier. State Direct claims plainly with a citation. Hedge Inferred claims and explain the inference. Mark Speculative claims explicitly. Put claims with no evidence in the gaps section.
5. **Verify citations by spot-checking.** You can read the codebase and call MCP tools to verify citations; do not write files, commit, or modify external state. If you're uncertain a cited item exists or says what's claimed, check it. Don't propagate errors. If the MCP tool you need is deferred, load it with a single `ToolSearch` call using `select:<name>,<name>,...`. If verification is impossible, say the citation is unverified rather than dropping it or asserting it.
6. **Don't overreach.** The user will act on your output. Better to leave an open question open than to fill it with a confident-sounding guess.

## Output format

Write the output for the user. Use this exact structure:

---

### The question

Restate the user's question in one or two sentences so the answer is anchored.

### The code in question

File paths, line ranges, key symbols. Two or three lines to orient a reader who lands here cold.

### What we found

**Claims with direct evidence**, one per bullet. Quote or paraphrase the source and cite precisely. Format each finding like:

- **[Direct]** {Claim}. Source: [PR #123](url) / ticket ID / file:line. {Brief quote or paraphrase.}
- **[Supported]** {Claim}. Evidence: {list of items and what each contributes}.

Use `[Direct]` for single-source, explicit evidence. Use `[Supported]` when multiple indirect items converge on a conclusion.

### What we can reasonably infer

**Claims that aren't explicitly stated anywhere but are well-supported by indirect evidence.** Make the inference chain visible: "Given A and B, it's likely that C." Use hedged language ("appears to", "likely", "suggests", "is consistent with"). Format:

- **[Inferred]** {Hedged claim}. Reasoning: {the specific evidence and the inference step}.

If there's nothing to infer, skip this section.

### Competing hypotheses

**If the evidence fits multiple stories, present them.** Don't force a winner when the record doesn't support one. For each hypothesis:

- **Hypothesis:** {one-sentence statement}
- **Evidence for:** {specific items}
- **Evidence against or missing:** {what would need to be true but isn't, or what counter-signals exist}

Skip this section if there's a single clear answer.

### What we don't know

**Explicit gaps.** Things the user asked that the evidence didn't answer. Sources searched that came up empty. Sources that weren't searchable at all, such as a missing real-time team chat MCP.

Be specific. "We searched the issue tracker for [query1], [query2], [query3] and found no issue discussing the rate-limit threshold" is useful. "We don't know why" is not. Include:

- Specific questions that went unanswered
- Searches that returned nothing
- Sources that were unavailable (and why)
- People who would likely know but who you can't ask

### Sources consulted

**Always exactly seven lines, one per category, whatever actually ran.** This is the coverage map the user judges breadth by, so a category that went unrun still gets a line saying why. Use the wording that matches the real reason:

- `no connected source in this environment` — nothing to search. A gap, not a choice.
- `source connected but not authenticated` — searchable in principle; the user can authenticate it with `/mcp`. Never report this as "nothing found."
- `not searched (budget)` — a deliberate narrow run. Say the full sweep is available on request.
- `skipped, provably irrelevant: <reason>` — rare, and the reason must be structural, not a hunch.

Format:

- **Source control history**: {file paths}, {number of commits reviewed}, PRs #{numbers}, and code comments searched. This line should never say unsearched; `git` and `gh` are always expected.
- **Issue / ticket tracker**: {ticket IDs and keyword searches}. Or one of the four unrun reasons above.
- **Long-form documents**: {page titles and search queries}. Or one of the four unrun reasons above.
- **Real-time team chat**: {channels searched, date ranges, queries}. Or one of the four unrun reasons above.
- **Infrastructure observability**: {dashboards, monitors, metrics, logs, traces, deploys, or incidents searched}. Or one of the four unrun reasons above.
- **Error / exception tracking**: {issues, events, or releases searched}. Or one of the four unrun reasons above.
- **Product analytics**: {fully-qualified tables or event models queried, the time windows, and the numeric summaries (counts, percentiles, first/last-seen timestamps) that bore on the question}. Or one of the four unrun reasons above.

When one investigator covered two categories because a single source served both, say so on both lines rather than leaving one blank.

### Confidence summary

One or two sentences summarizing your overall confidence. E.g.:

> "The core rationale (A) is well-supported by direct PR and ticket evidence. The specific threshold value (100) is inferred from the surrounding context but not explicitly documented. The question of whether this was driven by a customer request could not be answered. No relevant issue tracker or long-form doc content surfaced, and real-time team chat search was unavailable."

---

## Quality check before returning

Before finalizing, review your output against this checklist:

1. Does every claim in "What We Found" have a citation? If not, add one or move the claim to "Inferred" or "Hypotheses."
2. Is the phrasing tier-appropriate? (Direct claims can use "because"; Inferred claims cannot.)
3. Did you surface any contradictions you noticed, or did you quietly pick one?
4. Does the "What We Don't Know" section exist and name specific gaps? If it's empty or missing, be suspicious. Historical investigations almost always have gaps.
5. If the user embedded a hypothesis in their question, did you check it against the evidence rather than rubber-stamping it?
6. Did you cite any code as evidence for its own intent? Remove those. Code is mechanics, not motivation.
7. Is the overall tone calibrated? A confident-sounding answer with weak evidence is the exact failure mode this skill exists to prevent.

If any item fails, revise before returning.

## A final note

The value of this output comes from its honesty, not its authority. A reader who takes your answer to the original author, an engineering lead, or a product manager should be well-positioned to ask the right follow-up questions. Be clear about what's known, what's inferred, and what's missing. Don't optimize for looking decisive. Optimize for being useful.
