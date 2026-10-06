# Running Caddie in OpenCode

Apply this reference only in OpenCode. Claude Code and Codex keep their own
packaging, invocation spelling, and host adapters. The installed Caddie bundle
contains the shared instruction sources; resolve links from those sources.

## Skills and commands

This integration targets OpenCode v2 (verified with 2.0.22). The runtime registers
skills from the shared sources with IDs `caddie-<name>`, for example
`skill({ id: "caddie-how" })`. Translate `caddie:<name>` references to
`caddie-<name>` when using this tool. The registered body includes its absolute
source path; resolve linked references from that source.

Every workflow also has a `/caddie-<name>` command. The runtime submits the shared
body and this adapter into command invocations. `$ARGUMENTS` means the user's
invocation text, supplied as task context; it is not a shell environment variable.
When a workflow invokes another model-invoked skill, load it with `skill`.

The runtime maps `disable-model-invocation: true` to OpenCode's `autoinvoke: false`.
Explicit-only workflows remain available to the user as `@caddie-<name>` or
`/caddie-<name>` but are omitted from the model's available skill list. Invoke
`/caddie-caddie-mode`, `/caddie-recall`, `/caddie-automate-me`, and other explicit
workflows only on the user's request. A command does not grant permission for
unrelated external actions.

Use the available question tool when a workflow needs a user decision, otherwise
ask in conversation and preserve the workflow's wait for the answer.

## Delegation and tools

OpenCode's `subagent` tool dispatches registered subagents. Translate Claude roles:

| Shared role | OpenCode agent |
| --- | --- |
| `Explore` | `explore` |
| `general-purpose` | `general` |
| `caddie-agent` | `caddie-agent` |
| `code-reviewer` | `caddie-code-reviewer` |
| `code-simplifier` | `caddie-code-simplifier` |
| `comment-sicko` | `caddie-comment-sicko` |
| `issue-filer` | `caddie-issue-filer` |

Caddie's runtime registers native agents from the shared bodies, omits Claude-only frontmatter,
supplies the original source path, and leaves model selection to OpenCode. Pass
the task's scope, authorization, write ownership, evidence requirements, and return
contract. For `issue-filer`, supply the absolute bundled
`skills/file-issue/references/templates.md` path. A delegated `caddie-agent` may
read the shared mode body to implement the parent task; this is scoped delegation,
not automatic entry into the user's mode.

Use independent concurrent tool calls where supported. Foreground `subagent`
dispatch returns its result. For independent background work, use `background: true`
and rely on completion notifications rather than polling. Wait for every requested
review before evaluating findings. If host permissions
prevent delegation, use the workflow's stated fallback and disclose the limitation.
For autonomous adversarial review, dispatch a fresh `caddie-code-reviewer` with the
full change scope and steering; do not invoke the Claude Codex review plugin.

`Bash`, `Read`, `Glob`, and `Grep` mean OpenCode's `shell`, `read`, `glob`, and `grep`
tools. `Edit`/`Write` mean `edit`/`write`; patches use `patch`. Translate
arguments to the live schemas rather than copying Claude argument names.
Discover connected MCP tools from the current tool catalog; establish access with
a read-only call. `opencode mcp list` can diagnose configured connections, but
configuration alone is not authenticated access. Do not run `claude mcp list`.

## Creating project skills and personal modes

Use `.opencode/skills/<name>/SKILL.md` for a new model-invoked project skill and
`~/.config/opencode/skills/` (or the configured XDG directory) for personal scope.
Keep the frontmatter name equal to the directory name. User-defined skill names
must be unique across discovery directories; Caddie uses `caddie-<name>` IDs.

For an explicit-only personal mode, write its shared `SKILL.md` in the native
skill directory with `disable-model-invocation: true`. OpenCode v2 honors this
frontmatter flag (or `metadata.opencode/autoinvoke: false`). The user invokes it
with `@<handle>-mode`; optionally add a `.opencode/commands/<handle>-mode.md` command
that reads that source and supplies `$ARGUMENTS` as the task. Omit the flag only when
automatic invocation was requested. Preserve other metadata when changing the flag.

## History

For `recall` and `automate-me`, use the bundled
[OpenCode transcript reference](../skills/recall/references/opencode-transcripts.md).
It indexes exports for the requested project and digests only authored user and
assistant text, excluding the current session, children, synthetic context, tools,
and reasoning. A missing history source is an evidence gap, not an empty history.

## Hooks and host-specific features

The OpenCode runtime calls the shared Bash guards with normalized payloads:
`shell` is checked before execution; `edit`, `write`, and `patch` are checked
afterward. A rejected git command throws before the tool runs. Suppression feedback
is appended to the tool result; it cannot undo the edit. Retired writing skills are
rejected with a direction to load `caddie-ryan-voice-guide`. Hooks cover these built-in tool
paths, not arbitrary custom tools or edits performed through shell commands.

Bash and `jq` must be on PATH. Python 3 is required only for history workflows.
The Claude quota-bar UI module is not loaded in OpenCode. Install and update the
package through `opencode plugin add` and `opencode plugin update`. Local checkout
paths can be configured in `opencode.json(c)` for development. Restart OpenCode or
its service after shared source changes; checkout edits do not refresh installed
Git packages.

Official interfaces: [skills](https://opencode.ai/v2/docs/skills/),
[agents](https://opencode.ai/v2/docs/agents/), [commands](https://opencode.ai/v2/docs/commands/),
and [plugin hooks](https://opencode.ai/v2/docs/plugins/).
