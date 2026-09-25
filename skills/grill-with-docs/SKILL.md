---
name: grill-with-docs
description: Interview the user about an engineering design while recording agreed domain terms and consequential decisions. Use for "grill with docs", or when a design interview should maintain a glossary and ADRs. Use grilling alone for non-engineering decisions.
---

# Grill with docs

Read [grilling](../grilling/SKILL.md) for the interview and
[domain-modeling](../domain-modeling/SKILL.md) for the documentation discipline.
Run them together: ask the current round, resolve terminology from the answers,
and capture agreed definitions and decisions before the next round.

Start by reading the relevant code, existing glossary, and decision records. Use
engineering questions from grilling; establish desired behavior before choosing
implementation details. Surface differences between the current code and the proposed
model as decisions, rather than rewriting either as if they already agree.

This interview authorizes local glossary and ADR edits as agreements emerge. Proposed
answers stay in the conversation until accepted; a recommendation is not a decision.
Keep application code unchanged during an interview-only request. At the end, link the
changed documents, summarize the agreed design and any deferred questions, and apply
grilling's handoff rule. Documentation is the record of the interview, not permission
to implement it.
