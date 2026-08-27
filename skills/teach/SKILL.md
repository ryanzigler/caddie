---
name: teach
description: Explain a change, subsystem, or concept plainly until the person actually understands it, by running the `how` and `why` skills and weaving their findings into one account. Use for "teach me this", "help me understand X", "walk me through this subsystem", "explain this PR to me", or getting oriented in unfamiliar code. Not for debugging a failure and not for a one-line factual answer.
---

# Teach

Explain what a thing is, how it works, and why it's built that way, in one plain account at the person's pace. The goal is that they understand it, not that you change anything. Change nothing unless they ask.

Teach sits on top of `how` and `why`. Read enough code to get oriented, then let those skills do the investigation.

1. **Pick the few things they should walk away understanding.** Choose them from why they're asking (about to change it, reviewing it, debugging it, new to it) and what they already know, both read from the conversation, not quizzed out of them. Skip what they plainly already know. Put the depth where their question is.
2. **Delegate the digging.** Run `how` for how it works and `why` for why it's that way, then combine the results. Issue both in one turn so they run concurrently where the harness allows it. Match the size to the question: both for a subsystem, sometimes one is enough for a small change. Keep `why` narrow by default, since its full sweep is slow. Put the narrowing in the ask itself, a scoped question plus a source or two, so `why` records which categories it skipped. Widen it only when the reasons are the point. Reword their findings freely for teaching, with one exception: keep `why`'s confidence language intact. Its hedges are findings, not style.
3. **Start with a plain definition.** Name the thing and say what it is in general terms, the way a senior engineer would say it out loud, with its common name if it has one. Then tie it to the case in front of you ("in this repo, we use it to...") and build outward: how it works, the deeper reasons, the edge cases. Explain the mechanism, don't just name it. Walk through what happens as the person does the thing when that's what makes it land. Listing functions and constants is reference, not teaching.
4. **Give the smallest complete answer first,** a sentence or two, then stop. Add layers when they ask. Never a wall of text. Offer to go deeper or move on, and follow their lead. No quizzes, no pacing theater.
5. **Show, don't only tell.** Open the diff, the code, or a debugger when that's the fastest way to land it. Draw when a picture beats words, and build it up one part at a time: see [references/delivery.md](references/delivery.md).

Read [references/delivery.md](references/delivery.md) before writing the explanation. It carries the voice, density, and diagram rules, and this skill lives or dies on those.

**Reply:** the explanation itself, never a report about what you did. Lead with the main point, then the plain account of what it is, how it works, and why, then the threads worth chasing with `how` or `why`.
