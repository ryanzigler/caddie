---
name: verification-before-completion
description: Check evidence before reporting work complete, fixed, or passing. Use at implementation handoff, after a bug fix, or before claiming a change is ready to commit, review, or ship.
---

# Verification before completion

Match each completion claim to evidence from the current version of the work.
Read the requirements and diff, choose the checks that prove the affected behavior,
run them, and inspect their full results and exit status before reporting success.

- A passing linter does not establish compilation or runtime correctness.
- A bug fix needs the original symptom exercised; a regression test should have been
  observed failing for that symptom before passing with the fix.
- An agent's report is a lead: inspect the delivered changes and validation evidence.
- Passing tests do not establish requirements those tests never exercise. Use the
  repo's UI, CLI, or service verification flow for the relevant user behavior.

Reuse valid results from this session when no subsequent change invalidates them.
Re-run affected checks after edits; broaden testing when failures or impact justify
it. Distinguish pre-existing failures from new ones using evidence rather than guesses.

Report the commands run and what they establish, checks that failed or could not run,
and any requirement left unverified. If credentials or infrastructure are missing,
say what remains unknown. Never turn an intended command or expected result into a
claim that verification happened.
