---
name: blast-radius
description: "Find what a change could break outside its own diff, then prove the one fact it's safe because of by running real code instead of writing it up. Use whenever the impact beyond the diff is in question — 'what could this break', 'blast radius of X', 'is this safe to merge', 'what else touches this', 'will this break the other packages' — or when changing a shared package, an exported API, a schema, or a wire format."
---

In Codex, first read [the host adapter](../../references/codex.md).

# Blast radius

Find what a change breaks somewhere else, before it ships.

Companion to `how` and `why`. `how` tells you what the code does. `why` tells you why it is
shaped that way. Blast radius tells you what it breaks somewhere else.

Listing the callers is not the job. Anyone can grep those in a second. The job is the
breakage grep will not show you.

## Don't trust your own writeup

A blast-radius writeup that sounds right is worthless. It reads as convincing whether or
not it is true, and that is the trap. So don't hand back the writeup. Find the one or two
facts the whole thing depends on and prove them by running code. Words are where you
start, not what you ship.

### The evidence ladder

For every fact the change's safety depends on, get it as far down this ladder as is cheap,
and **say where it stopped**.

1. **You said so.** Worthless on its own.
2. **You pointed at the line.** A real `file:line`, or the library's own source.
3. **You showed the bad case can't happen.** You walked the failure step by step and it
   does not reach.
4. **You ran it.** A script or test that calls the real code and fails loud if you are
   wrong.
5. **You reproduced it in the running app.**

**Rungs 1 through 3 are unproven. Label them that way, in the writeup, in those words.**
Anything short of "I ran a script against the real code and here is the output" is a
hypothesis, however well argued. Do not round up, do not let a confident rung 3 walk out
the door dressed as a conclusion, and do not present a clean grep as proof of absence
without saying it is a grep.

Rung 4 is usually one small script that imports the same library version the app ships and
calls the exact function you are worried about. If that script is cheap and you skipped
it, go write it.

## Steps

1. **Read the change.** The diff, the symbols it adds, changes, and deletes, and what it
   now does differently — including the part the diff does not spell out. Use `why` step 2
   to pull the PR and commits.
2. **Find the one fact it's safe because of.** Most changes that look scary are safe
   because of a single fact, like "this call only drops already-dead cache entries and does
   nothing else". Find that fact. If it holds, most of the scary cases die at once. Spend
   your time here, not on a long list of maybes.
3. **Look where grep stops.** Read the source of the library you call, and check its
   pinned version and any local patch or override. Work out *when* things run: microtasks,
   unmount and teardown, effect ordering, build-time versus runtime. Follow what a symbol
   search misses — the JSON an API returns, a DB column, a wire format, bytes read by
   another language, a feature flag, a published package's declared exports and type
   surface, code three hops downstream in a consumer that has not been rebuilt.
4. **Be honest about each risk.** Give it a real chance of happening and a real cost if it
   does. Keep the risks you confirmed; list the ones you checked and cleared separately.
   Cite a real `file:line`, treat a search that finds nothing as an answer worth stating,
   and never invent a caller or an API.
5. **Prove the one fact.** Write a script or test that runs the real code, run it, and
   paste what happened. If you cannot prove it cheaply, mark it unproven.
6. **For a big or wide change, widen the search, not the prose.** Run several
   `general-purpose` subagents in parallel over different attack surfaces — one on runtime
   consumers, one on build and type surface, one on data and wire formats, one hunting the
   counterexample to your safety fact — and merge what comes back. Independent passes catch
   different real bugs. Drop any finding a pass cannot get to rung 2.

## What to hand back

- **What it does.** What changed, including the part that isn't obvious.
- **The one fact it's safe because of.** State it, name the rung it reached, and show the
  proof. If you couldn't prove it, write **unproven**.
- **Risks.** Only the real ones. Each names how it breaks, the `file:line`, how likely and
  how bad, its rung, and how to check. Paste the proof for the ones that matter.
- **Cleared.** What you checked and why it's fine, each with its rung.
- **Before you merge.** The cheapest test or repro that catches the real bug, including the
  script you wrote.

Write it through `ryan-voice-guide`, cite real code, and strip anything private before it goes
anywhere public.

**Reply:** the writeup above, with the one safety fact either proven at rung 4 or higher,
or explicitly marked unproven.
