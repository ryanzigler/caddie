---
name: principle-type-system-discipline
description: Design types so illegal states cannot be represented. Apply when modeling a domain or schema, writing or reviewing a function signature, choosing between optional fields and a discriminated union, branding ids, parsing external data at a boundary, or reaching for a cast, `any`, or a non-null assertion to get past the type checker.
---

# Type system discipline

The type checker is a proof assistant. Use it to eliminate impossible states, mismatched primitives, and unhandled variants at compile time. A case the types let you ignore becomes a runtime failure the compiler could have stopped. Prefer defining errors and special cases out of existence over proliferating handlers.

Applies to any statically typed language. The `typescript-best-practices` skill grounds it in TypeScript syntax.

## The patterns

**Make illegal states unrepresentable.** Model variants as sum types: discriminated unions in TypeScript, enums with payloads in Rust. Don't model state as a bag of optional fields where contradictory combinations compile. `{ completed: boolean; completedAt?: Date }` admits `completed: true, completedAt: undefined`, which is meaningless. Derive the boolean from a single source (`completedAt !== null`), or model the variants explicitly: `{ kind: 'open' } | { kind: 'done'; at: Date }`. If a bug forces the question "wait, can this combination actually happen?", the type is too loose.

**Types are constructions, not restrictions.** Build the type up from the values you want instead of carving them out of a looser type with checks. A non-empty list is a head plus a rest, not a list with a length check. A valid time range is a start plus a duration, not two timestamps you must keep ordered. No representation is privileged, so choose the shape that cannot build the illegal value and expose the interface callers need on top of it.

**Brand semantic primitives.** `UserId` and `OrderId` are strings underneath but must not be interchangeable. Branded intersections in TypeScript, newtypes in Rust. Validate once at creation, trust the type downstream.

**External data is untyped until parsed.** HTTP and RPC payloads, JSON, IPC messages, CLI args, config files, environment variables, database rows. Put a parse function at every boundary that turns unstructured input into the typed domain model. Validate once at the edge; do not re-validate deep in the call chain.

**Don't lie to the type system.** Casts, unsafe coercions, and assertion functions that bypass the compiler are runtime crashes waiting to happen. If the compiler can't prove a fact, prove it: validate, narrow, or refine the model. A cast is acceptable only where it is earned by validation immediately above it, or where it records a fact the compiler genuinely cannot see and you have written down what that fact is. A cast added to make an error go away is the postmortem you write next week.

**Exhaustive matching is the compiler's job.** When you match on a sum type, the compiler must fail the build if a new variant is added without handling. Use the idiom the language provides: a `never`-typed binding in a TypeScript default arm, an unannotated `match` in Rust.

**Derive types from authoritative schemas.** When an OpenAPI spec, GraphQL schema, Prisma schema, protocol buffer, database migration, or design-token file already defines a shape, derive from it instead of hand-rolling a parallel type. Manual duplication drifts silently.

**Strengthen a type only where partiality appears.** A runtime assertion, null check, or "this should never happen" throw marks the place a type is too weak. Push that check up into the type. Then stop. The type system's job is to track the cases each use site must handle, not to describe the data as precisely as possible. Prefer total functions: `sum` of an empty list is 0, so it takes the plain list; `head` of an empty list has no answer, so it demands the non-empty one. Extra precision costs reuse and ceremony and buys no safety.

## The tests

- "Can I write a comment explaining when this combination of fields is valid?" If yes, the type is too loose. Split it into a sum type.
- "Do two of my arguments share a primitive type but mean different things?" Brand them.
- "Where did this `any`, this `as`, this `!` come from?" Trace it back to the boundary and validate there instead.
- "If a new variant is added next month, will the compiler point at every place that needs a case?" If no, the match isn't exhaustive.
- "Is this type duplicating a shape another file already owns?" Derive it instead.
- "Am I strengthening this type to keep an operation total, or just to be more precise?" If nothing would otherwise fail, keep the plain type.
