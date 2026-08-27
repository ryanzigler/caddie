# Placement, ownership, and layering questions

Questions like "which package owns this", "is this the right layer", "do these need their own tsconfig", "should this be its own package" are not subsystem walkthroughs. They are answered from the workspace and build configuration plus the real import graph, and they are wrong more often than not when answered from directory names and intuition.

**Read the config before reasoning about it.** Every answer in this mode must cite specific config files and specific imports.

## What to read first

Read these before forming an opinion. Skip the ones the repo does not have.

- The workspace definition: `pnpm-workspace.yaml`, or `workspaces` in the root `package.json`, or the equivalent for whatever tool is in use.
- The task graph config: `turbo.json`, `nx.json`, or the root scripts.
- Each candidate package's `package.json`: `name`, `exports`, `main`, `types`, `files`, `dependencies`, `peerDependencies`, `devDependencies`, `publishConfig`, `sideEffects`.
- The tsconfig chain: the root config, each package's config, and what they extend. Note `references`, `composite`, `paths`, `moduleResolution`, `lib`, `target`, `jsx`, `types`.
- The release config if one exists: `.changeset/config.json` (`linked`, `fixed`, `ignore`, `access`).

Useful commands, one per line:

```
pnpm ls -r --depth -1
pnpm why <package-name>
pnpm ls --filter <package-name> --depth 0
npx tsc -p <path/to/tsconfig.json> --showConfig
turbo run build --dry=json
```

To find who actually imports the thing, grep for the import specifier rather than the file name, since re-exports hide the real consumer:

```
grep -rn "from '@scope/pkg" --include=*.ts --include=*.tsx .
```

## The questions and the evidence each one needs

### "Which package owns this?"

Evidence: the set of packages that import it today, and the direction of the dependency edges that each candidate placement would create.

Decide by dependency direction, not by topical fit. A module belongs in the package that all of its consumers already depend on, or in a package all of them can depend on without a new edge. If placing it in the topically obvious package would require that package to take a dependency on a consumer, that placement is wrong regardless of how well the name fits.

Always check for a cycle. Two packages that both need the module are a signal it belongs one level down, in a shared package, not in either of them.

### "Is this the right layer?"

Evidence: what the module imports, and what imports it.

A layer violation looks like a lower-level module importing from a higher-level one: a shared utility reaching into an app, a data-access module importing a UI type, a CLI package importing from a package that depends on it. Name the specific import that inverts the direction. "It feels like the wrong layer" is not an answer.

### "Do these need their own tsconfig?"

A separate tsconfig earns its existence only when the compiler genuinely needs different settings. Real reasons:

- Different `lib` or `types` (DOM versus node, or a test-only global set).
- Different `target`, `module`, or `moduleResolution` because the output is consumed differently.
- Different `jsx` setting.
- Project references, where `composite: true` plus `references` buys incremental builds and enforces the dependency graph at type-check time.
- A build config that must exclude tests while the editor config includes them.

Not reasons: wanting a separate `include` list that a single config already covers, wanting different `paths` that could be a workspace dependency instead, or symmetry with a sibling package that had a real reason.

Answer by naming which specific compiler options would differ. If none would, the answer is no.

### "Should this be its own package?"

Evidence: release cadence, consumer set, and dependency weight.

Extract when the module has consumers outside the current package's dependents, needs to version independently, or would let consumers avoid a heavy dependency. Do not extract for tidiness. Every extraction adds a package.json, a tsconfig, a build step, a changeset surface, and a version to keep in sync.

Say what the extraction costs, not just what it buys.

### "Should this be a separate entrypoint?"

Evidence: the `exports` map, what consumers import, and whether the module has side effects.

A subpath export is the cheaper alternative to extraction: it splits the public surface without splitting the release unit. Check whether the build tooling actually emits the extra entrypoint and whether `sideEffects` is set correctly, or consumers will pull in the whole package anyway.

## Answer shape

Answer in this structure. It is short on purpose; these questions want a decision, not an essay.

**Recommendation.** One or two sentences. Take a position.

**Why.** The dependency edges, config settings, or imports that drive it. Cite files and specifiers.

**What moves.** The concrete files, and their destination.

**Config changes required.** The exact `package.json`, tsconfig, and task-graph edits. Do not hand-wave this; it is usually where the real cost lives.

**What breaks.** Consumers that need updating, whether this is a breaking change for published packages, whether a changeset is needed and at what bump, and whether any lockfile or CI change follows.

**Alternatives rejected.** The placements you considered and the specific reason each loses. If the call is genuinely close, say so rather than manufacturing confidence.

## Failure modes

- Answering from directory names and package names without reading a single config file.
- Recommending extraction without enumerating the consumers that would have to change.
- Missing a dependency cycle that the recommended placement would create.
- Adding a tsconfig without naming an option that would actually differ.
- Treating the existing layout as correct by default. It is evidence of what someone did, not of what is right.
- Ignoring the release surface. In a published monorepo, a placement change is often a breaking change for someone.
