#!/usr/bin/env bash
# PreToolUse hook on the Skill tool.
# Blocks skills that caddie has retired in favor of one of its own, and tells
# the model which replacement to call instead. Exit 2 blocks; stderr reaches
# the model. Any other skill passes through untouched.
set -uo pipefail

payload="$(cat)"
skill="$(printf '%s' "$payload" | jq -r '.tool_input.skill // empty' 2>/dev/null)"

case "$skill" in
  superpowers:systematic-debugging)
    echo "superpowers:systematic-debugging is retired. Use the 'diagnosing-bugs' skill instead: it gates on a real red-capable command that has already been run, minimises the repro, and requires 3-5 ranked falsifiable hypotheses before probing." >&2
    exit 2
    ;;
  superpowers:brainstorming)
    echo "superpowers:brainstorming is retired. Use the 'grilling' skill instead: it asks the whole current frontier of decisions in one round, each with a recommended answer, looks facts up itself instead of asking, and stops for sign-off before any plan or code. Hand the settled design to superpowers:writing-plans afterwards if the work is multi-step." >&2
    exit 2
    ;;
  superpowers:writing-skills)
    echo "superpowers:writing-skills is retired. Use the 'writing-for-agents' skill instead for SKILL.md, CLAUDE.md, and AGENTS.md prose; use 'skill-creator' only when you need its scaffolding or eval tooling." >&2
    exit 2
    ;;
esac

exit 0
