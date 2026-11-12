# TypeScript patterns

Code examples for each rule in `SKILL.md`. The underlying principles are language-agnostic; see the `principle-type-system-discipline` skill.

## Branded types

Brand primitives so they can't be mixed up. Validate once at creation; downstream code trusts the type.

```ts
type AgentId = string & { readonly __brand: 'AgentId' };

const parseAgentId = (input: string) => {
  if (!isUUID(input)) throw new Error(`Invalid agent id: ${input}`);

  return input as AgentId; // brand constructor: the UUID check above is the proof
};

const focusAgent = (id: AgentId) => {
  /* input is trusted */
};
```

Match the `readonly __brand: 'X'` shape; don't invent a new convention. The constructor is the one place our own code casts.

## Discriminated unions

If a bug forces the question "wait, can this combination actually happen?", the type is too loose. Model variants with a literal discriminant: every variant shares the field name and each variant's value is unique, so impossible combos can't be represented.

```ts
// Don't. Boolean + optionals lets contradictory states exist.
interface DiffState {
  diff?: GitDiff;
  error?: string;
  loading: boolean;
}

// Do. Only valid states exist.
type DiffState =
  | { kind: 'loading' }
  | { diff: GitDiff; kind: 'ready' }
  | { error: string; kind: 'error' };
```

Pick one discriminant name (`kind`, `type`, `tag`) and stick to it.

## Constructive modeling

Build the type from parts that are all legal instead of restricting a loose type with runtime checks. Adding is easier than subtracting.

Non-empty, via a variadic tuple:

```ts
type NonEmpty<T> = [T, ...T[]];

// Don't: T[] plus a length check every caller must repeat
const pickWinner = (entries: string[]) => {
  if (entries.length === 0) throw new Error('no entries');

  return entries[Math.floor(Math.random() * entries.length)];
};

// Do: an empty value of the type can't exist
const pickWinner = (entries: NonEmpty<string>) =>
  entries[Math.floor(Math.random() * entries.length)];
```

Where a plain `T[]` arrives, narrow once with a guard. The fact then travels in the type:

```ts
const isNonEmpty = <T>(items: T[]): items is NonEmpty<T> => items.length > 0;
```

Even length, as pairs. TypeScript has no refinement types (no `items.length % 2 === 0` at the type level); you don't need one:

```ts
type Pairs<T> = [T, T][];
```

A time range, as start plus duration:

```ts
// Don't: a comment holds the invariant
interface TimeRange {
  end: Date; // start <= end
  start: Date;
}

// Do: a negative range can't be written; derive end when needed
interface TimeRange {
  durationMs: number;
  start: Date;
}
```

Keep `durationMs` a plain number. Brand it (per Branded types) only if a raw number could be passed where a duration is expected, not by reflex. A `Pairs<T>` is an even-length list under the interpretation you give it, the same way `{ start, durationMs }` is a range. Pick the representation that makes the bad state unconstructable, then expose the reading you need on top (`pairs.flat()`, a `rangeEnd()` helper).

## Simplest total type

Don't strengthen everything. Keep `T[]` when every operation on it is total:

```ts
const sum = (values: number[]) => values.reduce((total, value) => total + value, 0); // [] is 0, fine
```

Strengthen when the loose type forces a lie at a use site. The tells are `!`, `items[0] as T`, and a "should never happen" throw:

```ts
// Don't: partiality smuggled past the compiler
const newestSession = (sessions: Session[]) => sessions.at(0)!;

// Do: strengthen the input; the assertion disappears
const newestSession = (sessions: NonEmpty<Session>) => sessions[0];
```

Weakening the result to `Session | undefined` is the other total signature. Either way the empty case lands at the call site, the one place that knows what empty means.

## Inferred return types

The compiler already knows what a function returns. An annotation restates it, drifts when the body changes, and can widen what callers see.

```ts
// Don't. Restates the body and widens 'admin' | 'guest' to string.
const roleFor = (user: User): string => (user.isAdmin ? 'admin' : 'guest');

// Do. Inferred as 'admin' | 'guest'.
const roleFor = (user: User) => (user.isAdmin ? 'admin' : 'guest');
```

Annotate only where the compiler needs it:

- A type predicate (`items is NonEmpty<T>`) or an assertion function (`asserts value is User`). The annotation is the feature.
- An overload signature.
- Recursion the compiler reports it cannot infer.
- A project with `isolatedDeclarations` on, which requires annotations on exports.

When inference comes out too wide, fix the returned value first: `as const` for literals, `satisfies` to check a shape without widening it.

## `unknown` over `any`

`any` disables type checking for everything it touches. External data is always `unknown`. Narrow before use.

```ts
// Don't
const handle = (input: any) => input.foo.bar;

// Do
const handle = (input: unknown) => {
  if (typeof input === 'object' && input !== null && 'foo' in input) {
    // narrowed; compiler verifies access
  }
};
```

External sources include RPC payloads, `JSON.parse`, `postMessage`, IPC, file contents, environment variables, database results.

## No casts on our types

We declare every type in this codebase, so the type of our own values is never a mystery. A cast or non-null assertion on one of them is a smell: it says a type upstream is wrong or too loose. Fix that type instead of asserting past it.

```ts
// Don't. Our own reducer, asserting what its own types should say.
const session = state.sessions.find((session) => session.id === id) as Session;
const title = (event.payload as RenamePayload).title;

// Do. Handle the case the type reports, and model the payload as a variant.
const session = state.sessions.find((session) => session.id === id);

if (session === undefined) return state;

if (event.kind === 'rename') {
  const { title } = event.payload; // narrowed by the discriminant
}
```

When an `as` or `!` shows up on our own code, find why the compiler doesn't already know:

- Missing discriminant: add one, switch to a discriminated union.
- Overly wide source type (e.g. `Record<string, unknown>`): narrow it where it is declared.
- An annotation that widened a value: remove it and let inference keep the narrow type.
- Genuinely inexpressible: use a branded type or `satisfies`.

Casts belong only at the edge with code we don't control, and in the brand constructor above:

- A third-party type that is wrong at its source.
- A DOM API typed wider than the markup we wrote (`querySelector` returns `Element`).
- External data, and only after it has been validated. Prefer building the domain value from narrowed fields so no cast is needed:

```ts
const parseUser = (data: unknown) => {
  if (typeof data !== 'object' || data === null) {
    throw new Error('expected object');
  }

  if (!('id' in data) || typeof data.id !== 'string') {
    throw new Error('expected id');
  }

  if (!('name' in data) || typeof data.name !== 'string') {
    throw new Error('expected name');
  }

  return { id: data.id, name: data.name } satisfies User;
};
```

`satisfies User` is a check, not a cast: the compiler verifies the object against `User` without an annotation on the function. Keep each remaining cast's reason next to it in one line. A cast added to make a type error go away before the error was understood is never acceptable; treat the error as the finding and fix its cause. `as const` is not a cast and is always fine.

## Narrowing hierarchy

From best to last-resort:

1. **Discriminated union switch / if.** Compiler narrows automatically.
2. **`in` operator.** `'key' in obj` narrows to variants containing that key.
3. **`typeof` / `instanceof`.** For primitives and platform or library class instances.
4. **User-defined type guard.** When the above aren't enough.
5. **`as` cast.** Only at the edge of code we don't control, after validation.

```ts
const area = (shape: Shape) => {
  if ('radius' in shape) return Math.PI * shape.radius ** 2; // narrowed to circle

  return shape.width * shape.height; // narrowed to rect
};
```

## Type guards

A guard must actually verify the claim. A lying guard is worse than `as` because the bug hides behind a name that says it's safe.

```ts
const isCircle = (shape: Shape): shape is Shape & { kind: 'circle' } =>
  shape.kind === 'circle';
```

Prefer discriminant narrowing when possible. The guard adds a layer the reader has to follow.

## Exhaustiveness

In default arms, assign the discriminant to a `never`-typed local. The compiler errors if a new variant is added without handling.

```ts
// Value-returning switch
const area = (shape: Shape) => {
  switch (shape.kind) {
    case 'circle':
      return Math.PI * shape.radius ** 2;
    case 'rect':
      return shape.width * shape.height;
    default: {
      const _exhaustive: never = shape;

      return _exhaustive;
    }
  }
};

// Void switch
const draw = (shape: Shape) => {
  switch (shape.kind) {
    case 'circle':
      drawCircle(shape);
      break;
    case 'rect':
      drawRect(shape);
      break;
    default: {
      const _exhaustive: never = shape;
      void _exhaustive;
    }
  }
};
```

Return-style in value-returning switches; void-style in statement switches.

## `satisfies` over `as`

`satisfies` validates without widening literal types.

```ts
// Don't. Widens, loses literal types, and skips excess-property checks.
const config = { cols: 3, theme: 'dark' } as Config;

// Do. Validates AND preserves literal types.
const config = { cols: 3, theme: 'dark' } satisfies Config;
// config.theme is 'dark' (literal), not string
```

## Boundary validation

Validate once where data crosses in; trust types inside. The parse function is the only place that sees unstructured input, and it returns a named domain type.

- **Wire formats** (proto, JSON-RPC): parse with `ignoreUnknownFields` so forward-compatible changes don't break old clients.
- **Persisted JSON:** versioned blob with a try/catch around the parse.
- **Don't re-validate** deep in call chains.

## Schema-derived types

When a `.proto`, OpenAPI spec, GraphQL schema, or database migration already defines a shape, derive from the generated types instead of duplicating them.

```ts
// Don't. Duplicate shape, drifts when the schema changes.
interface CheckSummary {
  checks: { name: string; status: string }[];
  totalCount: number;
}

const renderChecks = (summary: CheckSummary) => {
  /* ... */
};

// Do. Derive from the generated schema type.
import type { ChecksMessage } from '<generated module>';

const renderChecks = (summary: Pick<ChecksMessage, 'checks' | 'totalCount'>) => {
  /* ... */
};
```

Reach for `Pick`, `Omit`, `Parameters`, `ReturnType`, `Awaited`, `typeof` before writing a new interface.

## Object args

A preference, not a law. It earns its keep on three or more parameters, and most of all on adjacent same-typed ones, where a swap still compiles. Two clearly different parameters are fine positional. Don't churn a published or widely called signature to satisfy this rule; apply it to new code and to signatures you are already changing.

```ts
// Don't. Swap two args, still compiles.
openFile(uri, {
  endColumn: 1,
  endLineNumber: 10,
  startColumn: 1,
  startLineNumber: 10,
});

// Do. Order-independent, self-documenting.
openFile({
  selection: {
    endColumn: 1,
    endLineNumber: 10,
    startColumn: 1,
    startLineNumber: 10,
  },
  uri,
});
```

Skip on hot paths: per-frame render, tokenizers, parsers, anything in a tight loop where the allocation cost matters.
