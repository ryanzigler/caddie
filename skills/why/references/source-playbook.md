# Source playbooks

One playbook per evidence category. Give each investigator only the single file matching its assigned category, plus `incident-postmortem.md` when the target looks defensive.

The playbooks name concrete tools as examples because concrete query vocabulary is what makes an investigator effective. **Adapt to whatever is actually connected.** If the connected issue tracker is Jira and the playbook talks about Linear, the search strategy carries over; the tool names do not. Never report a finding from a tool you did not actually call.

| Category | Playbook | Tools it uses as examples |
|---|---|---|
| Source control history | [`code-archaeology.md`](./sources/code-archaeology.md) | `git`, `gh`, a GitHub MCP |
| Issue / ticket tracker | [`issue-tracker.md`](./sources/issue-tracker.md) | Jira, GitHub Issues, Linear |
| Long-form documents | [`long-form-docs.md`](./sources/long-form-docs.md) | Notion, Confluence, Google Drive |
| Real-time team chat | [`team-chat.md`](./sources/team-chat.md) | Slack |
| Infrastructure observability | [`infrastructure-observability.md`](./sources/infrastructure-observability.md) | Railway, Datadog, Grafana |
| Error / exception tracking | [`error-tracking.md`](./sources/error-tracking.md) | Sentry MCP, `sentry-cli` |
| Product analytics | [`product-analytics.md`](./sources/product-analytics.md) | PostHog, BigQuery |

Cross-cutting:

- [`incident-postmortem.md`](./sources/incident-postmortem.md). Append this when the target looks defensive: null checks, retry, timeout, rate limit, feature flag, guard clause, fallback, memory guard.

For what each category contains and is strongest at, see [`evidence-categories.md`](./evidence-categories.md).
