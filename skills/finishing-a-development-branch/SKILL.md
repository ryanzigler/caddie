---
name: finishing-a-development-branch
description: Complete the integration or handoff of an implemented change. Use after a plan is verified, or when asked to finish a branch, open its PR, merge it, or leave the work ready for handoff.
---

# Finishing a development branch

Read the user's requested outcome, current git status, branch or detached HEAD,
upstream, and worktree list. Establish the intended target from the PR, plan, or repo
configuration; resolve ambiguity before merging into a guessed branch.
Apply [verification-before-completion](../verification-before-completion/SKILL.md)
to the current changes. Report failures and unverified requirements honestly; a draft
PR may describe incomplete work, but it must not present it as ready to merge.

Carry out the integration already authorized by the user. Do not ask them to choose
again merely because implementation has finished. When no integration was requested,
leave the changes ready for review and report their location and status. Finishing a
coding task does not by itself authorize committing, pushing, merging, or cleanup.

- **PR requested:** inspect the existing branch/PR state first to avoid duplicates.
  Commit only the intended files, push to the intended remote branch, follow the repo's
  PR template, and verify the returned PR's head and base. A detached HEAD needs a
  named branch; preserve host workspace ownership. Report the PR URL and checks.
- **Merge requested:** verify the exact source and target, preserve unrelated work,
  use the repo's supported merge workflow, and validate the integrated result. A
  rejected push or merge is a reason to inspect the new state, not to force it.
- **Handoff requested or integration unspecified:** retain the branch/worktree and
  progress artifacts. Report what is committed, what remains uncommitted, verification,
  and any unresolved findings.

Keep the worktree for PR iteration. Cleanup requires authorization and verified
provenance; a directory named `worktrees` does not establish who owns it. Preserve
host-managed workspaces by default. Before authorized removal, inspect modified and
untracked files and establish where the work is retained. A refused removal is a
blocker to cleanup, not permission to retry with force. Never discard work as a
side effect of reporting the task complete.
