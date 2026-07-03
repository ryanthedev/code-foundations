# Detection evidence — 04-loop-core-review

Per answer-key defect: proof it is detectable from the task artifacts alone —
the starter workspace (code + green visible suite) and the spec's requirement
text. No diff is shown to the reviewer; nothing below requires one. Witness
commands were run at authoring time from the starter (bun 1.3.14); the visible
suite over the planted code is `bun test` → **27 pass, 0 fail**.

## LC-1-conditional-default-cap (dw-unmet, DW-1.3)

- Trail: spec DW-1.3 ("no explicit limit → default cap, never unbounded") +
  spec edge case ("empty/invalid StopCondition → safe cap") vs
  `src/core/loop.ts:86-90`, where the fallback is `Number.MAX_SAFE_INTEGER`
  whenever `maxTokens` or `predicate` is set. The function's own doc ("never
  unbounded") contradicts the code.
- Witness (recorded):
  `resolveStop({...initial, iterations: 1_000_000}, {predicate:{kind:'file',path:'/never'}})`
  → `{"stop":false}`.

## LC-2-usage-fold-drops-input-tokens (hidden-defect, feeds DW-1.2 max-tokens)

- Trail: `LoopState.tokensUsed` doc in `src/core/types.ts` ("Cumulative tokens
  consumed (input + output)") + spec edge case ("tokensUsed is the input +
  output total") vs `src/core/loop.ts:64-68`, which adds only
  `event.outputTokens`. The visible test asserts only `toBeGreaterThan(0)`.
- Witness (recorded):
  `applyEvent(initial, {type:'usage', inputTokens:10, outputTokens:5}).tokensUsed`
  → `5` (spec: 15).

## LC-3-unconfigured-predicate-trips (dw-unmet, DW-1.2)

- Trail: spec DW-1.2 ("correct first-to-trip reason") + spec edge case ("a
  stop condition that is NOT configured must never be the reported stop
  reason") vs `src/core/loop.ts:94` — `predicate: state.predicateTripped` with
  no `cfg.predicate !== undefined` guard; the adjacent max-tokens branch
  (loop.ts:95) DOES guard on config, making the asymmetry visible.
- Witness (recorded):
  `resolveStop({...initial, predicateTripped:true}, {maxIterations:100})`
  → `{"stop":true,"reason":"predicate"}` (spec: `{stop:false}`).

## LC-4-infra-import-in-core (dw-unmet, DW-1.4)

- Trail: spec DW-1.4 ("no infra imports under src/core/") vs
  `src/core/ports.ts:9` (`import type { Database } from 'bun:sqlite'`, used at
  line 25). The visible `boundaries.test.ts` stays green because its
  `FORBIDDEN_SPECIFIERS` list omits `bun:` — readable in the same workspace.
- Witness (recorded): `grep -n "bun:sqlite" src/core/ports.ts` →
  `9:import type { Database } from 'bun:sqlite';`

## LC-5-any-in-run-event (dw-unmet, DW-1.1)

- Trail: spec DW-1.1 ("no `any` anywhere under src/core/") vs
  `src/core/types.ts:192` (`input?: any` on the tool_use RunEvent variant).
- Witness (recorded): `grep -n ": any" src/core/types.ts` →
  `192:  | { type: 'tool_use'; name: string; input?: any }`

## Stratification note (per SWR-Bench)

Violations span 3 files and 2 kinds (4 dw-unmet + 1 hidden-defect), sit inside
otherwise-verbatim committed corpus code, and carry no marker comments. Each
would-catch test is absent or realistically weakened (weak assertion,
incomplete grep list), so the green suite cannot separate them — only reading
the code against the DW text does.
