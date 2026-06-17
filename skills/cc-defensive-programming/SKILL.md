---
name: cc-defensive-programming
description: "Applies Code Complete's defensive programming rules: barricade design, assertion vs error-handling selection, input validation policy, and correctness-vs-robustness strategy for the current context."
user-invocable: false
---

# cc-defensive-programming

Defensive code keeps small failures from compounding into silent, hard-to-diagnose ones. These four checks catch the violations that corrupt data and hide bugs rather than crashing loudly — each is almost always required; exceptions need explicit justification:

| Check | Why |
|---|---|
| No executable code in assertions | Assertions are compiled out of production builds; the code vanishes with them |
| No empty catch blocks | Silently swallows bugs that cascade into harder failures downstream |
| External input validated at entry | Unvalidated input is security vulnerabilities and data corruption |
| Assertions for bugs only | Anticipated runtime errors need handling, not assertions (which are disabled in production) |

Shared thresholds and the information-hiding rationale: `Read(${CLAUDE_PLUGIN_ROOT}/references/cc-foundations.md)`.

## Two rules that override the textbook

- **"Internal team API" is still external.** Any data crossing a network or process boundary is external input — validate it, even from a service your own team owns.
- **A barricade reduces redundant validation; it does not replace defense-in-depth.** Inside the barricade you may assume data is validated — except for security-critical paths (auth, crypto, PII), where you validate again. Barricade validation has bugs too.

External input = any data not provably controlled by the current code path: user input, files, network/API/DB responses, environment variables, and data from any other service.

## When NOT to apply

- Pure functions without side effects (but still validate inputs at system boundaries).
- Prototype/spike code, time-boxed before committing to an error strategy.
- Test code — test doubles intentionally violate production patterns.
- Performance-critical inner loops where assertion overhead is profiled at >5%.

Security-critical code (authentication, authorization, cryptographic operations, PII handling) is never exempt, regardless of the above. When in doubt, validate.

## Modes

### CHECKER

Execute the defensive-programming, assertion, and exception checklists against the code: `Read(${CLAUDE_SKILL_DIR}/checklists.md)`. Output one row per item: `| Item | Status | Evidence | Location |`, status ∈ VIOLATION (missing validation, empty catch, side-effecting assertion) / WARNING (inconsistent handling, missing docs) / PASS.

### APPLIER

Produce assertion placement, error-handling strategy, barricade architecture, and validation implementations. Search the codebase for the existing error-handling pattern (exception vs return code vs Result type, custom exception classes, logging conventions) and follow it — consistency in error handling is what makes failures debuggable. Full gate: `Read(${CLAUDE_PLUGIN_ROOT}/references/pattern-reuse-gate.md)`.

## Assertion vs error handling

| Condition | Assertion | Error handling |
|---|---|---|
| Should never occur (programmer bug) | Yes | No |
| Can occur at runtime / anticipated bad input | No | Yes |
| External input | No | Yes — always validate |
| Internal interface, same module | Yes | No |
| Internal interface crossing a trust boundary | Yes | Yes |
| Public-API precondition violation | Yes | Yes |
| Security-critical / highly robust system | Both | Both (defense in depth) |

When a condition is genuinely unclear ("is this a bug or expected?"), clarify requirements with a domain expert rather than guessing.

## Correctness vs robustness

- **Correctness** — never return an inaccurate result; shut down rather than produce a wrong answer (safety-critical, financial, data pipelines).
- **Robustness** — keep operating even if results are sometimes inaccurate (consumer apps, internal tools).

| Domain | Lean toward | Key question |
|---|---|---|
| Safety-critical (medical, aviation) | Correctness | — |
| Enterprise/B2B, financial, data pipelines | Correctness | Would wrong data drive a bad business decision? Does downstream assume integrity? |
| SaaS platforms | Balanced | Blast radius of a wrong answer vs unavailability? |
| Consumer apps, internal tools | Robustness | Can the user recover from a crash? |
| Real-time systems | Context-dependent | Is stale data better or worse than no data? |

## Barricade design

1. Identify external interfaces (user input, files, network, APIs, inter-service calls).
2. Place validation at the barricade boundary — all external data checked here.
3. Inside the barricade, use assertions for internal bugs (data assumed validated).
4. Strategy: external boundary = error handling; internal = assertions.

Class-level barricade: public methods validate and sanitize; private methods within that class may assume safe data.

## Error-handling strategy options

Choose one and apply it consistently — error handling is an architectural decision.

| Strategy | Use for |
|---|---|
| Return neutral value | Display defaults, non-critical config |
| Substitute next valid data | Streaming/sensor data with redundancy |
| Return previous answer | Display refresh, non-critical caching (never financial data) |
| Substitute closest legal value | Input clamping, slider bounds |
| Log warning and continue | Non-critical degradation, feature flags |
| Return error code | APIs with status conventions, C-style interfaces |
| Centralized error handler | Consistent logging, monitoring integration |
| Display error message | User-facing apps (don't leak security info) |
| Shut down gracefully | Safety-critical, data-corrupting errors |

## Modern error propagation

Synchronous exception propagation assumes a synchronous call stack; these patterns need explicit handling:

- **async/await** — an unhandled rejection crashes Node; wrap awaited calls and re-throw domain-level exceptions.
- **Callbacks** — errors don't propagate; use the error-first `callback(error, result)` pattern or wrap in promises.
- **`Promise.all`** — first rejection loses other results; use `allSettled` and decide fail-entirely vs partial.
- **Event handlers / React** — synchronous throws are silently swallowed; log explicitly and use error boundaries for render errors.

## Offensive programming (development builds)

Make errors loud during development so they're found early; make them unobtrusive with graceful recovery in production. Techniques: make asserts abort, fill allocated memory and freed objects with junk, fail hard on default/else clauses, email error logs to yourself.

## Evidence

- "Garbage in, garbage out" is obsolete — production software must validate or reject [McConnell p.188].
- Error handling is an architectural decision, enforced consistently [McConnell p.197].
- Bugs cost ~100x more to fix in production than at design time [IBM Systems Sciences Institute].
- Mars Climate Orbiter was lost to a unit mismatch [NASA 1999] — nine months of success does not mean code is safe.

## Chain

| After | Next |
|---|---|
| Validation complete | `Skill(code-foundations:cc-control-flow-quality)` |
