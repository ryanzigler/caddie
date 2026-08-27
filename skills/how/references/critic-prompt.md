# Critic prompt template

Build each critic subagent's prompt from this template. Fill in the placeholders.

Each critic gets **one lens** from `critique-rubric.md`, not the whole rubric. That assigned narrowness is the point: it is what makes several critics running in parallel produce different findings instead of the same generic complaints.

---

You are reviewing the architecture of a codebase subsystem through one specific lens. An explanation of how it works has already been written. Read it to orient yourself, then read the actual code to form your own judgment.

## Architectural explanation

{EXPLANATION}

## Relevant files

{FILE_PATHS}

## Your assigned lens

{SINGLE_LENS_SECTION_FROM_CRITIQUE_RUBRIC}

Stay inside this lens. Other critics are covering the other lenses in parallel. If you notice something outside your lens that looks serious, note it in one line at the end under "Outside my lens" rather than investigating it.

## Instructions

Read the files listed above. Use the explanation as a map, but form your own opinions from the code itself. The explanation might miss things or frame them charitably.

Find architectural problems, not line-level bugs or style issues. Ask whether this subsystem is built well for what it needs to do and how it will need to evolve.

Do not write, edit, or create files.

For each finding:

1. **Severity**: `structural` | `concern` | `observation`
   - `structural`: a fundamental architectural problem. Wrong abstraction boundary, broken data model, coupling that will block future work.
   - `concern`: a real issue that makes the system harder to work with or reason about, but not fundamentally broken.
   - `observation`: worth noting. A tradeoff that might not age well, a pattern inconsistent with the rest of the codebase, technical debt.
2. **Finding**: the architectural issue. Be specific. Name the components, the boundary, the coupling.
3. **Evidence**: concrete code that demonstrates the problem. Don't just assert that "this is too coupled". Show the dependency chain.
4. **Impact**: what the issue costs. Harder to test? Harder to change? Performance cliff at scale? Be concrete about the consequence.

## What to avoid

- Line-level code review. Not your job here.
- Suggesting rewrites without demonstrating a problem with the current approach.
- "This could use more abstraction" without showing what the abstraction would actually solve.
- Flagging intentional tradeoffs with clear benefits as issues.
- Padding the list to look thorough.

If the architecture is sound through your lens, say so. An empty critique is a valid outcome and is preferred over a manufactured one.

## Output

```
## Lens
{your assigned lens}

## Findings

### 1. [Severity] Short title
**Components**: Which parts of the system are involved
**Finding**: What's wrong architecturally
**Evidence**: Concrete code references
**Impact**: What this costs in practice

### 2. [Severity] Short title
...

## Outside my lens
One line per item, or "none".
```
