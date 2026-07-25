# Code Foundations

**AI that codes like a senior engineer.** Checklists, quality gates, and verification built into every workflow.

> **Active development** - Installed via the marketplace below (currently v5.3.0); no tagged GitHub releases yet. The build workflow and skills are benchmark-validated, but subagent orchestration is still being tuned — expect changes.

---

## Pick Your Workflow

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/code-foundations:research` | Clarify what you want through facilitated conversation | Exploring ideas |
| `/code-foundations:plan` | Create implementation-ready plans | Feature planning |
| `/code-foundations:build` | Execute plans with quality gates | Implementing approved plans |
| `/code-foundations:debug` | Scientific debugging with task tracking | Bug hunting |

**Why this exists:** LLMs write code fast. Fast code without engineering discipline creates debt. This plugin loads proven checklists and mental models so Claude applies them automatically.

---

## Planning and Execution: Research to Build

Three commands work together: Research clarifies intent, Plan creates the plan, Build executes it.

```
/code-foundations:research "add notification system"
     ↓
.code-foundations/research/2026-01-30-notifications.md
     ↓
/code-foundations:plan .code-foundations/research/2026-01-30-notifications.md
     ↓
.code-foundations/plans/2026-01-30-notifications.md
     ↓
/code-foundations:build .code-foundations/plans/2026-01-30-notifications.md
```

### `/code-foundations:research` - Clarify What You Want

**Facilitated conversation to extract and document requirements.**

```
User: "/code-foundations:research add user notifications"

  → Facilitated conversation
  → Progressive narrowing: purpose, actors, context, boundaries, needs, risks
  → Save requirements to .code-foundations/research/ (Status: draft)
  → Optional verification: grill (adversarial Q&A, one question at a time)
    + cold-read subagent (fresh context, doc path only) → Status: confirmed
```

### `/code-foundations:plan` — Create the Plan

**Researches your codebase, audits available skills, then asks targeted questions.**

```
User: "/code-foundations:plan add user notifications"

  DISCOVER
  ├─ Search codebase for existing patterns
  ├─ Audit ALL available skills (from every installed plugin)
  │   → "React Native project detected → react-native-foundations:coding"
  │   → "Frontend UI work → design-for-ai:a11y-audit"
  ├─ Ask targeted questions (one at a time)
  └─ Produce problem statement

  EXPLORE (Medium/Complex)
  ├─ 2-3 structurally different approaches
  └─ Pre-mortem (Complex)

  DETAIL → SAVE → CHECK → CONFIRM → HANDOFF
  ├─ Phase specs with Skills field per phase
  ├─ Save plan to .code-foundations/plans/
  ├─ Subagent reviews plan with fresh eyes
  ├─ User confirms + corrections
  └─ Handoff to /code-foundations:build
```

**Skills loaded:** `ca-architecture-boundaries` (system-level boundaries, for shaping approaches and phase seams). Module-level design skills (`aposd-designing-deep-modules`, etc.) are matched per phase and loaded during DETAIL, not here.

**Task tracking:** Creates progress tasks at startup so you can see where plan is in its flow.

### `/code-foundations:build` - Execute the Plan

**Gated execution with subagents.** Each phase has mandatory quality checks.

```
User: "/code-foundations:build .code-foundations/plans/2026-01-30-notifications.md"

  BRANCH GATE
  └─ On main? → STOP. Create feature branch first.

  FOR EACH PHASE:
  ┌────────────────────────────────────────────────────────────┐
  │  BUILD        Build-agent: discovery + design + implement  │
  │       ⛔ Loads pre-gate + implement standards              │
  ├────────────────────────────────────────────────────────────┤
  │  REVIEW       Full gate + security-sensitive phases only   │
  │       ⛔ Cannot commit until reviewer returns PASS         │
  ├────────────────────────────────────────────────────────────┤
  │  COMMIT       Orchestrator commits (green suite is enough  │
  │               for Standard/Minimal — review comes later)   │
  └────────────────────────────────────────────────────────────┘

  EVERY N PHASES (Review cadence, default 3):
  ┌────────────────────────────────────────────────────────────┐
  │  BATCH REVIEW  Post-gate-agent over every un-reviewed      │
  │                phase at once + cross-phase coherence       │
  │       ⛔ Also fires before any Full phase and before the   │
  │          final VERIFY — nothing ships unreviewed           │
  └────────────────────────────────────────────────────────────┘
```

### Quality Gates per Phase

| Phase | Guidance | What Gets Enforced |
|-------|----------|-------------------|
| BUILD | Baseline discipline (agent definition) + per-phase skills | DW→test traceability, stub → implement → validate, test anchoring, scope clamp, plus assigned skill checklists |
| REVIEW | Debiased review protocol (agent definition) + per-phase skills | Execute-first verification, per-requirement evidence + trace, anti-overcorrection verdict |
| VERIFY | `performance-optimization`, `cc-refactoring-guidance` | Performance regressions, refactoring opportunities, build + tests + lint |

Gate policy is adaptive, and what it adapts is review *timing* — every phase is reviewed. Full (BUILD + blocking REVIEW, always runs alone) and security-sensitive phases (3-sample majority vote on fable) hold their commit until the reviewer returns PASS. Standard and Minimal phases commit on a green suite and are covered by a **batch REVIEW** that fires every `Review cadence` phases (default 3), before any Full phase, and once before the final VERIFY. Batching costs a window of un-reviewed HEAD and buys reviewer context: seeing several phases together surfaces cross-phase incoherence that isolated reviews structurally cannot. A batch FAIL is fixed forward against the committed code.

Skills assigned per phase during plan's SAVE step — gates load only those skills; each agent carries its own protocol. Independent Standard/Minimal phases (no dependency, disjoint `File scope`) build in parallel waves, each in its own worktree, integrated by cherry-pick in plan order.

The system saves every artifact to `.code-foundations/build/`. Per-phase commits enable rollback.

---

## Getting Stuff Done: Debug

### `/code-foundations:debug` - Scientific Debugging

**Predict, log, run, resolve.** Task list keeps you on track.

```
/code-foundations:debug login fails 20% of the time

  TASK #1: Investigate login failure
  ├─ PREDICT: "All tokens should be valid"
  ├─ LOG: Add at validateToken entry
  ├─ RUN: 2 of 10 fail, tokens valid
  └─ RESOLVE: Problem is downstream → narrow

  TASK #2: Narrow: validateToken result
  ├─ PREDICT: "Cache should HIT on second call"
  ├─ LOG: Add at cache check
  ├─ RUN: Two MISS within 10ms
  └─ RESOLVE: Race condition found → fix

  TASK #3: Fix: request deduplication
  └─ RESOLVE: Fix applied → verify

  TASK #4: Verify: parallel logins succeed
  └─ RUN: 100 parallel → 0 failures → Done!
```

**Skill loaded:** `cc-debugging` (scientific debugging method)

The task list prevents rabbit holes, missed verifications, and lost context.

### When to Use Each

| Situation | Command |
|-----------|---------|
| Vague idea, unclear requirements | `/code-foundations:research` |
| Need full feature planning | `/code-foundations:plan` |
| Have approved plan, ready to implement | `/code-foundations:build` |
| Bug hunting, need structured approach | `/code-foundations:debug` |

---

## Installation

```bash
# Add marketplace
/plugin marketplace add ryanthedev/rtd-claude-inn

# Install
/plugin install code-foundations@rtd

# Update
/plugin update code-foundations@rtd
```

---

## Credits

Based on *Code Complete, 2nd Edition* by Steve McConnell and *A Philosophy of Software Design* by John Ousterhout.

## License

MIT
