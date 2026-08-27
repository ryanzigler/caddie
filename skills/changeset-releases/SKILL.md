---
name: changeset-releases
description: Diagnose and drive changesets-based releases in a pnpm workspace. Use when asked to create or consolidate a changeset; when a merge did not bump or publish a package that changed; when the version, release, or publish workflow fails; when a consumer installs a stale version or `pnpm dlx` runs an old build; when a tag needs re-cutting or deleting; or when testing an unpublished build inside a consuming repo.
---

# Changeset releases

This skill diagnoses. To drive a release from pending changes to a verified publish, use
`cut-release`.

Two questions get confused constantly: *did the version bump happen* and *did the publish
happen*. They fail separately, for different reasons, in different jobs. Establish which
one you are looking at before proposing a fix.

## Never answer from the package's `private` flag alone

Read `.changeset/config.json` first, every time. It determines what a changeset does, and
the answer routinely contradicts the intuition that private packages do not need one.

A private package's changes reach users **through its public consumer's release**. If a
`fixed` or `linked` group couples the two, then a changeset naming the private package is
exactly what triggers the consumer's release, and declining to write one silently strands
the change.

Keys that change the answer:

| Key | Effect |
|---|---|
| `fixed` | Listed packages always release together at the same version. A changeset for any member bumps all members. |
| `linked` | Listed packages share a version line but only bump when individually changed. |
| `ignore` | Listed packages never release. A changeset naming one does nothing. |
| `privatePackages` | `version` and `tag` are independent. `{ version: true, tag: false }` means private packages get versioned but not tagged. |
| `updateInternalDependencies` | Which bump a dependent gets when an internal dependency bumps. |
| `access` / `publishConfig.registry` | Where publishing goes, and therefore which auth failures are possible. |

Before saying a changeset is unnecessary, state which key you read and what it says.

## "My change didn't ship" — work in this order

Stop at the first answer that explains it. Do not skip ahead to caches.

1. **Does the registry already have it?** `npm view <pkg> versions --json` — the whole
   local-cache theory is void if the version was never published.
2. **Was a changeset merged?** Check `.changeset/*.md` on the base branch and the merge
   history. A changeset added and then consumed by an earlier release is gone.
3. **Does the changeset name the right package?** A changeset for a consumer does not bump
   its dependency, and a changeset for a dependency only bumps the consumer if a `fixed`
   group or `updateInternalDependencies` says so.
4. **Is the package in `ignore`, or private with `version: false`?**
5. **Is the dependency edge in the right field?** Version propagation walks
   `dependencies`, not `devDependencies`. An internal package that ships inside its
   consumer's output but sits in `devDependencies` will not propagate. See the
   `workspace-packages` skill.
6. **Was the version PR merged?** The default flow opens a second PR that performs the
   bump. Until it merges, nothing publishes.
7. **Did the publish job actually run?** A failing unrelated job in the same workflow can
   block the release job while the bump looks complete.

Then, and only then, consider install-side caching — see
[references/stale-installs.md](references/stale-installs.md).

## Pipeline failures

Name the failing job before reading the log. "Version Packages" failing is a bump problem:
a malformed changeset, a package named in a changeset that no longer exists, a dirty tree,
or missing write permission to push the version branch. The publish step failing is an auth
or packaging problem: registry credentials, `publishConfig.registry` pointing somewhere the
token does not cover, a version already present, or `files`/`exports` omitting built output.

Fix the cause in the repo. Re-running a red publish job without a change reproduces it.

## Writing changesets

- One changeset per coherent change, naming every package a consumer would notice.
- Bump type describes the **consumer's** experience, not the size of the diff. A behaviour
  change a consumer must adapt to is a major, however small the patch.
- Consolidating many accumulated changesets is safe when the resulting bump per package is
  unchanged. Compute the effective bump per package before and after, and state both.
- Summaries land in a changelog other engineers read. Say what changed for the consumer,
  not which files moved.

## Tags and re-cutting a release

Deleting a tag deletes the release trigger, not the published artifact. If a version is
already on the registry, cut a new version instead of re-cutting the tag.

Keep every command on a single line — no backslash continuations.

```
git push origin --delete "<tag>" && git tag -d "<tag>"
```

## Testing an unpublished build in a consuming repo

Do not publish to test. Link the workspace build into the consumer, run it there, then
unlink. See [references/stale-installs.md](references/stale-installs.md) for the
linking and cleanup commands, and for why a stale `dlx` cache imitates a failed publish.

## Reporting

Say which of the two questions failed — bump or publish — name the config key or job that
explains it, and state what you verified against the registry rather than inferred.
