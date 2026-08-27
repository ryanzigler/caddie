---
name: cut-release
description: Drive a changesets release end to end in a pnpm workspace — cover every changed package with a changeset, confirm the plan, then run or trigger the release and verify the publish on the registry. Use for "cut a release", "release vX.Y.Z", "vX is out, create the next one", "ship what's pending", "bump and publish", or "publish the packages". Use the changeset-releases skill instead when a release already happened and something about it went wrong.
---

# Cut a release

Take the repo from "changes on main" to "version on the registry", and prove the last step.
`changeset-releases` explains the mechanics and diagnoses failures; this skill drives the
happy path and stops for one confirmation before anything leaves the machine.

Keep every command on a single line. Never `git stash`, `reset --hard`, or revert files you
did not write: the plan is inspected with `git diff`, not by undoing work.

## 1. Establish ground truth

Read, do not assume. Each item below is a fact you state back in the plan.

- **Config.** `.changeset/config.json`: `fixed`, `linked`, `ignore`, `privatePackages`, the
  `commit` hook, `baseBranch`. A `fixed` group means one changeset bumps every member.
- **Release mode.** Exactly one of:
  - **CI on merge** — a workflow on `push: main` runs `changeset version` and `changeset
    publish` itself (look for `changeset publish` in `.github/workflows/*.yml`). Humans
    only add changesets; the bot's `RELEASING:`/"Version Packages" commit is the release.
  - **Version PR** — `changesets/action` opens a "Version Packages" PR; merging it publishes.
  - **Local script** — a root script such as `release` or `bump` runs `changeset version
    && changeset publish && git push` from a laptop.
- **Baseline.** The last release commit (`git log --oneline -20 --grep RELEASING: --grep
  "Version Packages"`) and the current tag per package (`git tag --sort=-creatordate | head`).
  Tags are usually `<pkg>@<version>`, so "v0.2.0" names a package's version, not the repo's.
- **Pending.** `pnpm changeset status --verbose` — the bumps already planned. Pending
  changesets that were written before the baseline commit were consumed by it and are gone.
- **Registry.** `publishConfig.registry` or the workflow's `registry-url`; you verify
  against this later. Confirm the auth it needs is present locally only if the mode is
  local script.

**Done when:** you can name the mode, the baseline commit, and the registry, and
`changeset status` ran without error.

## 2. Resolve the target

If the user named a version ("v0.3.0"), find the package whose current version matches the
one they say is already out, and derive the bump that reaches the target. If the pending
changesets produce a different version, say so and ask which wins; do not silently bend one
to the other. In a `fixed` group, the target applies to every member.

If no version was named, the target is "everything changed since the baseline, at the bump
its changes deserve."

## 3. Cover every changed package

List packages touched since the baseline: `git diff --name-only <baseline>..HEAD -- packages
apps | cut -d/ -f1-2 | sort -u`, then map each directory to its `package.json` `name`. Also
include uncommitted work if the user means to release it; say which you included.

For each package with no pending changeset and not in `ignore`, write one directly in
`.changeset/<slug>.md` — the `changeset` CLI is interactive and cannot be driven:

```md
---
'@scope/name': minor
---

What changed, from the consumer's point of view.
```

Quote package names; scoped names break YAML unquoted. Bump by the consumer's experience,
not the diff size, and follow the "Writing changesets" rules in `changeset-releases`. A
private package coupled to a public one through `fixed` still needs its changeset.

To consolidate accumulated changesets into one, compute the effective bump per package
before and after with `pnpm changeset status --verbose` and keep them equal.

**Done when:** `pnpm changeset status --verbose` lists every changed, releasable package at
the intended bump and nothing else.

## 4. Confirm the plan

Show one block and wait for a yes:

- Mode, baseline commit, registry.
- Per package: current version → next version, bump type, the changelog line.
- Exactly what will run next and what it pushes, merges, or publishes.

Anything that leaves the machine — commit to a shared branch, push, PR, merge, publish —
waits behind this gate. Unattended runs need the gate pre-approved in the request.

## 5. Release, by mode

- **CI on merge.** Commit the changesets on a branch, push, open the PR with `gh pr create`,
  and hand the merge to the user unless they asked you to merge. If the repo's convention is
  direct pushes to `main` (the user says so, or the ruleset allows it), commit and push
  there. Then follow the release run to the end: `gh run list --workflow <release.yml>
  --limit 1` and `gh run watch <id> --exit-status`. A run skipped by its `RELEASING:` guard
  is the bot's own push, not a failure.
- **Version PR.** Commit and push the changesets, wait for the "Version Packages" PR, review
  its `CHANGELOG.md` and `package.json` diffs against the plan, and merge it only if the user
  approved merging. Watch the publish run as above.
- **Local script.** Run the build first (`pnpm build` or the script's own build step), then
  the repo's script exactly as written. Do not hand-roll `changeset version && changeset
  publish` when a script exists; it encodes the tag push and commit hook.

On a red run, stop and switch to `changeset-releases`: it separates a bump failure from a
publish failure. Re-running a red job unchanged reproduces it.

## 6. Verify the publish

Prove each package landed; the bot's green check is a claim, not proof.

- `npm view <pkg>@<version> version --registry <registry>` returns the version.
- `git ls-remote --tags origin "<pkg>@<version>"` shows the tag (skip for
  `privatePackages.tag: false`).
- The `RELEASING:` or "Version Packages" commit is on `main` and bumps the expected files.
- For a CLI package, `pnpm dlx <pkg>@<version> --version` from outside the repo runs the
  new build. A stale `dlx` cache imitates a failed publish; see
  `changeset-releases/references/stale-installs.md`.

**Reply:** per package, `<pkg> <old> → <new>`, the registry check output, the tag, and the
release commit. Anything you could not verify is marked unverified, with the command that
would settle it.
