# Review: Phase 2 - Debug + review tasks

Independent verification of `benchmarks/model-tiers/tasks/{03-kv-key-mismatch,03-storage-meter-dedup,
04-loop-core-review,04-hash-progress-review}/` against SCHEMA.md and the 5 Done-When items.
All commands below were executed directly by this reviewer (bun 1.3.14) from clean copies —
no claim here rests on any authoring-time record.

## Executed Results (Step 0)

| Task | Command | Result |
|---|---|---|
| 03-kv-key-mismatch | `bun test repro.test.ts` (clean starter, 5×) | exit 1 all 5 runs; 1 pass / 3 fail each run |
| 03-kv-key-mismatch | `bun test server.test.ts worker.test.ts` (clean starter) | 14 pass, 0 fail |
| 03-kv-key-mismatch | `bun test hidden.test.ts` (gold overlaid on hidden/) | 13 pass, 0 fail |
| 03-storage-meter-dedup | `bun test repro.test.ts` (clean starter, 5×) | exit 1 all 5 runs; 0 pass / 2 fail each run |
| 03-storage-meter-dedup | `bun test stats.test.ts quota.test.ts` (clean starter) | 11 pass, 0 fail |
| 03-storage-meter-dedup | `bun test hidden.test.ts` (gold overlaid on hidden/) | 12 pass, 0 fail |
| 04-loop-core-review | `bun test` (starter, planted code) | 27 pass, 0 fail |
| 04-loop-core-review | `bun test hidden.test.ts` (gold/report.md as sibling) | 4 pass, 0 fail |
| 04-loop-core-review | `bun test hidden.test.ts` (report.md absent) | 0 pass, 4 fail, exit 1 |
| 04-hash-progress-review | `bun test` (starter, planted code) | 10 pass, 0 fail |
| 04-hash-progress-review | `bun test hidden.test.ts` (gold/report.md as sibling) | 4 pass, 0 fail |
| 04-hash-progress-review | `bun test hidden.test.ts` (report.md absent) | 0 pass, 4 fail, exit 1 |

No typecheck/lint commands apply — these are static task fixtures (JSON/markdown/TS test
modules), not an application build.

## Requirement Fulfillment

### DW-2.1
PREMISE:  Both rung-3 tasks: failing repro command recorded in manifest and reproduces 5/5 times on clean starter.
EVIDENCE: `03-kv-key-mismatch/manifest.json:36` (`"repro": "bun test repro.test.ts"`); `03-storage-meter-dedup/manifest.json:37` (same field).
TRACE:    Copied each task's `starter/` to a fresh scratch dir, ran `bun test repro.test.ts` 5× per task → kv-key-mismatch: exit 1, "1 pass, 3 fail" identically all 5 runs; storage-meter-dedup: exit 1, "0 pass, 2 fail" identically all 5 runs.
VERDICT:  PASS

### DW-2.2
PREMISE:  Both rung-4 tasks: ≥3 planted violations each, with location, severity, 5-point anchors in answer-key.json.
EVIDENCE: `04-loop-core-review/answer-key.json` (5 defects: LC-1..LC-5); `04-hash-progress-review/answer-key.json` (4 defects: HP-1..HP-4).
TRACE:    Programmatic schema check (Node script) on both files: every defect object has `id, kind, location, severity, anchors, detectable_via`; `anchors.length === 5` for all 9 defects across both tasks; defect counts 5 and 4, both ≥3.
VERDICT:  PASS

### DW-2.3
PREMISE:  Every planted violation has recorded evidence it is detectable from task artifacts alone.
EVIDENCE: `detection-evidence.md` in each of the 4 task dirs.
TRACE:    Cross-referenced every answer-key defect id against its task's `detection-evidence.md` (Node script substring match) — all 9 ids (1 + 1 + 5 + 4) present with an artifact trail (file:line vs spec/doc text) and a witness command/output. I independently re-ran every witness (see Correctness Dimensions below) and every one reproduced the claimed value.
VERDICT:  PASS

### DW-2.4
PREMISE:  Self-verifiable gold validation: both rung-3 gold fixes applied to clean starters pass their hidden suites (command outputs recorded); rung-4 gold findings lists enumerate every answer-key defect 1:1 by inspection.
EVIDENCE: `03-kv-key-mismatch/gold/*`, `03-storage-meter-dedup/gold/stats.ts`, `04-loop-core-review/gold/report.md`, `04-hash-progress-review/gold/report.md`.
TRACE:    Rung-3: overlaid each task's `gold/` changed files onto a copy of `hidden/` (which is byte-identical to `starter/` plus `hidden.test.ts` — the only place `hidden.test.ts` exists) and ran `bun test hidden.test.ts` → kv-key-mismatch 13 pass/0 fail, storage-meter-dedup 12 pass/0 fail. Rung-4: read `gold/report.md`'s `## Issues` list against `answer-key.json` — loop-core-review's 5 issues map 1:1 to LC-1..LC-5 by id and location; hash-progress-review's 4 issues map 1:1 to HP-1..HP-4 by id and location.
VERDICT:  PASS

### DW-2.5
PREMISE:  Both rung-4 specs mirror an execute-first review dispatch (suite-first, per-DW verdict + evidence, PASS/FAIL) with zero plan/intent context.
EVIDENCE: `04-loop-core-review/spec.md`, `04-hash-progress-review/spec.md`, compared against `references/dispatch-templates.md` § REVIEW.
TRACE:    Both specs open with the identical independent-critic preamble ("You did not write this code and have no information about how or why it was written..."), a "FIRST ACTION: run the test suite ... BEFORE reading any source file" instruction, a PREMISE/EVIDENCE/TRACE/VERDICT slot per DW item, an Edge cases block, Files to review, How to run the suite, and an Output section requiring `OVERALL: PASS`/`OVERALL: FAIL`. Grepped both files for forbidden intent-framing tokens (`## Plan Context`, `## Progress`, `## Goal`, `Completed: Phase`, `discovery`, `problem statement`, `This is the first phase`, `Current: Phase`) — zero matches in either file.
VERDICT:  PASS

**All requirements met:** YES

## Test-DW Coverage
- [x] DW-2.1 — automated: repro command run 5× directly (Step 0).
- [x] DW-2.2 — automated: Node schema-check script over both answer-key.json files (Step 0-equivalent, executed).
- [x] DW-2.3 — observed behavior: cross-reference script + re-run of all 9 witness commands (no automated test framework applies to markdown cross-referencing; this is the correct fallback per protocol).
- [x] DW-2.4 — automated: `bun test hidden.test.ts` with gold overlay, both rung-3 tasks; manual 1:1 id/location inspection, both rung-4 tasks (report content has no natural automated test — inspection is the only mechanism, matching the DW's own "by inspection" wording).
- [x] DW-2.5 — automated: grep-based required/forbidden token check against both spec.md files.
- [x] Coverage matches the stated 100% level — every DW item has either an automated command I ran or a directly observed, independently reproduced behavior; none rest on unverified claims.

## Dead Code
None found. Grepped all four task directories for `FIXME|XXX|HACK|BUG:|VULN|planted|violation` marker comments (would leak the answer key) — zero hits, confirming violations aren't flagged in-code. Grepped for stray `console.log`/`console.debug` — zero hits.

## Correctness Dimensions

| Dimension | Status | Evidence |
|-----------|--------|----------|
| Concurrency | N/A | Phase deliverable is static task-fixture authoring (JSON/markdown/TS test modules), not live concurrent service code. The one concurrency-flavored planted defect (HP-2, event-loop yield) is domain content under test, independently re-verified below, not a defect in the deliverable itself. |
| Error Handling | N/A | Same reasoning — no live error-handling surface in the deliverable; fixture code's own error handling is domain content already checked via hidden-suite execution. |
| Resources | N/A | No file handles/connections/locks owned by this phase's own deliverable. |
| Boundaries | PASS | Re-ran every claimed witness independently rather than trusting the answer-key prose: LC-1 `resolveStop({...initial, iterations:1_000_000}, {predicate:{kind:'file',path:'/never'}})` → `{stop:false}` (matches); LC-2 `applyEvent(initial,{type:'usage',inputTokens:10,outputTokens:5}).tokensUsed` → `5` (matches, spec expects 15); LC-3 `resolveStop({...initial,predicateTripped:true},{maxIterations:100})` → `{stop:true,reason:'predicate'}` (matches); LC-4 `grep -n "bun:sqlite" ports.ts` → line 9 (matches); LC-5 `grep -n ": any" types.ts` → line 192 (matches); HP-1 `hashFiles` over 2 files → first report `{completed:1,...}`, never `{completed:0,...}` (matches); HP-2 `setTimeout(0)` scheduled before a yielding 5-file hash → did not fire during the hash, only after (matches — confirms the yield is a microtask, not a macrotask); HP-3 grew a 4-byte file to 8 bytes between stat and hash → hashed result size 8, reported `completedBytes` 4 (matches, confirms stale stat bytes are reported not hashed bytes); HP-4 `.upublishignore` containing `private/` with `private/notes.txt` on disk → `listFiles` still returns `private/notes.txt` (matches, confirms the `dir/` pattern form is unimplemented). All 9 witnesses reproduce exactly as claimed — no defect was found to be misdescribed, mislocated, or unreproducible. |
| Security | N/A | No untrusted-input-processing surface introduced by this phase itself; the fixture content's handling of file paths/KV keys is domain content already exercised by the hidden suites. |

## Loaded-Skill Criteria

| Skill | Criterion | Status | Evidence |
|-------|-----------|--------|----------|
| cc-debugging | STABILIZE — repro must be deterministic before any other step | PASS | Independently ran each rung-3 repro 5× on a clean starter copy; both tasks failed identically (same pass/fail counts) on every run — no flakiness observed. |
| cc-debugging | Root cause vs symptom — the answer-key's root-cause defects must be the actual write/read mismatch, not a downstream symptom | PASS | For both rung-3 tasks, read the write-side key construction against the read-side key construction directly (namespace-sites.ts/billing.ts vs access-control.ts; stats.ts STATS_SELECT vs quota.ts sumUniqueStorageForSpace) and confirmed the located lines are the actual point of divergence, not a downstream effect. |
| cc-quality-practices | Test Cases checklist — dirty:clean test ratio (TC-9..TC-13 vs TC-14..TC-17), "aim for 5:1" | PASS (with note) | Counted `test_dw_*`/`test_offdw_*` occurrences in both rung-3 `hidden.test.ts` files: kv-key-mismatch 8 dw / 5 offdw; storage-meter-dedup 6 dw / 6 offdw. This is far below the book's general 5:1 dirty:clean aspiration, but SCHEMA.md's own pinned contract for this artifact type is explicit and different ("at least one `test_offdw_*` per DW item") and both tasks meet it. The 5:1 figure is a general-application-suite statistic, not a stated requirement for these deliberately narrow, single-bug repro fixtures — extending it here would impose a requirement absent from the DW list and from the project's own governing contract (SCHEMA.md), so this is recorded as a note rather than a violation. |
| cc-quality-practices | Formal-inspection technique selection — was a mix of detection techniques used, not testing alone | N/A | This criterion targets designing a human QA process; the phase under review is authoring benchmark fixtures, not a live QA-process decision. |

## Notes (non-blocking)

- **SCHEMA.md is not amended to document `toolchain.repro`.** All 4 manifests conform to SCHEMA.md's pinned fields, and both rung-3 manifests additionally carry a `toolchain.repro` field (required by DW-2.1) that SCHEMA.md's documented schema (lines 21-40) does not mention. This is additive, not contradictory, and doesn't break any pinned field or DW item, but SCHEMA.md is explicitly the "manifest contract" other phases consume — a one-line doc addition there would close this drift. Not a FAIL: no DW item requires the schema doc itself to be amended, and SCHEMA.md is outside this phase's stated file scope (`tasks/03-*, tasks/04-*`).
- `gold/` directories correctly omit pinned files (kv.ts, access-control.ts, worker.test.ts, repro.test.ts for kv-key-mismatch; quota.ts, schema.ts, fixtures.ts, quota.test.ts, repro.test.ts for storage-meter-dedup) — the file lists present in each `gold/` exactly match each task's `allowed_change_scope`, which is a clean, verifiable diff-scope surface (see Edge cases below).
- Both rung-4 report-gates are honest about their own limits (doc comment: "Whether the findings are CORRECT is graded by the judge panel... this gate only verifies a review artifact of the required shape exists") — confirmed structurally: the gate passes on the presence/shape of `report.md` regardless of correctness, which is consistent with the plan's stated Phase-3 handoff.

## Edge Cases

- **Repro must be deterministic (n=5 fair grading).** VERIFIED — both rung-3 repros ran 5× each with identical pass/fail counts every time (kv-key-mismatch: 1 pass/3 fail ×5; storage-meter-dedup: 0 pass/2 fail ×5).
- **Planted violations must not be findable from diff shape alone.** VERIFIED — rung-3: `hidden/`'s buggy-file copies (billing.ts, namespace-sites.ts, space.ts / stats.ts) are byte-identical to `starter/` (confirmed via `diff`), so no starter-vs-hidden diff exists to leak the fix location. Rung-4: the agent under test is given only a single `starter/` workspace with no diff or "before" version shown at all, and a grep for marker comments (`FIXME|XXX|HACK|BUG:|VULN|planted|violation`) across both rung-4 starters returned zero hits — nothing flags the 9 planted defects in-code.
- **Rung-3 grading needs a diff-scope check surface.** VERIFIED — both rung-3 `answer-key.json` files carry an `allowed_change_scope` array (kv-key-mismatch: `["namespace-sites.ts","billing.ts","space.ts","server.test.ts"]`; storage-meter-dedup: `["stats.ts","stats.test.ts"]`) plus a `pinned_files` array, and each task's `gold/` file list matches its `allowed_change_scope` exactly — a rewrite touching a pinned file would be visibly out of scope against this surface.

**Verdict: PASS**
