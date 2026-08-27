# Infrastructure observability

This category covers whatever holds the runtime record: what actually happened in production, as opposed to what was planned or discussed. That might be a dedicated observability platform (Datadog, Grafana, Honeycomb, New Relic, Splunk), or it might be the hosting platform's own logs and metrics surface (Railway, Vercel, Cloud Run, Fly), or CI history. Use whichever is connected.

**Describe your queries by capability, not by tool name, when reporting.** The synthesizer needs to know you looked at "error rate for the 30 days around the merge", not that you called a particular function.

## What this source contains

- **Metrics.** Counters, gauges, histograms. A metric's *existence* is itself evidence: someone thought this number worth watching.
- **Monitors and alerts.** Conditions the team decided warranted waking someone up. A monitor firing at `rate_limit_hit > 10/min` is direct evidence the team worried about that threshold, and the threshold is frequently the literal answer to "why is this clamped at N?"
- **Dashboards.** Curated views. The charts show what the team considers important for a subsystem, and who built the view.
- **Logs.** The error conditions that motivated defensive code.
- **Traces and spans.** Request-level runtime data. The place to look for "why is there a timeout here".
- **Deploy history.** When each version shipped, and which deploys rolled back. Roll-forward-after-revert sequences are strong signals.
- **Incident records.** Formal incidents with timelines and linked postmortems.

## How to search it

Start broad, then narrow. **Time-bound every query** to a window bracketing the target's ship date, typically 30 days either side. Unconstrained log searches time out and waste the whole investigation.

1. **Identify the owning service or deployment.** List the projects, services, and environments the connected platform knows about, and pick the one the target code runs in. A finding from the wrong service is worse than no finding.
2. **Look at monitors and dashboards before metrics.** They encode what humans decided to care about, which is closer to motivation than raw numbers are. Note every threshold. Compare each one against the constants in the target code.
3. **Pull the metric trajectory around the ship date.** Error rate, response time, request volume, and any metric named after the target's domain. A spike immediately before the merge and stability after is meaningful supporting evidence, though not proof.
4. **Search logs narrowly.** Query by symbol, error string, or feature name, scoped to the owning service and a tight time window. Aggregate rather than dumping raw lines.
5. **Read the deploy timeline.** Which deploy contained the target commit, what happened to error rates immediately after, and whether anything was rolled back nearby.
6. **Search incidents.** If the target looks defensive, look for incidents in the weeks before it was added. An incident timeline containing "added a defensive check for X" is near-direct evidence.

When the platform has no dedicated observability surface, CI history is a usable fallback for the deploy-timeline question:

```
gh run list --limit 30 --json databaseId,name,conclusion,createdAt,headSha
gh run view <id> --log-failed
```

Railway-hosted services expose logs, service metrics, HTTP error rate, response time, and deployment lists through the Railway MCP; those cover items 3 through 5 above without a separate APM.

## What good evidence looks like here

- A monitor whose query and threshold match the constraint the code enforces: the code clamps to 100, the monitor alerts above 100/min
- A dashboard built by the target's author, with widgets corresponding to what the code measures or guards against
- A metric showing a production spike immediately before the merge and stable values after
- An incident record referencing the target code, the same symbols, or the same error strings
- Logs showing the exact error pattern the defensive code prevents, timestamped in the window before the change
- A deploy that was rolled back, then re-shipped with the target code in it

## Common pitfalls

- **Correlation is not causation.** A spike before a PR and calm after is suggestive, not definitive. Other changes landed in the same window. Check the neighboring commits and say what else shipped.
- **Overfitting to a chart you found.** Dashboards are made by humans and reflect that human's framing. A chart named "retry success rate" is evidence the team cared about retry success, not that it explains a specific line.
- **Vanished telemetry.** Metrics get renamed, deleted, or age out of retention. No data from the relevant window is a **gap**, not a null result. The distinction matters.
- **Noise at scale.** A common string returns thousands of log matches. Narrow by service, tag, and time aggressively.
- **Instrumented is not caused.** A metric exists because someone wanted to measure something, not because the code was written in response to it. Pair it with a commit or PR citation before implying causation.
- **Wrong environment.** Staging data answering a production question is not evidence. Check the environment tag.

## What to return

For each relevant item:

- Type: dashboard, monitor, metric, log pattern, trace, deploy, incident
- Name or title, and an identifier or link
- Owner and created or modified date
- The specific condition, query, threshold, or quote that bears on the question, verbatim where possible
- The time window you queried
- Relevance and strength: how tight the connection to the target actually is
