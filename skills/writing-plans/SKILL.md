---
name: writing-plans
description: Turn settled requirements into an implementation plan with bounded tasks and concrete verification. Use when asked to plan implementation or when substantial authorized work needs a durable execution plan.
---

# Writing plans

Read the requirements and the relevant code before decomposing work. Resolve facts
from the repo; ask only about decisions that materially affect scope or behavior.
If the user wants an interview, use [grilling](../grilling/SKILL.md), or
[grill-with-docs](../grill-with-docs/SKILL.md) when terminology and ADRs matter.

Use the repo's plan location, otherwise `docs/plans/YYYY-MM-DD-topic.md`. A small
change may need only an inline plan; avoid a document longer than the work warrants.

Record the goal, requirement source, constraints, and chosen approach. Divide work
into tasks that each deliver observable behavior. For each task identify:

- Files and responsibilities, checked against the real tree.
- Inputs, outputs, and interfaces shared with other tasks.
- Dependencies and acceptance criteria, including relevant failure cases.
- Verification commands and the result that would demonstrate success. Label commands
  or paths that remain unverified; expected output is not an observed result.

Specify decisions an implementer cannot infer, not entire function bodies. Put shared
constraints in one place. Include migrations, compatibility, and rollback only where
the change needs them. Check every requirement maps to a task, interfaces agree across
tasks, and verification exercises the behavior being promised.

For a plan-only request, deliver the plan and stop. If implementation is already
authorized, continue with [executing-plans](../executing-plans/SKILL.md). Ask for a
new decision only when the plan reveals a material choice outside that authorization.
