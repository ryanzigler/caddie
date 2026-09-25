---
name: code-review
description: Review a PR, branch, or working diff for correctness and requirement coverage. Use when asked for code review or at the review step of an implementation plan. Use address-review to handle findings already supplied.
---

# Code review

Resolve the requested scope before reviewing. For a working-tree-only request, use
`HEAD` as the committed baseline and include staged, unstaged, and relevant untracked
files; exclude already committed branch changes. For a branch or PR review, honor a
supplied base or derive the PR target/branch merge-base and state the choice. Include
working changes in that review only when requested. Pin base and head commits and
record the selected paths and working-tree state so moving refs cannot silently change
the review. Read untracked files explicitly; they do not appear in `git diff`.

Gather requirements from the user, linked issue/spec, or plan, plus applicable repo
standards. Missing requirements limit the review; report that gap and continue with
correctness checks instead of inventing a spec.

Dispatch the shipped `code-reviewer` agent (use its host-qualified name when required) with the scope, resolved revisions,
requirements and standards paths, and validation results. Give it these artifacts,
not the author's reasoning history. If custom agents are unavailable, use a general
reviewer with [the same brief](../../agents/code-reviewer.md); if delegation is
unavailable, review directly and disclose the lack of an independent reviewer.

The reviewer reports evidence and does not edit files or post comments. Check each
finding against the code, remove duplicates, and separate concrete defects from
optional preferences. For authorized implementation, fix supported findings and
verify the changes; [address-review](../address-review/SKILL.md) supplies the triage
discipline. Keep that triage local unless PR replies were separately requested.
A review-only request ends with findings, not unrequested fixes.

Lead with actionable findings ordered by severity, each with a location, trigger,
impact, and evidence. Then report requirement gaps and verification limits. If no
findings survive scrutiny, say so without claiming the software is defect-free.
