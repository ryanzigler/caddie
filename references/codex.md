# Running Caddie in Codex

This reference applies only in Codex. Claude Code keeps its existing tool calls,
agent registration, slash commands, and plugin paths.

## Inputs and skill calls

Where a skill says `$ARGUMENTS`, use the text supplied with its invocation, then
the conversation fallback that skill defines. `$ARGUMENTS` is Claude's substitution,
not a shell variable to read in Codex.

When a step calls another skill, load its installed `SKILL.md` using the available
skill loader or file reader and follow it. Use the installed catalog's name and
path; do not call an imaginary `Skill` tool or guess a plugin cache version.
Explicit invocation in Codex CLI uses `$` or `/skills`.

When a workflow needs a user decision, use the host's available question tool in
the modes where it is supported, otherwise ask in conversation. Preserve the
workflow's wait for the answer; a tool being unavailable does not supply an answer.

These Caddie workflows replace the corresponding retired workflows:

| Retired skill | Caddie replacement |
| --- | --- |
| `superpowers:systematic-debugging` | `caddie:diagnosing-bugs` |
| `superpowers:brainstorming` | `caddie:grilling` |
| `superpowers:writing-skills` | `caddie:writing-for-agents` |
| `caddie:unslop` | `caddie:ryan-voice-guide` |
| `anthropic-skills:humanize-writing` | `caddie:ryan-voice-guide` |
| `anthropic-skills:cro-metrics-writing` | `caddie:ryan-voice-guide` |

Use the replacement's actual instructions when one of these workflows is needed.
The Claude `Skill` hook does not enforce this routing in Codex.

## Subagents

Use the host's available spawn tool. Claude's `subagent_type` values below are
roles to translate, not Codex tool arguments:

| Claude role | Codex dispatch |
| --- | --- |
| `Explore` | An available explorer agent, otherwise a general agent instructed to read only. |
| `general-purpose` | An available general agent with the task's required tools. |
| `comment-sicko` | Read [the shared agent](../agents/comment-sicko.md), then pass its full Markdown body and the scoped task to a general agent. |
| `issue-filer` | Read [the shared agent](../agents/issue-filer.md), then pass its full Markdown body and the context packet to a general agent. |
| `code-simplifier` | Read [the shared agent](../agents/code-simplifier.md), then pass its full Markdown body and the scoped task to a general agent. |

For bundled agents, strip only YAML frontmatter; preserve the complete instructions.
Pass the absolute agent-file path so the child can resolve links relative to it.
For `issue-filer`, also pass the absolute path to
[fallback templates](../skills/file-issue/references/templates.md).
Do not assume an unrelated registered agent with the same name implements Caddie's
instructions. Claude model aliases such as `opus` stay in Claude frontmatter;
Codex uses the current host's model defaults unless the user requests a model.

Carry the same scope, write restrictions, evidence requirements, and return contract
into each child. Pass this reference when a child receives instructions containing
Claude tool names. `Bash` means the shell tool; `Glob`, `Grep`, and `Read` mean
file discovery, content search, and file reading using the available tools.

Launch independent tasks concurrently up to the host's available capacity. If the
skill needs more investigators, run the remaining ones as slots free up, then
synthesize all findings. Do not drop evidence categories to fit a concurrency cap.
Use the host's completion notifications and wait tools where the skill requires
collecting results. If delegation is unavailable, report that limitation; do not
describe an inline pass as an independent review or a background task.

## Paths and connected tools

Resolve bundled references from the installed skill or agent file, not the user's
working directory. From the directory containing `SKILL.md`, the plugin root is `../..`;
from the directory containing an agent Markdown file, it is `..`. Hook compatibility environment variables
are not guaranteed to exist in ordinary shell calls or child agents.

Discover connected services through the current host's tool catalog and tool search
when available. A configured MCP server is not proof of authenticated access.
Use a read-only request to establish access; report absent or unauthenticated
sources as gaps. Do not run `claude mcp list` to discover Codex connections.

## Hooks

Codex loads the shared `hooks/hooks.json` on hosts with plugin hooks enabled and
trusted. It reports shell and unified-exec calls as `Bash`, with the command in
`tool_input.command`. Patch calls report `apply_patch` with the patch in that same
field and also match `Edit` and `Write`. The existing matchers therefore reach the
git guard and suppression guard without a separate Codex hook configuration.

The git guard runs before execution. The suppression guard runs after execution
and asks for a correction; it cannot undo the edit. The retired-skill redirect
requires Claude's `Skill` tool, so use the routing table above in Codex. Hooks do
not cover every possible tool path or edits made through shell commands.

Codex provides `CLAUDE_PLUGIN_ROOT` for these shared hook commands. This guarantee
is scoped to hooks, not ordinary shell calls. See the official
[plugin packaging](https://developers.openai.com/plugins/build/plugins) and
[hook runtime](https://learn.chatgpt.com/docs/hooks) documentation.
