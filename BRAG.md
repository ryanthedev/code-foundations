# code-foundations

**A ~18,000-line knowledge system that teaches AI agents how to write software like a senior engineer — then verifies they did.**

## The Problem

AI coding agents generate code fast but lack engineering judgment. They skip design, proceed without clarifying ambiguity, ignore existing patterns, self-validate by default, and produce work that passes tests but misses requirements. There's no mechanism to inject decades of software engineering wisdom into an agent's decision-making loop — and no mechanism to verify the output against the intent.

## Key Decisions

**Distilling books into executable decision procedures, not summaries.**

Code Complete, A Philosophy of Software Design, Gang of Four, Working Effectively with Legacy Code, and Clean Architecture aren't referenced as reading material. Each is decomposed into skills — small, self-contained protocols with decision trees, thresholds, and checklists that an agent can follow mid-task. The `clarify` skill doesn't say "ask good questions." It classifies ambiguity into four fault types (intention, premise, parameter, expression), three directions (semantic, too broad, too narrow), then selects the question that maximally reduces uncertainty across competing hypotheses. The `cc-debugging` skill doesn't say "debug carefully." It enforces STABILIZE → LOCATE → HYPOTHESIZE → EXPERIMENT → FIX → TEST → SEARCH, where EXPERIMENT means proving a hypothesis *without* changing production code.

> Engineering knowledge encoded as process, not prose. The agent doesn't need to have read the book — it follows the extracted decision procedure.

**Prover-verifier architecture with adaptive gate policies.**

The build pipeline doesn't use a single agent that writes and reviews its own work. It dispatches a build agent (prover) and a separate post-gate agent (verifier) at a *lower model tier* — opus builds get sonnet reviews, sonnet builds get haiku reviews. The asymmetry is intentional: verification is computationally cheaper than generation, and a weaker model catching issues in a stronger model's output is a stronger signal than self-review. But the system doesn't blindly apply this to everything. Gate policy adapts per phase: Full (BUILD → REVIEW → commit) for high-risk work, Standard (tests-as-gate) for medium work, Minimal for trivial work. A catch-up review triggers dynamically when ungated phases accumulate.

> Non-uniform verification calibrated to risk. Research-backed: Plan and Budget showed 193.8% efficiency gain from adaptive verification; Thinkless showed 86.7% of easy queries are harmed by deep reasoning.

**A three-stage pipeline that separates knowing from planning from doing.**

Research, plan, and build are distinct commands with distinct outputs. Research produces confirmed requirements through facilitated conversation — the skill has opinions, matches the user's energy, and knows when to stop asking. Plan produces a plan file with phased implementation, skill assignments per phase, model overrides, and done-when items with unique IDs. Build consumes that plan file mechanically — worktree isolation, subagent dispatch, stub → implement → validate cycles, structured commits with epistemic-status trailers, trust reports. The plan is a contract between plan and build. Each stage can be used independently or chained.

> Requirements, architecture, and execution as separate concerns. The AI that clarifies your idea is not the same invocation that implements it.

**Done-when items as the thread through the entire system.**

Every plan phase has explicit done-when items (DW-1.1, DW-1.2, ...) that flow unchanged from plan through build dispatch into the post-gate review. The build agent maps each DW item to test cases. The post-gate agent independently verifies each DW item against the implementation with file:line evidence — using the original plan's items, not the build agent's interpretation of them. If the build agent silently descoped a requirement, the review catches it because the DW items came from the orchestrator, not from the test suite.

> Requirements traceability from plan to test to review, with independent verification at each handoff.

## How It Works

The system is structured as a Claude Code plugin: 19 skills, 4 commands, 2 agent templates, and 14 reference documents.

**Skills** are the knowledge layer. Each encodes a specific engineering discipline as an actionable protocol — not documentation to read, but procedures to follow. They're organized by source: `cc-*` skills from Code Complete (debugging, control flow, defensive programming, refactoring, quality practices), `aposd-*` from A Philosophy of Software Design (deep modules, complexity reduction, correctness verification), `gof-*` for Gang of Four patterns, `ca-*` for Clean Architecture boundaries, and `welc-*` for legacy code. Skills are invoked by agents during builds, loaded during reviews, and available standalone.

**Commands** are the workflow layer. `/research` facilitates requirements discovery. `/plan` produces implementation plans with complexity-adaptive tracks (Quick/Standard/Full). `/build` executes plans through gated phases with subagent dispatch. `/debug` guides scientific debugging. Commands orchestrate — they dispatch agents, manage tasks, enforce gates, and handle failures.

**References** are the orchestration-knowledge layer. Dispatch templates, gate failure protocols, worktree gates, and trust reports live here. Engineering guidance lives in the skills themselves — gates load each phase's assigned skills (with their checklists) directly, and each agent definition carries its own protocol, so it works even with zero skills assigned.

**Agents** are the execution layer. The build agent combines discovery, design, and implementation in one pass under an always-on baseline discipline: stub the interface, implement it, then validate each requirement with tests — requirement→test traceability (no silent descoping), test anchoring, and a scope clamp — design ceremony comes only from assigned skills. The post-gate agent is a debiased independent critic: it receives no intent-framing (no plan narrative, no progress summary, no build-agent reasoning — research shows such framing collapses bug detection by up to 93 percentage points), runs the test suite first, verifies each done-when item with evidence and an execution trace, checks five correctness dimensions (concurrency, errors, resources, boundaries, security), and returns a verdict that can only FAIL on demonstrated defects — never on inferred requirements or style opinions. Security-sensitive phases get a 3-sample majority-vote review. The orchestrator never touches code directly during builds — it dispatches, waits, commits, and handles failures.

## What Makes It Different

The naive approach to improving AI code quality is prompt engineering: tell the agent to "write clean code" or "follow best practices." That produces better-sounding code without better engineering. Code-foundations takes the opposite approach — it doesn't describe good engineering, it *operationalizes* it. McCabe complexity isn't mentioned as a concept; there's a threshold table (0-5: fine, 6-10: simplify, 10-20: exception only if flat dispatch with exhaustive cases, 20+: mandatory refactor). The APOSD error hierarchy isn't advice; it's a three-level decision procedure with validation gates at each level and explicit carve-outs for security-critical code.

The second difference is structural honesty about AI limitations. The system assumes the build agent will miss things — that's why the post-gate agent exists. It assumes the plan might be wrong — that's why there's a gate failure protocol with a 3-retry cap and mandatory user escalation. It assumes agents will silently descope requirements — that's why DW items flow from the orchestrator, not from the agent's self-report. Every design choice treats the AI as a capable but fallible executor that needs external verification, not a reliable system that occasionally needs a check.
