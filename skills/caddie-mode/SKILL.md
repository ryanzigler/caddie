---
name: caddie-mode
description: Apply Caddie's engineering workflow to a task, choosing a playbook and routing to the shipped skills for understanding, implementation, review, and verification.
disable-model-invocation: true
---

# Caddie mode

In Codex, first read [the host adapter](../../references/codex.md).

Use the invocation text as the task. If empty, use the current request; if neither
contains a task, ask for one. Enter this mode for the current conversation until
the user opts out. On later turns, apply it to engineering work and answer simple
questions directly. This is a conversation convention, not a persistent host setting.
Carry the active mode into a handoff when the user wants to resume it.

## Route the task

Read the request, repo instructions, and current state. Choose the narrowest matching
playbook from [references/playbooks.md](references/playbooks.md). Load that playbook
and put its steps in the host's plan or todo list before task-specific steps. For a
small task, keep the checklist inline. Record any skipped step with its reason.
For a mixed task, order the matching playbooks by dependency. For an unmatched task,
write a short bespoke plan with an observable completion criterion for each step.

Read each linked skill when its step applies; its instructions own that step.
Model-invoked skills can be routed automatically. A reference to an explicit-only
skill is a suggestion for the user, unless they separately requested that workflow.
Resume the existing plan on follow-up turns instead of restarting it.

## Work within the request

Proceed through authorized, reversible work and settle repo facts by inspection or
experiments. Ask about product choices or missing access that block dependent work;
continue independent work while waiting. A mode invocation does not authorize
sending messages, publishing, deploying, merging, or destructive cleanup. Honor
specific authorization already given without asking again. For unattended work,
read [autonomous-mode](../autonomous-mode/SKILL.md).

Name the domain and data shape before changing logic. Use
[domain-modeling](../domain-modeling/SKILL.md) when terms or design decisions need
recording, [principle-type-system-discipline](../principle-type-system-discipline/SKILL.md)
for typed contracts, and [typescript-best-practices](../typescript-best-practices/SKILL.md)
when reading or editing TypeScript. Use
[workspace-packages](../workspace-packages/SKILL.md) for package boundaries and
[blast-radius](../blast-radius/SKILL.md) when callers beyond the diff could break.
Keep the smallest change that satisfies the behavior and its verification.

Use [writing-for-agents](../writing-for-agents/SKILL.md) for skill and agent prose.
Use [ryan-voice-guide](../ryan-voice-guide/SKILL.md) for writing under Ryan's name;
a personal mode uses its user's own conventions instead.

## Delegate with the same contract

Delegate only when permitted by the user and host and useful for the scope. Give
independent tasks disjoint write ownership; serialize changes to shared files.
For code-writing or general helpers operating in this mode, use the shipped
[caddie-agent](../../agents/caddie-agent.md). In Claude Code, dispatch its registered
`caddie-agent` role, host-qualified when required. In Codex, use the adapter's
bundled-agent procedure. Add the absolute path to this `SKILL.md` to the brief.
Specialized skills retain their own agent roles, including independent reviewers.

Pass the original goal, later constraints, allowed paths and actions, acceptance
criteria, and verification commands. A child receives only its assigned scope,
not authority to extend the parent's task. Use host defaults unless the user has
chosen available models. Start new tasks and review rounds with fresh agents and
consolidated briefs; reuse a running agent only when its live process or uncommitted
state is needed. Inspect returned artifacts and evidence before accepting the result.
If delegation is unavailable, work inline and disclose the missing independence.

## Finish with evidence

Apply [verification-before-completion](../verification-before-completion/SKILL.md)
to the current artifacts. Report the result, consequential choices, checks actually
run, and remaining gaps. A read-only question ends with a cited answer. A change ends
with a verified diff or the integration the user requested, using
[finishing-a-development-branch](../finishing-a-development-branch/SKILL.md).
