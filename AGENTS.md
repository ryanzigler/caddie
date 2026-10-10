# Working on Caddie

Caddie ships skills, agents, hooks, mods, and MCP server configs for Claude Code,
Codex, and OpenCode as one plugin. There is no application code and no build step: the
`SKILL.md` files **are** the product. Prose here is a deliverable, not documentation of
one, so edit it with the care given to code.

This file is the single source of guidance for working on the repo in any host;
`CLAUDE.md` imports it. Keep shared rules here, and label anything host-specific with
its host.

## Layout

```
skills/<skill-name>/          # shared by every host
  SKILL.md                    # required
  references/                 # optional, loaded on demand
  agents/openai.yaml          # Codex invocation policy, when needed
  LICENSE                     # required for a skill adapted from another repo
claude-skills/<skill-name>/   # Claude Code only
agents/<agent-name>.md
hooks/hooks.json              # Claude hooks and mods
hooks/codex-hooks.json        # the same hooks without the `modules` key
hooks/<hook-name>.sh
hooks/<mod-name>.tsx          # Claude Code mod, typed by types/index.d.ts
.mcp.json, .codex-mcp.json    # MCP servers for Claude Code and Codex
opencode/                     # OpenCode runtime, the package.json entrypoint
references/codex.md           # Codex host adapter, shipped context
references/opencode.md        # OpenCode host adapter, shipped context
tests/
```

`<skill-name>` is kebab-case and matches the `name` in its frontmatter. Every host
auto-discovers skills from `skills/`; there is no index to maintain.

A skill that only makes sense in Claude Code goes in `claude-skills/` instead. The
Claude manifest's `skills` key adds that directory to the default `skills/` scan. The
Codex manifest and the OpenCode runtime read only `skills/`, and `package.json` leaves
`claude-skills/` out of its `files`, so no other host sees it. `generate-image` lives
there because Codex models generate images natively.

Agents live in `agents/` as single files. In Claude Code an agent's frontmatter `name`
is the string a skill passes as `subagent_type`, so it is kebab-case and matches the
filename. Codex does not register these files as agent types; skills reach them through
the host adapter, which passes the agent body to a general agent. OpenCode registers
them as native agents at runtime.

Hooks are bash scripts that read the tool payload from stdin with `jq`, exit 0 to pass,
and exit 2 with a stderr message to block. Claude reads `hooks/hooks.json`; Codex reads
`hooks/codex-hooks.json`, which must be the same hooks without the Claude-only `modules`
key that Codex rejects. Edit both together; a test enforces it. Test a shared hook with
both payload shapes: Codex reports shell calls as `Bash` and patches as `apply_patch`.
Test one by piping a payload into it:
`printf '%s' '{"tool_input":{"command":"git stash"}}' | hooks/destructive-git-guard.sh`.
Use `printf`, not `echo`: zsh's `echo` turns `\n` into a real newline and the JSON stops
parsing. `retired-skill-redirect.sh` and the `.tsx` mods are Claude-only. OpenCode
translates tool payloads in its own runtime; keep that separate from the Claude and
Codex hooks.

`hooks/user-instructions.md` holds Ryan's user-level instructions, printed into every
Claude Code and Codex session by a `SessionStart` hook. Edit it there, not in a
per-machine `~/.claude/CLAUDE.md` or `~/.codex/AGENTS.md`.

Caddie ships only MCP servers that no plugin provides. Every server in `.mcp.json` must
also appear in `.codex-mcp.json`; a test enforces it. Third-party plugins are installed
by `scripts/install-plugins.sh`, not copied into this repo.

## Host compatibility

Keep shared instructions in one place and put host-specific behavior behind an explicit
host condition. Shared skills that use Claude tool names, bundled agents, skill
invocations, or plugin-relative paths open with a pointer to
[references/codex.md](references/codex.md), which translates them for Codex. Read
[references/opencode.md](references/opencode.md) before changing OpenCode behavior.

Preserve Claude's `.claude-plugin/` manifests, `agents/` registration, hook events, and
invocation semantics when extending another host. Codex packaging lives in
`.codex-plugin/plugin.json` and points at the same `skills/`. OpenCode v2 loads the root
`package.json` entrypoint, `opencode/plugin.js`, which registers the same skills with
prefixed IDs and maps `disable-model-invocation` to `autoinvoke: false`.

## Writing a SKILL.md

Frontmatter requires `name` and `description`. `description` is the only thing the model
sees when deciding whether to load a skill. State both what the skill does and the
situations that should trigger it, in the words a request would actually use. A
description that only names the topic will not fire.

Add `disable-model-invocation: true` for skills with side effects that only a human
should trigger (deploys, releases, anything that writes outside the repo), and read
arguments from `$ARGUMENTS`. Every such skill in `skills/` also needs
`agents/openai.yaml` with `policy.allow_implicit_invocation: false`, the Codex
equivalent; the test suite enforces the pair.

Keep `SKILL.md` lean and put depth in `references/`, linked by relative path. The body
loads in full whenever the skill fires, so a long one taxes every invocation; a
reference file costs nothing until it is read. Write the body as instructions addressed
to the agent, not as an explanation for a human reader.

## Adapting a skill from another repo

Most skills here are adapted from [pstack](https://github.com/cursor/plugins/tree/main/pstack)
or [mattpocock/skills](https://github.com/mattpocock/skills). Adapting means rewriting,
not copying. A third-party skill wanted as-is comes from its own plugin through
`scripts/install-plugins.sh`; it is never vendored here. When adapting:

- Rewrite `description` to trigger on how a request is actually phrased, not on the topic.
- Port Cursor-specific tooling: subagent type names, model slugs, cloud execution,
  `~/.cursor` paths, `.mdc` rule files.
- Resolve references to skills this repo does not ship. A pointer to a missing skill is a
  defect, not a to-do. Inline what it carried, or cut it and say so.
- Decide invocability deliberately. Several upstream skills ship
  `disable-model-invocation: true`, which means they never fire on their own. Keep the flag
  only for a genuine human gesture.
- Copy the source repo's `LICENSE` into the skill directory. Attribution goes in
  `README.md`, not in the `SKILL.md` body.

## Verifying a change

Run the compatibility suite after any packaging, hook, or skill-layout change:

```
python3 -m unittest discover -s tests -v
```

It covers manifest and version agreement, invocation policies, the Claude-only split,
hook and MCP config parity, hook payloads from both hosts, the OpenCode runtime, and
transcript reading. The remaining checks need a host CLI:

- **Codex discovery**: `python3 tests/smoke_codex.py` installs the working copy into a
  temporary `CODEX_HOME` and confirms every shared skill is discovered.
- **OpenCode discovery**: `python3 tests/smoke_opencode.py` packs and installs the
  working copy into an isolated server. `--invoke` also runs a skill against an available
  free model and needs network access; `--guards` adds real hook rejections.
- **Claude manifests**: `claude plugin validate .` after editing anything in
  `.claude-plugin/`. It always reports one warning, that the root `CLAUDE.md` is not
  loaded as plugin context. That is correct, since the file is for working on the repo.
  Any other warning is real. `--strict` turns the standing warning into a failure, so
  read the output instead of relying on the exit code.
- **Claude mods**: `claude plugin test .` runs the `.tsx` mod tests.
- **Release versions**: `claude plugin tag . --dry-run` checks that `plugin.json` and the
  marketplace entry agree. The plain form also creates the release tag, and it refuses
  on a dirty tree, so run it after committing.

None of this proves a skill works. Verify that by invoking it in a fresh session with
the plugin installed from the working copy, and confirm it fires on a realistic request
rather than only on its own name. The README's installation section has the local
install commands for each host. Editing source does not refresh an installed copy: in
Claude Code, run `claude plugin marketplace update caddie` and restart the session; in
Codex, reinstall with `codex plugin add caddie@caddie` and start a new thread. An edit
that does not show up is usually a stale install, not a broken skill.

## Keeping things in sync

When a skill, agent, hook, mod, or MCP server is added, renamed, or removed:

- Update `README.md`, linking each name to its file under its section. An adapted skill
  needs its upstream link there.
- Bump `version` in all four places: `.claude-plugin/plugin.json`,
  `.claude-plugin/marketplace.json`, `.codex-plugin/plugin.json`, and `package.json`.
  The Codex version may add a local `+codex.<suffix>` cachebuster, but its base must
  match the others.
