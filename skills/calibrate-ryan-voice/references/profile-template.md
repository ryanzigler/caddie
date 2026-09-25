# Profile template

The fixed shape of `skills/ryan-voice-guide/references/profile.md`. Keep every heading, in this
order, so two calibrations diff section by section. The text under each heading here says what
the section holds; replace it with evidence.

```markdown
# Ryan's voice

Calibrated <YYYY-MM-DD>. Hand-picked pieces: <n>.

| Source | Items read | Date range | Notes |
| --- | --- | --- | --- |
<one row per source, including any marked unreachable>

## Core rules

Always: <habits present in effectively every piece, one per line>
Never: <things he does not do, one per line, each backed by a zero count in the evidence>
Usually: <habits with a rate, e.g. "Leads with the ask, then context (about 4 in 5 messages)">

## Registers

| Register | Length | Opener | Formality | Formatting | Structure |
| --- | --- | --- | --- | --- | --- |
| Peer chat | | | | | |
| Client-facing | | | | | owns structure and length for client work |
| PR and commit | | | | | |
| Long-form doc | | | | | |

## Vocabulary

Reaches for: <word or phrase, rate, register>
Never uses: <words a model would reach for that appear zero times>

## Signature phrases

| Phrase | Observed rate | Registers |
| --- | --- | --- |

## Mechanics

<punctuation, capitalization, emoji, code spans, bullets, bold, quotes, line breaks, each as a
one-line fact with a rate>

## Exemplars

<6 to 20 verbatim excerpts, each under 60 words, scrubbed, tagged with register and source; hand-picked pieces are tagged as such>

## Before and after

<3 to 8 pairs: a sentence as a model writes it, then as Ryan writes it, each pair grounded in a
cited habit above>
```

A section without evidence reads `Insufficient evidence: <what was missing>` in place of its
content. The header line `Calibrated` is what the applier checks; a profile that instead says
`Uncalibrated` makes the applier skip the voice pass.
