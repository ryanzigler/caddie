# Mining working preferences

Resolve these references relative to the installed plugin, not the user's checkout.
Use the current host's history only, unless the user requests another source.

## Claude Code

Read [the transcript reference](../../recall/references/transcripts.md) for record
shapes and digesting. Restrict discovery to the active project's verified history
directory. Its slug lookup is a candidate locator, not proof of project identity:
verify recorded `cwd` before reading content. Other checkouts or worktrees are in
scope only when requested. This narrower scope takes precedence over the recall
reference's instruction to include every matching repo slug.

Extract actual user text (`type: user`, string `message.content`, not `isMeta`) and
assistant prose for context. Exclude tool output, thinking, injected instructions,
and subagent records. Use timestamps for the requested window or update cutoff;
mtime only helps locate candidate files. Exclude the current session and eval or
throwaway conversations.

## Codex

Read [the Codex transcript reference](../../recall/references/codex-transcripts.md).
Use its bundled reader to index with the explicit project root and requested window,
then digest selected paths. The helper filters recorded `cwd`, injected context,
subagents, and the current thread. Check message timestamps for an update cutoff;
file mtime alone does not prove that every message is new.

## Synthesis

For substantial history, delegate disjoint slices to read-only general agents when
permitted and available. Give each the exact indexed files, scope, cutoff, reader
reference, and return schema: candidate rule, user evidence pointer, repeated
instances, contradictions, and confidence. For a small set or unavailable delegation,
digest inline. Never load whole rollouts into the main context or expand to unrelated
projects to compensate for an empty index.

Compare signals across slices before elevating them. Cite session id and message
number or timestamp for each candidate. Sanitize excerpts before including them in
shared artifacts. Missing history limits the evidence; it does not imply that the
user has no preferences. Direct answers in the interview can supply the missing rules.
