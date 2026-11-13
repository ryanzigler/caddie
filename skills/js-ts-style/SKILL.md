---
name: js-ts-style
description: Ryan's JavaScript and TypeScript code style — declarations, functions, exports, imports, file size and cohesion, control flow, naming, comments, React components, whitespace, and formatting. Use whenever writing, editing, or reviewing any .js, .jsx, .mjs, .cjs, .ts, .tsx, .mts, or .cts file, when scaffolding a new JS/TS project, and when asked to match "my style", "house style", or "how I write code".
---

# JS/TS style

Types are covered by the `typescript-best-practices` skill. This skill covers everything else about how the code reads.

## Precedence

These rules hold whether a project uses any formatter or linter or none. Write code that already follows them; never rely on a tool to fix it afterward.

1. **A formatter or linter the project already runs wins** on anything it enforces. If the project defines a format or lint script, run it on the files you touched.
2. **This skill decides everything else**, in new code and in code you rewrite, even when the surrounding file does otherwise. Do not restyle untouched code outside the diff.
3. **Do not add a formatter or linter** to a project unless the user asks for one.

## Rules

| Area              | Rule                                                                                                                                                                                                                       |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Declarations      | `const` by default. `let` is a smell: reach for an expression, early return, or helper first. Never `var`. One declarator per statement.                                                                                  |
| Functions         | Arrow functions assigned to `const` for module-level helpers, components, and callbacks. `function` only when it is required: generators, overloads, or a `this` binding.                                                |
| Classes | No classes. Write functions over plain data: state is a plain object typed by an `interface`, behavior is a function that takes it, private state lives in a closure, and variants are a discriminated union. Use a class only when code outside the project requires one, such as a framework base to extend (a custom element, a React error boundary) or a library that instantiates what you pass it. |
| Arrow bodies      | Concise body when the function is a single expression; braces and `return` only when there are statements.                                                                                                                |
| Modules           | ES modules only, never `require` or `module.exports` outside a `.cjs` file. Named exports only. A default export only where a framework or tool requires one (Storybook meta, framework route files, tool config files). |
| Files | One file holds one module, component, or responsibility. Split by cohesion, not by count: when a file starts doing a second job, the second job gets its own file. Aim for 200 lines or fewer; past 200, check for a second responsibility before adding more. Never let a file reach 500 lines: split it along a responsibility boundary before the edit that would cross the line. |
| Imports           | `import type { … }` when every specifier is a type, inline `type` specifiers when mixed. Use the project's path alias (`@/…`) over `../../`. Sort by module path: packages before aliased and relative paths.                                                  |
| Guards            | Early return for the empty, error, and not-found cases, then the main path unindented. No `else` after `return`. Collapse nested `if`s that share no other statements.                                                  |
| Braces            | Brace every `if`, `else`, `for`, and `while` body. The one exception is a whole statement on a single line, like `if (!user) return;`. A body on the line after its condition always gets braces, and so does a loop nested inside one. |
| Branching         | No nested ternaries. Three or more outcomes become `if`/`else if` or a `switch` over a discriminant.                                                                                                                       |
| Loops             | `for…of` over `.forEach` and over index loops; `.entries()` when the index is needed. `find`, `some`, `includes`, `startsWith`, `endsWith` over hand-rolled equivalents. Callbacks passed to array methods always return. |
| Equality          | `===` and `!==`. The single exception is `== null` / `!= null` to test for both `null` and `undefined`.                                                                                                                    |
| Expressions       | `?.` and `??` over `&&` chains and `\|\|` defaults. Template literals over concatenation, never nested. Object shorthand. Destructure object properties. Spread over `Object.assign` and `.apply`.                         |
| Errors            | Prefer a guard to `try`/`catch`. Omit an unused catch binding (`catch {`). Never catch only to rethrow.                                                                                                                    |
| Naming            | Descriptive names with no self-minifying (`project`, not `p` or `proj`) for every variable, parameter, function, and type, including callback parameters and catch bindings (`catch (error)`, not `catch (e)`). Name a collection in the plural and each element in its singular: `users.map((user) => …)`, `for (const user of users)`. Conventional whole words like `id` and `url` are fine. camelCase values, PascalCase components, classes, and types, SCREAMING_SNAKE_CASE module-level constants. Booleans read `isX`, `hasX`, `canX`. Prefix intentionally unused bindings with `_`. |
| Data functions | Name a function that reads or writes data for what it does, wherever the data lives: a REST API, a database, app state, or a value already fetched and held in a variable. Use a verb for the action (`get`, `send`, `post`, `update`, `request`), then the resource, in the plural when it returns a collection, and the lookup key when it selects by one. `getUser(userId)` returns a user, `getUsersById(userIds)` returns the users for those IDs, `sendEvent()` sends an analytics event, and `postUserProfileUpdate(profile)` updates a user's profile. |
| Ordering          | Object literal keys, interface members, and JSX props sorted alphabetically, unless the order carries meaning (precedence, a spread that must be overridden).                                                                              |
| Complexity        | Keep functions shallow. When a function needs a comment to explain its flow, or nests past two levels, extract a named helper.                                                                                             |
| React             | Components are named arrow `const` exports. Destructure props in the signature, typed by an `interface XProps`. Return `null` early for the empty state. Keys come from stable data, never the array index.             |
| Enums             | No `enum`. Use a string-literal union, or an `as const` object when the values are needed at runtime.                                                                                                                      |

## Write it finished

The first draft is the final draft. Write what `code-simplifier` and `no-comments` would leave behind, so neither needs a second turn:

- **No comments.** A name, a type, or an extracted helper says it instead. Keep only a license header, a doc comment on a public API, an issue link for a constraint the code cannot express, or a note on behavior forced by a dependency, platform, or protocol outside the project.
- **No suppressions.** Do not add `eslint-disable`, `biome-ignore`, `@ts-ignore`, `@ts-expect-error`, or `@ts-nocheck`; fix the cause. The only exceptions are a purely stylistic or faulty lint rule and a genuinely wrong third-party type, each with one line saying which. If the cause is outside your scope, stop and tell the user the rule and the cause.
- **No dead weight.** No commented-out code, unused parameters, exports nothing imports, wrappers that only forward, or abstractions with one caller and no second on the way.
- **No defense against the impossible.** Guard at the boundary where data enters; inside it, trust the types.
- **Clarity over brevity.** Simpler means fewer concepts, not fewer characters. Do not pack logic into dense one-liners.

## Whitespace

Blank lines split a function body into the steps it performs. No formatter adds them, so write them yourself:

- A blank line before every `return` that follows another statement. A `return` that opens its block needs none.
- A blank line before and after every multi-line statement: a braced conditional or loop, a nested function, a multi-line call or object literal.
- A blank line between a group of related declarations and the code that uses them. Related single-line declarations stay together without blank lines between them.
- No blank line directly after an opening `{` or directly before a closing `}`.

```ts
const fetchImpl = async (input: string | URL, init?: RequestInit) => {
  const url = new URL(input);
  const method = init?.method ?? 'GET';

  if (init?.body instanceof URLSearchParams) {
    for (const [key, value] of init.body) {
      url.searchParams.set(key, value);
    }
  }

  calls.push({ method, path: url.pathname });

  const route = routes[`${method} ${url.pathname}`];

  if (route === undefined) {
    throw new Error(`no route for ${method} ${url.pathname}`);
  }

  return Response.json(route);
};
```

## Formatting

Where the project's formatter does not decide these, write them by hand:

- Two-space indent, single quotes, and semicolons.
- Trailing commas in every multi-line array, object, parameter list, argument list, and import.
- Lines wrap at 80 columns. When an expression wraps, the operator (`&&`, `??`, `?`, `:`, `+`) starts the continuation line.
- A call, signature, or literal that does not fit on one line puts each item on its own line.

The `js-style-guard` hook reports `var`, `.forEach`, index `for` loops, CommonJS, loose equality, `any`, an unbraced body on the line after its condition, and a `return` with no blank line after the statement before it, as soon as an edit adds them. When it fires, fix the line. If the project's own tooling or language target requires the pattern (an ES5 browser script, for example), keep it and tell the user why.
