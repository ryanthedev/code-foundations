# Skill Catalog

This file carries richer when-to-match detail for the 19 internal code-foundations skills than
their one-line descriptions can. The plan/build skill-discovery steps match phase goals against
the **available-skills register** (all skills in context — the internal 19, now `user-invocable:
false` so model-discoverable but hidden from the slash menu, plus any external plugin skills);
this file is the tie-breaker that disambiguates the internal sibling pairs. It is NOT the source
of *which* skills exist — the register is. One entry per skill: `code-foundations:<name> — <when
to match>`. Disambiguation notes distinguish sibling pairs that share surface keywords.

---

## CC family — Code Complete process and metric skills

code-foundations:cc-debugging — Match when a phase involves active bug investigation: stabilizing a reproduction case, locating the defect source, or tracing root cause of a specific failure. Not for QA process design or test coverage planning (use cc-quality-practices).
code-foundations:cc-defensive-programming — Match when a phase designs or audits input validation, assertion policy, error-handling strategy, or barricade placement. Includes choosing between correctness and robustness under specific constraints.
code-foundations:cc-control-flow-quality — Match when a phase audits or restructures loop design, deeply nested conditionals, cyclomatic complexity reduction, guard-clause introduction, or boolean expression simplification.
code-foundations:cc-pseudocode-programming — Match when a phase designs new routines from scratch, particularly when requirements are vague or implementation order is unclear. Provides pseudocode-first workflow before any coding.
code-foundations:cc-quality-practices — Match when a phase designs the QA process itself: selecting defect-detection techniques, sizing test suites, planning review and inspection processes. Not for debugging an active bug (use cc-debugging).
code-foundations:cc-refactoring-guidance — Match when a phase modifies existing code structure without changing behavior, or must choose between refactor, rewrite, and fix-first. Includes commit-sequencing discipline.
code-foundations:cc-routine-and-class-design — Match when a phase designs or audits routines and classes at the routine level: cohesion, parameter count, LSP verification, inheritance vs containment. Not for system-level architecture (use ca-architecture-boundaries).
code-foundations:welc-legacy-code — Match when a phase must modify code that lacks tests: characterization test writing, seam identification, sprout/wrap application. Invoked conditionally from cc-refactoring-guidance when untested code is involved.

---

## APOSD family — A Philosophy of Software Design skills

code-foundations:aposd-designing-deep-modules — Match when a phase creates a new module, API, class, or service design from scratch. Generates and compares alternatives before implementation. Not for assessing existing designs (use aposd-reviewing-module-design); not for routine-level design (use cc-routine-and-class-design).
code-foundations:aposd-reviewing-module-design — Match when a phase assesses the quality of existing code: interface depth, information leakage, pass-through layers, cognitive load, unknown unknowns. Produces assessment only, not transformations (use aposd-simplifying-complexity for edits).
code-foundations:aposd-simplifying-complexity — Match when a phase must transform existing complex code: resolving error hierarchies, collapsing configuration proliferation, moving caller-side logic into modules. Produces edits, not just findings (distinguishes from aposd-reviewing-module-design which is assessment-only).
code-foundations:aposd-verifying-correctness — Match when a phase needs a post-implementation completeness check across functional, error-handling, concurrency, and security dimensions. Run after a coding phase is nominally complete, not during active bug investigation.

---

## CA family — Clean Architecture skills

code-foundations:ca-architecture-boundaries — Match when a phase designs system-level architecture: layer boundaries, dependency direction, separating business logic from infrastructure. For system scope (multiple components, layers, or services), not routine or module scope.

---

## GoF family — Gang of Four design pattern skills

code-foundations:gof-design-patterns — Match when a phase applies or selects a structural design pattern: Factory, Strategy, Observer, Decorator, Command, Adapter, Composite, Singleton, Builder, Proxy, Facade, Template Method, State, Visitor, or any other of the 23 GoF patterns.

---

## Standalone skills

code-foundations:clarify — Match when a phase begins with underspecified requirements, multiple valid interpretations, or critical unknowns. Produces a confirmed problem statement before any implementation work.
code-foundations:code-clarity-and-docs — Match when a phase writes or audits documentation, comments, naming, or AI-facing files (README, CLAUDE.md). Includes the comments-first workflow for new code.
code-foundations:code-standards — Match when a phase needs to establish or update the project's docs/code-standards.md. Run at the start of a new project or when conventions are undocumented.
code-foundations:performance-optimization — Match when a phase addresses a measured or suspected performance bottleneck: profiling, algorithm selection, data-structure changes, latency or memory targets.
code-foundations:planning — Match only when dispatched from the plan command for Medium or Complex tasks. Not for Quick-track plans. Internal to the plan pipeline; not a general-purpose phase skill.
