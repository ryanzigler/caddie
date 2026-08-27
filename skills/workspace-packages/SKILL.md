---
name: workspace-packages
description: Reason about a package's entrypoints, exports map, tsconfig layout, and dependency classification inside a pnpm/turborepo workspace. Use when adding, splitting, merging, renaming, or deleting a workspace package; when adding or changing an entrypoint or `exports` map; when asked whether a directory needs its own `tsconfig.json`; when an ambient declaration or `@types` package is not being picked up; when a consumer cannot import something that exists; or when deciding whether a dependency belongs in `dependencies`, `devDependencies`, `peerDependencies`, or the pnpm catalog.
---

# Workspace packages

A published package has two contracts: what consumers may import, and what the compiler
believes about each directory. Most defects in this area are one of those two contracts
disagreeing with the filesystem. Check the contract against reality before theorising.

## Establish ground truth first

Read these before proposing anything. Do not infer the layout from the package name.

1. `pnpm-workspace.yaml` — the workspace globs and the `catalog:` block.
2. The target package's `package.json` — `name`, `private`, `type`, `exports`, `files`,
   `publishConfig`, and every dependency field.
3. Every `tsconfig*.json` at or under the package root.
4. The build script or config that produces the directory `exports` points at.

## Route by the change

- Adding or changing an entrypoint → **The exports map is the boundary** below.
- "Does this directory need its own `tsconfig.json`?" → **One tsconfig per environment** below.
- A consumer cannot import something that exists → run the resolution check below.
- An ambient type or global is not recognised → **Ambient declarations** below.
- Choosing a dependency field → [references/dependencies.md](references/dependencies.md).
- Adding, splitting, merging, or deleting a package → [references/package-lifecycle.md](references/package-lifecycle.md).

## The exports map is the boundary

Once `exports` exists, it is exhaustive: a path not listed is not importable, no matter
that the file ships. Consumer-visible rules:

- Declare every intended entrypoint. Add `"./package.json": "./package.json"` — tools read it.
- Put the `types` condition **before** `default` in each entry. Condition order is
  significant and a `types`-last entry silently resolves to no types.
- `files` must cover every directory any `exports` path resolves into, or the published
  tarball omits them while local development keeps working.
- Exporting source (`./src/foo.ts`) instead of build output is a deliberate choice, not a
  mistake — it requires the consumer to compile it. Confirm which mode the package is in
  before "fixing" one to look like the other.

### Resolution check

After a build, verify the contract rather than asserting it. Every path referenced by
`exports` must exist on disk, and each `types` target must resolve:

```
node -e "const p=require('./package.json'),f=require('fs');const bad=[];const walk=(v)=>typeof v==='string'?[v]:Object.values(v||{}).flatMap(walk);for(const s of walk(p.exports)){if(s.startsWith('./')&&!s.includes('*')&&!f.existsSync(s))bad.push(s)}console.log(bad.length?'MISSING: '+bad.join(', '):'exports paths OK')"
```

Wildcard entries (`"./*"`) cannot be checked this way — resolve one real consumer import
per wildcard pattern instead, and say which one you checked.

## One tsconfig per environment

The unit is not the directory, it is the **compilation environment**: the globals, `lib`,
and module resolution a set of files needs. A package needs a separate `tsconfig.json`
wherever those differ, and a root-level one for files sitting at the package root.

A CLI package commonly has three environments plus the root:

| Directory | Environment | Needs |
|---|---|---|
| `src/` (CLI) | Node | `types: ["node"]`, Node `lib` |
| `inject/` | Browser, injected into a host page | DOM `lib`, no Node types, its own ambient globals |
| `scripts/` | Node build-time | `types: ["node"]` |
| package root | Node, for `build.ts` and config files | a root tsconfig that includes them |

The root case is the one most often missed: a package with per-directory configs but no
root config leaves `build.ts` and root-level scripts outside every project, so they resolve
no `@types` and report errors that look like a missing dependency. If root-level files
report missing Node globals, check for a root tsconfig before touching dependencies.

Extend the shared base config rather than restating compiler options per directory.

## Ambient declarations

A `globals.d.ts` or any ambient `declare` only applies if the tsconfig governing those
files **includes** it. A declaration file sitting beside the code it describes is still
inert if `include` does not reach it, or if a nearer tsconfig takes precedence. When a
global is reported missing, confirm which tsconfig governs the erroring file and whether
its `include` covers the declaration, before adding a second declaration.

## Reporting

State which contract was wrong — the exports map, the tsconfig scope, or the dependency
field — and name the file and key you changed. When a check could not be run, say which
one and why rather than reporting the change as verified.
