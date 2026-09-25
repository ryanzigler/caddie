---
name: no-comments
description: Audit a diff for lint and type-checker suppressions and for comments that paper over bad code, then delete what fails the audit and fix the cause the comment was hiding. Run manually with /no-comments.
disable-model-invocation: true
---

In Codex, first read [the host adapter](../../references/codex.md).

# No comments

A suppression comment and an explanatory comment are usually the same bug wearing different clothes: the code is not obvious, or it is not correct, and prose was cheaper than fixing it. Delete the prose, fix the code.

You wrote most of the comments in this diff, so you will defend them. Defer to the `comment-sicko` subagent's fresh read.

## Scope

`$ARGUMENTS`, if it names files or a diff. Otherwise the current diff against the base branch (default `main`), including the working tree. Never touch anything outside that scope.

## 1. Run the audit

In Claude Code, spawn a subagent with `subagent_type: "comment-sicko"` and pass it the scope. Do not restate its rules. In Codex, use the host adapter to supply the shared agent body and scope to a fresh subagent. It reports deletions, `MUST KILL` flags on the exact symbols that need reshaping, and skips.

## 2. Audit the suppressions first

This is the highest-value half of the pass, so do it before you look at ordinary comments.

Independently sweep the scope for every scoped suppression: `eslint-disable`, `eslint-disable-next-line`, `biome-ignore`, `@ts-ignore`, `@ts-expect-error`, `@ts-nocheck`, and their equivalents. Do not rely on `comment-sicko` having found them all.

For each one, look up the actual rule or read the actual type error. Then:

- **A suppression over a rule that catches real bugs, or that protects correctness, safety, or types, is a `MUST KILL`.** Delete the suppression, let the error surface, and fix the cause. Standing rule in this repo and in the user's global config: disabling a rule is never a fix. It requires explicit permission and a valid reason, and "it's a lot of work" is not a valid reason. If you cannot fix the cause inside the scope, leave the suppression, report it open, and say which rule and which cause.
- **A suppression over a faulty, pedantic, or purely stylistic rule may stay,** with one line naming the rule and why it's wrong here.
- **`@ts-expect-error` on a genuinely wrong third-party type may stay,** with the upstream issue link if one exists.
- **`// prettier-ignore` and formatter pragmas stay.** They are not correctness suppressions.

A long justification above a suppression is a confession, not a defense. Read it, then judge the rule.

## 3. Review the comment deletions

Inspect `comment-sicko`'s report and diff. Reject: edits to application code, anything outside the scope, deletions of exception-protected comments, misstated `MUST KILL` reasons, and flags that treat deliberate, correct code as guilty. Reshape flags on surprises in our own code stay actionable.

Do not restore comments you merely feel attached to. A keep survives only with proof it describes something we cannot change: a legal or license header, behavior forced by an external dependency, platform, vendor, or protocol; a doc comment defining a public API contract; or an issue or RFC link recording a constraint the code cannot express.

Before accepting a thin `IMPORTANT` or `do not remove` kill or keep, run `how` or `why` on the symbol it names. If a kill is ambiguous, do not restore it. If a keep is refuted or still ambiguous, delete it.

If the report is unusable, revert it and rerun once with the failure named. If the second run also fails, report it open and stop; the pass has failed.

## 4. Fix the cause, not the comment

Fix trivial accepted flags directly: delete the dead path, drop the unused parameter, call the real API. Then implement the smallest root-cause fix that removes each named workaround.

Fix the real cause and redesign as though the requirement had always existed, rather than bolting a guard onto the symptom. That is a statement of intent, not a license to widen the scope. If the root cause is outside the scope, land the smallest in-scope fix and report the rest open.

If a fix needs a design rather than a deletion, stop and sketch the shape in your report before implementing it. Don't invent an architecture inline in the middle of a deletion pass.

## 5. Constraint comments

Constraint comments say `do not remove`, `do not change wording`, or `talk to X before changing`. Leave keeps that are about something we cannot change. For the rest, offer the cheapest in-scope encoding that makes the constraint enforceable: a type, a runtime assertion, a test, or a CI check. Wait for approval; unattended runs need it pre-approved. If approved, encode it, then delete the comment. Otherwise delete the comment, report the constraint open, and sketch the out-of-scope work.

## 6. Report

Deletion count. Suppressions killed and suppressions left standing, each with its rule. Comments restored and why. Reruns. Design sketches. Fixes landed. Encoding offers and encodings. Unenforced constraints. Anything still open.
