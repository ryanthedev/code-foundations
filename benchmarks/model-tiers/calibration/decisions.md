# Calibration decisions

## Model-id check (2026-07-03T11:17:10Z)
- `sonnet-5 (claude-sonnet-5)`: ACCEPTED
- `opus-4.8 (claude-opus-4-8)`: ACCEPTED
- `fable-5 (claude-fable-5)`: ACCEPTED
- `sonnet-4.6 (claude-sonnet-4-6, judge)`: ACCEPTED
Verified via `claude -p "Reply with exactly the word: pong" --model <id> --max-turns 1 --output-format json`, one call per id, all returned result="pong" stop_reason=end_turn. Costs: sonnet-5=$0.0507 opus-4.8=$0.0763 fable-5=$0.1808 sonnet-4.6=$0.0478 (total $0.356).
- 2026-07-03T11:20:24Z [gold_validation] rung-3 diff-scope OK for 03-kv-key-mismatch, 03-storage-meter-dedup (programmatic); rung-4 full recall (5/5, 5/5 defects) for 04-loop-core-review, 04-hash-progress-review via live 3-judge panel
- 2026-07-03T11:48:13Z [vet_methodology_fix] Initial vet_task() ran codex/agy with unconstrained cwd, letting them browse hidden/ and answer-key.json (confirmed: codex read hidden/pristine.test.ts for 02-cas-refcount-quota). Fixed: vet now runs from an isolated tmp workspace containing only spec.md+starter/ (matching what the real subject session sees), with codex --skip-git-repo-check added (codex refuses non-git cwds otherwise). All 7 tasks re-vetted with the corrected harness.
- 2026-07-03T11:48:13Z [vet_result] 01-heartbeat-message: PASS/PASS (codex/agy).
- 2026-07-03T11:48:13Z [vet_result] 02-cas-bounded-concurrency: 2 of 3 independent judge-pair samples PASS/PASS (one split); accepted, noise flagged.
- 2026-07-03T11:48:13Z [vet_result] 02-cas-refcount-quota: FAIL/FAIL (2 independent runs, consistent) — codex: "dereferenceVersion nonempty return shape, duplicate-hash sizes, and live_version->site_versions mapping undefined". REJECTED — loops back to Phase 1 for a spec clarification, not rewritten here (out of Phase 4 scope).
- 2026-07-03T11:48:13Z [vet_result] 03-kv-key-mismatch: PASS/PASS (codex/agy).
- 2026-07-03T11:48:13Z [vet_result] 03-storage-meter-dedup: noisy across 3 samples (FAIL, disagreement, PASS) — majority-PASS, and the task is a debug rung where inference from evidence is the point; accepted with disagreement flagged.
- 2026-07-03T11:48:13Z [vet_result] 04-hash-progress-review: FAIL/FAIL (consistent) — "relies on undocumented external .upublishignore pattern forms and an unstated prior return contract not present in starter/spec". REJECTED — loops back to Phase 2 for a spec clarification, not rewritten here (out of Phase 4 scope).
- 2026-07-03T11:48:13Z [vet_result] 04-loop-core-review: disagreement (codex FAIL / agy PASS, repeated) — codex conflates a genuine implementation ambiguity (the review task IS supposed to surface it) with unsolvability; accepted with disagreement flagged.

### Task: 02-cas-refcount-quota (2026-07-03T11:48:20Z)
- Vet: verdict=FAIL quorum=2/2 judge_fail=False
- Pilot (sonnet-5): correct=None score=None tp=None fp=None fn=None
- Pilot (fable-5): correct=None score=None tp=None fp=None fn=None
- **Decision: REJECT** — vet failed

### Task: 04-hash-progress-review (2026-07-03T11:48:20Z)
- Vet: verdict=FAIL quorum=2/2 judge_fail=False
- Pilot (sonnet-5): correct=None score=None tp=None fp=None fn=None
- Pilot (fable-5): correct=None score=None tp=None fp=None fn=None
- **Decision: REJECT** — vet failed

### Task: 01-heartbeat-message (2026-07-03T11:52:36Z)
- Vet: verdict=PASS quorum=2/2 judge_fail=False
- Pilot (sonnet-5): correct=1 score=1.0 tp=0 fp=0 fn=0
- Pilot (fable-5): correct=1 score=1.0 tp=0 fp=0 fn=0
- **Decision: REJECT** — no headroom (both-perfect or both-fail on pilot)

### Task: 02-cas-bounded-concurrency (2026-07-03T11:56:06Z)
- Vet: verdict=None quorum=2/2 judge_fail=False
- Pilot (sonnet-5): correct=1 score=1.0 tp=0 fp=0 fn=0
- Pilot (fable-5): correct=1 score=1.0 tp=0 fp=0 fn=0
- **Decision: REJECT** — no headroom (both-perfect or both-fail on pilot)

### Task: 03-kv-key-mismatch (2026-07-03T12:00:20Z)
- Vet: verdict=PASS quorum=2/2 judge_fail=False
- Pilot (sonnet-5): correct=0 score=0.0 tp=0 fp=0 fn=0
- Pilot (fable-5): correct=0 score=0.0 tp=0 fp=0 fn=0
- **Decision: REJECT** — no headroom (both-perfect or both-fail on pilot)

### Task: 03-storage-meter-dedup (2026-07-03T12:03:39Z)
- Vet: verdict=None quorum=2/2 judge_fail=False
- Pilot (sonnet-5): correct=0 score=0.0 tp=0 fp=0 fn=0
- Pilot (fable-5): correct=0 score=0.0 tp=0 fp=0 fn=0
- **Decision: REJECT** — no headroom (both-perfect or both-fail on pilot)

### Task: 04-loop-core-review (2026-07-03T12:12:16Z)
- Vet: verdict=None quorum=2/2 judge_fail=False
- Pilot (sonnet-5): correct=1 score=1.0 tp=5 fp=0 fn=0
- Pilot (fable-5): correct=1 score=1.0 tp=5 fp=0 fn=0
- **Decision: REJECT** — no headroom (both-perfect or both-fail on pilot)
- 2026-07-03T12:15:50Z [SCORER_BUG_FOUND] Both 03-kv-key-mismatch and 03-storage-meter-dedup pilots (sonnet-5 AND fable-5, all 4 runs) were recorded correct=0 ("both-fail", no headroom) — but this is a FALSE NEGATIVE from score_run._diff_scope_ok, not a real model failure. Root cause: both tasks spec.md require outputs/report.md (per the research doc constraint 5, and SCHEMA.md report_file), but neither answer-key.json's allowed_change_scope lists "report.md" — so the mandatory report file is counted as an out-of-scope change on every single run, unconditionally failing _score_debug regardless of fix quality. Verified directly against both pilot run dirs: hidden suite passed 13/13 (03-kv-key-mismatch, sonnet-5 AND fable-5) and 12/12 (03-storage-meter-dedup, fable-5) — i.e. BOTH models produced a fix that fully passes the hidden suite on both tasks; diff_scope_ok was the only failing check, purely because report.md is absent from allowed_change_scope. validate_rung3_gold_diff_scope (DW-4.6) did not catch this because gold/ never includes a report.md — only a real agent output (which always writes one, per spec.md's explicit instruction) exercises the gap. ACTION REQUIRED (Phase 2, out of Phase 4 file scope): add "report.md" to allowed_change_scope in both tasks/03-kv-key-mismatch/answer-key.json and tasks/03-storage-meter-dedup/answer-key.json, then re-pilot. Both tasks are left status=rejected here because the CURRENT pilot data cannot license entry to the matrix (the headroom rule was evaluated against corrupted correct/score values) — not because the models failed.
- 2026-07-03T12:33:59Z [resume] Phase 4 resumed after loop-back commit 62060b4 (rung-3 answer keys +report.md; 02-cas-refcount-quota and 04-hash-progress-review spec clarifications). evals.json rebuilt from updated specs. Re-vetting the 4 fixed/affected tasks, then re-piloting; the 3 saturated tasks get one confirmation pilot each before final rejection.
- 2026-07-03T12:42:22Z [re_vet] 02-cas-refcount-quota: PASS/PASS (codex/agy) — spec clarification resolved the prior FAIL. Proceeds to pilot.
- 2026-07-03T12:42:22Z [re_vet] 03-kv-key-mismatch: PASS/PASS. Proceeds to pilot.
- 2026-07-03T12:42:22Z [re_vet] 03-storage-meter-dedup: disagreement again (codex FAIL / agy PASS; codex itself flips PASS/FAIL across samples — noisy). Not a consistent FAIL, so per the gate rule it proceeds to pilot with the disagreement flagged.
- 2026-07-03T12:42:22Z [re_vet] 04-hash-progress-review: FAIL/FAIL AGAIN (2 samples post-fix, both judges consistent). Residual gap: DW-2.2 requires verifying "defaults + every documented .upublishignore pattern form" but the new Ground rules section defines only the .upublishignore forms and the prior collectFilesWithHashes contract — the DEFAULT exclusion rules are still undefined in the spec. REJECTED again; loops back to Phase 2 (define the default exclusions in the Ground rules, mirroring the hidden suite).

### Task: 04-hash-progress-review (2026-07-03T12:42:22Z)
- Vet: verdict=FAIL quorum=2/2 judge_fail=False
- Pilot (sonnet-5): correct=None score=None tp=None fp=None fn=None
- Pilot (fable-5): correct=None score=None tp=None fp=None fn=None
- **Decision: REJECT** — vet failed

### Task: 02-cas-refcount-quota (2026-07-03T12:46:10Z)
- Vet: verdict=PASS quorum=2/2 judge_fail=False
- Pilot (sonnet-5): correct=1 score=1.0 tp=0 fp=0 fn=0
- Pilot (fable-5): correct=1 score=1.0 tp=0 fp=0 fn=0
- **Decision: REJECT** — no headroom (both-perfect or both-fail on pilot)

### Task: 03-kv-key-mismatch (2026-07-03T12:50:54Z)
- Vet: verdict=PASS quorum=2/2 judge_fail=False
- Pilot (sonnet-5): correct=1 score=1.0 tp=0 fp=0 fn=0
- Pilot (fable-5): correct=1 score=1.0 tp=0 fp=0 fn=0
- **Decision: REJECT** — no headroom (both-perfect or both-fail on pilot)

### Task: 03-storage-meter-dedup (2026-07-03T12:54:50Z)
- Vet: verdict=None quorum=2/2 judge_fail=False
- Pilot (sonnet-5): correct=1 score=1.0 tp=0 fp=0 fn=0
- Pilot (fable-5): correct=1 score=1.0 tp=0 fp=0 fn=0
- **Decision: REJECT** — no headroom (both-perfect or both-fail on pilot)
- 2026-07-03T12:56:47Z [saturation_confirm] 01-heartbeat-message: confirmation pilot (2nd sample) — sonnet-5 correct=1, fable-5 correct=1 again. Saturation confirmed at n=2; REJECT stands (informative: rung-1 tie was the research doc's own predicted outcome for function-level tasks).
- 2026-07-03T12:59:38Z [saturation_confirm] 02-cas-bounded-concurrency: confirmation pilot (2nd sample) — sonnet-5 correct=1, fable-5 correct=1 again. Saturation confirmed at n=2; REJECT stands.
- 2026-07-03T13:09:51Z [saturation_confirm] 04-loop-core-review: confirmation pilot (2nd sample) — sonnet-5 tp=5 fp=0 fn=0, fable-5 tp=5 fp=0 fn=0 again. Both models achieve perfect recall+precision on the planted-violation review at n=2. Saturation confirmed; REJECT stands. Notable for Q2 (REVIEW-tier rule): at effort=medium, the CHEAPEST matrix model found every planted violation the priciest model found — zero capability gap observed on this review task (n=2 per model).
- 2026-07-03T13:09:51Z [calibration_terminal] CALIBRATION COMPLETE — 0 of 7 tasks enter the matrix. Final per-task: 01-heartbeat-message REJECT (saturation, n=2 both-perfect); 02-cas-bounded-concurrency REJECT (saturation, n=2 both-perfect); 02-cas-refcount-quota REJECT (post-fix vet PASS/PASS but pilot both-perfect); 03-kv-key-mismatch REJECT (post-fix pilot both-perfect — the earlier both-fail was the scorer bug, now fixed and re-measured); 03-storage-meter-dedup REJECT (post-fix pilot both-perfect); 04-hash-progress-review REJECT (vet FAIL/FAIL persists post-fix: DW-2.2 default exclusion rules still undefined — loops back to Phase 2 a second time); 04-loop-core-review REJECT (saturation, n=2 both-perfect incl. 5/5 defect recall by BOTH models). The pre-registered headroom rule fired exactly as designed: it prevented spending ~105 matrix runs measuring ties. Matrix is therefore vacuously complete (0 cells); no results-*.csv produced. The dominant empirical signal for Phase 5 / the report: at effort=medium, claude-sonnet-5 and claude-fable-5 are INDISTINGUISHABLE on every surviving-quality task in this suite (12 pilot comparisons, all ties at perfect) — the corpus-sourced tasks as authored do not reach the difficulty band where tiers separate.
