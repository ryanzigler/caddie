# Issue / ticket tracker

Examples throughout are Jira, GitHub Issues, and Linear. Adapt to whichever tracker is connected. The search strategy carries over; the tool names do not.

## What this source contains

- Issues describing features, bugs, and their motivation
- Specs, PRDs, and design notes attached to or embedded in issues
- Parent/child and epic/story relationships, where the broader initiative carries the "why"
- Comments: clarifications, scope changes, decision records
- Labels and components (`compliance`, `customer-request`, `perf`, `incident-followup`) that signal the *type* of motivation
- Status transitions and sprint history that explain scope changes
- Linked PRs and commits

This is where product and business context lives: the "we're doing this because customer X asked" or "this is for the Q3 compliance initiative" layer.

## How to search it

1. **Start with linked tickets.** If the seed commits or PRs reference IDs (`ENG-1234`, `PROJ-567`, `#89`), fetch those first and read them in full, including every comment. A ticket ID in a commit message is the single highest-yield lead in this category.
2. **Search by keyword.** Query the feature name, the key symbol, the error string, and the business term. Try several phrasings and casual variants; ticket titles are written by humans in a hurry. In Jira, JQL text search (`text ~ "..."`) covers summary, description, and comments; a summary-only search will miss the rationale.
3. **Walk the hierarchy.** A sub-task or story is tactical. Fetch its parent, epic, or initiative. That is usually where the motivation is stated.
4. **Read attached and linked specs.** Project- or epic-level documents are where rationale is most often captured. If a ticket links out to a document tool, do not chase it; record it under "Additional leads" for the long-form documents investigator.
5. **Check labels, components, and fix versions.** Labels hint at the category of motivation. Fix versions and due dates tie work to deadlines, which often reveal the forcing function.
6. **Search by author and date window.** Tickets created or closed by the PR author in the two weeks around the merge date frequently surface the real driver even when nothing links them.

## What good evidence looks like here

- A description stating the business problem: "Customer Acme needs X because of their SOC 2 audit"
- A comment recording a decision: "We went with approach B because A would require touching the billing service"
- A parent epic titled like an initiative: "Q3 enterprise readiness", "Reduce payment failures"
- An attached PRD or spec
- Labels like `customer:acme`, `incident-followup`, `compliance`, `perf-regression`

## Common pitfalls

- **Scope drift.** The ticket a PR references may have been reopened with different scope. Read the whole history, including transitions.
- **Mechanical templates.** Some teams require a "Why" section and fill it with boilerplate. Generic text ("improve user experience") is not a real answer. Say so rather than quoting it as evidence.
- **Stale tickets.** Old tickets often reflect a plan that changed. Check dates against the code's ship date.
- **Duplicate chains.** Follow "duplicate of" relationships back to the canonical ticket.
- **Permission walls.** If you cannot access an issue, that is a gap. Record the ID and say it was inaccessible. Do not guess at its contents.
- **The tracker was not used.** Plenty of real work never gets a ticket, especially in a library or tooling repo. An empty result is a legitimate finding about how the team works.

## What to return

For each relevant ticket:

- ID and title
- The motivation quoted verbatim from the description or a comment. The synthesizer needs exact text to cite, not your paraphrase
- Labels, parent or epic, project
- Author, created date, resolved date
- Link
- Whether it is direct or circumstantial evidence
