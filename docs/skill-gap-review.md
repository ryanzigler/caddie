# Skill comparison and Superpowers migration

Reviewed September 25, 2026 against:

- [mattpocock/skills at c55ee46](https://github.com/mattpocock/skills/tree/c55ee46073ed923f86ce59a5eb3b6d895095d1b7), its active engineering and productivity catalog. Miscellaneous, deprecated, and in-progress experiments are outside this recommendation set.
- [obra/superpowers at 8ca22db](https://github.com/obra/superpowers/tree/8ca22dba9a94f28898bbce59f2537ff4d87c747d), plus the locally installed 6.4.1 skill inventory.
- Caddie's 22 existing skills, three agents, manifests, and hooks.

The repository comparison was followed by a read-only audit of local Claude invocation records. The observed usage below informed the additional implementation and branch-finishing workflows. All changes are repository-only; installed plugins and user/project settings are outside this task.

## Changes made

`wizard` already existed with its license and template. Its template has the same behavior as upstream; Caddie formats one command on a single line. Keep it rather than install another copy.

Added `grill-with-docs` and its reusable `domain-modeling` discipline. The former combines the existing interview with incremental glossary and ADR edits. Updated `grilling` to distinguish engineering, non-engineering, and mixed decisions. Interview-only requests still stop at agreement; an already authorized implementation does not require a second permission ceremony.

Added `writing-plans`, `executing-plans`, `subagent-driven-development`, `finishing-a-development-branch`, `tdd`, `code-review`, `verification-before-completion`, and a read-only `code-reviewer` agent. These are small local adaptations, not a vendored Superpowers framework. Their cross-references resolve inside Caddie. They preserve concrete interfaces, one behavior per test cycle, independent review, and evidence-based handoff. They omit mandatory worktrees, per-task commits, repeated permission requests, fixed numbers of review cycles, and the always-on bootstrap.

Removed the Superpowers cases from the retired-skill redirect hook. During integration with newer main, preserved its new writing-skill redirects and registration. With Superpowers removed, there is no need to intercept three of its skills while the rest remain callable. Replaced the two remaining runtime references to its planning and verification skills. Historical names remain in this migration document only.

## Matt Pocock comparison

| Upstream capability | Caddie coverage and recommendation |
| --- | --- |
| `grilling`, `grill-me` | Updated `grilling` is the reusable interview and direct user entry point; a second wrapper adds little. |
| `grill-with-docs`, `domain-modeling` | Added both; respect existing document layout and record accepted decisions only. |
| `wizard` | Already present; retained. |
| `diagnosing-bugs` | Already adapted, including reproduction, minimization, ranked hypotheses, and regression evidence. Keep one owner. |
| `writing-for-agents` | Already adapted with a skill-mechanics reference. Keep. |
| `handoff` | Already present. Keep Caddie's `docs/handoffs/` convention. |
| `wait-what` | `bro` handles plain-language restatement; `teach` handles deeper explanation. Improve these if misunderstandings recur rather than add a third name now. |
| `teach` | Names overlap but goals differ: upstream provides a persistent learning workspace; Caddie explains code and changes. Add a separate learning workflow only if longitudinal teaching is wanted. |
| `tdd` | Added a small test-first discipline. Retain refactoring while green; avoid mandatory approval of each test seam. |
| `code-review` | Added review and a read-only reviewer. Requirement coverage and correctness are distinct checks; `address-review` remains the owner of incoming-finding triage. |
| `implement` | New `executing-plans` covers the core execution path without adopting upstream's tracker setup and commit policy. |
| `codebase-design`, `improve-codebase-architecture` | Highest-value remaining engineering gap: `how` critiques a named subsystem and `blast-radius` probes a particular change, but neither surveys a codebase for worthwhile structural improvements. Add a focused architecture-survey entry point; reuse `how`, type discipline, and blast-radius rather than duplicate them. |
| `prototype` | Useful next addition: separate throwaway state-model experiments from UI alternatives, with an explicit question and disposal boundary. No equivalent in Caddie. |
| `research` | Useful next addition for forward-looking external research with primary sources and a saved artifact. `why` investigates history and `how` explains code; neither owns this job. |
| `to-spec`, `to-tickets` | Real gap when work crosses sessions or needs multiple issue owners. `file-issue` captures one report; it does not synthesize a settled spec or maintain dependency edges. Add local drafting first, with tracker publication explicitly scoped. |
| `to-questionnaire` | Useful when a stakeholder outside the session must answer. Different from live grilling; add if asynchronous discovery is common. |
| `resolving-merge-conflicts` | Useful specialized guidance, but adapt before adoption: preserve both intents, avoid unconditional `stage everything`, and honor a user's request to abort. Existing git guards do not resolve conflicts. |
| `triage`, `wayfinder` | Defer until there is a concrete backlog-management need. They introduce tracker roles, state transitions, and substantial workflow ownership. |
| `setup-matt-pocock-skills` | Do not import. The selected Caddie skills discover existing conventions and need no upstream setup dependency. |
| `ask-matt` | Defer a router until skill discovery becomes a demonstrated problem. README grouping currently provides a smaller index. |

## Superpowers replacement map

| Superpowers skill | Caddie destination or deliberate omission |
| --- | --- |
| `brainstorming` | `grilling`; `grill-with-docs` for engineering interviews that maintain records. |
| `systematic-debugging` | Existing `diagnosing-bugs`. |
| `writing-skills` | Existing `writing-for-agents`; authoring tools can still scaffold or evaluate skills independently. |
| `writing-plans` | New `writing-plans`. |
| `executing-plans` | New `executing-plans`. |
| `test-driven-development` | New `tdd`, scoped to test-first work rather than every edit. |
| `requesting-code-review` | New `code-review` and `code-reviewer`. |
| `receiving-code-review` | Existing `address-review`. |
| `verification-before-completion` | New skill of the same name. `create-verification-skill` builds a harness; it does not replace checking completion evidence. |
| `dispatching-parallel-agents` | Existing `how`, `why`, `recall`, and `blast-radius` already coordinate exploration. `subagent-driven-development` adds explicit ownership and task reviews for delegated implementation. |
| `subagent-driven-development` | Added after the usage audit confirmed eight successful loads. Preserve fresh implementers, independent task reviews, durable progress, and final integration review. Use focused artifacts and host-native tools instead of importing the upstream scripting framework. |
| `using-git-worktrees` | Keep worktree management conditional inside execution; reuse the host-provided worktree. No new global worktree mandate. |
| `finishing-a-development-branch` | Added after five observed successful loads. Honor the requested PR, merge, or handoff; preserve host workspaces and uncommitted files. No automatic cleanup or repeated integration-choice menu. |
| `using-superpowers` | Remove with the plugin. No replacement session bootstrap forcing a skill before every response. |
| `diagnosing-superpowers` | Omit the retired framework's own diagnostics. Caddie may eventually need its own behavioral evaluation workflow. |

## Agent gaps and existing updates worth making

The missing general code reviewer is now present. Keep its contract read-only and share it between requested reviews and implementation handoff. Separate spec and correctness reviewers can be added later if one reviewer repeatedly misses either dimension; they need not become two permanent agent roles immediately.

A dedicated research agent could accompany a future research skill. Implementation delegation now has a scoped worker brief inside `subagent-driven-development`; it uses available host workers rather than requiring another permanent agent type. Do not add permanent planner or architect roles solely because another plugin has them; first define their distinct inputs, outputs, and authority.

Existing improvements identified but kept outside this integration:

- `code-simplifier` imposes TypeScript/React preferences even on unrelated code and treats nearly all mutable locals as suspect. Make the consuming repo's standards primary and route language-specific rules conditionally.
- `comment-sicko` describes itself as report-only while instructing deletion and reporting files touched. Choose a consistent read-only or editing contract and align `no-comments` with it.
- `autonomous-mode` prefers an optional Codex review plugin and falls back to self-review. It can now use Caddie's reviewer as an independent fallback; this is a separate integration choice, not a remaining Superpowers dependency.
- Skill validation here checks packaging and links, but behavioral evaluations should cover routing, interview stopping behavior, existing authorization, absent tools, and uncommitted review scope as the catalog grows.

## Observed local usage

A read-only scan of 865 JSONL files under the local Claude projects directory found
51 distinct `Skill` tool invocation attempts naming `superpowers:` skills, dated
June 3 through September 21, 2026. Calls were deduplicated globally by tool-use ID
so forked transcripts do not inflate counts. Results were matched by that ID.

| Skill | Returned without error | Error or denied |
| --- | ---: | ---: |
| `subagent-driven-development` | 8 | 0 |
| `systematic-debugging` | 6 | 8 |
| `writing-plans` | 5 | 0 |
| `finishing-a-development-branch` | 5 | 0 |
| `receiving-code-review` | 2 | 0 |
| `brainstorming` | 1 | 14 |
| `test-driven-development` | 1 | 0 |
| `using-git-worktrees` | 1 | 0 |

Transcripts containing subagent-driven-development loads also contained subsequent
agent dispatches. This supports preserving delegated implementation, but does not
prove every prescribed review gate completed. A successful tool return establishes
that the skill loaded, not that its workflow finished. Failed calls are not counted
as usage of the workflow. Startup-hook injection, direct file reads, plain-text
commands, deleted history, and other hosts are not captured by this measure; zero
explicit calls is not proof a skill was unused.

Only aggregate metadata is recorded here. Private project names, conversation text,
task content, and transcript identifiers are excluded.

## Optional future installed-plugin cutover

The user explicitly chose repo changes only. No installed-plugin cutover is pending
as part of this task. The following is a future migration note, not an action to run
now.

The repo changes do not change an already installed plugin cache. Install/update the prepared Caddie version using the user's chosen marketplace before relying on the new skills, then restart the consuming session.

The machine inspected for this review has `superpowers@claude-plugins-official` enabled at user scope and four project-scope installation records. Its installed Claude Caddie version is 0.3.0, so these working-tree additions are not live yet. After Caddie is loaded, disable that plugin at the same scope (or uninstall it if desired). Inspect project and local overrides in any consuming repo, plus explicit `superpowers:` references in its instructions and permission settings. Remove obsolete redirects/denies only where they belong to this migration; preserve unrelated permissions.

Confirm a fresh session exposes Caddie's planning, interview, review, and verification skills without the Superpowers startup hook. Keeping an unused download in a cache is different from an enabled plugin; disabled cache files do not need to be manually deleted.

## Validation performed

Claude plugin validation passed for the marketplace (strict), plugin manifest, skills,
and agents. The plugin manifest retains the existing warning that root `CLAUDE.md`
is contributor guidance rather than shipped plugin context. Local name/link checks
passed for all 37 skill and agent entry points; all three manifest versions are 0.6.0.
The wizard template passed `bash -n`, and `git diff --check` passed.

An independent instruction walkthrough covered a career interview, an engineering
interview with glossary edits, an approved plan with a credential-blocked check, and
review of uncommitted/untracked changes. It prompted corrections to fact-finding
fallbacks, agent naming, and working-tree review scope. A follow-up walkthrough covered delegated execution, explicit inline execution,
resuming with dirty edits, a host-managed detached worktree, and repeated review
failures. It prompted an explicit uncertainty rule for missing historical baselines.
This is instruction-level validation, not proof of invocation in a freshly installed
Claude session.

The skill-creator Python validator could not run because the local interpreter lacks
PyYAML; Claude's component validator supplied the frontmatter/package checks instead.
No persistent plugin installation, disabling, publishing, or live-session reload was performed.

## Main-branch integration

Preserved the newer main branch's Codex packaging, host adapters, writing-profile
skills, and writing-skill redirects. Synchronized the Claude manifest, Codex manifest,
and Claude marketplace at 0.6.0. Compatibility tests cover retained redirects and
the removal of Superpowers redirect behavior.

The integrated tree passed all 16 compatibility tests. A temporary Codex installation
and loader smoke check discovered all 33 skills without errors; normal installed
plugins and settings remained untouched. All 37 skill/agent entry-point links resolved.
