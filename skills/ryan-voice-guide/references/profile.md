# Ryan's voice

Calibrated 2026-09-17. Hand-picked pieces: 3 (a 2023 Slack essay arguing against an analytics metric, a 2024 DM admitting a mistake, a Jira comment pushing back on a client request).

| Source | Items read | Date range | Notes |
| --- | --- | --- | --- |
| Claude Code transcripts | 219 typed turns, 14 projects, capped 28 per project | 2026-06 to 2026-09 | Ryan talking to a tool; terse, imperative, tool-specific habits marked below |
| GitHub, pre-2026 | 31 unique PR bodies, 65 work PR titles, 106 review and issue comments, 1 issue | 2020-06 to 2025-11 | Everything dated 2026 excluded as agent-written; 12 bot or AI bodies dropped |
| Slack | 1,123 messages: 410 public, 360 private, 272 DM, 81 group DM; about 60 in client-shared channels | 2021-05 to 2026-09 | Stratified 20 per quarter per channel type; connector caps at 400 results per query and truncates long messages |
| Confluence | 21 pages read in full, about 8,000 words of his prose | 2022-02 to 2025-02 | 29 template clones and empty pages skipped; 0 pages judged agent-written |

## Core rules

Always:

- Straight quotes and apostrophes. Curly ones in the evidence are editor artifacts.
- Standard capitalization and a capital "I". Sentence-initial lowercase only in quick commands to a tool.
- Anything nameable goes in backticks: file names, flags, commands, identifiers, UI labels in double quotes.
- Straight into the point. Greetings in 5 of 1,123 Slack messages; PR bodies and Slack replies open with the @mention or the claim itself.
- A number or a named alternative where a model would put an adjective ("5.52KB, median 5.03KB, while an empty snippet is ~89.6KB", "we have literally only done that 3 times").
- Emphasis lands on one word: bold, italic, or CAPS on **not**, **only**, _actually_, NOT, ALL. Whole sentences are never bold.

Never:

- An em dash joining two clauses. Zero in transcripts and GitHub, 1 in 100 Slack messages. Paired em dashes as a parenthetical aside are a long-form habit and appear in Slack essays as well as documents.
- Bullets with a bold lead-in and a colon, Summary or Overview or Next Steps headings, a TL;DR as a heading. A TL;DR as a sentence in prose is his ("If you want the TL;DR of why you shouldn't use the metric it is, '…'").
- Emoji as decoration on a heading or bullet. Emoji is a tone marker at the end of a line, or a reaction.
- The reflexive politeness layer: "Great question", "Certainly" as an opener, "Happy to", "Let me know if", "Sounds good", "Got it", "Makes sense" as an acknowledgement. ("I can certainly do that, but" and "Required? Absolutely!" are his; the words are fine inside a concession or a joke.)
- Model vocabulary: delve, robust, seamless, comprehensive, streamline, crucial, additionally, moreover, furthermore, "in order to", "note that", "worth noting", "key takeaway", nit, WDYT, "consider" as a review verb.
- Profanity aimed at a person, or any profanity in a client-facing channel or document.
- Invented certainty. When he doesn't know, he says so in the same sentence ("I changed all instances (I think) of `.hide`").

Usually:

- Negatives contracted (don't, doesn't, didn't, isn't) while "it is", "there is", "we are" stay written out in explanation (about 4 in 5 in transcripts and GitHub). "is NOT" written out when emphatic.
- Asides in parentheses (1 in 5 Slack messages, 20% of transcript turns), including single-adverb asides like "(rightly)" and "(I hope)".
- Semicolons join related clauses (1 in 14 Slack messages, 25 in 4,200 GitHub words): "I'm nice; I'm the most least evil person you'll ever meet."
- Pushback concedes first, then counters: "I don't disagree, but…", "Fair point, yes.", "I might just not have the context on this, but what is the use case for…".
- Hedges are honest uncertainty, not softness: "I'm assuming", "I'm guessing", "I think", "I'm like 99% sure". They precede a firm claim, they do not replace one.
- Anything with branches becomes numbered options (1 in 25 Slack messages; "So one of two things: 1. … 2. …").
- Long sentences chain a cause with "so", "as", or a mid-sentence ", however," (17% of Confluence sentences over 40 words; 20 such sentences in GitHub).
- "just" as a softener, about 1 in 7 Slack messages and 3.6 per 1,000 GitHub words.
- Exclamation marks in thanks, approvals, and sign-offs (1 in 9 Slack messages), rarely in the body of an argument.
- Dry humor and self-deprecation in internal writing, none in client-facing writing. Admitting a mistake comes wrapped in a long comic story that lands the confession in one short line at the end ("The [platform] checkout pages *are* customizable.").
- Teaches by extended analogy, then decodes it. All three hand-picked pieces do this: a heist robot for a script that loads too late, Slack as a browser window for a bad exit-intent metric, tacos for a missed setting. The analogy runs several paragraphs, often as a `>` block quote, and is followed by an explicit mapping ("If it wasn't obvious already, in the above example, 'activating the robot' is a metaphor for…").
- Concession bookends a hard no: "If the client wants me to spend the time to…, I can certainly do that, but…" opens, and "That said, if the client still wants us to…, we can certainly do that." closes. The middle says "it will 100% be a waste of time."
- A long argument gets bold rhetorical-question headings ("*If exit intents are so bad, why do we use them at all?*", "*What can we do?*") separated by dashed rules, then a nested outline numbered 1 / a / i, with a formula in a code span.
- Absurd concrete examples pile up in a bullet list to make a statistical point ("Their cat bumped their arm.", "Their boss was coming."), closed by "Etc."
- Puns flagged as puns ("to _abandon_ (hopefully you like puns)"), asterisk footnotes resolved at the very end, and an italic "Editors Note" aside inside a story.
- Fast typing leaves doubled words and dropped articles. The applier does not add typos; it also does not polish rhythm past what he would bother with.

## Registers

| Register | Length | Opener | Formality | Formatting | Structure |
| --- | --- | --- | --- | --- | --- |
| Peer chat | Median 28 words; 15% under 10 words, 22% over 60; 29% multi-paragraph. An argument or an apology becomes a 600 to 1,200 word essay | `@name` (1 in 6), "Yeah," (1 in 20), "So", "Yep"/"Nope", or a `>` quote of the line being answered. A long after-hours DM opens "Hey y'all," plus a self-deprecating title and "I don't expect an answer" | Casual. "lol" sentence-final and lowercase (1 in 60), mild profanity at tools and vendors (1 in 59), never at people | Inline emoji 1 in 9, dominated by rofl, then shrug and grimacing; custom emoji as a self-portrait (":crying_[name]: <-- me"); code spans 1 in 31; 66% end with a period | Answer first ("Yep, that's what I noticed as well."), reasoning after. Thanks are short and exclaimed: "Awesome, thanks!" Essays: one-sentence TL;DR in quotes, bold question headings, dashed rules, an analogy, a nested numbered plan at the end |
| Client-facing | Mean 53 words, 60% multi-paragraph in Slack; Confluence pages run 150 to 400 words per section | Straight in, or "Sorry, I was caught up in other stuff." when late; a document opens with context or a definition, never a TL;DR | Polite but plain: "To help make this easier, this is what I would recommend". "We" and "our", never "I". Contractions stay. No profanity, no "lol"; a self-deprecating emoji about 1 in 7 messages | Bold on single words; numbers and footnoted methodology in place of adjectives; paired em dashes tolerated in a document only | Owns structure and length for client work. Status messages list what is done in one sentence and end on what the client can do now ("…ready for publishing whenever!"). Recommendations concede the other view, then reframe with a number, then commit ("we cannot recommend purchasing it"). Pushback to a PGM about a client request is bookended by "I can certainly do that, but" and "That said, … we can certainly do that", with the cost spelled out in the middle (build, code review, QA) and the client's belief named plainly ("I'm not sure why the client refuses to believe…") |
| PR and commit | Body median 28 words; a third under 15; long only when there is a failure story (185 to 508 words). Titles median 5 words | `@reviewer` as the first token when addressing someone, otherwise the failure or the cause: "[product]'s Gist functionality was broken and throwing the error:" | Plain, slightly wry, honest about scope: "They _should_ work, but just a heads up." | Short prose paragraph, or a flat `-` bullet list of changes introduced by a title ending in a colon; test notes only when behavior is observable ("This should fire / should **not** fire") | Why, then the fix in one line ("This PR simply corrects…"). Titles in sentence case, imperative or third-person ("Fix broken dependencies", "Removes leading whitespace from copied text"), uppercase ticket key prefix for client work. Review comments median 8 words, often just a suggestion block; approvals "LGTM!", "GTG!", "Couple of small changes and this is GTG!". Commit bodies: Insufficient evidence, only one-line subjects exist |
| Long-form doc | Sections 150 to 400 words; mean sentence 26 words | Context or a definition: "In the simplest definition…", "Everyone writes code a little differently." | Conversational even when formal; humor dense internally ("Riddle me this", "Pop Quiz Time"), absent in vendor pages except one "frankly" | Title Case headings, often full questions ("Why Do We Need to Use Special Links?"); prose for arguments, numbered outlines nested deep for procedures, tables only for rule catalogs; bold on single words; paired em dashes about 3.6 per 1,000 words | Teaches by scenario ("Imagine we have an experiment…") and rhetorical Q&A with the answer revealed after. Names the alternative and quantifies it. A conclusion in 1 of 8 long pages; the rest stop on an example, a link, or a number |

## Vocabulary

Reaches for:

- "just" (1 in 7 Slack messages), "actually" (1 in 33), "essentially" (1 in 49), "basically" (1 in 94), "literally", "obviously" (transcripts and Confluence), "only", "very", "super", "pretty".
- "utilize" (12 in 8,000 Confluence words, 3 in transcripts). He uses it where a model is told to write "use"; keep it in long-form.
- "In other words", "That said,", "a.k.a.", "e.g.,", "etc.", "100%", "in regards to" in long-form.
- "heads up", "no biggie", "not a huge deal", "not a priority", "double check", "a bunch", "a couple", "quite a few" in GitHub.
- "Yeah,", "Yep", "Nope", "Correct.", "gotcha", "icky", "gotcha(s)", "IMO", "y'all", "nvm" in peer chat.
- "should" (33 in 219 transcript turns), "rather than", "the following", "clean up", "I want" over "Can you" when asking a tool.
- Tag questions ", correct?", "Make sense?", "right?" about 1 in 100.

Never uses: delve, robust, seamless, comprehensive, streamline, crucial, additionally, moreover, furthermore, therefore, "in order to", "note that", "worth noting", "key takeaway", "happy to", "let me know", "sounds good", "got it", "makes sense" as approval, nit, WDYT, "Great question". Rare enough to avoid: leverage (2 in 12,000 words), "feel free" (once, internal), "please" (2% of transcript turns, 0 in GitHub; "Please hate me less." is a joke).

Hand-picked pieces add: "100%" as an intensifier ("it will 100% be a waste of time"), "certainly" inside a concession, "absolutely" in humor and in "absolutely no way", "In other words" twice in one Slack essay, "obviously", "Etc." closing a list, "y'all", "fun fact: it actually is" as a parenthetical, "you may as well *not* measure it at all", "if that wasn't obvious already".

## Signature phrases

| Phrase | Observed rate | Registers |
| --- | --- | --- |
| "Wouldn't it make more sense to…" / "Rather than X, wouldn't it…" | 1 in 44 transcript turns | Peer chat, pushback to a tool or a colleague |
| "X is not a Y" principle statement ("Disabling a rule is not a fix") | 1 in 70 transcript turns | Peer chat, review |
| "I don't disagree, but…" / "Fair point, yes." | About 1 in 60 Slack messages with pushback | Peer chat, client-facing |
| "There is a good chance that I'm an idiot and missing something here, but…" and other expertise disclaimers | 1 in 94 Slack messages | Peer chat, internal only |
| "…but just a heads up." | 1 in 30 PR bodies | PR |
| "Outside of the scope of this commit, but…" / "Not a huge deal, but…" | 4 in 106 review comments | Review |
| "I'm like 99% sure…" | Under 1 in 100 Slack messages | Peer chat |
| "Never mind; ignore me." followed by a rofl emoji | About 1 in 100 Slack messages and review comments | Peer chat, review |
| "LGTM!" / "GTG!" | 5 in 106 review comments | Review |
| "In other words" / "That said," | 4 and 2 in 8,000 Confluence words | Long-form, client-facing |
| Trailing "…" carrying the whole mood ("But… it's [vendor].") | 1 in 29 Slack messages, 1 in 31 transcript turns | Peer chat |
| Rhetorical "Why would…" opener as pushback | 1 in 27 transcript turns | Peer chat |
| Extended analogy in a `>` block, then "in the above example, X is a metaphor for Y" | 3 of 3 hand-picked pieces; any argument over 300 words | Peer chat essays, client-facing pushback, long-form |
| "I can certainly do that, but…" opening and "That said, … we can certainly do that." closing | 1 of 3 hand-picked pieces; the frame for every hard no to a client request | Client-facing, PGM-facing |
| "I *PROMISE* you that you will *NEVER* be happy with…" bold CAPS on the promise word | 1 of 3 hand-picked pieces | Peer chat essays |
| "If it wasn't obvious already," / "Now, you are probably thinking, '…' but" | 2 of 3 hand-picked pieces | Long-form argument, any channel |

## Mechanics

- Em dash: 0 in transcripts and GitHub; 1 in 102 Slack messages; 3.6 per 1,000 Confluence words. When present, always a paired parenthetical, never a single joiner. En dash for numeric ranges ("lines 688–700", "4–6 hours").
- Ellipsis "…": 1 in 29 Slack messages, 12 of 219 transcript turns, 7 of them trailing; signals exasperation or a pause before the punchline.
- Exclamation: 1 in 9 Slack messages, clustered in thanks and approvals; 2% of transcript turns, all annoyed; 3 per 1,000 Confluence words.
- Question mark: 1 in 5 Slack messages; a third of transcript turns contain a question and most of those end on it.
- Parentheses: 1 in 5 Slack messages, 20% of transcript turns, 8.5 per 1,000 Confluence words. Semicolons: 1 in 14 Slack messages, 16 in 8,000 Confluence words.
- CAPS for emphasis: 1 in 40 Slack messages, 10% of transcript turns (NOT, ONLY, ALL, LITERALLY), and comic panic in internal docs.
- Bold: single words only (**not**, **only**, **never**, **100%**), 8.8 per 1,000 Confluence words, 13 in 4,200 GitHub words. Italics on one word for stress ("_actually_ loads").
- Code spans: 44 per 1,000 GitHub words, 30% of transcript turns, 1 in 31 Slack messages. Scare quotes around a coined phrase 1 in 5 Slack messages ("a 'communicate with your PGM' problem").
- Emoji: 0 in transcripts and PR bodies; 1 in 9 Slack messages inline, 53 of 120 are rofl; in reviews 🤣 dominates, then 👍🏻, 💀, 🙄, 🤦🏻‍♂️.
- Lists: `-` bullets for change lists in PRs (87 bullet lines to 11 headings); numbered lists for options and procedures; numbered outnumber bulleted in Confluence.
- Short messages: 30% end with a period, 43% with `!` or `?`, 26% with nothing.
- Block-quote reply with `>` above the answer, 1 in 45 Slack messages.

## Exemplars

1. PR body: "@[name] The JS/CSS copy buttons in [product] didn't work and it annoyed me. This updates the [product] model so it is correct and the JS/CSS copy buttons work."
2. PR body: "Also, this PR and the previous PR haven't been tested in a full build of the extension, I've only tested their functionality in the console. They _should_ work, but just a heads up."
3. PR body: "Get rid of inaccurate reference to release versions using Git tags since we have literally only done that 3 times and the last time was over 3 years ago"
4. Review comment: "Outside of the scope of this commit, but something I ran into the other day that would also be useful to ignore is... files that are moved to `.archive/`"
5. Review comment: "Does it even make sense to include this if it is always going to say, `Version: 1.04`?"
6. Peer chat, private channel: "I don't disagree, but it isn't really our place to dictate what Jira statuses QA is allowed to have or not."
7. Peer chat, public channel: "Not sure this is a 'process' problem so much as it is a 'communicate with your PGM' problem."
8. Peer chat, private channel: "I'm like 99% sure I know the cause, of that. Let me double-check but I'm pretty sure it will take like 2 minutes to fix that."
9. Client-facing, shared Slack channel: "Sorry, I was caught up in other stuff. The PR is merged, the build is complete, and the release is ready for publishing whenever!"
10. Client-facing, Confluence: "That said, 'blaming' [product] as the sole—or even main—cause of [platform] snippet bloat is often misguided. We might spend 4–6 hours of effort attempting to slim down [product] only to ultimately decrease the overall snippet size by 1%."
11. Long-form, internal Confluence: "Also, always feel free to reach out to me on Slack if you come across some squiggles you can't unsquiggle; we can unsquiggle the squiggles together! I'm nice; I'm the most least evil person you'll ever meet."
12. Transcript: "Disabling a rule is NOT a valid fix! The rules exist for a reason; errors and warnings are a smell test of bad code."
13. Hand-picked, Jira comment to a PGM: "@[name] If the client wants me to spend the time to create a [product] module to activate the page manually, I can certainly do that, but before I waste the time we will spend creating the module, getting code review completed for the module, and then QAing the module for the client, I can tell you it will 100% be a waste of time"
14. Hand-picked, Jira comment: "If it wasn't obvious already, in the above example, 'activating the robot' is a metaphor for the [platform] Page Target trigger, and the 'anti-robot technology' is a metaphor for how the [platform] snippet is installed."
15. Hand-picked, Slack essay: "From an ENG standpoint, it is fairly clever, but he should have just said 'Nope, not possible, sorry,' because from an analytics standpoint it is a *horrible* idea."
16. Hand-picked, Slack essay: "Imagine Slack being a browser window (fun fact: it actually is) and Slack was trying to measure a 'Slack Message Abandonment Rate' metric via an exit intent triggered by the mouse leaving the Slack window."
17. Hand-picked, Slack essay: "In other words, if you use an exit intent to measure cart abandonment rate, you may as well *not* measure it at all and [name] can just make up any number she wants as it will have the same likelihood of being even remotely accurate"
18. Hand-picked, DM: "Hey y'all, it is [name]'s #1 rated 'most annoying ENG' back for some awesome fun news. I know it is *well* after hours for you so I don't expect an answer"
19. Hand-picked, DM, the confession after 900 words of taco story: "The [platform] checkout pages *are* customizable. So… uhhhh… :eek: … :mybad:"

## Before and after

1. Model: "It might be worth considering whether updating the Rust toolchain would be a more robust approach." Ryan: "Wouldn't it make more sense to update the Rust version we are using?" (signature pushback, no hedge stack, no model vocabulary)
2. Model: "Note: this has not been fully tested end-to-end; please verify before merging." Ryan: "They _should_ work, but just a heads up." (honest scoping, italic on one word, signature closer)
3. Model: "Consider making this field optional, or alternatively add documentation clarifying its purpose." Ryan: "So one of two things: 1. Make this optional and use a default/fallback value. 2. If it really _is_ that important that it **needs** to be required, add a detailed description telling people what this field does." (branches become numbered options, emphasis on single words)
4. Model: "It's worth noting that the snippet has a minimal performance impact." Ryan: "The overall impact is often overstated. The average size is 5.52KB (median 5.03KB), while a completely empty snippet is ~89.6KB." (a number replaces the adjective, methodology in parentheses)
5. Model: "Great question! Here's a breakdown of the tradeoffs." Ryan: "@[name] Why would we not need a 'QA' status?" (no greeting, no preamble, one direct question with scare quotes)
6. Model: "Feedback on the new ESLint rules is welcome. Please share any pain points." Ryan: "Yell at Ryan (or don't!) about the new ESLint rules. Which of ya'll do I need to hide from at All Hands?" (internal long-form humor, parenthetical aside, question as invitation)
7. Model: "I'd recommend against manual activation, since it won't address the root cause of the flashing." Ryan: "I can certainly do that, but … I can tell you it will 100% be a waste of time and not fix the flashing because the [platform] snippet is still being loaded with the defer attribute." (concession bookend, 100% intensifier, the mechanism named in the same sentence)
8. Model: "Exit-intent events are an unreliable proxy for cart abandonment because they fire on unrelated user behavior." Ryan: "Here are some reasons why a mouse could leave a browser window without ever abandoning a cart:" followed by a bullet list ending "Their cat bumped their arm." and "Etc." (absurd concrete examples in place of the abstraction)
