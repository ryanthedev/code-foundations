---
name: aposd-simplifying-complexity
description: "Transforms complex code by applying APOSD's pull-complexity-downward principle: resolves error hierarchies, collapses configuration, and moves caller-side logic into modules. Produces edited code, not just assessment."
user-invocable: false
---

# Skill: aposd-simplifying-complexity

## Error Reduction Hierarchy

The best way to deal with exceptions is to define errors out of existence.

**Priority order:** Define out → Mask → Aggregate → Crash (app-level only)

---

## Pull Complexity Downward

### Decision Procedure

Before adding complexity to an interface (new parameters, new exceptions, new caller responsibilities):

```
1. Is this complexity closely related to the module's existing functionality?
   NO  → Should it be pulled into a DIFFERENT module?
         YES → Identify correct module, pull there
         NO  → Leave in place (may be inherent to caller's domain)
   YES → Continue

2. Will pulling down simplify code elsewhere in the application?
   NO  → Do not pull down (no benefit)
   YES → Continue

3. Will pulling down simplify the module's interface?
   NO  → Do not pull down (risk of leakage)
   YES → Pull complexity down
```

**All three conditions must be YES to pull down.**

**Critical Constraint:** Pulling down UNRELATED complexity creates information leakage. If the complexity isn't intrinsic to the module's core abstraction, it doesn't belong there—find the right home or leave it with the caller.

### Configuration Parameters

| Situation | Wrong Approach | Right Approach |
|-----------|---------------|----------------|
| Uncertain what value to use | Export parameter | Compute automatically |
| Different contexts need different values | Export parameter | Use reasonable default, expose only for exceptions |
| Policy decision unclear | Let user decide | Make a decision and own it |

**Configuration parameters represent incomplete solutions.** Every parameter pushes complexity to every user/administrator. Prefer dynamic computation over static configuration.

---

## Error Reduction Hierarchy

Apply in order of preference:

| Priority | Technique | How It Works | Example |
|----------|-----------|--------------|---------|
| **1** | Define out | Change semantics so error is impossible | `unset(x)` = "ensure x doesn't exist" (not "delete existing x") |
| **2** | Mask | Handle at low level, hide from callers | TCP retransmits lost packets internally |
| **3** | Aggregate | Single handler for multiple exceptions | One catch block in dispatcher handles all `NoSuchParameter` |
| **Special** | Crash | Print diagnostic and abort (app-level only) | `malloc` failure in non-recoverable contexts |

**Note on "Crash":** This is NOT level 4 of a hierarchy—it's a special case for truly unrecoverable errors in application code. Libraries should NEVER crash; they expose errors for callers to decide.

### Error Reduction Decision Procedure

```
When facing an exception handling decision:

1. Can semantics be redefined to eliminate the error condition?
   YES → Define out of existence
   NO  → Continue

2. Can exception be handled at low level without exposing?
   YES → Mask
   NO  → Continue

3. Can multiple exceptions share the same handling?
   YES → Aggregate
   NO  → Continue

4. Is error rare, unrecoverable, and non-value-critical?
   YES → Just crash (app-level only)
   NO  → Must expose (exception information needed outside module)
```

### When NOT to Apply Hierarchy

| Exception Case | Why | What to Do Instead |
|----------------|-----|-------------------|
| **Security-critical errors** | Aggregating auth errors loses security-relevant distinctions | Keep distinct types for audit/logging |
| **Retry-differentiated errors** | Callers need different retry strategies per error type | Expose type info for retry decisions |
| **Silent data loss risk** | Define-out can mask user errors, complicate debugging | Fail fast for essential data errors |
| **Library code** | Callers should decide crash policy, not library | Expose errors; let app-level code crash |

### Validation Gates

| Technique | Gate Question |
|-----------|---------------|
| **Define out** | Does anyone NEED to detect this error case? |
| **Mask** | Does the caller have ANY useful response to this error? |
| **Aggregate** | Do callers handle these errors identically? |
| **Crash** | Is this (a) application-level code, (b) truly unrecoverable, AND (c) crash acceptable? |

### Define-Out Appropriateness Test

Before defining an error out of existence, verify it's an *incidental* error (safe) not an *essential* error (must fail fast):

| Question | If YES → | If NO → |
|----------|----------|---------|
| Would this state occur in normal, correct operation? | Safe to define out | Fail fast |
| Can the caller proceed meaningfully with the "defined out" state? | Safe | Expose error |
| Does the user/system have another way to detect this condition if needed? | Safe | Consider exposing |

---

## Obviousness Techniques

### Three Ways to Make Code Obvious

| Technique | How | When to Use |
|-----------|-----|-------------|
| **Reduce information needed** | Abstraction, eliminate special cases | Design-level changes |
| **Leverage reader knowledge** | Follow conventions, meet expectations | Incremental improvements |
| **Present explicitly** | Good names, strategic comments | When other techniques insufficient |

### Obviousness Test

If a code reviewer says your code is not obvious, **it is not obvious**—regardless of how clear it seems to you.

### Common Obviousness Problems

| Problem | Why Nonobvious | Fix |
|---------|----------------|-----|
| Generic containers (Pair, Tuple) | `getKey()` obscures meaning | Define specific class with named fields |
| Event-driven handlers | Control flow hidden | Document invocation context |
| Type mismatches | `List` declared, `ArrayList` allocated | Match declaration to allocation |
| Violated expectations | Code doesn't do what reader assumes | Document or refactor to meet expectations |

---

## Output Gate

Before presenting simplified code, produce a technique analysis table — this is the evidence that the hierarchy was applied:

```
| Error Condition | Technique | Gate Check | Reasoning |
|-----------------|-----------|------------|-----------|
| [each error]    | [1-4]     | [PASS/FAIL]| [why]     |
```

Proceed only when the following are true:

- Technique analysis table present for each error condition
- Complexity moved to fewer places (not just relocated)
- Interfaces are simpler than before
- Callers do less work than before
- Error handling is consolidated or eliminated
- Reader needs less context to understand

If a criterion legitimately cannot be satisfied, present the code with the failed criterion and reason stated.

---

## Principle Conflict Resolution

| Conflict | Resolution Heuristic |
|----------|---------------------|
| **Define Out vs Fail Fast** | Define out for *incidental* errors. Fail fast for *essential* errors. |
| **Mask vs Explicit Handling** | Mask when caller has no useful response. Expose when caller's response differs. |
| **Aggregate vs Specific Messages** | Aggregate the HANDLING, preserve specificity in the MESSAGE. |
| **Pull Down vs Single Responsibility** | Only pull down complexity RELATED to module's core purpose. |
| **Obviousness vs Brevity** | When define-out creates non-obvious behavior, add explanatory comment. |
| **Simplify vs Performance** | Prefer simplicity unless profiling proves performance-critical. |

---

## Red Flags

| Red Flag | Symptom | Transformation |
|----------|---------|----------------|
| **Scattered exceptions** | Same error handled in many places | Aggregate to single handler |
| **Configuration explosion** | Many parameters exported | Compute automatically, provide defaults |
| **Caller doing module's work** | Logic outside that belongs inside | Pull complexity down |
| **Over-defensive code** | Checks for impossible conditions | Define errors out |
| **Generic containers** | `Pair<X,Y>` obscures meaning | Create named structure |
| **Comment-dependent understanding** | Code unreadable without comments | Refactor for obviousness |
| **Masked error without observability** | Applying Mask or Define-out but no logging, metrics, or alternate signal when the error actually occurs | Every masked error needs an observability escape hatch (log, metric, health check) so operators can detect when masking hides a real problem |

---

Detailed checklists: `Read(${CLAUDE_SKILL_DIR}/checklists.md)`

---

## Chain

| After | Next |
|-------|------|
| Simplification done | `Read(${CLAUDE_PLUGIN_ROOT}/skills/aposd-verifying-correctness/SKILL.md)` — verify interface simplified |
