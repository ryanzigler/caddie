# Real-time team chat

Examples throughout are Slack. Adapt to whichever chat source is connected (Discord, Teams, Mattermost). The search strategy carries over.

## What this source contains

- Real-time discussion of problems and decisions
- Incident channels where fire-drill decisions were made
- Design threads where tradeoffs were argued out
- Questions answered by a senior engineer that never made it into a doc
- Post-merge discussion explaining why something was revisited
- DMs, which are usually not searchable. Scope accordingly and say so

This is frequently where the real decision got made, especially for changes too small to warrant a document. It is also the most ephemeral source: threads get deleted, channels get archived, and retention policies silently erase history.

## How to search it

Check the connected chat tool's schema before querying; capabilities vary a lot, and some tools can search public channels only. If authentication fails, stop and report the gap rather than working around it.

1. **Author-bounded search.** Messages from the PR author in the window around the merge date. This narrows the space dramatically and hits gold more often than any keyword search.
2. **Keyword search for the feature name and key symbols.** Include misspellings, abbreviations, and casual phrasings. People do not type `RateLimitInterceptor` in chat.
3. **PR and commit URL search.** PRs get pasted into channels when they are reviewed or when they break something. Search for the PR URL, or just `/pull/<number>`.
4. **Error string search.** If the code handles a specific error, search the error text. Incident threads surface this way.
5. **Channel-scoped search.** Narrow to the likely channels: engineering channels, project channels, incident and severity channels, the owning team's channel, and any design-review channel.
6. **Thread traversal.** When you find a relevant message, fetch the entire thread. The decision almost always lives in the replies, not the parent.

## What good evidence looks like here

- A thread where tradeoffs were explicitly debated ("I was going to use A but B is better because…")
- An incident message describing the bug the code prevents
- A reviewer's question and an authoritative answer from the author or lead
- A reference to a meeting where a decision was made, which the long-form docs investigator can then chase
- A product or customer-facing person explaining a customer ask

## Common pitfalls

- **Retention cliffs.** Messages older than the workspace retention window are gone. If you find nothing before a certain date, report the cliff explicitly. "Nothing found before 2024" reads very differently from "retention only goes back to 2024."
- **Unsearchable DMs.** Many decisions happen in DMs. You will miss them. State it as a known limitation rather than concluding no discussion happened.
- **Jokes read as decisions.** Chat is casual. "lol just ship it" is not a decision, even when it immediately precedes the commit. Look for considered discussion.
- **Context collapse.** A single message read without its thread often means something different. Always fetch the thread.
- **Auth failures.** If the tool is not authenticated, stop. Do not invent findings. Report that chat was not searchable and that the user can authenticate it.

## What to return

For each relevant thread:

- Channel name
- Permalink or thread ID
- Participants
- Date range of the discussion
- The key quotes, verbatim, with attribution
- What the thread was part of: a review, an incident, a design discussion
- Whether it is direct or circumstantial evidence
