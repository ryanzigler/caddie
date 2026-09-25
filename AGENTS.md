# Working on Caddie in Codex

Caddie ships skills, agent instructions, and command hooks for Claude Code and
Codex. The skill prose is the product. Keep shared instructions in one place and
put host-specific behavior behind an explicit host condition.

Read [references/codex.md](references/codex.md) when following a workflow that uses
Claude tool names, bundled agents, skill invocations, or plugin-relative paths.
That adapter is shipped context; this file is guidance for working on the repo.

## Compatibility

Preserve Claude's `.claude-plugin/` manifests, `agents/` registration, hook events,
and invocation semantics when extending Codex support. Codex packaging lives in
`.codex-plugin/plugin.json` and points at the same `skills/`. Both hosts discover
`hooks/hooks.json`; changes to shared hooks must be tested with both payloads.

Codex does not register the Claude agent Markdown files as agent types. Reuse their
bodies through the host adapter. For each skill with
`disable-model-invocation: true`, keep `agents/openai.yaml` with
`policy.allow_implicit_invocation: false` beside its `SKILL.md`.

## Editing and verification

Use kebab-case skill directories matching frontmatter `name`. Put optional depth
in linked `references/`. Keep upstream licenses beside adapted skills and update
the README skill list when adding or removing a workflow.

Run `python3 -m unittest discover -s tests -v` after compatibility changes. The
suite covers packaging, hook payloads, and transcript reading; skill behavior still
needs a realistic invocation in a fresh session using the installed plugin.

For releases, keep the base version synchronized across both plugin manifests and
the Claude marketplace entry. A local Codex cachebuster may add `+codex.<suffix>`
without changing the Claude version. Follow the README installation instructions
to test a working copy; editing source does not refresh an installed cache.
