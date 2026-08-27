# Patterns to detect and fix

Use this catalog during the editing pass. Fix patterns in context. Do not make mechanical replacements that change meaning or create worse prose.

## Content

1. **Puffery.** Phrases such as "pivotal moment," "testament to," "evolving landscape," "setting the stage for," "indelible mark," and "deeply rooted" inflate ordinary claims. State what happened.
2. **Name-dropping.** A list of publications or authorities is not evidence. Keep the relevant source and say what it reported.
3. **Superficial -ing phrases.** Tacked-on clauses such as "highlighting," "ensuring," "reflecting," "showcasing," and "fostering" often pretend to explain significance. Delete them or make the causal claim explicit and support it.
4. **Promotional language.** Words such as "nestled," "vibrant," "breathtaking," "groundbreaking," "renowned," "stunning," and "must-visit" read like ad copy. Use neutral, concrete descriptions unless promotion is the requested tone.
5. **Vague attribution.** "Experts believe," "industry reports suggest," and "some critics argue" hide the source. Name it or remove the claim.
6. **Formulaic adversity.** "Despite challenges, it continues to thrive" says little. Name the setback and the actual result.

## Language

7. **Stock AI vocabulary.** Watch for additionally, crucial, delve, enduring, enhance, fostering, garner, interplay, intricate, landscape used abstractly, pivotal, showcase, tapestry used abstractly, testament, underscore, and vibrant. Prefer the plain word that fits the sentence.
8. **Fancy forms of "is" or "has."** "Serves as," "stands as," "boasts," and "features" often add nothing.
9. **"Not just X, but Y."** State the real point directly.
10. **Forced groups of three.** Use the natural number of examples or claims.
11. **Synonym cycling.** Do not rotate through "protagonist," "main character," "central figure," and "hero" to avoid repetition. Pick the accurate term and reuse it.
12. **False ranges.** Avoid "from X to Y" when the endpoints do not form a meaningful scale. Name the topics directly.

## Style

13. **Em dash overuse.** Repeated em dashes create a recognizable rhythm. Prefer a period or comma when the sentence does not need the interruption. Do not replace every dash with parentheses or a hyphen.
14. **Colon overuse.** Colons work before lists and examples. Rewrite colons used as generic mid-sentence connectors.
15. **Boldface overuse.** Do not bold every proper noun, acronym, or key phrase.
16. **Inline-header lists.** A bold label followed by a colon often restates the same words: "**Performance:** Performance improved." Use prose or make the lead-in carry distinct information.
17. **Title Case Headings.** Use sentence case unless the requested style says otherwise.
18. **Decorative emoji.** Remove emoji that decorate headings or bullets without conveying information.
19. **Typographic mannerisms.** Do not normalize straight or curly quotes against the project's established style. In plain-text and code-oriented docs, prefer straight quotes unless instructed otherwise.

## Communication artifacts

20. **Chatbot phrases.** Cut "I hope this helps," "Let me know if," "Of course," "Certainly," and theatrical claims such as "Found the smoking gun." Respond directly.
21. **Cutoff disclaimers.** "While specific details are limited" is not a substitute for evidence. Find the source, state the known limit precisely, or remove the claim.
22. **Sycophancy.** Cut reflexive praise such as "Great question" and "You're absolutely right." Address the substance.

## Filler

23. **Filler phrases.** "In order to" becomes "to." "Due to the fact that" becomes "because." Delete "It is important to note that."
24. **Stacked hedges.** "Could potentially possibly be argued that it might" becomes one accurate hedge, often "may."
25. **Generic conclusions.** Replace "The future looks bright" with a specific plan, consequence, or fact. If there is none, stop earlier.

## Jargon

26. **Abstract metaphor nouns.** Substrate, wedge, vector, locus, vantage, nexus, primitive used as a noun, harness used metaphorically, API surface, bedrock, scaffolding used metaphorically, modality, paradigm, gold-plating, ratchet used metaphorically, evacuate for moving code, endgame, north star, and flywheel often hide a simpler concrete term. Name the actual mechanism. For example, "substrate" may mean "base," "wedge in" may mean "add," and "evacuate" may mean "move out."

## Plain speech

27. **Feelings in place of mechanisms.** "The database stays close at hand," "SQL you can read," and "types that follow your schema" evoke a feeling without explaining behavior. Name the mechanism, instruction, or number: "`.toSQL()` returns the exact string sent to the database" or "a column rename fails the build." If a sentence could appear unchanged in another project's docs, it probably says nothing about this project.
28. **Dense sentences.** If a reader must backtrack, split the sentence or drop clauses. Give each sentence one main job.
29. **Unnecessary passive voice.** Prefer a named actor when it matters: "the compiler validates queries" instead of "queries are validated." Keep passive voice when the actor is unknown or irrelevant.
30. **Adverbs propping up weak verbs.** Replace "significantly improves" with the measured change. Use a stronger verb when one exists. Keep an adverb when it carries real meaning.
31. **Fancy synonyms for plain words.** "Utilize" becomes "use," "leverage" often becomes "use," "facilitate" becomes "help," "numerous" becomes "many," and "in the event that" becomes "if."

## Final audit

Check the edited text for:

- repeated sentence shapes or transitions;
- polished but empty claims;
- examples that could belong to any project;
- opinions or personality added without support;
- a rewrite that no longer sounds like the intended author.
