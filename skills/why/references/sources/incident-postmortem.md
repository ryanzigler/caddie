# Incident and postmortem context

Not a separate source. A **cross-cutting angle** appended to whichever playbook you were given.

Incidents motivate defensive code more often than any other single cause ("we added this check after the X outage"). So when the target looks defensive — null checks, retry logic, timeout handling, rate limiting, feature flags, guard clauses, fallbacks, memory guards — hunt for incident history *inside your own assigned source*. Do not go chase another source; record cross-source leads under "Additional leads".

What the incident angle looks like in each category:

- **Source control.** Commit messages containing "incident", "outage", "hotfix", "add defensive check", or a revert followed by a re-apply. A same-day merge is itself a signal of a fire drill.
- **Issue tracker.** Tickets labeled `incident`, `sev-*`, `postmortem-action-item`, `reliability`. Postmortem action items are frequently filed as ordinary tickets with no obvious link to the code.
- **Long-form docs.** Postmortems mentioning the target file, feature, or error string. Go straight to the "Action items" section; it usually maps to specific code.
- **Real-time chat.** Incident and severity channels around the dates the target was added. This is where the decision was actually made, in real time, and it is often the only record.
- **Infrastructure observability.** Formal incident records with timelines. Also dashboards and monitors created *as* postmortem action items, whose creation date will sit within days of the target's merge.
- **Error tracking.** Issues whose first-seen and last-seen window brackets the ship date, and stack traces passing through the target.
- **Product analytics.** Events that classify a user-visible failure often spike during an incident window. A drop in that count after the target ships is circumstantial support that the code resolved the symptom.

If you find an incident reference, fetch the full postmortem if it is inside your source. Postmortems typically have an action-items section that ties directly to code changes, and that section is the closest thing to a direct citation this category produces.

Evidence is strongest when several sources corroborate: an incident ID appears in a ticket, which appears in a postmortem, which appears in a chat thread linking the target PR, and the error count drops after the fix. You will only see your slice of that chain. Report your slice precisely, with dates, and let the synthesizer assemble it.

Skip this angle entirely for code that does not look defensive. It is a targeted lens, not a default.
