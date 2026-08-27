# Product analytics and the warehouse

This category is the product and data view, complementing infrastructure observability's infra and runtime view. It answers what users actually did, which experiments ran, how feature usage evolved, and where a threshold constant came from.

Examples throughout are PostHog and BigQuery. Adapt to whatever is connected (Amplitude, Mixpanel, Snowflake, Databricks, ClickHouse, a Postgres analytics schema). If both a product-analytics tool and a warehouse are connected, one investigator owns both and its coverage line names both.

## What this source contains

- **Product events.** Feature invocations, clicks, submissions, accepts and rejects, client-reported errors
- **Feature flags and experiments.** Flag definitions, rollout history, exposure and outcome data. Often the direct answer to "why is this gated"
- **Usage and billing events.** For cost- or volume-driven decisions
- **Session recordings and replays**, where enabled
- **Warehouse tables and models.** Whatever the team's pipelines produce, plus lineage showing which consumers depend on a field
- **Query history.** Answers "was this query expensive?", "when did load spike?", "did someone run a backfill here?"

## Orient before you query

**Never report a result from a table, event name, or flag key whose existence you did not confirm.** Schemas are organization-specific and this is the classic failure mode in this category. Probe first.

In BigQuery:

```
bq ls --datasets --project_id=<project>
bq ls <project>:<dataset>
bq show --schema --format=prettyjson <project>:<dataset>.<table>
bq query --use_legacy_sql=false "SELECT table_name FROM \`<project>.<dataset>.INFORMATION_SCHEMA.TABLES\` WHERE table_name LIKE '%<keyword>%'"
bq query --use_legacy_sql=false "SELECT column_name, data_type FROM \`<project>.<dataset>.INFORMATION_SCHEMA.COLUMNS\` WHERE table_name = '<table>'"
```

In PostHog, the `exec` tool's own command list is the schema. Use `event-definition` and `property-definition` to confirm an event and its properties exist before querying them, `feature-flag` and `experiment` for flag and experiment lookups, and `execute-sql` or `query` for the actual analysis. Read the `command` parameter's description rather than guessing at a subcommand.

**Time-bound every query.** These tables are large and unconstrained scans time out or cost money. Filter to a window bracketing the ship date, typically 30 days either side, wider only with a stated reason.

## Investigation patterns that tend to pay off

Pick the one that matches the target.

1. **Usage trajectory around the merge.** Daily event counts across a ±30 day window. A step function from zero to steady volume within a day or two of the merge is strong circumstantial evidence that PR launched the feature. A decay to zero suggests a deprecation, which is directly relevant to "why does this code still exist".
2. **Where a threshold came from.** The distribution — median, p95, p99, max — of the relevant property in the 14 days *before* the PR. A p99 that matches the target's constant is good evidence the number was chosen from data rather than picked arbitrarily. This is the single highest-value query in this category for "where did this number come from" questions.
3. **Flag and experiment lookup.** Find the flag key referenced in the target code, then pull its rollout history and any experiment attached to it. A flag whose rollout completed the week of the merge, or an experiment concluded just before it, ties the code to a ship decision.
4. **Error-classifying events.** If the product tracks client-reported failures, a drop in that event count after a defensive-code PR is circumstantial support that the code resolved the user-visible symptom, even when infra and error-tracking signal is noisy.
5. **Query history for migrations and backfills.** In BigQuery, `INFORMATION_SCHEMA.JOBS_BY_PROJECT` filtered on `query LIKE '%<table_or_symbol>%'` with a tight `creation_time` window surfaces the expensive queries that likely motivated a rewrite. Sort by `total_bytes_processed` or duration.
6. **Lineage.** If the target reads from or writes to a modeled table, that model's own definition usually lives in a repo. Hand that lead to the source control investigator rather than chasing it.

## What good evidence looks like here

- A feature-usage series that steps up from zero within a day of the merge
- A pre-ship p99 that matches a constant in the target code
- A flag or experiment record naming the target's flag key, with a decision dated near the ship date
- An error-classifying event whose daily count falls sharply after a defensive-code PR

## Common pitfalls

- **Instrumented is not caused.** An event exists because someone wanted to log it, not because the target code exists in response to it. Pair with a commit or PR citation before claiming causation.
- **Silent instrumentation changes.** A step function in event volume may mean a new event started being logged, not that behavior changed. Check for an instrumentation change in the same window before reading a ramp as a launch signal.
- **Schema drift.** Event properties evolve. A column that exists today may not have existed when the target was written, and older rows may carry it only inside an untyped JSON blob.
- **Pipeline lag.** Modeled tables rebuild on a schedule. For very recent events, fall back to the raw event source and deduplicate.
- **Retention cliffs.** If the relevant window predates the table's retention or its creation date, that is a **gap**, not a null result. Say so explicitly so the synthesizer does not read "no rows" as "no activity".
- **Unconfirmed tables.** Reporting a result from a table you assumed existed, or an empty result from a table name you guessed wrong, is worse than reporting a gap.
- **Notebooks and saved analyses.** Exploratory analyses an engineer wrote before a change are often not reachable through a SQL interface. If you suspect the rationale lives in one, name it as a gap.

## What to return

For each relevant finding:

- Type: product event, flag or experiment, usage or billing event, query-history row, warehouse table
- The fully-qualified table or event name and the **exact query you ran**
- The time window queried
- A compact numeric summary: counts, percentiles, first and last seen timestamps. Do not dump raw rows
- The temporal relationship to the ship date, stated as dates ("first row 2024-08-15, PR #49074 merged 2024-08-14") rather than as a conclusion
- Relevance and strength: direct, circumstantial, or weak
