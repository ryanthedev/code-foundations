# Code Foundations

**AI that codes like a senior engineer.** Checklists, quality gates, and verification built into every workflow.

---

## Pick Your Workflow

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/code-foundations:review` | Profile-driven code review | Pre-commit, PR review |
| `/code-foundations:whiteboarding` | Create implementation-ready plans | Feature planning |
| `/code-foundations:building` | Execute plans with quality gates | Implementing approved plans |
| `/code-foundations:code` | Pseudocode-first development | Know what to build, want design collaboration |
| `/code-foundations:prototype` | Quick feasibility proof | Technical uncertainty |
| `/code-foundations:debug` | Scientific debugging with task tracking | Bug hunting |

**Why this exists:** LLMs write code fast. Fast code without engineering discipline creates debt. This plugin loads proven checklists and mental models so Claude applies them automatically.

---

## Code Review System

**Single command.** Profile-driven. Parallel subagents.

```bash
/code-foundations:review --sanity          # 99 checks, quick pre-commit
/code-foundations:review --pr              # 548 checks, full PR review
/code-foundations:review --profile <name>  # Custom profile
```

### Profiles

| Profile | Checklists | Checks | Use Case |
|---------|------------|--------|----------|
| `--sanity` | 1 | 99 | Pre-commit sanity check |
| `--pr` | 10 | 548 | Full PR review |
| Custom | varies | varies | Your saved configuration |

**Create custom profiles:** `/code-foundations:review-profile --setup`

### Architecture: 4-Phase Pipeline

```
┌──────────────┐     ┌──────────────┐     ┌───────────────┐     ┌──────────┐
│  EXTRACTION  │ ──▶ │   CHECKING   │ ──▶ │ INVESTIGATION │ ──▶ │  REPORT  │
│   (haiku)    │     │ (per checklist)│   │    (haiku)    │     │          │
└──────────────┘     └──────────────┘     └───────────────┘     └──────────┘
```

| Phase | What Happens | Parallelism |
|-------|--------------|-------------|
| **Extraction** | Parse code into semantic units (functions, classes) | 1 agent per 5 files |
| **Checking** | Run checklists against code, skills as agent personas | 1 agent per checklist |
| **Investigation** | Verify findings, reduce false positives | 1 agent per 5 findings |
| **Report** | Merge results, generate actionable output | Single agent |

### Skills as Personas

Each checklist loads skills that become the checking agent's persona:

```yaml
# Profile example
checklists:
  - path: skills/cc-defensive-programming/checklists.md
    skills: [cc-defensive-programming]  # Agent adopts this expertise
```

The PR profile covers: defensive programming, complexity reduction, module design, code layout, control flow, correctness verification, quality practices, performance, optimization, and documentation.

---

## Planning and Execution: Whiteboarding to Building

Two commands that work together. Whiteboarding creates the plan. Building executes it.

```
/code-foundations:whiteboarding "add notification system"
     ↓
docs/plans/2026-01-30-notifications.md
     ↓
/code-foundations:building docs/plans/2026-01-30-notifications.md
```

### `/code-foundations:whiteboarding` - Create the Plan

**Discovery-oriented brainstorming.** Researches your codebase before asking questions.

```
User: "/code-foundations:whiteboarding add user notifications"

  RESEARCH FIRST
  ├─ Search codebase for existing patterns
  ├─ Find similar implementations
  └─ Note naming conventions, error handling

  QUESTIONS (one at a time)
  ├─ "What notification types do you need?"
  │   ☐ Email only
  │   ☐ Push + Email
  │   ☐ In-app + Email
  └─ Wait for answer → ask next question

  2-3 STRUCTURALLY DIFFERENT APPROACHES
  ├─ Option A: Queue-based (recommended)
  ├─ Option B: Synchronous
  └─ Option C: Event-sourced

  → Saves to docs/plans/YYYY-MM-DD-<topic>.md
```

**Skills loaded:** `cc-construction-prerequisites`, `aposd-designing-deep-modules`

### `/code-foundations:building` - Execute the Plan

**Gated execution with subagents.** Each phase has mandatory quality checks.

```
User: "/code-foundations:building docs/plans/2026-01-30-notifications.md"

  BRANCH GATE
  └─ On main? → STOP. Create feature branch first.

  FOR EACH PHASE:
  ┌────────────────────────────────────────────────────────────┐
  │  DISCOVERY     Explore subagent reads codebase             │
  │       ⛔ Cannot proceed until discovery complete           │
  ├────────────────────────────────────────────────────────────┤
  │  PRE-GATE      Pseudocode subagent designs the solution    │
  │       ⛔ Cannot implement until pseudocode exists          │
  ├────────────────────────────────────────────────────────────┤
  │  IMPLEMENT     Implementation subagent writes code         │
  ├────────────────────────────────────────────────────────────┤
  │  POST-GATE     Reviewer subagent checks quality            │
  │       ⛔ Cannot commit until reviewer returns PASS         │
  ├────────────────────────────────────────────────────────────┤
  │  CHECKPOINT    Commit with phase summary                   │
  └────────────────────────────────────────────────────────────┘
```

### Quality Gates per Phase

| Gate | Skills Loaded | What Gets Enforced |
|------|---------------|-------------------|
| PRE-GATE | `cc-pseudocode-programming` | Design before code, routine cohesion |
| PRE-GATE | `aposd-designing-deep-modules` | Interface depth, information hiding |
| POST-GATE | `aposd-verifying-correctness` | Requirements coverage, boundary conditions |
| POST-GATE | `cc-defensive-programming` | Error handling, input validation |

**Every artifact is saved** to `docs/building/` for review. Per-phase commits enable rollback.

---

## Getting Stuff Done: Code, Prototype, Debug

### `/code-foundations:code` - Pseudocode First

**Design loop, then implementation loop.** You know what to build. You want to collaborate on the design before code exists.

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

The design loop is where changes are cheap. Once you say "let's build," the contract is set.

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

**Chains into planning:** Prototype success flows into `/code-foundations:whiteboarding` for full planning.

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

The task list prevents rabbit holes, forgotten verifications, and lost context.

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

## Credits

Based on *Code Complete, 2nd Edition* by Steve McConnell and *A Philosophy of Software Design* by John Ousterhout.

## License

MIT
