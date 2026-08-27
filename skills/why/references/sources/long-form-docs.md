# Long-form documents

Examples throughout are Notion, Confluence, and Google Drive. Adapt to whichever document source is connected. A meeting-notes tool counts here when it holds decision records.

## What this source contains

- PRDs and product briefs
- Technical specs and RFCs
- Architectural decision records
- Meeting notes from design and architecture reviews
- Team pages carrying domain context
- Postmortems
- Runbooks, which often explain defensive code directly
- Strategy documents that set priorities

This is where "why" lives in long form before it becomes code. A significant feature usually has a document. A small change usually does not, and that absence is itself informative.

## How to search it

1. **Keyword search, several angles.** Try the feature name, key symbols and class names from the target, the PR author's name, user-visible error strings, and the business term. Design docs are frequently authored weeks before the code lands, so an author-plus-date search often beats a keyword search.
2. **Open candidates in full.** Read the whole document, not the preview or the summary. Rationale is usually mid-document, under a heading like "Alternatives considered", "Open questions", or "Appendix".
3. **Follow backlinks and child pages.** Design docs commonly push alternatives, appendices, and implementation notes into sub-pages, and the rejected-approach reasoning ends up there.
4. **Query structured collections.** Databases, spaces, or shared drives holding meeting notes, ADRs, or postmortems are worth querying directly by date range around the ship date, not only by keyword.
5. **Check personal or draft spaces.** At many companies the exploratory thinking that preceded the code sits in the author's own notebook rather than the team space.

When a document links out to a ticket or a chat thread, do not chase it. Record it under "Additional leads".

## What good evidence looks like here

- A PRD with a "Problem statement" or "Motivation" section that matches the target's purpose
- An explicit "Alternatives considered" or "Rejected approaches" section. This is the highest-value artifact in this entire category, because rejected alternatives are almost never recoverable from any other source
- A postmortem naming the target as the fix for a specific incident
- Meeting notes recording "we decided X because Y", from the same author and date range as the PR
- An ADR filled out non-trivially: status, context, decision, consequences

## Common pitfalls

- **Outdated docs.** Specs are written before implementation and rarely updated. The document may describe a plan that changed. Cross-check against the shipped diff.
- **Doc versus reality drift.** A spec may say "we'll do X" while the code does Y. Flag the divergence; the synthesizer surfaces it as a contradiction rather than picking a side.
- **Boilerplate templates.** A required "Why" section filled with fluff is not evidence. Look for specificity.
- **Unlinked docs.** The most relevant document is often linked from nowhere. Broad keyword searches are the only way to find it.
- **Multiple drafts.** When a topic has several documents, find the finalized or most recently updated one, and check dates before quoting.
- **Access-restricted pages.** A page you cannot open is a gap. Name it.

## What to return

For each relevant document:

- Title and URL
- Authors and last-updated date
- The motivation text quoted verbatim, with the section it came from
- Whether the document was finalized or a draft, and whether it predates or postdates the code
- Relevant linked pages, so the synthesizer can cite them
