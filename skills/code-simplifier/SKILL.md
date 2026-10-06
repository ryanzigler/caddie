---
name: code-simplifier
description: Simplify recently changed code for clarity and maintainability while preserving behavior. Use when asked to simplify or tidy a diff or to run Caddie's code-simplifier.
---
In OpenCode, first read [the host adapter](../../references/opencode.md).


# Simplify code

Use the files or diff the user names, otherwise the recently changed code in the
current task. Keep unrelated code outside the scope.

In Claude Code, delegate to the existing `code-simplifier` agent with that scope.
In Codex, read [the Codex dispatch instructions](../../references/codex.md), then
dispatch the [shared code-simplifier](../../agents/code-simplifier.md) as specified
there. In OpenCode, dispatch `caddie-code-simplifier` through
[the OpenCode adapter](../../references/opencode.md). Keep its instructions intact,
including its behavior-preservation rule.

Collect the agent's result and report the changes and validation. If delegation
is unavailable, read the shared instructions and perform the simplification
inline, stating that no separate agent ran.
