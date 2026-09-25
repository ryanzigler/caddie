---
name: typescript-best-practices
description: TypeScript type-level discipline in concrete syntax. Use when reading or editing any .ts, .tsx, or .mts file, when resolving a TypeScript error, when shaping a schema, prop, or API type, and whenever a cast, `any`, or non-null assertion appears in the diff.
---

# TypeScript best practices

Apply the `principle-type-system-discipline` skill first; this skill grounds it in TypeScript syntax.

| Rule                  | Summary                                                                                                                                                                                                                                              |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Discriminated unions  | Model variants with a `kind` literal discriminant so impossible states can't be represented. No optional-field bags.                                                                                                                                 |
| Branded types         | Brand primitives with `& { readonly __brand: "X" }` so they can't be mixed up. Validate once at creation.                                                                                                                                            |
| Constructive modeling | Build the shape so the illegal value can't be constructed. `[T, ...T[]]` for non-empty, `[T, T][]` for even length, `start` plus `duration` for a range. Not a runtime guard, not a wish for refinement types.                                       |
| Simplest total type   | Keep `T[]` while every operation on it stays total. Strengthen to `NonEmpty<T>` only where the loose type forces `!`, a cast, or a "should never happen" throw.                                                                                      |
| `unknown` over `any`  | External data is `unknown`. `any` disables type checking everywhere it touches.                                                                                                                                                                      |
| No unvalidated casts  | A cast must be earned. Validate first, or write down the fact the compiler cannot see. Never add an `as` to make an error go away before you understand the error.                                                                                   |
| Narrowing hierarchy   | Discriminant switch > `in` operator > `typeof`/`instanceof` > user-defined type guard > `as`.                                                                                                                                                        |
| Type guards           | Must verify the claim. A lying guard is worse than `as`, because the bug hides behind a name that says it's safe. Name them `isX` or `hasX`.                                                                                                         |
| Exhaustiveness        | Inline `const _exhaustive: never = x;` in default arms so the compiler errors when a new variant is added.                                                                                                                                           |
| `satisfies` over `as` | Validates the value without widening literal types.                                                                                                                                                                                                  |
| Boundary validation   | Parse where data crosses in, into a named domain type. `Record<string, unknown>` (however spelled) stops at that parse. Validate once at the edge, then trust the types inside.                                                                      |
| Schema-derived types  | Reach for `Pick`/`Omit`/`Parameters`/`ReturnType`/`Awaited`/`typeof` before declaring a new interface.                                                                                                                                               |
| Object args           | Prefer an options object over three or more positional parameters, especially same-typed ones. A preference, not a law: don't churn a published or widely called signature for it, and skip it on hot paths (per-frame render, tokenizers, parsers). |
| Real tests            | Don't mock what you can run. Prefer the framework's real test primitives with leak and disposable checks, and verify UI in a running build. Mock only what you can't run locally.                                                                    |
| Structured telemetry  | Prefer structured logger diagnostics carrying enough context to debug from an id. No `console.log` in shipped code.                                                                                                                                  |
| Prefer interfaces     | If a type can be created with as an `interface` instead of a `type`, an `interface` should be used.                                                                                                                                                  |

A TypeScript error is a finding, not noise. Fix the cause. Silencing it with a cast, `any`, or a suppression comment is not a fix.

Examples for every rule: [references/patterns.md](references/patterns.md).
