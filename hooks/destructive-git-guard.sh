#!/usr/bin/env bash
# PreToolUse hook on Bash.
# Blocks git commands that discard work the model did not create. A subagent's
# `git stash` once wiped ~190 uncommitted files in a shared worktree, and
# `checkout --`/`reset --hard` have reverted user edits more than once. Exit 2
# blocks and the message reaches the model; the user can still run the command
# themselves with the `!` prefix, or approve it explicitly in the conversation.
set -uo pipefail

payload="$(cat)"
cmd="$(printf '%s' "$payload" | jq -r '.tool_input.command // empty' 2>/dev/null)"
[ -n "$cmd" ] || exit 0

case "$cmd" in
  *"git stash"*)
    echo "Blocked: 'git stash' discards uncommitted work that may not be yours, and in a shared worktree it takes other agents' edits with it. Commit to a WIP branch or use a fresh worktree instead. If the user really wants a stash, ask them to run it with the ! prefix." >&2
    exit 2 ;;
  *"git reset --hard"*|*"git reset --merge"*)
    echo "Blocked: 'git reset --hard' throws away uncommitted changes, including edits the user made outside this session. Show 'git status' and 'git diff --stat' to the user and ask before discarding anything." >&2
    exit 2 ;;
  *"git checkout -- "*|*"git checkout ."*|*"git restore ."*|*"git restore --worktree"*|*"git restore -W"*)
    echo "Blocked: reverting working-tree files discards edits you may not have made. Never revert files you did not edit in this session. Revert one named file only after confirming with the user that the change is yours." >&2
    exit 2 ;;
  *"git clean -f"*|*"git clean -xf"*|*"git clean -fd"*|*"git clean -df"*)
    echo "Blocked: 'git clean' deletes untracked files, which includes work the user has not committed yet. List them first and ask." >&2
    exit 2 ;;
  *"git push --force"*|*"git push -f "*|*"git push -f"|*"git push --force-with-lease"*)
    echo "Blocked: force-pushing rewrites shared history. Ask the user to confirm the branch and remote, then have them run it with the ! prefix." >&2
    exit 2 ;;
  *"git branch -D "*)
    echo "Blocked: 'git branch -D' deletes an unmerged branch and its commits. Use 'git branch -d' (refuses when unmerged) or ask the user." >&2
    exit 2 ;;
esac

exit 0
