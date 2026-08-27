# Adding, splitting, merging, and deleting a package

## Before splitting or merging

A package boundary earns its existence by having a different **release cadence**, a
different **consumer set**, or a different **compilation environment**. Directory tidiness
is not a reason. Merging packages that always release together removes real coordination
cost; splitting packages that always release together adds it.

State which of the three reasons applies before proposing a new boundary. If none does,
say so and recommend a directory instead of a package.

## Adding a package

1. Create the directory under a path matched by the workspace globs.
2. `package.json`: `name`, `version`, `type`, `exports`, `files`, and `publishConfig`
   matching the registry the other packages use. Set `private: true` if it is internal.
3. Add a `tsconfig.json` extending the shared base — including one at the package root if
   root-level files exist.
4. Reference dependency versions through the catalog where one exists.
5. Wire the build and test scripts to the names the pipeline already calls, so the root
   task runner picks it up with no extra configuration.
6. Run the workspace's own check task from the repo root and confirm the new package is
   included in the run. A package the pipeline silently skips looks healthy and is not.

## Deleting a package — caller inventory first

Deleting the directory is the last step, not the first. Inventory callers before removing
anything, because a workspace-internal consumer fails at build time while an external
consumer fails after publish, when it is expensive.

```
grep -rn "@scope/package-name" --include=package.json --include=*.ts --include=*.tsx --include=*.json --include=*.yaml --include=*.yml . | grep -v node_modules
```

Then work the checklist. Each item has produced a real broken state:

- [ ] Every importing package migrated off it, in the same change.
- [ ] Removed from other packages' dependency fields.
- [ ] Catalog entries in `pnpm-workspace.yaml` that existed only for it.
- [ ] `tsconfig` `references`, `paths`, or `include` entries naming it.
- [ ] CI job matrices, workflow filters, and required-check names.
- [ ] `.changeset/config.json` — `fixed`, `linked`, and `ignore` arrays list packages by
      name and do not error when a listed package disappears.
- [ ] Root README and any docs listing the packages.
- [ ] Lockfile regenerated.
- [ ] If it was ever published, deprecate the published versions on the registry rather
      than assuming deletion from the repo reaches installed consumers. Unpublishing is
      usually the wrong tool and may be blocked by the registry.

## Renaming

A rename is a delete plus an add, with one addition: the old name keeps resolving for
anyone who has already installed it. If external consumers exist, publish a final version
of the old name that re-exports the new one and deprecate it with a message naming the
replacement. Do not treat a rename as a refactor when the name is on the registry.

## Verifying a boundary holds

The cheap check is that nothing imports past a package's declared entrypoints. Deep
imports into another package's internals compile locally through the workspace symlink and
then fail for a real consumer, because `exports` does not admit them.

```
grep -rnE "from ['\"]@scope/[a-z0-9-]+/(src|dist|lib)/" --include=*.ts --include=*.tsx . | grep -v node_modules
```

Any hit is either a missing entrypoint in the target package's `exports` or an import that
should go through an existing one. Decide which, and say which.
