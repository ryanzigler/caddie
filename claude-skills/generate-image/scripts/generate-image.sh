#!/usr/bin/env bash
# Ask Codex (ChatGPT subscription) to generate one image and copy it to <output>.
#
# Usage: generate-image.sh "<prompt>" <output.png> [--size WxH] [--ref <image>]...
#
# Prints the absolute output path on success. On failure, prints the tail of the
# Codex log to stderr and exits nonzero.

set -euo pipefail

usage='usage: generate-image.sh "<prompt>" <output.png> [--size WxH] [--ref <image>]...'

if [[ $# -lt 2 ]]; then
  echo "$usage" >&2
  exit 2
fi

prompt="$1"
out="$2"
shift 2

size=""
refs=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --size)
      [[ $# -ge 2 ]] || { echo "$usage" >&2; exit 2; }
      size="$2"; shift 2 ;;
    --ref)
      [[ $# -ge 2 && -f "$2" ]] || { echo "generate-image: reference image not found: ${2:-}" >&2; exit 2; }
      refs+=("$2"); shift 2 ;;
    *)
      echo "generate-image: unknown argument: $1" >&2
      echo "$usage" >&2
      exit 2 ;;
  esac
done

if ! command -v codex >/dev/null 2>&1; then
  echo "generate-image: codex CLI not found on PATH. Install it (brew install codex) and run: codex login" >&2
  exit 127
fi

if ! codex login status >/dev/null 2>&1; then
  echo "generate-image: codex is not logged in. Run: codex login" >&2
  exit 1
fi

out_dir="$(cd "$(dirname "$out")" 2>/dev/null && pwd)" || {
  echo "generate-image: output directory does not exist: $(dirname "$out")" >&2
  exit 2
}
out="$out_dir/$(basename "$out")"

# Codex runs in a private empty directory so it cannot touch the caller's
# project, and it never needs the final path: the image tool saves to
# $CODEX_HOME/generated_images/<thread-id>/, and this script does the copy.
workdir="$(mktemp -d "${TMPDIR:-/tmp}/generate-image.XXXXXX")"
log="${workdir}.jsonl"
cleanup() { rm -rf "$workdir" 2>/dev/null || true; }
trap cleanup EXIT

size_line=""
[[ -n "$size" ]] && size_line=$'\nSize: '"$size"
ref_line=""
[[ ${#refs[@]} -gt 0 ]] && ref_line=$'\nThe attached image(s) are references. Follow the prompt about how to use them.'

request="Generate exactly one image with your image_generation tool.

Prompt: ${prompt}${size_line}${ref_line}

Call the image_generation tool once with this prompt. You may tighten the wording, but keep every concrete requirement. Do not write code, run shell commands, or create the image any other way. When the tool returns, reply with the single word: done"

ref_args=()
for ref in "${refs[@]+"${refs[@]}"}"; do
  ref_args+=(--image "$ref")
done

# Low reasoning effort: Codex only has to forward the prompt to the image tool,
# and high effort adds minutes of latency without improving the image.
if ! codex exec --json --skip-git-repo-check -s read-only -C "$workdir" \
  -c model_reasoning_effort='"low"' "${ref_args[@]+"${ref_args[@]}"}" -- "$request" \
  </dev/null >"$log" 2>&1; then
  echo "generate-image: codex exec failed. Last 30 lines of log:" >&2
  tail -n 30 "$log" >&2
  echo "(full log: $log)" >&2
  exit 1
fi

thread_id="$(grep -o '"thread_id":"[^"]*"' "$log" | head -n 1 | cut -d'"' -f4 || true)"
images_dir="${CODEX_HOME:-$HOME/.codex}/generated_images/${thread_id}"

img=""
if [[ -n "$thread_id" && -d "$images_dir" ]]; then
  img="$(ls -t "$images_dir"/*.png 2>/dev/null | head -n 1 || true)"
fi

if [[ -z "$img" || ! -f "$img" ]]; then
  echo "generate-image: codex finished without generating an image. Last 30 lines of log:" >&2
  tail -n 30 "$log" >&2
  echo "(full log: $log)" >&2
  exit 1
fi

cp "$img" "$out"
rm -f "$log" 2>/dev/null || true
echo "$out"
