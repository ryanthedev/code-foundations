# benchmarks/model-tiers/ — cross-rung manifest contract

Pinned in Phase 1 (`.code-foundations/plans/2026-07-03-model-tier-benchmark.md`, Phase 1 Produces).
Every rung — 1 (easy-build), 2 (hard-build), 3 (debug), 4 (review) — conforms to this file. Phases
2-5 consume it read-only; changing a field here is a plan amendment, not a per-phase decision.

## Task directory layout

```
tasks/<NN-slug>/
  spec.md          # what the agent under test sees. Done-When items + "Output paths" only.
                    # NEVER hints at the hidden suite's contents or the gold solution.
  starter/         # the workspace root the agent is given (own package.json/tsconfig —
                    # self-contained, no dependency on the source repo's config or node_modules).
  hidden/          # ground truth. The agent under test never sees this directory.
  gold/            # reference solution: starter/ with the Done-When items correctly
                    # implemented. Validates the task (DW-1.2) before it enters the matrix.
  manifest.json    # see schema below.
```

## manifest.json schema

```json
{
  "id": "02-cas-refcount-quota",
  "rung": 2,
  "source": {
    "repo": "upublish-backend",
    "plan": ".code-foundations/plans/2026-06-03-cas-dedup-resume.md",
    "phase": "Phase 1: Foundation — schema, refcounts, hybrid quota"
  },
  "toolchain": {
    "install": "bun install",
    "test_hidden": "bun test hidden.test.ts"
  },
  "starter_dir": "starter",
  "report_file": null,
  "answer_key": null
}
```

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | Matches the directory name (`NN-slug`). |
| `rung` | yes | `1` easy-build, `2` hard-build, `3` debug, `4` review/judgment. |
| `source.repo` | yes | The corpus repo the task was ported from (directory name under `~/repos/`). |
| `source.plan` | yes | Path to the plan file, relative to `source.repo`'s root. **Cross-repo plans** (the plan document lives in a different repo than the phase's actual code target — real corpus shape, e.g. a backend plan with a phase whose `**Repo:**` field names a sibling skill/client repo) instead use a path relative to `~/repos/` (e.g. `../upublish-backend/.code-foundations/plans/<file>.md`), so the field always resolves to a real file regardless of which repo owns the plan doc. |
| `source.phase` | yes | The exact phase heading (`### Phase N: <name>`) the task ports. |
| `toolchain.install` | yes | Shell command, run once from the (copied) `starter_dir` before any test run. |
| `toolchain.test_hidden` | yes | Shell command that runs the hidden suite against `outputs/` — see Execution contract. |
| `starter_dir` | yes | Relative path (from the task dir) to the workspace root given to the agent. |
| `report_file` | rung 3/4 only | Path (relative to `outputs/`) to the artifact judges grade (e.g. `report.md`). `null` for rungs 1-2 (graded by hidden suite only). |
| `answer_key` | rung 3/4 only | Path to `answer-key.json` — never shown to the agent under test. `null` for rungs 1-2. |

## Execution contract (build rungs 1-2)

1. Copy `starter_dir` to a scratch workspace.
2. Run `toolchain.install` from that scratch workspace.
3. The agent under test works in the scratch workspace; it writes new/modified files to `outputs/`
   under the paths named in the task's `spec.md` "Output paths" section.
4. The harness copies every file under `outputs/` into the same directory as the hidden suite
   (`hidden/`), overwriting any starter copy of the same filename. Hidden tests import sibling
   modules by the exact filenames declared in `spec.md`'s "Output paths" — this is the seam that
   lets `toolchain.test_hidden` run as a flat `bun test` invocation with no path rewriting.
5. Run `toolchain.test_hidden` from that merged directory. Exit 0 = suite green; this is the
   rung's correctness signal (`score_run`, Phase 3, wraps this exit code).

**Pristine-starter check** (the second clause of DW-1.2 — a task-authoring gate, not a matrix
step): before any agent touches the task, confirm the untouched `starter/` is not already broken.
Where every hidden-test import already resolves against the starter's OWN exports (the fix only
changes behavior inside an existing function — task 01 is this shape), this is simply `bun test
hidden.test.ts -t offdw` run directly against the starter in place of `outputs/`: must be green.
The `test_dw_*` subset is expected to FAIL on the pristine starter (the Done-When behavior does not
exist yet) — that is correct, not a defect.

Where a task ADDS wholly new exports (a hard-build task growing new functions — task 02/03 are this
shape), a single hidden-test file cannot be filtered this way: a strict-ESM runtime (bun) resolves
every static import at module load, before any test-name filter applies, so a file importing a
symbol the starter doesn't export yet fails to load at all, not just the tests that use it. Such
tasks split the ground truth into two files: `hidden/pristine.test.ts` — imports ONLY the symbols
the starter already exports, asserting they still work correctly untouched (this is the actual
DW-1.2 "pristine starter is green" evidence for these tasks) — and `hidden/hidden.test.ts` — the
full `test_dw_*`/`test_offdw_*` suite, which requires the new symbols to exist and is what
`toolchain.test_hidden` runs for real grading (against `gold/` at authoring time, against an
agent's `outputs/` in the matrix).

## Hidden-suite test naming

- `test_dw_*` — behavior a specific Done-When item states. At least one per DW item.
- `test_offdw_*` — preserved/existing behavior the spec does not exemplify, plus dirty edge cases
  (error paths, bad data, boundaries). At least one per DW item (cc-quality-practices: dirty tests,
  not just happy paths — a DW-echo-only suite cannot separate model tiers).

## Rung-2 (hard-build) multi-seam requirement

A hard task's `gold/` must differ from its `starter/` in **≥2 files** (excluding
`package.json`/`tsconfig.json` boilerplate) — checked by a plain filename-set diff. This is the
"genuinely multi-step, not a harder single-shot" requirement from the plan's Scope.

## Gold-solution validation (DW-1.2, first clause)

For every task: copy `gold/` over a clean `starter/` copy, run `toolchain.install` +
`toolchain.test_hidden` — must be 100% green. Recorded per-task in
`.code-foundations/build/2026-07-03-model-tier-benchmark-phase-1-discovery.md` with the literal
command output.

## Sabotage check (proves the suite detects, not echoes)

A one-line deliberate break of the gold solution must fail `toolchain.test_hidden` — otherwise the
hidden suite cannot separate a correct implementation from a broken one, which is exactly what a
DW-echo-only suite fails to do.
