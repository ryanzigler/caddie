---
name: recall
description: "Rebuild working context from prior Claude Code or Codex sessions, live git/gh state, and the shared record (tickets, PRs, prod errors), then hand back a tight current-state brief. Use for 'recall my work on X', 'catch me up', 'what have I been working on', 'where did I leave off', typically right after a /clear."
disable-model-invocation: true
---

In Codex, first read [the host adapter](../../references/codex.md).

# Recall

Rebuild the user's recent working context and hand back a capsule of where things stand
and what to do next. `$ARGUMENTS` is the topic and, if given, the window. Empty
`$ARGUMENTS` means recent work in the active project.

Keep it tight. Read only what the in-scope threads need, then stop. **The heavy reading
fans out to parallel subagents; the main thread keeps only their findings and the final
brief.** Never read a whole transcript into the main context — they run 300 KB to 1 MB
each and half a dozen of them will bury the brief you were asked for.

Context lives in two records. Prior sessions hold what was done and decided. The shared
record holds what happened around the same code under other names: symptoms reported by
users, fixes that shipped and got reverted, errors still firing in prod. A feature with a
long bug tail keeps most of its story there, so don't reconstruct it from transcripts
alone.

## Steps

1. **Route, then scope.** A full state capsule already in the prompt (paths, branch, the
   change) means skip the mining and use it. A request for a human-readable write-up of
   the work is a different task. Recall loads working context before acting.

   Pin the window ("recent" defaults to the last 7 days), the topic if named, and the
   project (default the active one; never read another project's transcripts unasked).
   State the scope back before searching. Never quietly turn "all" into "recent N".

2. **Build the triage index yourself.** Default to the current host's session history.
   An explicit request for Claude or Codex history selects that source regardless of
   the current host; search both only when requested. For Claude Code, use
   [references/transcripts.md](references/transcripts.md). For Codex, use
   [references/codex-transcripts.md](references/codex-transcripts.md). Run the selected
   index in the main thread. Titles or first prompts, mtimes, and prompt counts tell
   you which sessions are worth opening. Report unavailable history as a gap.

3. **Fan out over the candidates.** Spawn parallel `general-purpose` subagents, each
   taking a slice of the candidate sessions. Give every subagent
   the selected transcript reference by absolute path and require its digest command rather
   than reading files whole. Order by mtime, never by UUID. Skip the current session and
   obvious noise (subagent, eval, and throwaway sessions). For one or two candidates, skip
   the fan-out and digest them directly.

   Each subagent returns one block per session, same schema: topic, the user's goal,
   decisions, open threads, struggles and corrections, artifacts (PRs, tickets, branches),
   each citing the session UUID. Raw transcripts stay in the subagents.

4. **Sweep the shared record** whenever the topic names a feature, file, package,
   subsystem, or bug. This is the default, not a judgment call, and "my work on X" does
   not exempt it — a named target carries history that never appears in your own
   transcripts, and that history is the point.

   Run one investigator per source, in parallel with step 3: source control and PRs
   (`gh`, GitHub MCP), the issue tracker and long-form docs (Atlassian MCP), error
   tracking (Sentry), product analytics and session data (PostHog). Steer each away from
   "why was this built this way" toward "what is the current state, what was tried and
   didn't hold, what are users still reporting". The **why** skill carries the per-source
   query playbooks — reuse them rather than reinventing the vocabulary, and inherit its
   posture: null results are findings, and an unavailable MCP is skipped and named as
   skipped, not worked around.

   Skip this step only for pure activity recall with no named target ("what did I do this
   week"), where prior sessions and live state are the whole answer.

5. **Verify against live state.** A transcript or a stale ticket is history, not current
   truth. Take the branches, PRs, and tickets that steps 3 and 4 surfaced and check them
   with `git` and `gh`. Where the answer hinges on what an agent actually ran, have a
   subagent read the relevant region of the real transcript, not a trimmed retelling.

6. **Write the brief** to the contract below. Group by thread, stay on the named topic.

## Output contract

Lead with the capsule, then thread status, then problems, then the next move. Deeper
detail goes below, or gets cut.

- **Capsule.** At most 5 bullets. What this work is and where it stands overall.
- **Threads.** One line each, prefixed with exactly one status tag: `[merged #N]`,
  `[open PR #N]`, `[in flight <branch>]`, `[verified, uncommitted]`, `[reverted #N]`, or
  `[planned, not started]`. An untagged thread is not done, so tag it.
- **Problems.** At most 5, the recurring ones. Include symptoms users keep reporting and
  any fix that shipped and was reverted, so the next attempt starts where the last failed.
- **Next move.** The single most useful next action, concrete.

An adjacent feature or ticket stays out unless it blocks this one. When the capsule and
thread lines outgrow a screen, cut detail before cutting threads. Write the brief through
the **ryan-voice-guide** skill. Cite session findings by UUID and shared-record findings by source
(PR #, ticket ID, Slack permalink, Sentry issue). Sanitize private context before any
output that leaves the machine.

**Reply:** the brief, to the contract above.
