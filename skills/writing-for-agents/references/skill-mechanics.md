# Skill mechanics

The skill-specific branch of [`writing-for-agents`](../SKILL.md): what changes when the document
is a skill — frontmatter, the invocation choice, and router skills. Everything else about
writing it is the universal reference in `SKILL.md`.

## Invocation

The frontmatter flag below is Claude Code's control. For the same explicit-only
behavior in Codex, also add `agents/openai.yaml` inside that skill directory with:

```yaml
policy:
  allow_implicit_invocation: false
```

For a model-invoked skill, omit this policy or set it to `true`. Keep both hosts'
settings in sync. Codex explicit invocation uses `$` or `/skills`; Claude slash
commands keep their existing spelling. OpenCode v2 honors
`disable-model-invocation: true` and exposes explicit skills through `@<skill-id>`.
Caddie's registered OpenCode IDs use `caddie-<name>`; its commands use
`/caddie-<name>`. See [the OpenCode adapter](../../../references/opencode.md).

Two choices, trading the two loads:

- A **model-invoked** skill keeps a `description`, so the agent can fire it autonomously and
  other skills can reach it. You can still type its name: model-invocation always _includes_
  user reach, since a description only ever adds agent discovery and never removes the human's.
  The description is the skill's top-level context pointer, forced to stay loaded at all times —
  permanent context load in exchange for discoverability. A model-invoked skill whose content is
  all reference is also one home for shared reference: another skill can invoke it, so reference
  needed by several skills lives in one place. Mechanics: omit `disable-model-invocation`, and
  write a model-facing description carrying the trigger branches, with the pointer-writing rules
  in `SKILL.md` applying in full.
- A **user-invoked** skill strips the description from the agent's reach: only the human typing
  its name can invoke it, and no other skill can. Zero context load, but it spends cognitive
  load — you are the index that must remember it exists. Mechanics: set
  `disable-model-invocation: true`, and the `description` becomes human-facing, a one-line
  summary with trigger lists stripped.

Pick model-invocation only when the agent must reach the skill on its own, or another skill
must. If it only ever fires by hand, make it user-invoked and pay no context load.

Shared reference that two user-invoked skills both need can live in neither: with no
descriptions, neither can fire the other. Push it to a plain file outside the skill system —
external reference that any skill can point at.

## Splitting by invocation

The invocation cut of splitting; the sequence cut lives in `SKILL.md`. Split off a model-invoked
skill when you have a distinct leading word that should trigger it on its own — a trigger word
you actually use in your prompts — or when another skill must reach it. You pay context load for
the new always-loaded description, so that independent reach has to be worth it.

## Router skills

When user-invoked skills multiply past what you can remember, that piled-up cognitive load is
cured by a **router skill**: one user-invoked skill that names the others and when to reach for
each, so the human has one skill to remember instead of many. It can only hint, never fire them:
user-invoked skills have no description, so nothing but the human can reach them.
