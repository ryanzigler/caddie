# Reading OpenCode transcripts

Use Python 3.9 or later and the bundled `../scripts/opencode_transcripts.py` helper.
This reader targets OpenCode v2 JSON session exports, not its private database.
Resolve the helper from this reference, not the project being recalled.

## Index first

Choose a private export directory for this recall run. The context supplied by
Caddie's runtime includes the current OpenCode session ID; pass it explicitly.
Run from the requested project:

```bash
python3 "<script>" --project "$PWD" --exports-dir "<private-export-dir>" \
  --exclude-session "<current-session-id>" index --days 7
```

The helper calls `opencode session list --format json` and `opencode session export`
only for candidates whose recorded directory is the requested project or a
descendant. It writes private export files and prints one index row per eligible
top-level session: ID, export path, cwd, title, updated timestamp, prompt count,
and first-prompt preview. It verifies the exported location again before indexing.
User and assistant prose are the only topic-search inputs. Titles are navigation
hints, not evidence of work performed.

Use `--days 0` when all history is requested and `--topic <text>` for a topic.
The default session listing cap is 1000; reaching it fails explicitly. Increase
`--max-sessions` rather than presenting a truncated index as all history.
For a separately running server, supply `--server <url>` before `index` or `digest`.
The CLI uses its configured credentials; never print them.

For exports already obtained by the user, add `--offline` to `index`. A missing
export directory, inaccessible CLI/server, invalid export, or unsupported format
is an access gap. An empty successful index means no matching supported sessions.

## Digest the selected sessions

```bash
python3 "<script>" --project "$PWD" --exports-dir "<private-export-dir>" \
  --exclude-session "<current-session-id>" digest "<path-from-index>" --limit 40
```

Each row has its session/message evidence pointer, timestamp, role, and authored
text. Continue with `--start <next_start>` when a digest reports more messages.
The reader selects `user.text` and assistant `content` blocks with `type: text`.
It omits reasoning, tool inputs/results, synthetic/system messages, injected skills,
compaction, and shell output. User text can still quote generated instructions;
distinguish quoted material from a working preference during synthesis.

Exports must remain within the chosen directory and match the project scope.
Current and child sessions are rejected during digest as well as indexing. A
session moved between projects may contain older out-of-scope messages; the reader
tracks location-switch records and excludes regions outside the requested project.
Cite session and message IDs, then check branches and PRs against live state.
Keep private exports out of shared artifacts and remove only this run's scratch
exports after the digest evidence has been recorded.
