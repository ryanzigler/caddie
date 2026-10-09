#!/usr/bin/env bash
# Installs the third-party plugins Ryan uses in Claude Code and Codex, so every machine
# matches. Caddie itself is enabled by each machine's settings file, and ships the MCP servers
# that have no plugin of their own.
# Safe to re-run. Run `codex login` first: the openai-curated-remote plugins need it.
set -uo pipefail

failed=()
run() {
  echo "+ $*"
  "$@" || failed+=("$*")
}

claude_marketplaces=(anthropics/claude-plugins-official openai/codex-plugin-cc vast-ai/vast-claude-plugin upstash/context7)
claude_plugins=(
  claude-md-management@claude-plugins-official
  commit-commands@claude-plugins-official
  figma@claude-plugins-official
  receipts@claude-plugins-official
  security-guidance@claude-plugins-official
  session-report@claude-plugins-official
  skill-creator@claude-plugins-official
  typescript-lsp@claude-plugins-official
  codex@openai-codex
  vastai@vast-ai
  context7@context7-marketplace
)
codex_marketplaces=(upstash/context7)
codex_plugins=(
  context7@context7-marketplace
  figma@openai-curated-remote
  github@openai-curated-remote
  google-calendar@openai-curated-remote
  google-drive@openai-curated-remote
)

# Desktop-only: these need a local browser or Messages.app.
if [[ "$(uname)" == Darwin ]]; then
  claude_plugins+=(chrome-devtools-mcp@claude-plugins-official imessage@claude-plugins-official)
fi

for marketplace in "${claude_marketplaces[@]}"; do run claude plugin marketplace add "$marketplace"; done
for plugin in "${claude_plugins[@]}"; do run claude plugin install "$plugin"; done

for marketplace in "${codex_marketplaces[@]}"; do run codex plugin marketplace add "$marketplace"; done
for plugin in "${codex_plugins[@]}"; do run codex plugin add "$plugin"; done

if ((${#failed[@]})); then
  printf '\nFailed:\n' >&2
  printf '  %s\n' "${failed[@]}" >&2
  exit 1
fi
echo "Done. Restart Claude Code and Codex to load the changes."
