# Reading Claude Code transcripts

Everything here was verified against real files on this machine. Run the commands; do not
improvise a different shape.

## Where they live

`~/.claude/projects/<slug>/<session-uuid>.jsonl`, one file per session.

Derive `<slug>` from the absolute project path by replacing every `/` with `-`, which
leaves a leading `-`:

```
/Users/ryan/Developer/work/crometrics/libraries  ->  -Users-ryan-Developer-work-crometrics-libraries
```

Two things bite here.

**The leading `-` looks like a CLI flag.** Always address these paths as `./<slug>` or as a
full absolute path. `ls -Users-ryan-...` fails with "unrecognized option".

**The rule is not exact for path segments containing a dot.** Older Claude Code versions
also turned `.` into `-`, newer ones keep it, so worktree paths under `.claude-worktrees/`
exist under both spellings. Never assume the derived slug exists. Derive it, and if the
directory is absent, list and match:

```
ls -1 ~/.claude/projects | grep -i '<repo-basename>'
```

That also catches the same repo checked out at more than one path (this machine has both
`-Users-ryan-Code-work-crometrics-stalker` and `-Users-ryan-Developer-work-crometrics-stalker`).
Include every matching slug for the repo in scope, worktrees included.

Alongside each `<session-uuid>.jsonl` there may be a `<session-uuid>/` directory holding
`subagents/agent-*.jsonl` (with `agent-*.meta.json` giving `agentType`, `description`,
`model`) and `tool-results/*.txt` for offloaded large tool output. Read those only when the
question is specifically what a subagent did.

## Record shape

Every line is one JSON object with a `type`. The types that carry content:

| `type` | What it holds |
|---|---|
| `user` | A turn from the user side. `message.content` is a **string** for a prompt Ryan actually typed, and an **array** when it is carrying `tool_result` blocks. `isMeta: true` marks injected context (expanded slash commands, system reminders), not something he wrote. |
| `assistant` | `message.content` is an array of blocks: `text`, `thinking`, `tool_use`, each with `.type`. A `tool_use` block has `.name` and `.input`. |
| `ai-title` / `custom-title` | A one-line session title. Repeated; take the last. |
| `last-prompt` | `.lastPrompt`, **truncated with a trailing `…`**. Cheap for triage, useless as content. |
| `attachment`, `mode`, `permission-mode`, `atis-latch`, `queue-operation`, `system`, `file-history-snapshot`, `cost-state` | Bookkeeping. Ignore. |

`user` and `assistant` records also carry `cwd`, `gitBranch`, `timestamp`, `sessionId`,
`uuid`, and `parentUuid` — use `gitBranch` and `timestamp` for the thread status tags.

There is no `summary` record and no `isSidechain: true` in current transcripts. Do not
grep for either.

## Triage index

Run this first, in the main thread. It is cheap and gives you the whole project at a
glance: newest sessions, their titles, and how many turns Ryan actually typed.

```
cd ~/.claude/projects && for f in $(ls -t ./<slug>/*.jsonl | head -30); do t=$(jq -rs '[.[]|select(.type=="custom-title" or .type=="ai-title")|(.customTitle // .aiTitle)]|last // "(untitled)"' "$f"); n=$(jq -r 'select(.type=="user" and (.isMeta|not) and (.message.content|type=="string"))|1' "$f" | wc -l | tr -d ' '); echo "$(basename "$f" .jsonl)  $(date -r "$f" '+%Y-%m-%d %H:%M')  prompts=$n  $t"; done
```

Order by file mtime (`ls -t`) or the `timestamp` field, never by UUID — the names are random.

Restrict to a window with `find`:

```
find ~/.claude/projects/<slug> -maxdepth 1 -name '*.jsonl' -mtime -7
```

## Finding the sessions that matter

Grep filenames only, in mtime order, then read only the hits:

```
cd ~/.claude/projects && ls -t ./<slug>/*.jsonl | head -40 | xargs grep -ril '<topic>'
```

Skip the current session's own UUID and any session whose title marks it as an eval or
throwaway.

A common word will match nearly every file, because injected context (`CLAUDE.md`, system
reminders, skill bodies) is stored inline in every session. Verified: grepping `changeset`
across one project matched 22 of 30 sessions. So grep for something specific — a package
name, a symbol, a ticket ID, an error string — and cross-check the hits against the triage
index titles before spending a subagent on any of them.

## Digesting one session

**Never `cat` a `.jsonl` into context.** These files run 300 KB to 1 MB each. Extract a
digest instead — human prompts, assistant prose, and tool calls without their output:

```
jq -r 'if .type=="user" and (.isMeta|not) and (.message.content|type=="string") then "\n=== USER === " + .message.content elif .type=="assistant" then (.message.content[]? | if .type=="text" then "ASSISTANT: " + .text elif .type=="tool_use" then "TOOL " + .name + ": " + ((.input.command // .input.file_path // .input.pattern // .input.description // "") | tostring) else empty end) else empty end' ./<slug>/<uuid>.jsonl
```

Typed slash commands show up inside string content as
`<command-name>/clear</command-name>`, so `/clear` boundaries are visible and mark where
one piece of work stopped and the next began.

Widen from that digest only where the digest itself points — add `thinking` blocks when
you need the reasoning behind a decision, add `tool_result` blocks when the question is
what an error actually said.
