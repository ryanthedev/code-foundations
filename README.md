# Code Foundations

**AI that codes like a senior engineer.** Checklists, quality gates, and verification built into every workflow.

> **Experimental** - This plugin is under active development. We are fine-tuning subagent orchestration to ensure reliable skill loading and phase execution. We will add GitHub releases once the plugin stabilizes.

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
  → Save confirmed requirements to .code-foundations/research/
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

**Skills loaded:** `aposd-designing-deep-modules`, `aposd-reviewing-module-design`

**Task tracking:** Creates progress tasks at startup so you can see where plan is in its flow.

### `/code-foundations:build` - Execute the Plan

**Gated execution with subagents.** Each phase has mandatory quality checks.

```
User: "/code-foundations:build .code-foundations/plans/2026-01-30-notifications.md"

  BRANCH GATE
  └─ On main? → STOP. Create feature branch first.

  FOR EACH PHASE:
  ┌────────────────────────────────────────────────────────────┐
  │  BUILD        Build-agent: discovery + design + implement │
  │       ⛔ Loads pre-gate + implement standards              │
  ├────────────────────────────────────────────────────────────┤
  │  REVIEW       Post-gate-agent checks quality (Full gate)   │
  │       ⛔ Cannot commit until reviewer returns PASS         │
  ├────────────────────────────────────────────────────────────┤
  │  COMMIT       Orchestrator commits after gates pass        │
  └────────────────────────────────────────────────────────────┘
```

### Quality Gates per Phase

| Phase | Guidance | What Gets Enforced |
|-------|----------|-------------------|
| BUILD | Baseline discipline (agent definition) + per-phase skills | DW→test traceability, stub → implement → validate, test anchoring, scope clamp, plus assigned skill checklists |
| REVIEW | Debiased review protocol (agent definition) + per-phase skills | Execute-first verification, per-requirement evidence + trace, anti-overcorrection verdict |
| VERIFY | `performance-optimization`, `cc-refactoring-guidance` | Performance regressions, refactoring opportunities, build + tests + lint |

Gate policy is adaptive: Full (BUILD + REVIEW), Standard (BUILD + tests), Minimal (BUILD only). Skills assigned per phase during plan's SAVE step — gates load only those skills; each agent carries its own protocol. Security-sensitive phases get a 3-sample majority-vote REVIEW.

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
