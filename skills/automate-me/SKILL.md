---
name: automate-me
description: Create or update a personal mode skill from the user's working conventions, project-scoped conversation history, and a short interview.
disable-model-invocation: true
---

# Automate me

In Codex, first read [the host adapter](../../references/codex.md).

Use the invocation text for the requested handle, scope, destination, and create or
update intent. Produce one `<handle>-mode` skill for this user. Use
[writing-for-agents](../writing-for-agents/SKILL.md) and its skill mechanics reference
for authoring. [caddie-mode](../caddie-mode/SKILL.md) is an example of granularity,
not a set of preferences to copy. This workflow does not enter that mode.

## 1. Locate the mode and scope the evidence

Inspect the active project's host-native skill directories for an existing mode.
In Claude Code, use `.claude/skills/`; in Codex, use `.agents/skills/`. Search nested
categories too. Check personal directories for the chosen handle when the user
requests personal scope: `~/.claude/skills/` or `${CODEX_HOME:-~/.codex}/skills/`.
An explicit destination takes precedence. Preserve an existing mode's path and
category. For a new mode, default to the project directory; ask for a handle when
it cannot be inferred. Use kebab-case for the directory and frontmatter name.

When an existing mode is found, update it if that was requested; otherwise ask
whether to update or start fresh. Resolve multiple candidates before editing.
Read the existing rules and preserve those the user has not contradicted. For an
update, use the last edit or commit date as the history cutoff when known; report
an unknown cutoff and use the stated window instead.

State the history scope before reading: active project, current host, last four
weeks by default. A user-specified scope or window takes precedence. History is
optional evidence: if unavailable or declined, continue with current instructions
and the interview. Read [references/history.md](references/history.md) when mining.

## 2. Mine and interview

Collect recurring corrections and explicit preferences about response style,
autonomy, delegation, code shape, verification, and git or review process. Return
an evidence ledger of candidate rules, session/message pointers, confidence, and
contradictions. Assistant behavior alone does not establish a user preference.
Prefer patterns repeated across sessions. A direct user instruction is sufficient;
a single inferred habit needs confirmation. Recent explicit corrections override
older inferred habits; unresolved contradictions become interview questions.

Ask one or two focused questions per round with the host's supported question tool,
otherwise in conversation. Offer concrete choices and recommendations. For a new
mode, ask which candidate rules to keep and what is missing. For an update, ask what
has changed. Include identity or destination questions only while unresolved.
Wait for required answers; optional unanswered questions supply no approval. When
an unattended draft was explicitly requested, write a draft from established rules
and label unresolved choices rather than inventing preferences.

## 3. Draft the user's rules

Use [references/mode-template.md](references/mode-template.md) as a skeleton.
Include only sections with specific, supported rules. Keep operational instructions
short and refer to available skills or project docs instead of repeating their bodies.
For another user's mode, use that user's prose preferences; Ryan's voice profile is
not a generic cleanup step. Keep evidence and confidence in the review summary,
not in every instruction the future agent must load.

Write the file at the resolved destination, preserving unrelated files and existing
rules. Default to `disable-model-invocation: true`. In Codex, also write
`agents/openai.yaml` with `policy.allow_implicit_invocation: false`. If the user
explicitly requests automatic invocation, omit the Claude flag and remove or update
only that Codex policy, preserving other metadata. Describe specific triggers for
that user's mode rather than generic coding keywords. Decide conversation persistence
explicitly; default to active after invocation until opt-out in that conversation.
A new conversation requires invocation again unless the user chose automatic entry.

A personal mode encodes working preferences within the current task's authority.
It cannot grant standing permission for external messages, publishing, destructive
actions, or overriding host instructions. Record any requested permission boundary
accurately and honor session-specific authorization when it exists.

## 4. Validate and hand over

Check directory and frontmatter names match, YAML parses, linked resources exist,
and explicit invocation policies agree. Read the draft back against the evidence:
every rule must come from an explicit instruction, a confirmed candidate, or an
uncontradicted rule in the existing mode. Drop unsupported defaults and duplicates.

Show the path, a concise draft summary, evidence gaps, and invocation instructions:
Claude Code uses `/<handle>-mode`; Codex uses `$<handle>-mode` or `/skills` after
starting a fresh session or refreshing discovery. Ask for feedback on accuracy and
missing conventions; iterate in place. Where available, try a realistic task in a
fresh session and ask whether its behavior matches the user's intent. A loader check
only proves discovery. Finish with the files ready for review; commit or open a PR
only when requested, using
[finishing-a-development-branch](../finishing-a-development-branch/SKILL.md).

For a task-specific skill or one narrow workflow, use the host's skill-authoring
workflow rather than turning it into a personal mode.
