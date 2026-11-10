#!/usr/bin/env bash
# PostToolUse hook on Claude edits and Codex apply_patch.
# Flags mechanically detectable violations of the js-ts-style skill in the
# JS/TS lines the model just added: var, .forEach, index for-loops, CommonJS,
# loose equality, `any`, a control statement whose body sits unbraced on the
# next line, and a return with no blank line after the statement before it.
# String literals and comments are stripped first so prose never trips it.
# Exit 2 feeds the message back to the model.
set -uo pipefail

payload="$(cat)"

# One [file, kind, text] row per line. kind is "+" for an added line, " " for
# patch context (used only as the line before an added one), and "@" for a
# break between hunks or edits.
rows="$(printf '%s' "$payload" | jq -r '
  if .tool_name == "apply_patch" then
    reduce (.tool_input.command // "" | split("\n")[]) as $line ({file: null, out: []};
      if ($line | test("^\\*\\*\\* (Add|Update) File: ")) then .file = ($line | sub("^\\*\\*\\* (Add|Update) File: "; "")) | .out += [[.file, "@", ""]]
      elif ($line | startswith("*** Move to: ")) then .file = ($line | sub("^\\*\\*\\* Move to: "; ""))
      elif ($line | startswith("*** ")) then .file = null
      elif .file == null then .
      elif ($line | startswith("@@")) then .out += [[.file, "@", ""]]
      elif ($line | startswith("+")) then .out += [[.file, "+", $line[1:]]]
      elif ($line | startswith(" ")) then .out += [[.file, " ", $line[1:]]]
      else . end) | .out[]
  else
    (.tool_input.file_path // "") as $file
    | [.tool_input.new_string?, .tool_input.content?, (.tool_input.edits? // [] | .[]?.new_string?)]
    | map(select(. != null))[]
    | ([$file, "@", ""], (split("\n")[] | [$file, "+", .]))
  end | @tsv' 2>/dev/null)"
[ -n "$rows" ] || exit 0

hits="$(printf '%s\n' "$rows" | awk -F '\t' -v q="'" '
  BEGIN { single = q "([^" q "\\\\]|\\\\.)*" q }
  $1 !~ /\.[cm]?[jt]sx?$/ { next }
  $2 == "@" { prev = ""; next }
  {
    file = $1
    line = substr($0, length($1) + length($2) + 3)
    code = line
    if (code ~ /^[[:space:]]*(\/\/|\/\*|\*)/) { prev = "//"; next }
    gsub(single, q q, code)
    gsub(/"([^"\\]|\\.)*"/, "\"\"", code)
    gsub(/`[^`]*`/, "``", code)
    sub(/[[:space:]]*\/\/.*$/, "", code)
    before = prev
    prev = code
    if ($2 != "+") next

    rule = ""
    if (code ~ /(^|[^.[:alnum:]_$])var[[:space:]]+[[:alpha:]_$[{]/) rule = "var: use const, or let when reassigned"
    else if (code ~ /\.forEach\(/) rule = ".forEach: use for...of"
    else if (code ~ /for[[:space:]]*\([[:space:]]*(let|var)[[:space:]]+[[:alpha:]_$][[:alnum:]_$]*[[:space:]]*=[^;]*;/) rule = "index for-loop: use for...of, with .entries() for the index"
    else if (file !~ /\.c[jt]s$/ && code ~ /(^|[^.[:alnum:]_$])require\(|module\.exports|(^|[^.[:alnum:]_$])exports\.[[:alpha:]_$]+[[:space:]]*=/) rule = "CommonJS: use import and export"
    else if (code ~ /^[[:space:]]*(}[[:space:]]*)?((else[[:space:]]+)?if|for([[:space:]]+await)?|while)[[:space:]]*\(.*\)[[:space:]]*$/ || code ~ /^[[:space:]]*(}[[:space:]]*)?else[[:space:]]*$/) rule = "unbraced body on the next line: wrap it in { }, or keep the whole statement on one line"
    else if (code ~ /^[[:space:]]*return([[:space:];(]|$)/ && before ~ /[;}][[:space:]]*$/) rule = "return right after a statement: add a blank line before it"
    else {
      loose = code
      gsub(/[!=]==/, "", loose)
      gsub(/[!=]=[[:space:]]*null([^[:alnum:]_$]|$)/, "", loose)
      gsub(/(^|[^[:alnum:]_$])null[[:space:]]*[!=]=/, "", loose)
      if (loose ~ /[!=]=/) rule = "loose equality: use === or !== (== null is the one exception)"
      else if (file ~ /\.[cm]?tsx?$/ && code ~ /(:|[[:space:]]as|<)[[:space:]]*any([^[:alnum:]_$]|$)/) rule = "any: use unknown and narrow, or the real type"
    }
    if (rule != "") printf "  %s: %s\n    %s\n", file, rule, line
  }' | head -16)"
[ -n "$hits" ] || exit 0

{
  echo "You just added code that breaks the js-ts-style skill:"
  printf '%s\n' "$hits"
  echo "Rewrite those lines to follow the rule shown. If this project's own lint config or language target requires the pattern (an ES5 browser script, for example), keep it and tell the user why."
} >&2
exit 2
