---
name: ryan-voice-guide
description: Write anything published under Ryan's name in Ryan's own voice, from a calibrated profile of his real writing, after stripping AI-writing tells. Use whenever drafting a PR description, commit message, Slack or email message, doc, README, release note, or issue as Ryan; when asked to "make this sound like me", "humanize this", "make it less robotic", or "de-AI this"; when asked "does this sound like me"; and when another skill routes Claude's own reply through it for the tells pass alone. Not for code, code comments, or SKILL.md and CLAUDE.md prose.
---

In Codex, first read [the host adapter](../../references/codex.md).

# Ryan voice guide

Make the text something Ryan would have written, not something a generic human would have.
The voice lives in [references/profile.md](references/profile.md); the AI tells to remove live
in [references/patterns.md](references/patterns.md). Read both before editing a word.

If the profile header says it is uncalibrated, do the tells pass only, tell the user to run
`/calibrate-ryan-voice`, and say the voice pass was skipped.

## Situations

- **Drafting as Ryan.** Apply the passes below while writing. Say nothing about the voice
  work; the draft is the deliverable.
- **Rewriting pasted text.** Return only the rewritten text: no preamble, no change log, no
  quotation wrapper. A code block in stays a code block out.
- **Diagnosing.** When asked whether something sounds like him, name the lines that don't and
  what he would say instead. Rewrite nothing unless asked.
- **Writing to Ryan.** When another skill sends Claude's own reply here, run passes 1, 2, and 5
  and skip the voice: the reply is Claude's, so the read-back question becomes "is every line
  plain and specific?"

If the user names another writing skill for this piece, that skill governs it.

## Passes

1. **Fix the constants.** Facts, names, numbers, dates, quotations, citations, code, and any
   structure the destination requires stay exactly as they are through every later pass.
2. **Strip tells.** Work through the pattern catalog once. A pattern is a problem when it
   obscures the point or repeats mechanically, not merely when it appears.
3. **Pick the register.** Match the destination to one row of the profile's register table.
   That row decides length, opener, formality, and formatting, including structure and length
   for client-facing work. Where the row says `Insufficient evidence`, borrow the nearest row
   and lean on the tells pass; a commit body, for example, takes the PR body's shape.
4. **Apply the voice.** `Always` and `Never` rules hold on every line. `Usually` habits apply
   where the sentence takes them naturally. A signature phrase appears at most once per piece,
   only where the content already calls for it, and never in a piece shorter than his own
   typical gap between uses.
5. **Read it back as him.** Ask of each sentence, "would Ryan have written this?" and of the
   whole, "does this contain anything he would not bother to say?" Cut what fails the second
   question before polishing what fails the first.

Invent nothing to make it sound human: no anecdotes, opinions, certainty, or first-person
experience the source did not carry. Done when every line passes step 5 and the constants from
step 1 are unchanged.
