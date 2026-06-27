# Harder-Tasks Hunt — finding the headroom where skills matter

**Premise:** every earlier task washed out because baseline sonnet was already at the
ceiling (memorized, well-specified functional problems). Research (NoFunEval; LiveCodeBench;
multiple 2025 security studies showing 12–65% of LLM code triggers CWEs) pointed to
**security and non-functional requirements** as where baseline reliably fails. We built
research-grounded harder tasks and ran a cheap baseline-gap pre-check (no-skill, n=3) before
any A/B.

## Baseline-gap pre-check verdict (does baseline leave a measurable gap?)

| Task | Source | Baseline result | Gap? |
|---|---|---|---|
| SQL injection | custom (CWE-89) | parameterized `?` by default — attack 3/3 defended | ❌ secure |
| Command injection | custom (CWE-78) | used Python `open()`, never a shell — 2/2 defended | ❌ secure |
| Pair-sum | custom (perf) | O(n) set-based by default — 3/3 | ❌ efficient |
| Counter | custom (concurrency) | unlocked `+= 1`, but CPython GIL masks the race | ⚠️ untestable |
| Theatrical Players | Fowler/Bache kata | refactors well unprompted (CC 7→5, fn 36→17) | 🟡 thin |
| TPMS | Bache kata | one run failed the seam/testability contract (2/3) | 🟡 small |
| **Path traversal** | custom (CWE-22) | **leaks parent file — attack defended only 1/5** | 🟢 **real** |

Out of ~9 harder tasks, exactly **one** (path traversal) had a clean, reliable baseline gap.
Notable secondary finding: **sonnet's defaults are mostly secure** — it parameterizes SQL and
avoids shell-outs without being told. The literature's ~33% vuln rate reflects older/weaker
models; this model's one clear blind spot here is path-traversal containment.

## The A/B that finally shows skill value (path traversal, n=5)

| Arm | Per-run attack defense | Fully defended |
|---|---|---|
| NO-SKILL | 1/2, 1/2, 1/2, 1/2, 2/2 | **1/5 (20%)** |
| cc-defensive-programming | 2/2, 2/2, 1/2, 1/2, 2/2 | **3/5 (60%)** |
| aposd-verifying-correctness | 2/2 ×5 | **5/5 (100%)** |

`aposd-verifying-correctness` took defense from **20% → 100%**; `cc-defensive-programming` from
**20% → 60%**. Verified genuine: with-skill impls add a real containment check
(`os.path.realpath(target).startswith(realpath(base) + os.sep)` → raise on escape) that the
baseline omits.

**This is the first clean positive in the whole investigation** — and it pinpoints *when* skills
help: only where the base model has a genuine blind spot, not on the memorized tasks it already
aces. It also shows the **specific** skill matters: `verifying-correctness` (whose post-impl
checklist explicitly has a security dimension naming this failure mode) fully closed the gap,
while general `defensive-programming` only halved it.

## Consolidated conclusion across the whole study

1. **Delivery (Read vs Skill-load): wash.** The migration cost no quality.
2. **Build-time skill effect on memorized/easy tasks: ~nil.** Baseline already encodes the
   practice (correctness, efficiency, structure, even SQL/shell security).
3. **Skills DO help on genuine blind spots.** Path-traversal containment: a relevant skill
   moved defense 20%→100%. Headroom is the prerequisite; security blind spots are where it lives.
4. **Pick the skill whose checklist names the failure mode.** verifying-correctness > generic
   defensive-programming on this security gap.
5. **Measurement caveats:** n=5; LLM-judge metrics saturate (use objective/behavioral tests);
   CPython GIL makes naive concurrency untestable; this is all BUILD-time (Minimal gate) — the
   REVIEW-gate enforcement path is still untested and may extend skill value further.

## Practical implication

For a capable model, loading generic best-practice skills is low-value on routine work and
high-value precisely on the model's blind spots. The leverage is (a) identifying those blind
spots (security containment is one) and (b) routing the *specific* matching skill — ideally via
the REVIEW gate, which can fail insecure code and force the fix even when the build agent's first
draft missed it.
