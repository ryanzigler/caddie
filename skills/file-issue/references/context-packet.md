# The context packet

Everything the `issue-filer` agent will ever know about this report. It has no view of the
conversation, so anything not written here is lost.

Assemble it from what is already in front of you. Do not go looking; the agent has its own
bounded look-around, and this step is supposed to be free.

## Fields

**The report, verbatim.** The user's own words, quoted, before you tidy them. Your summary of
what they meant goes underneath as your reading, marked as yours. Their phrasing carries
information yours will drop.

**Resolved pronouns.** "It", "this", "that thing", "the same problem as before" — every one
of them replaced with the actual subject. This is the single most common failure, and it
produces an issue about nothing.

**Where they were.** The file, function, or PR under discussion when they said it, with real
paths. If they were looking at a diff or a failing test, name it.

**Error output, verbatim and complete.** Any stack trace, failing test output, or log line
from this conversation, in a fenced block, uncut. Do not summarize an error; the string is
the searchable part.

**What you already know.** Anything established in this session that bears on the report —
a decision made, a constraint, a thing already ruled out. This is what keeps the agent from
filing an issue for something you resolved twenty minutes ago.

**Target repo.** If the user named one, or if the report is about a different repo than the
one you are working in, say which. Otherwise say the working directory and let the agent
resolve it.

**The working directory,** as an absolute path. The agent runs `gh` and `git` from it.

## What to leave out

The rest of the session. A long transcript dump buries the report and costs the agent the
budget it needs for the look-around. Only what bears on this one issue.

Your own theory of the root cause, unless the user gave it. An unverified guess in the
packet becomes an assertion in the issue, and then someone chases it.
