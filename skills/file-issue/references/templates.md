# Fallback issue templates

Used only when the target repo has no `.github/ISSUE_TEMPLATE/`. A repo that ships its own
templates always wins; these exist so an issue never lands shapeless.

Fill each placeholder and delete the angle-bracket guidance. **Delete any section you cannot
fill honestly** — an empty heading is worse than no heading, because it reads as investigated
and empty rather than never checked. `Open questions` is the one section that always stays.

---

## Bug

```markdown
## What happens

<The observed behavior, in one or two sentences. The reporter's words, not a paraphrase
that smooths off the specifics.>

## What should happen instead

<If the reporter said. If they did not, state the expectation the code itself implies and
mark it as your inference.>

## Steps to reproduce

<Numbered steps, only if they were actually observed. If they were not — and from a passing
report they usually were not — delete this heading entirely and use the one below.>

## Not yet reproduced

<What the reporter was doing when they noticed it. Say plainly that nobody has yet confirmed
a reliable sequence.>

## Error output

<Stack trace, failing test output, or log line, verbatim and uncut, in a fenced block.
Delete this section if there is none. Never paraphrase an error string — the string is the
part people search for.>

## Where it likely lives

- `path/to/file.ts:42` — <what this code does and why it is implicated>

<Only files actually opened. A citation nobody read is worse than no citation. Delete the
section if the look-around found nothing.>

## Environment

- Branch: `<branch>` at `<short sha>`
- Version: `<package version, if there is one>`

## Open questions

- [ ] <What a maintainer would need answered before starting.>
```

---

## Feature

```markdown
## The problem

<The situation that prompted this — what is awkward, slow, or impossible today. Not the
proposed solution restated as a need. If the reporter only gave a solution, say so and
describe the problem it implies, marked as your inference.>

## Proposed behavior

<What it should do, from the outside. Behavior, not implementation, unless the reporter
specified an implementation.>

## Where it would live

- `path/to/file.ts` — <why this is the seam>

<Delete if the look-around found nothing.>

## Alternatives considered

<Only if the reporter named one, or if an existing mechanism already does most of this.
Delete otherwise — an invented list of rejected alternatives is noise.>

## Open questions

- [ ] <What has to be decided before this can be built.>
```

---

## Chore

```markdown
## What needs doing

<The concrete change. Cleanup, dependency bump, tooling, or config.>

## Why now

<What makes it worth doing. "Tidiness" is a real answer; say it rather than inventing
urgency.>

## Scope

- <files or packages affected>

## Open questions

- [ ] <Anything that would change the approach.>
```

---

## Footer

Append this to every issue built from a fallback template, so a reader knows the `Open
questions` are real rather than decorative:

```markdown
---
<sub>Captured from a passing report and filed automatically. Details above marked
unverified have not been confirmed.</sub>
```
