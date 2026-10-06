---
name: calibrate-ryan-voice
description: Rebuild the ryan-voice-guide profile from Ryan's real writing across Claude Code transcripts, pre-2026 GitHub, Slack, and Confluence, then prove it with one paragraph per register.
disable-model-invocation: true
---

In Codex, first read [the host adapter](../../references/codex.md).
In OpenCode, first read [the host adapter](../../references/opencode.md).

# Calibrate Ryan's voice

Rewrite `skills/ryan-voice-guide/references/profile.md` from evidence. Every run re-mines every
source; nothing carries over from the last profile except the section headings in
[references/profile-template.md](references/profile-template.md). Run from the caddie repo root.

## 1. Collect hand-picked pieces

`$ARGUMENTS` may carry pasted pieces or the word `skip`. If it carries neither, ask once, up
front, for 5 to 10 pieces Ryan considers "very me", especially registers the mining misses:
client emails, peer Slack messages, a long doc. Take whatever he gives and continue. Record the
count in the coverage table, including zero.

**Done when:** the pieces are in context and counted.

## 2. Mine every source in parallel

Dispatch one `general-purpose` subagent per source, all in one message, each carrying the
shared brief in [references/mining-brief.md](references/mining-brief.md) plus its source
section. Read-only: a miner never sends, reacts, comments, or writes outside the scratchpad.

- **Transcripts**: Ryan's typed turns in `~/.claude/projects/**/*.jsonl`.
- **GitHub**: PR bodies, PR comments, and issues by `ryanzigler` created before 2026-01-01.
- **Slack**: his messages across the full history the connector reaches, DMs included,
  stratified across years and channel types, capped near 1,000.
- **Confluence**: pages he created in the last 5 years, capped at 20, read in full.

A miner that cannot reach its tools reports "unreachable" for the coverage table. It never
substitutes another source, and you never fill the gap from memory.

**Done when:** four reports are in hand, each with a coverage table, observations with
counts, scrubbed excerpts, and generic-versus-Ryan pairs.

## 3. Merge into the profile

Fill the template section by section, keeping its headings and order so a recalibration diffs
cleanly. Rules carry a frequency: `Always`, `Never`, or `Usually` with a rate. Signature
phrases carry an observed rate and the registers they appear in. Where sources disagree, the
register table records the difference instead of averaging it.

Excerpts follow one policy regardless of source: verbatim, under 45 words, with every client,
company, product, and person identifier replaced by `[client]`, `[product]`, or `[name]`.
Nothing personal from a DM, nothing dated 2026 from GitHub, nothing a miner judged
agent-written. Hand-picked pieces shape the rules and yield excerpts under the same policy.

A section the evidence cannot support says `Insufficient evidence` and names what was
missing, so the applier defers to the tells pass there rather than guessing.

**Done when:** every heading has content or an `Insufficient evidence` line, and the header
carries today's date, the hand-picked count, and the coverage table.

## 4. Prove it

Take one generic, model-written paragraph of about 60 words and rewrite it three times with
the new profile: peer Slack message, client-facing update, PR description. Put the three in the
reply beside the coverage table. Then write the profile file and delete the miners' raw dumps
from the scratchpad; the profile is the only thing that keeps his words, and it keeps them
scrubbed.

**Reply:** path written, coverage table, the three paragraphs, and any section marked
`Insufficient evidence`. Ryan redirects from there; his corrections go into the next run's
hand-picked pieces, or straight into the profile if he prefers.
