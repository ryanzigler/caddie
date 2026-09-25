---
name: file-issue
description: Capture a bug or feature idea as a properly formatted GitHub issue without stopping what you are doing. Use when the user reports something in passing rather than asking for it now — "I just thought of a new feature", "here's a bug I noticed", "we should add X someday", "make a note that Y is broken", "file an issue for this", "open a ticket for that", "TODO for later". A background agent formats it and creates it with `gh`; the current work is not interrupted.
---

In Codex, first read [the host adapter](../../references/codex.md).

# File an issue

The user just said something out loud while doing something else. It costs them nothing to
say and it costs you almost nothing to capture, and that asymmetry is the entire point:
handing this to a background agent and going straight back to work is the behavior. Do not
turn a passing thought into a conversation.

## Does this apply

Yes when the report is **for later** — noticed, thought of, worth writing down.

No when the user wants it handled **now**. "This is broken, fix it" is `diagnosing-bugs`.
"Let's build X" is `grilling`. Filing an issue instead of doing the work is a way of not
doing the work.

If the request is both — "this is broken, fix it and file an issue" — do the work, and
dispatch the filer alongside it. If you genuinely cannot tell, do the work and ask in one
line whether they also want it filed. Filing is public and cheap to skip; guessing wrong
puts something on a public tracker that they wanted handled quietly.

## 1. Build the context packet

This is the step that decides whether the issue is any good. The agent starts with an empty
context window: it cannot see this conversation, the file you have open, the stack trace
three messages up, or what "it" refers to. Everything it needs has to be in the prompt.

Do not investigate to build this. Everything here is already in front of you, and the agent
does its own look-around. Assemble it from what you have and dispatch.

The packet is specified in [references/context-packet.md](references/context-packet.md).
Read it before you dispatch. Resolving pronouns is the part that is always skipped and always
matters: "the retry thing is broken" means nothing an hour later, in a different repo, to an
agent that was not here.

## 2. Dispatch in the background

In Claude Code, one agent, `subagent_type: "issue-filer"`, with the packet as its prompt.
Do not restate the agent's rules; it has them. In Codex, dispatch through the host adapter
with the shared agent body, the packet, and the absolute fallback-template path.

Subagents run in the background and notify on completion, so this does not block. Dispatch it
in the same message as the next step of whatever you were doing, and keep going.

## 3. Acknowledge in one line, then go back to work

One line — `Filing that as an issue in the background.` — then resume the interrupted task in
the same message. No preamble about what the agent will do, no draft of the issue for
approval, no list of what you put in the packet. The user asked not to be interrupted; a
paragraph about not interrupting them is an interruption.

Never wait on the agent. If the user's next message arrives first, answer it.

## 4. Relay the result when it lands

The agent's report is not shown to the user, so the URL only exists if you pass it on. When
the notification arrives, add one line wherever you are: the issue URL and its title.

Two things escalate past one line, because both mean something is unresolved:

- **It filed nothing.** Say why in one line and hold the full body it returned, so a retry
  costs nothing.
- **It found an existing issue instead.** Give that issue's URL and say it was already open.

Everything else — the template it used, what it marked unverified — stays folded away unless
the user asks.
