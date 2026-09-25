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
  caddie:unslop)
    redirect "caddie:unslop" "caddie:ryan-voice-guide" \
      "It runs the same AI-tells pass from the same pattern catalog, then applies Ryan's calibrated voice profile, so the result sounds like him rather than like a generic human."
    ;;
  anthropic-skills:humanize-writing)
    redirect "anthropic-skills:humanize-writing" "caddie:ryan-voice-guide" \
      "It strips the same AI tells and then applies Ryan's calibrated voice profile. Humanizing toward a generic human is the wrong target when the text is published as Ryan."
    ;;
  anthropic-skills:cro-metrics-writing)
    redirect "anthropic-skills:cro-metrics-writing" "caddie:ryan-voice-guide" \
      "Its client-facing register owns structure and length as well as wording, learned from Ryan's own client documents, so the house rules are not lost. If the user explicitly asked for cro-metrics-writing by name, say so and ask before proceeding."
    ;;
esac

exit 0
