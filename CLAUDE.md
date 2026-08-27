# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A collection of personal Claude Code skills, shipped as a plugin. There is no application code and no build step: the `SKILL.md` files **are** the product. Prose here is a deliverable, not documentation of one, so edit it with the care given to code.

## Layout

Skills are flat directories under `skills/`:

```
skills/<skill-name>/
  SKILL.md          # required
  references/       # optional, loaded on demand
  LICENSE           # required for a skill adapted from another repo
agents/<agent-name>.md
```

`<skill-name>` is kebab-case and must match the `name` in its frontmatter. Skills are
auto-discovered from `skills/` by the plugin loader. There is no index to maintain in
`.claude-plugin/plugin.json`.

Agents live in `agents/` as single files and are also auto-discovered. An agent's
frontmatter `name` is the string a skill passes as `subagent_type`, so it must be
kebab-case and match the filename.

This repo is consumed only as a plugin. There is no symlink or copy step, so a skill is
never live until the plugin is installed and the marketplace is current.

## Adapting a skill from another repo

Most skills here are adapted from [pstack](https://github.com/cursor/plugins/tree/main/pstack)
or [mattpocock/skills](https://github.com/mattpocock/skills). Adapting means more than
copying:

- Rewrite `description` to trigger on how a request is actually phrased, not on the topic.
- Port Cursor-specific tooling: subagent type names, model slugs, cloud execution,
  `~/.cursor` paths, `.mdc` rule files.
- Resolve references to skills this repo does not ship. A pointer to a missing skill is a
  defect, not a to-do. Inline what it carried, or cut it and say so.
- Decide invocability deliberately. Several upstream skills ship
  `disable-model-invocation: true`, which means they never fire on their own. Keep the flag
  only for a genuine human gesture.
- Copy the source repo's `LICENSE` into the skill directory. Attribution goes in `README.md`,
  not in the `SKILL.md` body.

## Writing a SKILL.md

Required frontmatter is exactly `name` and `description`:

```yaml
---
name: skill-name
description: What it does, and when to use it.
---
```

`description` is the only thing the model sees when deciding whether to load a skill. It
must state both what the skill does and the situations that should trigger it, in terms
that match how a request would actually be phrased. A description that only names the
topic will not fire.

Add `disable-model-invocation: true` for skills with side effects that only a human
should trigger (deploys, releases, anything that writes outside the repo), and read
arguments from `$ARGUMENTS`.

Keep `SKILL.md` lean and put depth in `references/`, linked by relative path. The body is
loaded in full whenever the skill fires, so a long one taxes every invocation; a
reference file costs nothing until it is read. Write the body as instructions addressed
to Claude, not as an explanation for a human reader.

## Verifying a change

There are no unit tests. A skill is verified by invoking it: run `/<skill-name>` in a
session where the plugin is installed, and confirm it fires on a realistic request rather
than only on its own name.

Install the working copy as a local marketplace rather than the published repo, so edits
are testable before they are pushed:

```
claude plugin marketplace add /path/to/caddie
```

```
claude plugin install caddie@caddie
```

After editing a skill, run `claude plugin marketplace update caddie` and restart the
session. An edit that is not picked up is usually a stale marketplace, not a broken skill.

After editing either manifest in `.claude-plugin/`, run:

```
claude plugin validate . --strict
```

That validates `marketplace.json`; pass the path explicitly to check the other:

```
claude plugin validate .claude-plugin/plugin.json
```

That one reports a warning about the `CLAUDE.md` at the repo root not being loaded as
plugin context. The warning is expected and correct: this file documents the repo for
anyone working in it and is not shipped as plugin context. Do not pass `--strict` to this
second command, because it promotes that standing warning to a failure.

`claude plugin tag` checks that `plugin.json` and the marketplace entry agree on the
version, which catches the mismatch the section below warns about. Use `--dry-run` for the
check, because the plain form also creates the release tag:

```
claude plugin tag . --dry-run
```

It refuses on a dirty working tree, so run it after committing.

## Keeping things in sync

When a skill or agent is added, renamed, or removed:

- Update the **Skills** list in `README.md`, linking each name to its `SKILL.md`. Agents go
  under **Agents**. An adapted skill needs its upstream link there.
- Bump `version` in **both** `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`.
  They are separate files with separate copies of the version, and a mismatch ships the
  wrong metadata.
