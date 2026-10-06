---
name: subagent-driven-development
description: Execute a substantial plan using a fresh implementer and independent review for each task. Use when a plan has separable implementation tasks that benefit from isolated context, or when the user asks for delegated implementation. Prefer executing-plans for small or tightly coupled work and when the user selects inline execution.
---
In OpenCode, first read [the host adapter](../../references/opencode.md).


# Subagent-driven development

In Codex, read [the host adapter](../../references/codex.md) for bundled reviewer
and agent dispatch; the Claude agent name is not a registered Codex role.


Coordinate implementation, task review, and final integration review. Keep decisions
and progress in durable files so a resumed session does not repeat completed work.
Use the host's available agent tools and respect its delegation limits. If delegation
is unavailable, use [executing-plans](../executing-plans/SKILL.md) inline and disclose
that independent task implementation was unavailable.

## Prepare

Read the plan, requirement sources, applicable repo instructions, and working-tree
state. Reuse the current suitable workspace. If concurrent work requires isolation,
create a separate worktree through the host or git and record its provenance. Existing
dirty changes belong to their author; never reset or stash them to simplify setup.

Create or reuse a progress record beside the plan, following the repo's convention.
Identify the plan and workspace; record each task's scope, dependencies, status,
implementer identity, verification evidence, review findings, and material decisions.
Inspect actual changes before trusting a completion entry from an earlier session.
If a prior baseline is missing and later edits overlap the task, mark its verification
status uncertain until current changes and checks establish what remains complete.
Do not attribute overlapping edits by guesswork or automatically rerun its implementer.
Keep the record and useful evidence at handoff; do not automatically delete them.

Check shared interfaces and conflicting ownership before dispatch. Batch small edits
of the same kind into one task when they need only one verification/review cycle.
Execute implementers sequentially by default. Parallel implementation is appropriate
only when file ownership and dependencies are disjoint and integration is accounted for.

## Implement and review each task

1. Capture the task's starting revision and working-tree changes. For a dirty tree,
   preserve a task baseline or patch snapshot including relevant untracked content;
   a commit range alone cannot distinguish old edits from the worker's changes.
2. Dispatch a fresh implementer using [references/implementer.md](references/implementer.md).
   Supply the task text or path, requirement source, exact file ownership, shared
   contracts, dependencies, acceptance criteria, and report location. Pass focused
   artifacts rather than the full conversation. Follow host/user model choices.
3. Resolve worker questions from the repo and agreed requirements. Escalate a product
   decision only when it cannot be inferred and affects authorized scope. Continue
   independent work while a dependent task is blocked.
4. Inspect the returned changes and evidence. Dispatch the shipped `code-reviewer`
   (host-qualified where required) with [its brief](../../agents/code-reviewer.md),
   the task requirements, exact task diff, relevant files, and test evidence. Request
   separate verdicts for requirement coverage and implementation correctness. The
   implementer's self-review does not substitute for this independent review.
5. Verify findings before acting. Return supported defects to the implementer, rerun
   affected checks, then obtain a review of the fixes and their immediate effects.
   Record rejected findings with evidence and deferred work with its consequence.
   Unresolved defects that invalidate a dependent task block that task.
6. Mark the task complete only after its acceptance criteria and review are satisfied.
   Record blocked or partial status explicitly. Move to the next ready task without
   asking permission to continue work already authorized.

If a fix cycle repeats the same failure without new evidence, stop dispatching the
same brief. Diagnose the common assumption, revise the task or provide missing context,
and record the decision. Never convert an unresolved correctness defect into a passing
review merely because a retry budget ran out.

## Finish

Review the combined result with [code-review](../code-review/SKILL.md), including the
interactions between tasks and the recorded deferred findings. Fix supported defects
and run [verification-before-completion](../verification-before-completion/SKILL.md).
Then use [finishing-a-development-branch](../finishing-a-development-branch/SKILL.md)
for the authorized integration or handoff. Report completed and blocked requirements,
material decisions, deferred findings, and verification limits.
