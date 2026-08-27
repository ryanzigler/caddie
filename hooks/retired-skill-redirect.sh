#!/usr/bin/env bash
# PreToolUse hook on the Skill tool.
# Blocks skills that caddie has retired in favor of one of its own, and tells
# the model which replacement to call instead. The block is a structured deny
# decision on stdout with exit 0, not exit-2 stderr: this is a routing choice,
# and the stderr path renders it to the user as a hook failure.
# Any other skill passes through untouched.
#
# Stock macOS bash is 3.2, which cannot parse a here-document inside $( ), so
# the message is piped into jq rather than captured into a variable first.
set -uo pipefail

# $1 retired skill, $2 exact `skill` argument for the replacement, $3 why it wins.
redirect() {
  cat <<EOF | jq -Rs '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: .}}'
$1 is retired in favour of $2. Nothing has gone wrong: the work still needs a
skill, and $2 is the one that covers it.

Call the Skill tool now with skill: $2

$3

Do not reconstruct $1's process from memory, do not paraphrase its steps, and do
not start investigating without a skill loaded. Its replacement is not the same
process and following the wrong one from memory is the failure this block exists
to prevent. If the replacement turns out to be wrong for this situation, say so
and ask — do not fall back to working unskilled.
EOF
  exit 0
}

payload="$(cat)"
skill="$(printf '%s' "$payload" | jq -r '.tool_input.skill // empty' 2>/dev/null)"

case "$skill" in
  superpowers:systematic-debugging)
    redirect "superpowers:systematic-debugging" "caddie:diagnosing-bugs" \
      "It gates on a real red-capable command that has already been run, minimises the repro, and requires 3-5 ranked falsifiable hypotheses before probing."
    ;;
  superpowers:brainstorming)
    redirect "superpowers:brainstorming" "caddie:grilling" \
      "It asks the whole current frontier of decisions in one round, each with a recommended answer, looks facts up itself instead of asking, and stops for sign-off before any plan or code. Hand the settled design to superpowers:writing-plans afterwards if the work is multi-step."
    ;;
  superpowers:writing-skills)
    redirect "superpowers:writing-skills" "caddie:writing-for-agents" \
      "It covers SKILL.md, CLAUDE.md, and AGENTS.md prose. Use skill-creator:skill-creator instead when you need its scaffolding or eval tooling."
    ;;
esac

exit 0
