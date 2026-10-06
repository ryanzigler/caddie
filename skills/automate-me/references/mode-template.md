# Personal mode skeleton

Substitute the confirmed handle, purpose, and rules. Omit empty sections and remove
all placeholders before saving. An update preserves the user's existing structure
where possible. This skeleton is not a list of preferences to impose.

```markdown
---
name: <handle>-mode
description: Apply the user's confirmed working conventions to the current task.
disable-model-invocation: true
---

# <Handle> mode

Apply these conventions after explicit invocation for the current conversation,
until the user opts out. Stay within the task's authorization and host instructions.

## Response style

<Confirmed rules for length, tone, format, and audience.>

## Workflow

<Confirmed rules for understanding, decisions, implementation, and delegation.
Link available workflow instructions instead of copying them.>

## Verification and delivery

<Confirmed completion evidence and integration boundaries.>
```

For explicit-only Codex modes, save `agents/openai.yaml` beside the skill:

```yaml
policy:
  allow_implicit_invocation: false
```

OpenCode v2 honors `disable-model-invocation: true` in the native skill directory.
Invoke a personal mode with `@<handle>-mode`; see
[the host adapter](../../../references/opencode.md) for optional command wrappers.

For automatic invocation explicitly requested by the user, replace the generic
example description with specific entry triggers, omit `disable-model-invocation`,
and omit or enable the Codex policy. The mode's rules remain scoped to the task.
