# Caddie

Reads the green, hands you the right club.

Personal engineering skills, agents, hooks, and mods for Claude Code, Codex, and OpenCode.

## Installation Options

### OpenCode v2

Install with OpenCode's native plugin manager:

```bash
opencode plugin add github:ryanzigler/caddie
```

OpenCode installs the Git package and adds it to your global configuration. For one
project, add `"github:ryanzigler/caddie"` to the `plugins` array in its
`opencode.json(c)` instead. The package includes the shared skills, references,
agent instructions, and guards; its runtime registers five native subagents.

To test a local checkout, add its absolute root path to that array:

```json
{
  "plugins": ["/PATH/TO/CLONED/REPO"]
}
```

Restart OpenCode or its service after installation. Invoke `/caddie-how <task>`,
`/caddie-caddie-mode <task>`, or any `/caddie-<skill-name>` command. Skills also use
`@caddie-<skill-name>`. The runtime registers all 35 shared workflows; explicit-only
workflows have `autoinvoke: false`, so they remain selectable without appearing in
the model's available skill list.

This integration targets OpenCode v2.0.22. Its [host adapter](references/opencode.md)
translates delegation, tools, and workflow paths. The runtime bridges the shared
git, suppression, and retired-skill guards to v2 tool hooks. The guards require
Bash and `jq`; optional history workflows require Python 3.9+. Installation does
not require Python. The Claude quota-bar UI module stays Claude-only.
OpenCode v1 uses a different plugin API and is not supported by
this entrypoint. See the official [v2 plugin documentation](https://opencode.ai/v2/docs/build/plugins/).

Manage the installed package with OpenCode:

```bash
opencode plugin update github:ryanzigler/caddie
opencode plugin remove github:ryanzigler/caddie
```

Package installations use OpenCode's cache; editing a source checkout does not
refresh an installed Git package. For local development, use the checkout path
above and restart OpenCode after shared source changes.

If you installed an earlier working copy with the Python installer, preserve any
custom edits and remove its `.caddie-install.json`, `caddie/`, `plugins/caddie.js`,
and `agents/caddie-*.md` from that OpenCode config directory before switching.
Keeping both installations would register Caddie twice.

Verify with:

```bash
python3 -m unittest discover -s tests -v
python3 tests/smoke_opencode.py
python3 tests/smoke_opencode.py --invoke
python3 tests/smoke_opencode.py --invoke --guards
```

The smoke test packs the working copy, installs it through `opencode plugin add`
from a disposable Git repository, then starts an isolated server and checks
discovery and explicit invocation policy. `--invoke` also runs the `how` command with an available free model,
checks a completed subagent, and digests the resulting history export. It requires
network access to that model provider. `--guards` also checks actual shell rejection
and suppression feedback through tool calls in disposable sessions.
[History support](skills/recall/references/opencode-transcripts.md)
uses v2 session exports with project, current-session, child-session, and prose filters.

### Codex

From a local checkout, register the repository's existing marketplace and install:

```bash
codex plugin marketplace add /PATH/TO/CLONED/REPO
codex plugin add caddie@caddie
```

Start a new thread after installation. Use `$` or `/skills` to select a skill from
the installed catalog. These commands are verified with Codex CLI 0.154.0.

Codex uses [its own manifest](.codex-plugin/plugin.json), the shared `skills/`, and
the existing Claude-compatible marketplace. For local updates, reinstall with
`codex plugin add caddie@caddie`, then start a new thread. If the installed version
is cached, add a fresh `+codex.<timestamp>` suffix to the Codex manifest version
before reinstalling; keep the base version aligned with the Claude manifests.

Skills that depend on Claude tools follow the [Codex adapter](references/codex.md).
Bundled agents are dispatched with their shared instructions; they are not
automatically registered as Codex agent types. Workflows that need parallel agents
require a host with delegation available. Explicit-only skills carry Codex's
`allow_implicit_invocation: false` policy alongside Claude's frontmatter flag.

On Codex hosts with plugin hooks enabled, review and trust the bundled hooks before
expecting them to run; until then the `SessionStart` user instructions are not
injected either. The shared git and suppression hooks require Bash and `jq`;
Codex transcript recall also requires Python 3. The retired-skill redirect is
Claude-only; Codex follows the adapter's replacement table. See the official
[plugin packaging](https://developers.openai.com/plugins/build/plugins) and
[hook documentation](https://learn.chatgpt.com/docs/hooks) for host requirements.

### Claude Code

The following installation options use Claude Code's marketplace and settings.

### Want it in every project on your machine:

```shell
/plugin marketplace add ryanzigler/caddie
/plugin install caddie@caddie
```

### Want it in one repo, for anyone who clones it. Commit to `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "caddie": {
      "source": {
        "source": "github",
        "repo": "ryanzigler/caddie"
      }
    }
  },
  "enabledPlugins": {
    "caddie@caddie": true
  }
}
```

### Want it in one repo, for only you?. Add it to `.claude/settings.local.json`:

> [!IMPORTANT]
> Ensure `**/.claude/*.local.json` (or similar) is in your `.gitignore`!

```json
{
  "extraKnownMarketplaces": {
    "caddie": {
      "source": {
        "source": "github",
        "repo": "ryanzigler/caddie"
      }
    }
  },
  "enabledPlugins": {
    "caddie@caddie": true
  }
}
```

### Want out of a repo that enables it. Add to `.claude/settings.local.json`:

```json
{
  "enabledPlugins": {
    "caddie@caddie": false
  }
}
```

### Want to work on it locally:

```bash
claude plugin marketplace add /PATH/TO/CLONED/REPO
claude plugin install caddie@caddie
```

#### Then after every edit:

```bash
claude plugin marketplace update caddie
```

## Start with a mode

Use `caddie-mode` for an engineering task. It picks a playbook, routes to Caddie's
existing skills, and carries the work through review and verification. It stays
active within that conversation until you opt out. New conversations need a new
invocation.

In Claude Code, run `/caddie:caddie-mode <task>`. In Codex, select
`$caddie:caddie-mode` or use `/skills`, then supply the task. In OpenCode, run
`/caddie-caddie-mode <task>`.

Use `automate-me` to create your own `<handle>-mode`. It combines project-scoped
history with a short interview, or updates an existing mode from what's changed.
Missing history is fine; the interview can supply the rules. Personal modes default
to explicit invocation and project-local placement: `.claude/skills/` in Claude
Code, `.agents/skills/` in Codex, `.opencode/skills/` in OpenCode. Select
`/caddie:automate-me` in Claude Code, `$caddie:automate-me` / `/skills` in Codex,
or `/caddie-automate-me` in OpenCode.

## Skills

### Modes and personalization

- [`caddie-mode`](skills/caddie-mode/SKILL.md): an explicit engineering entry point with playbooks for investigation, bugs, features, prototypes, skill authoring, review, releases, and unattended work.
- [`automate-me`](skills/automate-me/SKILL.md): creates or updates a user's personal mode from supported preferences, scoped history, and an interview.

### Types and code shape

- [`principle-type-system-discipline`](skills/principle-type-system-discipline/SKILL.md): design types so illegal states can't be represented.
- [`typescript-best-practices`](skills/typescript-best-practices/SKILL.md): the same discipline in concrete TypeScript syntax. Fires on any `.ts`, `.tsx`, or `.mts` edit.
- [`code-simplifier`](skills/code-simplifier/SKILL.md): delegates a scoped cleanup to the shared code-simplifier agent, preserving behavior.
- [`workspace-packages`](skills/workspace-packages/SKILL.md): entrypoints, `exports` maps, tsconfig layout, and dependency classification in a pnpm workspace.
- [`changeset-releases`](skills/changeset-releases/SKILL.md): why a package didn't bump or publish, and what to check before you blame a cache.
- [`cut-release`](skills/cut-release/SKILL.md): drives the release instead: covers every changed package with a changeset, confirms the plan, runs or triggers the release for the repo's mode, and proves the version is on the registry.

### Debugging and impact

- [`diagnosing-bugs`](skills/diagnosing-bugs/SKILL.md): refuses to theorize until one command, already run, goes red. Then minimize, then rank hypotheses.
- [`blast-radius`](skills/blast-radius/SKILL.md): what a change breaks outside its own diff, on a graded evidence ladder.
- [`why`](skills/why/SKILL.md): evidence archaeology across git, tickets, error tracking, and analytics. One investigator per source.
- [`no-comments`](skills/no-comments/SKILL.md): audits lint and type suppressions, then deletes comments that paper over bad code.
- [`address-review`](skills/address-review/SKILL.md): gathers findings from the PR's review threads, a Codex result, or pasted text into one ledger, verifies each against the code, fixes what holds, refutes what doesn't, and replies on the PR.

### Understanding and context

- [`how`](skills/how/SKILL.md): parallel explorers into one explanation. Also answers which package owns a thing.
- [`teach`](skills/teach/SKILL.md): explains until it lands, without the lecture voice.
- [`recall`](skills/recall/SKILL.md): rebuilds working context from prior sessions, live git state, and the shared record.
- [`handoff`](skills/handoff/SKILL.md): writes a handoff document to `docs/handoffs/` before a context reset.
- [`bro`](skills/bro/SKILL.md): restates the last message in plain language.

### Before building

- [`grilling`](skills/grilling/SKILL.md): asks every currently answerable decision at once, each with a recommendation, then waits. Uses different questions for engineering and non-engineering decisions.
- [`grill-with-docs`](skills/grill-with-docs/SKILL.md): engineering interviews that record agreed terminology and consequential decisions as they emerge.
- [`domain-modeling`](skills/domain-modeling/SKILL.md): maintains domain glossaries and ADRs without mixing proposals with accepted decisions.
- [`writing-plans`](skills/writing-plans/SKILL.md): turns settled requirements into tasks with concrete interfaces and verification.
- [`wizard`](skills/wizard/SKILL.md): generates a bash wizard for the steps only a human can do, like entering a secret.
- [`file-issue`](skills/file-issue/SKILL.md): captures a bug or feature you mentioned in passing as a formatted GitHub issue, filed by a background agent so the current work never stops.

### Implementation and review

- [`executing-plans`](skills/executing-plans/SKILL.md): implements a plan, records progress, reviews the changes, and verifies the result.
- [`subagent-driven-development`](skills/subagent-driven-development/SKILL.md): coordinates fresh implementers, task reviews, durable progress, and a final integration review.
- [`finishing-a-development-branch`](skills/finishing-a-development-branch/SKILL.md): carries out authorized integration or leaves a verified handoff, preserving host-managed workspaces.
- [`tdd`](skills/tdd/SKILL.md): tests behavior through public interfaces, one red-green-refactor slice at a time.
- [`code-review`](skills/code-review/SKILL.md): checks correctness and requirement coverage with an independent reviewer.
- [`verification-before-completion`](skills/verification-before-completion/SKILL.md): matches completion claims to current evidence.

### Working unattended

- [`autonomous-mode`](skills/autonomous-mode/SKILL.md): no questions, no unexecuted plans; decisions get made and written down, and the diff gets an adversarial Codex review before the run reports back.

### Proof and prose

- [`create-verification-skill`](skills/create-verification-skill/SKILL.md): builds a project-local skill that drives the real app, and runs it once before handing it over.
- [`writing-for-agents`](skills/writing-for-agents/SKILL.md): how to write a `SKILL.md` or `CLAUDE.md` that behaves the same way every run.
- [`ryan-voice-guide`](skills/ryan-voice-guide/SKILL.md): strips AI-writing tells, then rewrites anything published as Ryan in his own voice, from a profile calibrated against his real writing. Replaces `unslop`, `humanize-writing`, and `cro-metrics-writing`.
- [`calibrate-ryan-voice`](skills/calibrate-ryan-voice/SKILL.md): rebuilds that profile from Claude Code transcripts, pre-2026 GitHub writing, Slack, and Confluence, then proves it with one paragraph per register. Human-triggered.

## Agents

- [`caddie-agent`](agents/caddie-agent.md): runs a scoped delegated task under the shared `caddie-mode` instructions. Specialist workflows keep their own agent roles.

- [`code-reviewer`](agents/code-reviewer.md): reads the requested diff, requirements, and standards; reports concrete defects without editing or posting. Spawned by `code-review`.

- [`comment-sicko`](agents/comment-sicko.md): deletes comments and flags suppressions. Spawned by `no-comments`.
- [`issue-filer`](agents/issue-filer.md): formats a rough report into a real GitHub issue, checks for duplicates, obeys the repo's own templates, and creates it with `gh`. Spawned by `file-issue`.
- [`code-simplifier`](agents/code-simplifier.md): tidies recently written code to house style (arrow functions, named exports, no nested ternaries, `const` everywhere) without changing behavior.

## Hooks

Shipped in [`hooks/hooks.json`](hooks/hooks.json); each guard is a few lines of bash and exits 2 with a message the model reads.

- [`user-instructions.sh`](hooks/user-instructions.sh): on `SessionStart`, prints [`user-instructions.md`](hooks/user-instructions.md) into the session context in both Claude Code and Codex. It is the single source for what used to be `~/.claude/CLAUDE.md`; edit it here.
- [`retired-skill-redirect.sh`](hooks/retired-skill-redirect.sh): redirects retired writing skills (`unslop`, `humanize-writing`, and `cro-metrics-writing`) to `ryan-voice-guide`.
- [`destructive-git-guard.sh`](hooks/destructive-git-guard.sh): blocks `git stash`, `reset --hard`, `checkout --`/`restore`, `clean -f`, force pushes, and `branch -D`. Each one has discarded work in a real session. The user can still run them with the `!` prefix.
- [`suppression-guard.sh`](hooks/suppression-guard.sh): fires after an edit that adds `eslint-disable`, `@ts-ignore`, `@ts-expect-error`, `biome-ignore`, and friends, and sends the model back to fix the cause. `no-comments` is the manual, whole-diff version of the same rule.

Adapted skills carry their upstream `LICENSE` (MIT) next to the `SKILL.md`.

## Third-party plugins

Plugins Caddie does not ship are installed by [`scripts/install-plugins.sh`](scripts/install-plugins.sh), for both Claude Code and Codex. It also adds the user-scope Harvest MCP server, which has no plugin. Re-running it is safe.

```bash
codex login && scripts/install-plugins.sh
```

Codex's curated plugins need `codex login` first. When the Harvest server is first added to Codex, a browser opens to authorize it; Claude Code asks for that through `/mcp` instead. Project-specific plugins, such as Railway, belong in that project's settings, not here.

## Mods

Claude Code function hooks, registered as `modules` in the same [`hooks/hooks.json`](hooks/hooks.json). They draw in the terminal and in Claude Desktop's Code tab. Function hooks are early access: if a mod does not appear, add `"CLAUDE_CODE_ENABLE_FUNCTION_HOOKS": "1"` to the `env` block of `~/.claude/settings.json` and start a new session.

- [`quota-bar`](hooks/quota-bar.tsx): a band above the prompt showing the context window by `/context` category and each plan usage limit with a forecast to its reset. `/quota` toggles it. Its state contract is [`types/index.d.ts`](types/index.d.ts) and its tests are [`tests/quota-bar.test.tsx`](tests/quota-bar.test.tsx), run with `claude plugin test .`.

## Sources and migration

`caddie-mode`, its `caddie-agent` wrapper, and `automate-me` adapt
[Lauren Tan's pstack](https://github.com/cursor/plugins/tree/main/pstack) mode and
personalization workflows. They use Caddie's shipped skills and host adapter in
place of Cursor-specific tools and model defaults. The MIT licenses live beside
the adapted skills.

`grilling`, `grill-with-docs`, `domain-modeling`, `wizard`, and `tdd` are adapted from
[Matt Pocock's skills](https://github.com/mattpocock/skills). `writing-plans`,
`executing-plans`, `subagent-driven-development`, `finishing-a-development-branch`,
and `verification-before-completion` adapt selected workflows from
[Superpowers](https://github.com/obra/superpowers). `code-review` combines ideas from
both. Their licenses live beside the adapted skills.

Caddie does not require Superpowers. The [skill comparison and migration notes](docs/skill-gap-review.md)
map replacements, explain what was retained, and list remaining candidates.

## Compatibility checks

```bash
python3 -m unittest discover -s tests -v
```

The suite checks packaging, explicit invocation policy, both hosts' hook payloads,
and Codex transcript filtering. It does not substitute for invoking a skill in an
installed session or confirming that a host has enabled and trusted the hooks.

With Codex CLI installed, verify installation and discovery through its actual loader:

```bash
python3 tests/smoke_codex.py
```

This uses a temporary `CODEX_HOME`, checks that every Caddie skill is discovered,
and removes the temporary installation. It leaves your normal Codex configuration
and installed plugins untouched and does not make model requests.
