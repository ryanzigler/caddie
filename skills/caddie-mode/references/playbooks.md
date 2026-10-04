# Caddie playbooks

Read the matching section before opening the task checklist. Each linked skill owns
its process; keep its completion gates when composing playbooks.

## Investigation

For how, why, placement, or design-rationale questions. Stay read-only unless the
user requests a change.

1. Pin the question and evidence scope.
2. Use [how](../../how/SKILL.md) for runtime flow or ownership, or
   [why](../../why/SKILL.md) for motivation and history. Use both when needed.
3. Cross-check the answer against source and current state; label inference and gaps.
4. Answer the question with evidence and consequential tradeoffs.

## Bug fix and performance

For defects, failing CI, crashes, and measured regressions.

1. Use [diagnosing-bugs](../../diagnosing-bugs/SKILL.md) to build and run the failing
   feedback loop, minimize it, and test ranked hypotheses before fixing.
2. For performance, pin workload and environment, capture a baseline, and compare
   the same measurement after the change; check that it still does equivalent work.
3. Implement the root-cause fix and regression protection at the real failure seam.
4. Use [code-review](../../code-review/SKILL.md) on the change and resolve findings.
5. Use [verification-before-completion](../../verification-before-completion/SKILL.md)
   on the original symptom and affected behavior, then finish within authorization.

## Feature and refactoring

For new behavior, migrations, or behavior-preserving structural changes.

1. Read affected code and callers. Use [how](../../how/SKILL.md) when flow or ownership
   is unclear; name the behavior, domain shape, and constraints to preserve.
2. Resolve material design choices with [grill-with-docs](../../grill-with-docs/SKILL.md)
   when needed; record accepted decisions with [domain-modeling](../../domain-modeling/SKILL.md).
3. Use [writing-plans](../../writing-plans/SKILL.md) for substantial work. Record
   dependencies, independent work, shared writes, and the smallest useful decomposition.
4. Use [executing-plans](../../executing-plans/SKILL.md) for an existing or newly written
   plan; it owns execution, review, verification, and handoff. For a small inline
   change, implement it, review with [code-review](../../code-review/SKILL.md), and
   apply [verification-before-completion](../../verification-before-completion/SKILL.md).
   Use [tdd](../../tdd/SKILL.md) when test-first work is requested or selected.
5. Finish within the user's authorized outcome; report preserved behavior for a refactor.

## Prototype and visual work

For a sketch to settle a design choice or a UI change that needs visual evidence.

1. State the decision or visible behavior to test and the acceptance criteria.
2. Build the smallest runnable experiment in an isolated, reversible location.
3. Drive the relevant surface with the host's available tools; capture observations
   or screenshots against the specified states and viewport. For parity, compare
   the reference and result under the same conditions.
4. Report the decision and evidence. Promote the experiment through the Feature
   playbook only when production implementation is requested.

## Skill and agent authoring

For creating or editing instructions, including a personal mode.

1. Use [writing-for-agents](../../writing-for-agents/SKILL.md), including its skill
   mechanics reference for invocation policy; identify the decisions the prose changes.
2. Draft shared instructions once, with host behavior behind explicit conditions.
3. Validate frontmatter, local links, licenses, catalog documentation, and both hosts'
   invocation policy. Run the repo's packaging checks when applicable.
4. Exercise realistic requests in a fresh installed session when available; distinguish
   loader checks from behavior checks and report what remains untested.
5. Review against the request and finish within authorization.

## Review and PR follow-up

For reviewing work, handling findings, or getting a PR ready.

1. Pin the PR or diff scope and requested outcome.
2. For a new review, use [code-review](../../code-review/SKILL.md). For supplied
   findings or PR threads, use [address-review](../../address-review/SKILL.md).
3. For authorized fixes, verify the affected behavior and current checks. A review-only
   request ends with findings. Posting replies follows the user's requested scope.
4. If watching was requested, use the host's watcher when available. If integration was
   requested, use [finishing-a-development-branch](../../finishing-a-development-branch/SKILL.md).

## Release

For package versioning and publishing.

1. Use [changeset-releases](../../changeset-releases/SKILL.md) to diagnose release
   state or prepare changeset coverage in a pnpm workspace.
2. For a requested release, use [cut-release](../../cut-release/SKILL.md); it owns
   the release plan, authorization gates, publication, and registry verification.
3. Report the observed version and remaining gaps.

## Unattended and multi-phase work

For sustained work, stepping away, or multiple dependent phases.

1. Use [autonomous-mode](../../autonomous-mode/SKILL.md) when the user grants unattended
   operation; retain that skill's boundaries and decision record.
2. Use [writing-plans](../../writing-plans/SKILL.md) for phases, dependencies, completion
   criteria, and resumable progress. Plan-only requests stop with the plan.
3. For authorized implementation, use [executing-plans](../../executing-plans/SKILL.md)
   and record evidence after each unit. Honor an explicit pause immediately.
4. Leave current state and next steps for resumption. Suggest the explicit-only
   `handoff` or `recall` workflows when the user wants a context transfer or pickup;
   invoke them only when that workflow was requested.
