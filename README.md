# Code Foundations

**AI that codes like a senior engineer.** Checklists, quality gates, and verification built into every workflow.

> **Experimental** - This plugin is under active development. We are fine-tuning subagent orchestration to ensure reliable skill loading and phase execution. We will add GitHub releases once the plugin stabilizes.

---

## Pick Your Workflow

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/code-foundations:whiteboarding` | Create implementation-ready plans | Feature planning |
| `/code-foundations:building` | Execute plans with quality gates | Implementing approved plans |
| `/code-foundations:code` | Pseudocode-first development | Know what to build, want design collaboration |
| `/code-foundations:prototype` | Quick feasibility proof | Technical uncertainty |
| `/code-foundations:debug` | Scientific debugging with task tracking | Bug hunting |

**Why this exists:** LLMs write code fast. Fast code without engineering discipline creates debt. This plugin loads proven checklists and mental models so Claude applies them automatically.

---

## Planning and Execution: Whiteboarding to Building

Two commands work together: Whiteboarding creates the plan, Building executes it.

```
/code-foundations:whiteboarding "add notification system"
     ↓
docs/plans/2026-01-30-notifications.md
     ↓
/code-foundations:building docs/plans/2026-01-30-notifications.md
```

### `/code-foundations:whiteboarding` - Create the Plan

**Researches your codebase, audits available skills, then asks targeted questions.**

```
User: "/code-foundations:whiteboarding add user notifications"

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
  ├─ Save plan to docs/plans/
  ├─ Subagent reviews plan with fresh eyes
  ├─ User confirms + corrections
  └─ Handoff to /code-foundations:building
```

**Skills loaded:** `aposd-designing-deep-modules`, `aposd-reviewing-module-design`

**Task tracking:** Creates progress tasks at startup so you can see where whiteboarding is in its flow.

### `/code-foundations:building` - Execute the Plan

**Gated execution with subagents.** Each phase has mandatory quality checks.

```
User: "/code-foundations:building docs/plans/2026-01-30-notifications.md"

  BRANCH GATE
  └─ On main? → STOP. Create feature branch first.

  FOR EACH PHASE:
  ┌────────────────────────────────────────────────────────────┐
  │  BUILD        Build-agent: discovery + pseudocode + code   │
  │       ⛔ Loads pre-gate + implement standards              │
  ├────────────────────────────────────────────────────────────┤
  │  REVIEW       Post-gate-agent checks quality (Full gate)   │
  │       ⛔ Cannot commit until reviewer returns PASS         │
  ├────────────────────────────────────────────────────────────┤
  │  COMMIT       Orchestrator commits after gates pass        │
  └────────────────────────────────────────────────────────────┘
```

### Quality Gates per Phase

| Phase | Standards Loaded | What Gets Enforced |
|-------|-----------------|-------------------|
| BUILD | `references/pre-gate-standards.md` + `references/implement-standards.md` | Design-before-code, interface depth, control flow, naming, complexity |
| REVIEW | `references/post-gate-standards.md` | Correctness, quality, module design, error handling |
| VERIFY | `performance-optimization`, `cc-refactoring-guidance` | Performance regressions, refactoring opportunities, build + tests + lint |

Gate policy is adaptive: Full (BUILD + REVIEW), Standard (BUILD + tests), Minimal (BUILD only). Skills assigned per phase during whiteboarding's SAVE step.

The system saves every artifact to `docs/building/`. Per-phase commits enable rollback.

---

## Getting Stuff Done: Code, Prototype, Debug

### `/code-foundations:code` - Pseudocode First

**Design loop, then implementation loop.** You know what to build and want to collaborate on design first.

```
PHASE 1: DESIGN LOOP
├─ Draft pseudocode (flow + contracts)
├─ Explore subagent researches if needed
├─ Tasklist tracks decisions
├─ User feedback → refine
└─ "Ready to build?" → explicit confirmation

PHASE 2: IMPLEMENTATION LOOP
├─ Subagent implements from pseudocode
├─ Unit tests → integration tests
├─ Commit checkpoint
└─ User picks next task
```

**Skills loaded:** `cc-pseudocode-programming`, `cc-defensive-programming`

Change costs nothing in the design loop. Once you say "let's build," the contract holds.

### `/code-foundations:prototype` - Prove Feasibility

**One question. Minimum code. Maximum learning.**

```
User: "/code-foundations:prototype can I use WebSockets with this auth?"

  SCOPE: "Can I establish authenticated WebSocket connection?"
  MINIMUM: <50 lines, happy path only
  EXECUTE: Write code, run it
  RESULT: YES / NO / PARTIAL

  → Saves to docs/prototypes/YYYY-MM-DD-<slug>.md
```

**Skills loaded:** `cc-pseudocode-programming`, `aposd-reviewing-module-design`

**Chains into planning:** A successful prototype feeds directly into `/code-foundations:whiteboarding` for full planning.

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
| Know what to build, want design collaboration | `/code-foundations:code` |
| Technical uncertainty, prove it works | `/code-foundations:prototype` |
| Need full feature planning | `/code-foundations:whiteboarding` |
| Have approved plan, ready to implement | `/code-foundations:building` |
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

## Experimental

### Code Review System

> LLM code review is non-deterministic — the same code can produce different feedback on each run. We ground every check in explicit checklists with pass/fail criteria so the agent evaluates against defined standards, not intuition.

**Single command. Parallel subagents.** Runs checklists against your code with specialized checking agents.

```bash
/code-foundations:review --sanity   # 14 core checks, quick pre-commit
/code-foundations:review --pr       # 546 checks, full PR review
```

#### Architecture

**Sanity (4-phase):**
```
EXTRACTION (haiku) → ORCHESTRATE (sonnet) → CHECKING (sonnet) → INVESTIGATION (sonnet)
```

**PR (5-phase):**
```
EXTRACTION (haiku) → CHECK ORCH (haiku) → CHECKING (sonnet) → ORCHESTRATE (haiku) → INVESTIGATION (sonnet)
```

| Phase | What Happens | Parallelism |
|-------|--------------|-------------|
| **Extraction** | Parse code into semantic units (functions, classes) | 1 agent per 5 files |
| **Check Orch** | Group checks by ID prefix (PR only) | Single agent |
| **Checking** | Run checklists against code | 1 agent per prefix group |
| **Orchestrate** | Dedupe, batch findings, create investigation tasks | Single agent |
| **Investigation** | Verify findings, capture code context and diff | 1 agent per 5 findings |

---

## Credits

Based on *Code Complete, 2nd Edition* by Steve McConnell and *A Philosophy of Software Design* by John Ousterhout.

## License

MIT
