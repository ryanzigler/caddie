# Error / exception tracking

Examples throughout are Sentry, reachable either as an MCP server or through the `sentry-cli` binary. Adapt to whichever error tracker is connected (Rollbar, Bugsnag, Airbrake, or the error-tracking surface of a product-analytics platform). Inspect the connected tool's schema before querying; tool names differ and guessing wastes a round trip.

## What this source contains

Error tracking is the archive of things that went wrong. For defensive, corrective, or error-handling code it often holds the direct motivation: the specific exceptions, stack traces, and frequencies that pushed someone to add a check, a catch, a retry, or a fallback.

- **Issues.** Grouped errors with event counts, first-seen and last-seen timestamps, affected releases, assignees, and comments
- **Events.** Individual instances within an issue: stack traces, tags, breadcrumbs, user context
- **Releases.** Deploy records with associated issues, which answer "which version fixed this?"
- **Resolution notes and comments.** Sometimes contain an engineer's actual root-cause note
- **Replays and profiles**, where enabled. Less useful for "why", occasionally decisive for "why is this slow"

The most valuable thing this category provides is **temporal correlation**: "this issue was created 2024-01-02, peaked at 500 events/day, and stopped appearing after v2.14.0 on 2024-01-15, the release that shipped the defensive check."

## How to search it

1. **Orient.** Establish the organization and project slug before anything else. A search against the wrong project returns a confident empty result, which is the worst possible output.
2. **Search issues related to the target.** Good query components, in rough order of yield: the exception class the target handles, the error message string the target checks for, the function or class name of the target, the file path of the target.
3. **For each candidate issue, get the four timestamps that matter.** First seen: when did the error start? Last seen: when did it stop, and does that line up with the ship date? Affected releases: which versions saw it, which was the last? Frequency trajectory: did it spike and then get resolved?
4. **Pull a representative event in full.** Does the stack trace actually pass through the target code? Do the tags and breadcrumbs match the conditions the target defends against? A matching issue title with a non-matching stack trace is a false positive.
5. **Cross-reference releases against the merge date.** Find the release that contained the target commit, then look at what the issue did across that boundary.
6. **Treat AI root-cause features as hypothesis generators, not evidence.** If the tool offers an automated analysis, it is inference. The events, stack traces, and timestamps are the primary evidence. Never cite a generated narrative as though an engineer wrote it.

When only the CLI is available, `sentry-cli info`, `sentry-cli releases list`, and the issue-listing subcommand cover items 1, 3, and 5. Run `sentry-cli --help` first rather than assuming a subcommand exists.

## What good evidence looks like here

- An issue whose first-seen is shortly before the target's PR and last-seen shortly after
- Stack traces that pass through or land on the target function, showing the exact failure mode being defended against
- A comment on the issue from the PR author describing the fix
- The target's PR or commit message referencing an issue URL or ID from this tool. This is the strongest possible finding in this category, and it makes the link direct rather than circumstantial
- A high-volume issue that stops entirely at the release containing the target

## Common pitfalls

- **Grouping drift.** Errors are grouped by fingerprint. A refactor or rename can track the "same" error under a new issue ID. If an issue ends abruptly, check for a new issue starting immediately after before concluding it was fixed.
- **Release correlation is noisy.** A release contains many commits. An issue stopping at v2.14.0 does not prove the target fixed it. Cross-reference the exact commit and say what else shipped in that release.
- **Silent upstream fixes.** Sometimes the error stops because a dependency or an upstream service changed, not because of the defensive code. Correlation suggests the fix; it does not prove authorship.
- **Resolved is not fixed.** Issues get marked resolved by hand with no code change. Treat `resolved` as a human marker, not evidence.
- **Sampling.** Some projects sample aggressively. A low event count may mean heavy sampling rather than a rare error. If the sample rate is unknown, say so.
- **Retention.** If the relevant window predates retention, that is a gap, not a null result.

## What to return

For each relevant issue:

- Issue ID and title, project and organization
- First seen and last seen timestamps
- Event count, and the sampling rate if known
- Affected releases
- A representative stack trace excerpt showing relevance to the target, verbatim rather than summarized
- The correlation with the target's ship date, stated as dates rather than as a conclusion
- Link, and any author comments or resolution notes
- Whether the link to the target is direct (cited in the PR) or circumstantial (timing only)
