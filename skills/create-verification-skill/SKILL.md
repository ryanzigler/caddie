---
name: create-verification-skill
description: "Generate a project-local verification skill that drives the real app the way a user does — any language, framework, or platform — and prove it runs before handing it over. Use for /create-verification-skill, \"make a control skill for this repo\", or when a project has no scripted way to prove UI, CLI, or service behavior."
disable-model-invocation: true
---

# Create a verification skill

Every serious project needs a scripted way to drive the real app and prove behavior:
launch it, exercise a feature the way a user would, capture evidence. This skill generates
that as a project-local skill at `.claude/skills/verify-<app>/`, tailored to the repo. It
is what [verification-before-completion](../verification-before-completion/SKILL.md) assumes already exists — without a
harness, "verified" collapses back into "the tests passed".

Write the generated output for the next agent, not for a human. It will be read cold,
mid-task, by an agent that has never seen the app.

## 1. Interview the repo, not the user

Answer these from the codebase and only ask the user what you cannot observe:

- **Surface:** what does a user actually touch? A web UI, a CLI/TUI, a desktop app, an
  API, a mobile app, a library? A repo can have several; pick the primary one and note the
  rest.
- **Run:** how does the app start locally? Prefer the repo's own documented dev command
  (package scripts, Makefile, README quickstart). Note ports, env vars, seed data, auth.
- **Drive:** how can an agent interact with it programmatically? Existing harnesses first —
  Playwright/Cypress specs, expect scripts, PTY helpers, curl-able endpoints, a debug
  port. Only then pick a generic recipe: a browser or CDP session for web and Electron, a
  tmux/PTY harness for CLI/TUI, plain HTTP for services.
- **Observe:** what evidence can be captured? Screenshots, terminal transcripts, response
  bodies, logs, exit codes, DB state.
- **Isolate:** can two instances run side by side (ports, data dirs, profiles)? If not, say
  so in the generated skill: refusing to double-drive a shared instance beats corrupting
  the user's session.

If the checkout does not build or start as-is, fix that first (or report it precisely)
before generating. A skill written against a broken base teaches wrong steps. When an
irrelevant missing asset blocks startup (a static dir the API never serves, a sample
config), the generated skill may create it, clearly marked as verification scaffolding,
and remove it in cleanup.

## 2. Generate the skill

Write `.claude/skills/verify-<app>/SKILL.md` with frontmatter of exactly `name:
verify-<app>` and a `description` naming the app, the surface, and when to reach for it.
Without frontmatter the skill never registers. Reach for the `skill-creator` skill if you
need the authoring mechanics.

Each section below must be grounded in what the interview actually found, with no
placeholders left:

- **Launch:** the exact command that starts the app for verification, and how to tell it is
  ready (a log line, a port answering, a prompt). Include teardown. For a short-lived CLI
  or TUI there is no server to keep alive: launch means build the binary (or install deps)
  once, then start each drive in its own isolated PTY or tmux session.
- **Doctor:** one read-only check answering "is this instance worth driving?" — process up,
  right version/build, port owned by us, auth valid. An agent runs this first whenever
  anything looks off.
- **Drive:** the harness recipe with real selectors and commands from this repo, not
  examples. Prefer stable handles (ARIA labels, data attributes, prompt strings, route
  paths) over coordinates and tab order.
- **Evidence:** what to capture for a proof and where it goes. State the proof standards:
  exercise the real user path, not internal setters or test-only endpoints; capture the
  action and the resulting state, not just the final screen; verify side effects (files
  written, rows inserted, messages sent) alongside what is visible; mocks only where a
  production boundary already isolates the external system. When the safe path is a dry-run
  or test mode, verify what it actually skips by observing files, network, and git refs
  rather than trusting its name — some dry-runs still hit the network or open a browser.
- **Cleanup:** how to tear down instances the run created. Never kill by process name; kill
  what you started. Cleanup removes instances and scratch state, never the evidence: proof
  artifacts survive teardown, in a location the skill names.
- **Helpers:** any script the skill ships is executable and its invocation is shown in the
  skill body. A helper the reader has to reverse-engineer is not a helper.

## 3. Seed the feature map

Create `.claude/skills/verify-<app>/features/README.md` plus one file per user-facing
feature you can identify (aim for the top 3-5 to start, from routes, commands, menus, or
docs). Follow the shape in
[`references/feature-map-example/`](references/feature-map-example/): a README index and
one file per feature. Each file answers, from the user's point of view, what the feature
is, how to reach it, how to drive it with the harness, and what observable end state proves
it works. The four H2s are `Sub-features`, `How to get to it (user POV)`,
`Driving it with <harness>`, and `Gotchas`.

The map is the repo's maintained verification source. A proof that drives one convenient
entry point is incomplete when the map lists others.

## 4. Prove the generated skill before handing it over

**This is the step that makes the difference between a deliverable and a draft.** Run the
generated skill's own instructions end to end, once: launch, doctor, drive ONE mapped
feature (one is enough — the map exists so later runs cover the rest), capture evidence,
clean up. After cleanup, confirm the evidence still exists at the named location; a cleanup
that eats the proof fails this step.

Fix what fails and run it again. Run the generated cleanup after every failed iteration
too, so broken attempts do not strand processes and ports. A generated skill that was
never executed is a draft, not a deliverable — do not hand it over and do not describe it
as working.

## 5. Keeping it current

Say this in the handoff, and write the short version into the generated
`features/README.md` so the next agent inherits it.

- The map rots the moment the app changes. When a route, command, flag, selector, or
  user-visible flow changes, the matching feature file changes in the same commit as the
  code. Treat a stale recipe as a broken test.
- A drive step that fails is a fork in the road: either the app regressed or the map is
  wrong. Determine which before editing either one. Silently rewriting the map to match new
  behavior is how a regression gets ratified.
- Add a feature file when a feature ships, not later. Delete one when the feature goes.
- Re-run step 4 against the changed feature after editing its file. An edited recipe that
  was never executed is back to being a draft.
- Prune the evidence directory on its own schedule; never as part of cleanup.
