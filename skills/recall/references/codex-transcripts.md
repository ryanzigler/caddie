# Reading Codex transcripts

Use Python 3.9 or later and the bundled `../scripts/codex_transcripts.py` helper.
Resolve that path from this reference, not from the project being recalled.
The helper reads local JSONL rollouts under `${CODEX_HOME:-~/.codex}/sessions/`
and `archived_sessions/`. It does not query hosted chats or Claude history.

## Index first

Run from the project being recalled, replacing `<script>` with the helper's absolute
path. Pass the project root explicitly; only sessions whose recorded `cwd` is that
directory or a descendant are included.

```bash
python3 "<script>" --project "$PWD" index --days 7
```

The output is one JSON object per session, newest modification first: session id,
absolute path, cwd, mtime, prompt count, and a first-prompt preview. This preview is
not an authored title. Skip eval and throwaway runs after inspecting it. The current
`CODEX_THREAD_ID` and subagent sessions are excluded automatically; use
`--exclude-session <id>` when the host supplies the current id another way.

Use `--days 0` when the user asks for all history. `--topic <text>` searches user and
assistant prose, not tool output or injected developer instructions. For another
explicitly requested checkout or worktree, run a separate index with its project
path. Do not search unrelated projects to compensate for an empty index.

## Digest the selected sessions

```bash
python3 "<script>" --project "$PWD" digest "<path-from-index>" --limit 40
```

The helper emits user and assistant text from `response_item` message records,
with timestamps and numbered messages. It skips system/developer instructions,
reasoning records, tool calls and tool output, and known injected user-context
records. It does not print an `event_msg` duplicate of the same message. User-role
text can still include other injected context; distinguish that from the user's
own statements when writing the brief.

If output ends with `next_start`, continue with `--start <next_start>` when the
remaining portion is relevant. Do not describe a partial digest as the full session.
Read a specific raw record only when the question requires the exact command or
error omitted by this digest. Never load an entire rollout into the main context.

## Format and access gaps

The local rollout format is an implementation detail, not a stable export API.
The helper expects `session_meta.payload` with `cwd` and `id` (or `session_id`),
and `response_item.payload` messages with a role and text content blocks. These
shapes were checked against local Codex rollouts. Invalid or incomplete JSON lines
produce a warning rather than silently disappearing.

An empty index means no matching supported local sessions. A missing directory or
an unreadable file is an access gap. If a known session produces no messages,
inspect its record keys and report an unsupported format instead of asserting
that nothing happened. Cite session ids in findings, and check branches and PRs
against live state before describing them as current.
