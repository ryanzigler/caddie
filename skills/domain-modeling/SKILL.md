---
name: domain-modeling
description: Sharpen domain terminology and record consequential design decisions. Use when defining project concepts, resolving conflicting meanings, maintaining a glossary or CONTEXT.md, or writing ADRs.
---

# Domain modeling

Read the repo's document conventions first. If `CONTEXT-MAP.md` exists, follow it to
the relevant context and its ADRs; otherwise look for an existing glossary or root
`CONTEXT.md`. Preserve the repo's layout. Create a root `CONTEXT.md` and `docs/adr/`
only when there is an agreed term or decision to record and no established location.

During design discussions:

- Challenge words that conflict with the glossary. Distinguish different concepts
  that share a name, and synonyms that refer to one concept.
- Propose a canonical term and test its meaning with concrete edge cases. Ask about
  cardinality, lifecycle, ownership, and what happens when relationships change.
- Check factual claims against code. Distinguish current behavior, intended behavior,
  and an unresolved discrepancy.
- Record accepted terms promptly. Keep rejected proposals and unresolved questions
  out of the accepted glossary. When document edits were not requested or authorized,
  present the proposed entries instead.

A glossary entry gives the canonical term, a short domain definition, and misleading
synonyms to avoid when useful. Include relationships and invariants that define the
concept. Keep implementation choices, task lists, and general programming vocabulary
out of a domain glossary. Preserve unrelated content in existing context documents.

Write an ADR sparingly: the choice is costly to reverse, surprising without context,
and reflects a real tradeoff. Capture the context, decision, reason, and meaningful
rejected alternatives. Follow existing numbering and status conventions; otherwise
use the next `docs/adr/NNNN-slug.md`. Mark proposals as proposed. Preserve past accepted
records and link a superseding decision when revisiting one.

Finish with the terms and decisions changed, links to their records, and unresolved
contradictions. Agreement about terminology does not authorize code changes.
