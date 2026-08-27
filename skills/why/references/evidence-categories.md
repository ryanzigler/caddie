# The seven evidence categories

Every category overlaps with the others, but each one owns a kind of evidence none of the rest can recover. Use this file to know what to expect back from an investigator, how to word a gap when a category returns empty, and (only in the rare provably-irrelevant case) how to justify not running one.

Example sources are illustrative. Classify whatever is actually connected in this environment by its name, its server instructions, and its tool names.

## 1. Source control history

**Contains:** commit history, PR descriptions, review threads, inline comments, tests, ADRs kept in-repo, CHANGELOG entries, co-changed files.

**Sources:** `git` and the `gh` CLI, or a GitHub / GitLab MCP server.

**Strongest at:** implementation-time rationale captured during review. PR descriptions stating the problem, review threads debating alternatives, inline comments encoding a non-obvious constraint, test names that encode the motivating edge case, commit messages linking a ticket or incident.

**Most trustworthy**, because it ties directly to the diff that shipped. Always searched.

## 2. Issue / ticket tracker

**Contains:** tickets, epics and parent initiatives, spec attachments, comments recording scope changes, labels categorizing the motivation, milestones tying work to deadlines.

**Sources:** Jira, Linear, GitHub Issues, Shortcut, Plane.

**Strongest at:** the product or business forcing function. Customer requests ("Acme needs this for their SOC 2 audit"), compliance deadlines, parent-initiative framing ("Q3 enterprise readiness"), labels like `customer:*`, `incident-followup`, `compliance`, `perf-regression`.

Reach for it hardest when the why is external to engineering.

**Gap wording:** "Issue tracker not searched. No connected source." Or, when it ran empty: "Searched Jira for [queries] across [range]. No ticket discusses this."

## 3. Long-form documents

**Contains:** PRDs, specs, RFCs, design docs, ADRs, postmortems, team pages, meeting notes, runbooks.

**Sources:** Notion, Confluence, Google Docs or Drive, Coda. Meeting-notes tools count when they hold decision records.

**Strongest at:** design rationale written out before it became code. Problem statements, explicit "alternatives considered" and "rejected approaches" sections, strategy docs that set priorities, ADRs with a finalized decision, postmortem action items that map to specific code.

**Gap wording:** name the searches. An absent design doc is meaningful evidence that the decision was made informally.

## 4. Real-time team chat

**Contains:** decision threads, incident channels, reviewer Q&A, post-merge discussion, and the casual "we decided X because Y" message that never reached a doc.

**Sources:** Slack, Discord, Microsoft Teams, Mattermost.

**Strongest at:** real-time deliberation that never got written up. Fire-drill decisions during an incident, back-and-forth between author and reviewer, rationale for a change too small to warrant a PRD.

Especially important when the source control, ticket, and doc trail is all thin. Also the most ephemeral: retention policies delete old messages, and DMs are usually unsearchable. Say so when it applies.

## 5. Infrastructure observability

**Contains:** metrics, monitors and alert thresholds, dashboards, logs, APM traces, deploy history, formal incident records.

**Sources:** Datadog, Grafana, Honeycomb, New Relic, Splunk. Also a platform's own logs and metrics surface, such as a Railway, Vercel, or Cloud Run MCP or CLI, which carries deploy history and error rates even without a dedicated APM.

**Strongest at:** the infrastructure reality that motivated the code. A monitor whose threshold matches a code constant, a metric spike in the window right before a merge, a dashboard created as a postmortem action item, an incident timeline naming the target.

Reach for it hardest when the target reacts to an infra signal: timeouts, retries, rate limits, circuit breakers, memory guards.

## 6. Error / exception tracking

**Contains:** grouped issues with first-seen and last-seen timestamps, individual events with stack traces, release associations, resolution notes.

**Sources:** Sentry (MCP or `sentry-cli`), Rollbar, Bugsnag, Airbrake. Some product-analytics platforms also carry error tracking; if that is the only error source connected, this category and category 7 share one investigator.

**Strongest at:** the specific exceptions that motivated defensive or corrective code. Stack traces passing through the target function, an issue whose first-seen/last-seen window brackets the ship date, a release correlation showing an error stopping at a specific version.

Reach for it hardest for catch blocks, null guards, type guards, retries, and fallbacks.

## 7. Product analytics

**Contains:** product events, feature-flag and experiment exposure data, usage and billing events, session data, warehouse query history, pipeline and model lineage.

**Sources:** PostHog, Amplitude, Mixpanel; and warehouses such as BigQuery (`bq` CLI or MCP), Snowflake, Databricks, ClickHouse, Postgres analytics schemas.

**Strongest at:** the product and data reality that shaped the code. A usage trajectory that steps up from zero within a day of a merge is strong circumstantial evidence that PR launched the feature. Experiment or flag exposure tied to a ship decision. A pre-ship distribution that reveals where a threshold came from, such as a `128 * 1024` limit matching the p99 of an upload-size column. Pipeline scale evidence for a migration or backfill.

Reach for it hardest for flag-gated code, experiment-driven ships, data migrations, and "where did this number come from" questions.

## When two sources land in one category

One investigator owns both, and its coverage line names both. Do not split a category across two investigators; the one-per-category rule is what keeps the coverage map legible.

## When a source could fit two categories

Pick the category matching its primary evidence and note the ambiguity in the coverage map. A product-analytics platform that also does error tracking is primarily product analytics; say that the error-tracking category was covered by it, so the reader knows the coverage is partial rather than absent.
