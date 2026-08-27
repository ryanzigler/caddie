#!/usr/bin/env bash
# PostToolUse hook on Edit, Write, and MultiEdit.
# Flags lint and type-checker suppressions the model just wrote. Disabling a
# rule is not a fix: it needs an explicit reason and the user's permission, and
# "it's a lot of work" is not a reason. Exit 2 feeds the message back to the
# model so it can remove the suppression and fix the cause instead.
set -uo pipefail

payload="$(cat)"
written="$(printf '%s' "$payload" | jq -r '
  [ .tool_input.new_string?, .tool_input.content?, (.tool_input.edits? // [] | .[]?.new_string?) ]
  | map(select(. != null)) | join("\n")' 2>/dev/null)"
[ -n "$written" ] || exit 0

pattern='eslint-disable|biome-ignore|@ts-ignore|@ts-expect-error|@ts-nocheck|# *type: *ignore|# *noqa|#\[allow\(|oxlint-disable|stylelint-disable|prettier-ignore'
hits="$(printf '%s' "$written" | grep -nE "$pattern" | grep -vE 'prettier-ignore' | head -5)"
[ -n "$hits" ] || exit 0

file="$(printf '%s' "$payload" | jq -r '.tool_input.file_path // "the file"' 2>/dev/null)"
{
  echo "You just added a lint or type suppression to ${file}:"
  printf '%s\n' "$hits" | sed 's/^/  /'
  echo "A suppression is not a fix. Remove it and fix the cause the rule or type error is pointing at. It may stay only when the rule is faulty, pedantic, or purely stylistic, or the third-party type is genuinely wrong, and then only with one line naming the rule and why it is wrong here. If you believe this is one of those cases, say so to the user instead of leaving it silently."
} >&2
exit 2
