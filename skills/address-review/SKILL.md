---
name: address-review
description: Triage review findings from any source — a PR's review comments and threads, a Codex review or adversarial-review result, or text the user pasted — verify each one against the code, fix what holds, push back on what doesn't, and reply on the PR. Use for "address the review", "Claude called this out on PR review", "Address Codex's findings", "fix what the reviewer flagged", "respond to the PR comments", or whenever review output is pasted or a PR has unresolved review threads.
---

In Codex, first read [the host adapter](../../references/codex.md).

# Address review

Review output is a set of claims about the code. Treat every claim, whoever made it, the same
way: restate it, check it against the codebase, then either fix it or refute it with a
reason. Verified before implemented. No "you're absolutely right", no thanks; the fix or the
counter-argument is the reply.

## 1. Collect every finding into one ledger

Pull from every source that exists here, then dedupe across them; the same bug is often
reported by Codex and the PR bot in different words.

- **Pasted text or the conversation.** Findings in `$ARGUMENTS` or the last message, and a
  Codex `--wait` result already printed above.
- **Claude-hosted Codex job store, when installed.** `node "<codex-plugin>/scripts/codex-companion.mjs" result --json`
  from the repo root, where `<codex-plugin>` is the newest directory under
  `~/.claude/plugins/cache/openai-codex/codex/`. "No finished Codex jobs" means the source is
  empty, not missing. If the companion is absent, mark that source unavailable. In
  Codex, also collect review results already in the conversation or in an explicitly
  supplied artifact; do not assume the Claude companion is installed or launch a new
  review just to fill an empty source.
- **The PR.** `gh pr view --json number,url,headRefOid,baseRefName` finds the PR for the
  current branch (or take the number from `$ARGUMENTS`). Then read the review bodies, the
  unresolved inline threads, and the issue comments per
  [references/pr-comments.md](references/pr-comments.md). Skip deploy and CI bots
  (`vercel[bot]` and the like); keep review bots (`claude[bot]`, `macroscopeapp[bot]`) and
  humans. Skip threads already resolved.

Number each finding: source, `file:line` if it cites one, the claim in one line, and a
`thread id` for anything you will reply to. **Done when:** every finding from every present
source is a row, duplicates are merged with both sources listed, and the empty sources are
named.

## 2. Understand before touching anything

Restate each claim as the requirement it implies. If any row is unclear, stop and ask about
those rows before implementing any of them — findings are often related, and a partial
reading produces the wrong fix. A row that conflicts with a decision the user already made
in this session is a question for the user, not a fix.

## 3. Verify each claim against the code

Inline comments were written against the PR's `headRefOid`; the branch may have moved.
Read the cited lines at the current HEAD and confirm they still say what the reviewer saw.

For each row, establish:

- Does the claim hold? Read the code path, not just the cited line. Run the failing input
  if the claim is behavioral.
- Why is the code this way? `git log -L` or `git blame` on the lines; a reviewer without
  that history often flags something deliberate.
- Would the suggested change break a caller, another platform, or an existing test?
- Is the "proper implementation" being asked for actually used? `grep` for callers. Unused
  means remove it, not build it out.

Verdict per row: **confirmed**, **refuted** (with the fact that refutes it), **unverifiable**
(with what would settle it), or **out of scope** (real but not this PR's job). Show the
ledger with verdicts. Then proceed to fix the confirmed rows; wait only if step 2 left
questions open or the user asked to approve fixes first.

## 4. Fix the confirmed rows

Order: anything that breaks or is a security hole, then one-line fixes, then the ones that
need design. One row at a time; after each, run the check that proves it — the test, the
type checker, the repro. A confirmed bug gets a regression test where a seam exists that
exercises the real pattern. A finding fixed by silencing a rule is not fixed.

If a fix needs a design rather than an edit, sketch it in the report and stop on that row
rather than improvising an architecture mid-pass.

## 5. Reply on the PR

Commits, pushes, and PR replies leave the machine. Show the diff and the drafted replies,
then ask once; an unattended run needs this pre-approved in the request.

Per thread, one reply, using the commands in
[references/pr-comments.md](references/pr-comments.md):

- **Confirmed and fixed:** what changed and the commit. `Fixed in abc1234: <what changed>.`
  Then resolve the thread.
- **Refuted:** the fact and where it lives. `<Claim> doesn't hold: <file:line> does <X>
  because <Y>.` Leave the thread open for the reviewer.
- **Out of scope or unverifiable:** say which, and what would settle it. Leave open.

Findings from Codex or pasted text have no thread; they get their line in the report only.

## 6. Report

The ledger, one line per row: number, source, verdict, and either the commit that fixed it
or the reason it stands. Then what is still open and what input closes each. Anything you
could not verify is marked as such, never rounded up to fixed.
