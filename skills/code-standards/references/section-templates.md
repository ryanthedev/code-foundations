# Section Templates

## Contents

1. [Structural and quality rules](#structural-rule)
2. [1. Forbidden Patterns](#1-forbidden-patterns)
3. [2. Code Examples](#2-code-examples)
4. [3. Error Handling](#3-error-handling)
5. [4. Imports & Dependency Direction](#4-imports--dependency-direction)
6. [5. Testing Patterns](#5-testing-patterns)
7. [6. Naming Conventions](#6-naming-conventions)
8. [7. File Organization](#7-file-organization)
9. [8. Technology Decisions](#8-technology-decisions)
10. [9. Exemplar Files](#9-exemplar-files)
11. [Format Rules](#format-rules)

---

Detailed format for each section in `docs/code-standards.md`. Every section follows the same structure:

```
## Section Name

[Rule statement — 1-2 sentences, the constraint itself]

[Code example — MANDATORY, with WHY annotation]
```

**Structural rule:** Keep the rule statement and the example visually separate. Never weave constraints into narrative prose — constraints embedded in running text dissolve by paragraph three (NLD-P, 2602.22790). State the rule, then show the code.

**Example quality rule:** Examples should explain WHY the pattern works, not just show the code. Annotate with comments that make the reasoning visible. Interpretable examples outperform raw code blocks by ~25% on task accuracy (CL4SE, 2602.23047).

---

## 1. Forbidden Patterns

**Purpose:** LLMs default to training-data averages. Contrastive framing (DO/DON'T) resists confirmation bias more reliably than positive examples alone — when an agent sees only "the right way," it more readily accepts its own violations as correct (2603.18740).

**Include:** The anti-pattern, WHY it's forbidden, and the correct alternative with code.
**Exclude:** Don't list 20 items. 3-5 high-impact forbidden patterns is the sweet spot.

**Good:**
```markdown
## Forbidden Patterns

**Never use `any` type** — use `unknown` and narrow:
```typescript
// BAD — `any` disables type checking and propagates silently through call chains
function parse(input: any) { return input.name; }

// GOOD — `unknown` forces explicit narrowing, catching misuse at compile time
function parse(input: unknown): string {
  if (typeof input === "object" && input !== null && "name" in input) {
    return (input as { name: string }).name;
  }
  throw new Error("invalid input");
}
```

**Never mutate function parameters:**
```typescript
// BAD — caller's object is modified, causing action-at-a-distance bugs
function addDefaults(config: Config) { config.timeout ??= 5000; }

// GOOD — returns new object, original is untouched
function addDefaults(config: Config): Config { return { timeout: 5000, ...config }; }
```
```

---

## 2. Code Examples

**Purpose:** 2-3 do/don't pairs showing the most important conventions applied together. This is the highest-ROI section — LLMs anchor on concrete contrastive examples more than any other format.

**Include:** Real before/after or wrong/right pairs extracted from the codebase. Focus on the conventions most likely to be violated. Annotate WHY the DO version is better.

**Good:**
```markdown
## Code Examples

### API Route Handler
```typescript
// DO — from src/routes/users.ts:28
// Validates input with schema, returns typed errors, keeps handler thin
export async function GET(req: Request): Promise<Response> {
  const params = parseParams(req, userQuerySchema);
  if (!params.ok) return errorResponse(400, params.error);

  const result = await userService.list(params.value);
  if (!result.ok) return errorResponse(500, result.error);

  return json(result.value);
}

// DON'T — uses `any`, raw SQL in handler, swallows error context
export async function GET(req: Request) {
  try {
    const { page, limit } = req.query as any;
    const users = await db.query("SELECT * FROM users");
    return new Response(JSON.stringify(users));
  } catch (e) {
    console.error(e);
    return new Response("Error", { status: 500 });
  }
}
```
```

---

## 3. Error Handling

**Purpose:** LLMs default to try/catch with console.error. Show the project's actual strategy with WHY it was chosen.

**Include:** The specific pattern with a code example extracted from the codebase. Whether errors are thrown, returned, or logged. Where error boundaries live.

**Good:**
```markdown
## Error Handling

Result type pattern — never throw for expected errors.

```typescript
// From src/lib/result.ts — central type used across all services
type Result<T, E = Error> = { ok: true; value: T } | { ok: false; error: E };

// From src/services/auth.ts:42 — callers check .ok instead of catching
// This makes error paths visible in the type signature, not hidden in throws
function authenticate(token: string): Result<User, AuthError> {
  if (!token) return { ok: false, error: new AuthError("missing token") };
  // ...
  return { ok: true, value: user };
}
```

Exceptions are reserved for programmer errors (bugs) only. Expected failures use Result.
```

---

## 4. Imports & Dependency Direction

**Purpose:** Import ordering and dependency direction are invisible to LLMs without explicit guidance. This section prevents the most review churn.

**Include:** Import order, barrel file conventions, which modules can import from which.
**Exclude:** Don't list every import — show the pattern.

**Good:**
```markdown
## Imports & Dependency Direction

Import order (enforced by ESLint):
1. Node builtins (`node:fs`, `node:path`)
2. External packages (`react`, `zod`)
3. Internal absolute (`@/lib/...`, `@/components/...`)
4. Relative (`./`, `../`)

Dependency direction — inner layers cannot import outer layers:
- `lib/` → no internal imports (leaf modules)
- `services/` → may import from `lib/`
- `routes/` → may import from `services/` and `lib/`
- Never import from `routes/` into `services/` or `lib/`

No barrel files (`index.ts` re-exports). Import from the specific module.
```

---

## 5. Testing Patterns

**Purpose:** Not "write tests" but "how this project writes tests." Helpers, fixtures, and the specific framework patterns matter more than general testing advice.

**Include:** Test framework, helper functions, fixture patterns, what's mocked vs real.
**Exclude:** Generic testing advice.

**Good:**
```markdown
## Testing Patterns

Framework: Bun test runner (`bun test`).

Fixtures use factory functions from `test/helpers.ts`:
```typescript
// From test/helpers.ts:15 — single source of test data, overrides for variation
function createTestUser(overrides?: Partial<User>): User {
  return { id: "test-1", name: "Test User", ...overrides };
}
```

Never construct test data with raw object literals — always use the factory.

Database tests use `withTestDb()` wrapper that handles setup/teardown:
```typescript
// Wrapper manages connection lifecycle — test only sees the db handle
test("creates user", withTestDb(async (db) => {
  const user = await createUser(db, { name: "Alice" });
  expect(user.id).toBeDefined();
}));
```
```

---

## 6. Naming Conventions

**Purpose:** Anchor naming patterns so generated code matches the codebase.

**Include:** Variable, function, file, and module naming with examples extracted from actual code. Note any domain-specific terminology.
**Exclude:** Language defaults the LLM already follows (camelCase in JS, snake_case in Python).

**Good:**
```markdown
## Naming Conventions

Files: `kebab-case.ts` for modules, `PascalCase.tsx` for React components.
- `src/utils/parse-config.ts` — utility module
- `src/components/UserCard.tsx` — React component

Domain terms:
- "workspace" not "project" (matches the UI and database schema)
- "member" not "user" when in workspace context

Boolean variables: `is`/`has`/`should` prefix.
- `isActive`, `hasPermission`, `shouldRetry`
```

---

## 7. File Organization

**Purpose:** Tell the LLM where to put new files. Without this, it guesses and often gets it wrong.

**Include:** Directory purpose, co-location rules, where tests live relative to source.

**Good:**
```markdown
## File Organization

```
src/
├── components/    # React components, co-located with styles
│   └── UserCard/
│       ├── UserCard.tsx
│       ├── UserCard.test.tsx    # Tests next to source
│       └── UserCard.module.css
├── lib/           # Pure functions, no side effects
├── services/      # Business logic, may have side effects
└── routes/        # API route handlers
```

New features: create a directory under the appropriate layer. Co-locate tests.
```

---

## 8. Technology Decisions

**Purpose:** Capture non-obvious technology choices that an LLM can't infer from imports alone.

**Include:** Framework-specific constraints, version-locked decisions, "we chose X over Y because Z."
**Exclude:** Anything obvious from package.json/Cargo.toml/go.mod. Don't restate the stack.

**Good:**
```markdown
## Technology Decisions

- React Server Components for all data fetching. Never `useEffect` for initial data load.
- Zod for runtime validation at API boundaries. TypeScript types alone are not sufficient at runtime.
- Bun as runtime and test runner. Do not add Jest or Vitest.
```

**Bad:**
```markdown
## Technology Decisions

- We use React for the frontend
- We use PostgreSQL for the database
- We use TypeScript
```

The bad example restates what the LLM can see from imports. Zero information gain.

---

## 9. Exemplar Files

**Purpose:** Point to 1-3 files that demonstrate multiple conventions applied together. LLMs generalize from concrete, complete examples better than from rules (CL4SE, 2602.23047).

**Include:** File path, what makes it exemplary, which conventions it demonstrates.

**Good:**
```markdown
## Exemplar Files

**`src/services/auth.ts`** — demonstrates:
- Result type error handling
- Input validation at boundary
- Factory pattern for test fixtures
- Correct import ordering

**`src/components/UserCard/UserCard.tsx`** — demonstrates:
- Component file organization
- Co-located test pattern
- CSS module usage
- Props interface design
```

---

## Format Rules

1. **Separate rule from example.** State the constraint in 1-2 sentences, then show the code block. Never interleave constraints into narrative paragraphs.
2. **Annotate examples with WHY.** Add comments explaining what makes the pattern better, not just what it does. Interpretable > raw.
3. **Every section needs a code snippet or file pointer.** No exceptions. A section that's pure prose should be deleted or merged into another section.
4. **Extract from actual code.** Don't invent idealized examples. Use real file paths and line numbers where possible.
5. **Only non-obvious conventions.** If it's what any competent developer in that language would do by default, leave it out.
6. **Show wrong AND right.** Anti-pattern + correction pairs anchor conventions more reliably than positive examples alone.
7. **Keep it short.** Aim for under 300 lines. Trim filler aggressively.
