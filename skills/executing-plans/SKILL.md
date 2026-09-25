---
name: executing-plans
description: Implement an existing plan task by task, preserving requirements and recording verification. Use when asked to execute a plan or continue its implementation.
---

# Executing plans

Read the plan, its requirements, repo instructions, and current working-tree state.
Check completed tasks against actual changes before resuming. Preserve other work;
reuse an existing suitable worktree. Isolation is a tool for conflicting work, not
an automatic prerequisite for every task.

Check shared interfaces and task dependencies before implementation. Execute each
ready task and verify its acceptance criteria before marking it complete. Use
[tdd](../tdd/SKILL.md) for test-first behavior changes and
[diagnosing-bugs](../diagnosing-bugs/SKILL.md) for failures needing diagnosis.
Record completed tasks, commands and outcomes, and material deviations in the plan
or its existing progress record so another session can resume.

Choose the execution mode from the task and the user's preference. Honor an explicit
inline choice. For substantial plans with separable tasks that benefit from fresh
contexts, use [subagent-driven-development](../subagent-driven-development/SKILL.md)
when delegation is available and permitted; it owns implementation and review from
that point. For small, tightly coupled tasks or absent agent tools, continue inline
using this skill. Do not switch back and forth recursively.

Correct routine plan defects within the requested scope and record why. Continue
through authorized tasks without asking to proceed after each one. A missing
credential or unresolved product decision blocks its dependent work; finish other
independent tasks while it is unresolved.

At the end, run [code-review](../code-review/SKILL.md), resolve supported findings,
and apply [verification-before-completion](../verification-before-completion/SKILL.md).
Then use [finishing-a-development-branch](../finishing-a-development-branch/SKILL.md)
for the authorized integration or handoff, reporting completed and blocked requirements,
deviations, and evidence.
