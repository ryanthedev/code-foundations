# Plan ↔ Build Integration

How `/code-foundations:plan` and `/code-foundations:build` chain together. Reference material — orchestrator does not need this hot path.

---

## Expected Flow (Single Build)

```
/code-foundations:plan "user story"  OR  /code-foundations:plan .code-foundations/research/<doc>.md
  ↓
[Shared steps: code-standards scan → clarify (5-round cap) → confirmed problem statement]
  ↓
[Quick track: decompose → detail → cross-cut → save → check → present]   (Simple)
[Standard/Full pipeline (skill: planning), staged in place:                (Medium/Complex)
   Discover → Classify → Explore → Decompose → Detail → Cross-cut → Save → Check → Confirm → Handoff]
  ↓
[Each phase gets **Model:**, **Gate:**, **Skills:**, **Depends on:**, **File scope:** — Gate drives build's gate policy, Depends on + File scope drive wave derivation]
[Save to .code-foundations/plans/YYYY-MM-DD-topic.md — Status: draft until the user confirms the presented plan, then ready]
  ↓
[Drop thinking effort for the build run — the plan carries the reasoning (low for all-serial plans, default when any phase carries File scope)]
  ↓
/code-foundations:build .code-foundations/plans/YYYY-MM-DD-topic.md
  ↓
[Worktree Gate → creates .claude/worktrees/<slug>/]
[Per-phase gated execution in worktree (BUILD → REVIEW per the phase's **Gate:**)]
[Tests pass → orchestrator commits per phase]
[Summary report with merge instructions]
```

---

## Expected Flow (Parallel Builds)

```
Claude Instance 1                        Claude Instance 2
────────────────                        ────────────────
/plan "auth system"            /plan "notifications"
  → saves plan                              → saves plan
  → clear + build                         → clear + build

/build (worktree: auth-system)       /build (worktree: notifications)
  → .claude/worktrees/auth-system/        → .claude/worktrees/notifications/
  → feature/auth-system branch            → feature/notifications branch
  → all phases run isolated               → all phases run isolated
  → report: "merge when ready"            → report: "merge when ready"

                    User merges both to main when ready
```

**Key constraint:** Each parallel build must target a different plan file. Never run two build instances against the same plan.

---

## Intra-Build Waves

Parallelism also exists *within* one build: phases with no dependency between them, disjoint `**File scope:**` globs, and Standard/Minimal gates run their BUILD agents concurrently in separate phase worktrees, integrated sequentially by the orchestrator (cherry-pick, plan-order commits). The planner opts a phase in by giving it `File scope`; build derives the waves — see `commands/build.md` Wave Derivation. This composes with inter-build parallelism above: waves inside each instance, instances across plan files.

---

## Plan File Model Syntax

Every phase carries a `**Model:**` field. The ladder: **fable** (judgment-heavy: novel architecture, security-sensitive design, cross-cutting refactors) → **sonnet** (the default — Sonnet 5 handles well-specified implementation fast and cheap) → **haiku** (mechanical: config edits, renames, doc moves). **opus** stays a valid override for when fable is unavailable or the user asks for it.

```markdown
### Phase 1: Simple Config
**Model:** haiku
- [ ] Update config file

### Phase 2: Complex Engine
**Model:** fable
- [ ] Build query parser
- [ ] Implement optimizer
```

`**Model:**` is required on every phase — there are no legacy plans; build stops and asks for a re-plan when the field is missing. REVIEW runs one tier below BUILD, floored at sonnet (fable→sonnet, opus→sonnet, sonnet→sonnet — never haiku) — prover-verifier asymmetry, intentional; the sonnet floor exists because haiku's planted-defect recall proved unreliable on REVIEW-shaped tasks (round-2 model-tier benchmark, 0/5 on one review task). The one deliberate exception: security-sensitive REVIEW samples run on **fable** regardless of the BUILD model — for security, verification rigor beats cost asymmetry.

Model facts worth knowing when assigning (as of 2026-07 — re-verify via the claude-api skill when this feels stale):

- **Fable 5** — strongest judgment; give it intent ("why") framing in dispatch prompts; its failure mode is over-elaboration, not laziness, so pair with a brevity nudge on long tasks.
- **Sonnet 5** — new tokenizer (~1.0–1.35× the tokens of Sonnet 4.6 for the same input); adaptive thinking on by default; excellent default builder.
- **Opus 4.8** — literal instruction follower: state scope explicitly ("apply to every section, not just the first").
- **Haiku 4.5** — needs explicit, self-contained prompts; anchor output formats with an example.

---

## Thinking Effort Doctrine

Effort follows where the reasoning lives:

- **Planning: high.** The plan is the highest-leverage artifact — decomposition, seam contracts, and gate/model assignment are judgment work. This is where deep thinking pays.
- **Building: low for all-serial plans, default when any phase carries `**File scope:**`** (wave-eligible — the plan never stores waves; build derives them). The plan already contains the strategic reasoning; serial orchestration is dispatch work. Wave builds keep default effort because the orchestrator retains real judgment (integration failures, wave-failure handling). The subagents think in their own contexts either way — orchestrator effort doesn't cascade to them.
- **Subagent depth (BUILD/REVIEW agents): derived from the phase, not the orchestrator.** The Agent tool has no `effort` parameter, so depth is steered by the wording-sensitive phrases below, injected by build's Effort Alignment (`commands/build.md`): BUILD agents get "Think carefully" unless the phase `**Model:**` is haiku (mechanical → "Answer directly"); REVIEW agents always get "Think carefully" — a reviewer that skims misses defects, mirroring the sonnet REVIEW floor. Build stops to ask the user only when a phase's `**Model:**` (effort) and `**Gate:**` (rigor) disagree — the effort doesn't match the risk.

In dispatch prompts, steer per-agent depth with the wording-sensitive phrases: encourage with "This task involves multi-step reasoning. Think carefully before responding."; suppress with "Answer directly without deliberating." — not with hand-written step plans.

Worktree provides filesystem isolation from other builds.
