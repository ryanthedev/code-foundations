# Review report — core domain + ports

## Suite output

`bun test`: 27 pass, 0 fail (loop.test.ts, boundaries.test.ts). A green suite —
but several requirements are unmet in ways the suite never exercises.

## Done-When verification

- DW-1.1: All domain types + port interfaces are strict-clean with no `any`
  anywhere under `src/core/`.
  PREMISE: no `any` in types.ts/ports.ts/loop.ts.
  EVIDENCE (file:line): src/core/types.ts:192 — `{ type: 'tool_use'; name: string; input?: any }`.
  TRACE (input→output): `grep -n ': any' src/core/*.ts` → one hit, types.ts:192.
  VERDICT: FAIL

- DW-1.2: `resolveStop` returns the correct first-to-trip reason for each
  single condition AND a deterministic precedence when ≥2 trip together.
  PREMISE: each condition trips only when configured AND met; ties resolve by
  STOP_PRECEDENCE.
  EVIDENCE (file:line): src/core/loop.ts:94 — `predicate: state.predicateTripped`
  has no `cfg.predicate !== undefined` guard (contrast the max-tokens branch,
  loop.ts:95, which does guard on config); src/core/loop.ts:64-68 — the usage
  fold adds only `event.outputTokens`, undercounting the budget the max-tokens
  condition compares against (LoopState.tokensUsed documents "input + output").
  TRACE (input→output): `resolveStop({...initial, predicateTripped: true}, {maxIterations: 100})`
  → `{stop: true, reason: 'predicate'}` although no predicate is configured
  (expected: `{stop: false}`); `applyEvent(initial, {type:'usage', inputTokens:10, outputTokens:5}).tokensUsed`
  → `5` (expected 15), so a `maxTokens: 15` budget does not trip when it should.
  VERDICT: FAIL

- DW-1.3: A `StopCondition` with no explicit limit resolves to a default
  max-iteration cap (never unbounded).
  PREMISE: `maxIterations` unset → DEFAULT_MAX_ITERATIONS applies regardless of
  other conditions.
  EVIDENCE (file:line): src/core/loop.ts:86-90 — the fallback is conditional:
  `cfg.maxIterations ?? (cfg.maxTokens !== undefined || cfg.predicate !== undefined ? Number.MAX_SAFE_INTEGER : DEFAULT_MAX_ITERATIONS)`.
  TRACE (input→output): `resolveStop({...initial, iterations: 1_000_000}, {predicate: {kind:'file', path:'/never'}})`
  → `{stop: false}` — a predicate-only loop whose predicate never trips is
  unbounded.
  VERDICT: FAIL

- DW-1.4: Boundary-violation greps find no infra imports under `src/core/`.
  PREMISE: zero infra import specifiers in core modules.
  EVIDENCE (file:line): src/core/ports.ts:9 — `import type { Database } from 'bun:sqlite'`
  (used at ports.ts:25 for `DbHandle`). Type-only does not matter: it is an
  infra import in the pure layer.
  TRACE (input→output): `grep -rn "bun:sqlite" src/core/` → ports.ts:9. The
  visible boundaries test stays green because its FORBIDDEN_SPECIFIERS list
  omits `bun:` entirely.
  VERDICT: FAIL

## Edge cases

- Three conditions tripping together: precedence array order holds — OK.
- Zero-iteration job: `maxIterations: 0` honored (not nullish-defaulted) — OK.
- One-shot fresh state: does not spuriously stop — OK.
- Empty `StopCondition`: default cap applies — OK (the hole is non-empty
  configs, see DW-1.3).
- Cumulative token accounting: BROKEN — input tokens dropped (see DW-1.2).
- Unconfigured condition never the stop reason: BROKEN for predicate (see
  DW-1.2).

## Issues

1. [LC-1] src/core/loop.ts:86-90 — default iteration cap silently disabled
   when maxTokens or predicate is set; predicate-only/token-only loops are
   unbounded. Violates DW-1.3 (doc comment "never unbounded" contradicts code).
2. [LC-2] src/core/loop.ts:64-68 — usage fold drops `inputTokens`;
   `tokensUsed` undercounts and `maxTokens` budgets trip late or never.
   Violates the cumulative input+output contract (LoopState.tokensUsed doc)
   feeding DW-1.2's max-tokens condition. The visible test only asserts
   `toBeGreaterThan(0)`, which cannot catch this.
3. [LC-3] src/core/loop.ts:94 — predicate trip lacks the
   `cfg.predicate !== undefined` guard; a stale `predicateTripped` flag stops
   a loop that configured no predicate, reason 'predicate'. Violates DW-1.2.
4. [LC-4] src/core/ports.ts:9,25 — `bun:sqlite` import (type-only) in the pure
   core layer; `DbHandle` re-exports an infra type. Violates DW-1.4. The
   boundaries test's specifier list omits `bun:`, so it cannot catch this.
5. [LC-5] src/core/types.ts:192 — `input?: any` on the tool_use RunEvent
   variant; the rest of the file uses `unknown` for opaque payloads. Violates
   DW-1.1.

OVERALL: FAIL
