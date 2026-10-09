#!/usr/bin/env bash
# SessionStart hook.
# Prints Ryan's user-level instructions. Claude Code and Codex both add a
# SessionStart hook's plain stdout to the session context, so this replaces a
# per-machine ~/.claude/CLAUDE.md or ~/.codex/AGENTS.md.
cat "$(dirname "$0")/user-instructions.md"
