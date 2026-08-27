# Caddie

Reads the green, hands you the right club.

Personal [Claude Code skills](https://docs.claude.com/en/docs/claude-code/skills) and agents, packaged as one plugin.

## Installation Options

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

## Skills

### Types and code shape

- [`principle-type-system-discipline`](skills/principle-type-system-discipline/SKILL.md): design types so illegal states can't be represented.
- [`typescript-best-practices`](skills/typescript-best-practices/SKILL.md): the same discipline in concrete TypeScript syntax. Fires on any `.ts`, `.tsx`, or `.mts` edit.
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

- [`grilling`](skills/grilling/SKILL.md): asks every currently answerable decision at once, each with a recommendation, then waits. Replaces `superpowers:brainstorming`.
- [`wizard`](skills/wizard/SKILL.md): generates a bash wizard for the steps only a human can do, like entering a secret.
- [`file-issue`](skills/file-issue/SKILL.md): captures a bug or feature you mentioned in passing as a formatted GitHub issue, filed by a background agent so the current work never stops.

### Working unattended

- [`autonomous-mode`](skills/autonomous-mode/SKILL.md): no questions, no unexecuted plans; decisions get made and written down, and the diff gets an adversarial Codex review before the run reports back.

### Proof and prose

- [`create-verification-skill`](skills/create-verification-skill/SKILL.md): builds a project-local skill that drives the real app, and runs it once before handing it over.
- [`writing-for-agents`](skills/writing-for-agents/SKILL.md): how to write a `SKILL.md` or `CLAUDE.md` that behaves the same way every run. Replaces `superpowers:writing-skills`.
- [`unslop`](skills/unslop/SKILL.md): removes AI-writing tells and restores a specific human voice.

## Agents

- [`comment-sicko`](agents/comment-sicko.md): deletes comments and flags suppressions. Spawned by `no-comments`.
- [`issue-filer`](agents/issue-filer.md): formats a rough report into a real GitHub issue, checks for duplicates, obeys the repo's own templates, and creates it with `gh`. Spawned by `file-issue`.
- [`code-simplifier`](agents/code-simplifier.md): tidies recently written code to house style (arrow functions, named exports, no nested ternaries, `const` everywhere) without changing behavior.

## Hooks

Shipped in [`hooks/hooks.json`](hooks/hooks.json); each script is a few lines of bash and exits 2 with a message the model reads.

- [`retired-skill-redirect.sh`](hooks/retired-skill-redirect.sh): blocks `superpowers:systematic-debugging`, `superpowers:brainstorming`, and `superpowers:writing-skills`, naming the caddie skill that replaced each. Pair it with a `permissions.deny` entry for the same skills so the block holds even if the hook is skipped.
- [`destructive-git-guard.sh`](hooks/destructive-git-guard.sh): blocks `git stash`, `reset --hard`, `checkout --`/`restore`, `clean -f`, force pushes, and `branch -D`. Each one has discarded work in a real session. The user can still run them with the `!` prefix.
- [`suppression-guard.sh`](hooks/suppression-guard.sh): fires after an edit that adds `eslint-disable`, `@ts-ignore`, `@ts-expect-error`, `biome-ignore`, and friends, and sends the model back to fix the cause. `no-comments` is the manual, whole-diff version of the same rule.

Adapted skills carry their upstream `LICENSE` (MIT) next to the `SKILL.md`.
