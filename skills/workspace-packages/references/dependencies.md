# Classifying a dependency

Decide by asking what the **consumer's install** needs, not by what makes the local build pass.

| Field | Test |
|---|---|
| `dependencies` | The consumer needs this at runtime after installing the package. |
| `devDependencies` | Only this repo needs it — tests, linting, the build toolchain. Never reaches a consumer. |
| `peerDependencies` | The consumer must supply it, and two copies would break (React, a bundler plugin's host). |
| `optionalDependencies` | Install may fail and the package still works. |

## The failure that keeps recurring

**A workspace package that is bundled into a published package's output is not a
devDependency.** If the only way a change to package B ever reaches a user is through
package A's release, then B participates in A's publish, whatever B's `private` flag says.

Getting this wrong produces a specific, confusing symptom: the local build works, the
publish succeeds, and the released package is missing behaviour — or the release does not
happen at all, because version propagation walks `dependencies` and does not walk
`devDependencies`. See the `changeset-releases` skill for the release half of this.

Before classifying an internal workspace dependency, answer in writing:

1. Is B's code present in A's published output, or does A load B at runtime?
2. If B changes and A is not re-released, can a user observe B's change? If no, B is part
   of A's release path.
3. Does the release configuration already encode that coupling (a `fixed` or `linked`
   group in `.changeset/config.json`)? If it does, the dependency field must agree with it.

## Workspace protocol

Internal dependencies use `workspace:` so they resolve to the local package and are
rewritten to a real version range on publish. Confirm the rewrite happened by inspecting
the packed tarball rather than the source `package.json`:

```
pnpm pack --pack-destination /tmp && tar -xzOf /tmp/*.tgz package/package.json | head -60
```

## pnpm catalog

When `pnpm-workspace.yaml` defines a `catalog:`, a dependency version lives there once and
each package references it as `"catalog:"`. Add the version to the catalog and reference it;
do not pin a second copy in the package. A version pinned directly in a package that also
exists in the catalog is a drift bug waiting to happen — flag it rather than matching it.

A published package's catalog references are resolved at publish time, so a catalog entry is
still a real constraint on consumers for anything in `dependencies`.
