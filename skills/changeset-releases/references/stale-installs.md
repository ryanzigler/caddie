# Stale installs, caches, and release age

A consumer running an old build looks identical to a failed publish. These are different
problems and the check order matters, because clearing caches "fixes" nothing when the
version was never published and wastes the diagnosis.

Keep every command on a single line — no backslash continuations.

## 1. Confirm what the registry has

```
npm view <pkg> versions --json
```

```
npm view <pkg> dist-tags
```

If the expected version is absent, this is a publish problem. Stop here and go back to the
`changeset-releases` pipeline section. If it is present, note its publish timestamp — you
need it for the release-age check below.

```
npm view <pkg> time --json
```

## 2. Release age can delay a fresh version deliberately

pnpm can refuse to install a version younger than a configured age. When that setting is
active, a correctly published version is unavailable to installs for that window, which
presents as "the publish did not work."

Check the workspace and the user config for a minimum release age setting and for its
exclusion list, then compare the version's publish timestamp against the window:

```
grep -rn "minimumReleaseAge" pnpm-workspace.yaml .npmrc ~/.npmrc 2>/dev/null
```

If a package needs to bypass the window, it goes in the exclusion list beside the setting
rather than the window being removed globally. Confirm the setting's exact name against
the installed pnpm's documentation before editing — do not guess the key.

## 3. The dlx cache

`pnpm dlx` resolves and caches independently of any project's lockfile, so it can keep
running an old build after a successful publish.

Verify which version is actually executing before clearing anything — a version pin in the
invocation is a more common cause than a stale cache:

```
pnpm --package=<pkg>@latest dlx <bin> --version
```

To force a fresh resolution, pin the exact version in the invocation:

```
pnpm --package=<pkg>@<exact-version> dlx <bin>
```

The cache directory can be located rather than assumed:

```
pnpm store path
```

```
pnpm config get cache-dir
```

Clearing a cache is a last resort and it hides the real cause. If clearing appears to fix
it, say that the underlying resolution question is still unanswered.

## 4. CI installs

CI runners have their own cache keyed independently of a developer machine, so a stale run
in CI proves nothing about a local install and the reverse. When a CI log shows an old
version resolving, read the resolved path in the stack trace — it usually names the exact
version that ran, which is faster than reasoning about cache state.

## Testing an unpublished build in a consuming repo

Publishing to test pollutes the version history and burns a version number. Link instead.

Build the package first, then link the workspace copy into the consumer:

```
pnpm --filter <pkg> build
```

```
cd <consumer-repo> && pnpm link --global <path-to-package>
```

For a CLI, running the built entrypoint directly avoids linking altogether and is usually
the faster check:

```
node <path-to-package>/dist/<entry>.js <args>
```

Undo the link when finished, and confirm the consumer resolves the published version again
rather than assuming the unlink took:

```
cd <consumer-repo> && pnpm unlink --global <pkg> && pnpm install
```

Leaving a link in place is a real hazard: the consumer keeps building against local source,
so a broken published package looks healthy until someone else installs it.
