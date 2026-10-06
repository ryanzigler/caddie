---
name: handoff
description: Compact this conversation into a handoff document in the repo's docs/handoffs/, so a fresh session can pick the work up after a context reset.
disable-model-invocation: true
---

In Codex, first read [the host adapter](../../references/codex.md).
In OpenCode, first read [the host adapter](../../references/opencode.md).

Write a handoff document summarising the current conversation so a fresh agent can continue the
work.

Save it to `docs/handoffs/<YYYY-MM-DD>-<short-slug>.md` in the current repository, creating
`docs/handoffs/` if it does not exist. Keeping it in the repo means it survives a reboot and
gets reviewed like a plan, alongside `docs/plans/`. Tell the user the path when you are done.

Include:

- **State**: what is done, what is in progress, what is untouched.
- **Next steps**: the immediate next action, stated concretely enough to start on.
- **Landmines**: what was already tried and failed, decisions taken and why, anything
  surprising about this codebase that the next session would otherwise rediscover.
- **Suggested skills**: which skills the next agent should use, and for what. In Claude Code,
  invoke them with the Skill tool; in Codex, use the installed skill loader or read the
  installed `SKILL.md`. In OpenCode, use `skill` for model-invoked workflows
  and `/caddie-<name>` for workflows requiring explicit user invocation.

Write pointers, not copies. Anything already captured in another artifact — a spec, a plan, an
issue, a PR, a commit, a diff — is referenced by path, number, or URL rather than summarised
into the handoff. Duplicated content goes stale against its source, and the next session can
read the original.

Redact sensitive information: API keys, tokens, passwords, connection strings, and personally
identifiable information.

If `$ARGUMENTS` is non-empty, treat it as a description of what the next session will focus on
and tailor the document to that: lead with what that work needs, and compress the rest.
