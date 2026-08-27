# Code archaeology (git and in-repo)

## What this source contains

- Commit history: messages, dates, authors, diffs
- PR descriptions, review comments, and discussion threads, via `gh` or a GitHub MCP
- Inline code comments, TODOs, FIXMEs, deprecation notes
- ADRs (architectural decision records) if the repo keeps them
- Tests. Names and assertions often encode the edge cases that motivated a change
- Related files modified in the same commits, the co-change signal
- CHANGELOG entries and release notes in the repo
- Changeset files (`.changeset/*.md`) in a changesets-managed repo. These carry a human-written, release-facing rationale that often says more than the commit message
- Issue and ticket IDs mentioned in commit messages and PR bodies

The most trustworthy source, tied directly to the code, and the most complete. Everything that went through the repo should be here.

## Building the code anchor

These are the commands the lead runs inline before spawning anyone, and the ones the source control investigator expands on. One command per line.

```
git blame -L <start>,<end> <file>
git log --oneline -20 -- <file>
git log -1 --format=%B <commit>
gh pr view <number> --json title,body,author,createdAt,mergedAt,labels,closingIssuesReferences,comments,reviews
```

## How to search it

Expand the seed commit list:

```
git log --follow --oneline -- <file>
git log -S '<exact_string_from_code>' -- <file>
git log -G '<regex>' -- <file>
git show <hash>
git log <old>..<new> -p -- <file>
```

`git log -S` is the pickaxe: commits that added or removed that exact text. It is the single most effective way to find where a magic number or a specific string came from.

For each substantive commit, pull the PR context. The `reviews` and `comments` fields are where the real signal usually is:

```
gh pr view <number> --json title,body,author,createdAt,mergedAt,labels,closingIssuesReferences,comments,reviews,files
gh pr list --search "<keyword>" --state all --limit 30 --json number,title,mergedAt
gh api "repos/{owner}/{repo}/commits/<hash>/pulls"
```

Look for out-of-band docs and in-repo rationale:

```
grep -rln -i 'architecture.decision' --include=*.md .
grep -rn -C2 -E '(TODO|FIXME|HACK|XXX|NOTE)' <target_file>
grep -rln '<symbol>' --include=*test* --include=*spec* .
grep -rn '<symbol>' .changeset CHANGELOG.md 2>/dev/null
```

In a monorepo, widen the blame from the file to the package. A constant's rationale often lives in a sibling file's PR, or in the changeset that shipped the package version that introduced it:

```
git log --oneline -30 -- <package-dir>
git log --oneline --all --grep '<package-name>'
```

## What good evidence looks like here

- A PR description that explains the problem being solved, not just the change ("this fixes the pagination bug that caused X")
- A long review thread where alternatives were debated
- An inline comment near the target line explaining a non-obvious constraint
- A test named `handles_edge_case_when_X` that reveals the motivating edge case
- A commit message referencing a ticket or incident ID
- A changeset or CHANGELOG entry summarizing the user-visible rationale in the author's own words

## Common pitfalls

- **Squash-merge flatlands.** If the repo squashes PRs, individual branch commits are gone. Fall back to the PR body and comments.
- **Misleading commit messages.** "Small refactor" sometimes hides an intentional behavior change. Read the diff, not the message.
- **Cargo-culted patterns.** The author may have copied a pattern without understanding it. If the pattern originated earlier in the codebase, investigate *that* commit instead.
- **Bot commits.** Dependabot, Renovate, changesets release commits, and automated backports usually carry no motivation. Skip them when hunting intent, but note that a release commit's changeset body may not be automated.
- **Treating code as evidence of intent.** The code is not evidence for why it exists. Evidence comes from messages, PRs, comments, tests, and docs. Never cite "the function is named X" as evidence of intent.

## What to return

Every commit, PR, comment, changeset, or test that bears on the question, with:

- The exact text, quoted
- The hash, PR number, or file:line
- Author and date
- Whether it is direct (explicitly addresses the question) or circumstantial
