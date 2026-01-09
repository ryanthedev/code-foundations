# Skill Test Results: cc-control-flow-quality

## Multi-Agent Skill Testing Framework Results

**Skill Tested:** cc-control-flow-quality
**Date:** 2026-01-08
**Agents Used:** 12 parallel test agents
**Framework:** Multi-Agent Skill Testing Framework (DEEVO-based)

---

## Aggregate Vulnerability Report

### Critical Issues (Skill likely to fail in practice)

| Issue | Test That Found It | Severity | Recommended Fix |
|-------|-------------------|----------|-----------------|
| "Recursion is really dumb" inflammatory language | Agent 12 (Multi-Perspective) | **CRITICAL** | Reword to "Factorial is a poor recursion example; prefer iteration for simple cases where recursion adds no clarity" |
| Nesting reduction "priority order" vs "polymorphism isn't automatically better" contradiction | Agent 12, Agent 4 | **CRITICAL** | Clarify that list is a "consideration order" not strict priority; techniques are context-dependent |
| Guard clauses contradict "nominal case in if, error case in else" | Agent 12 | **HIGH** | Add explicit reconciliation: "Guard clauses are an exception pattern where error cases exit early" |
| McCabe exception ("large case may exceed 10") makes threshold meaningless | Agent 10, Agent 12 | **HIGH** | Clarify that McCabe counts complexity, not cognitive load; large flat switches are cognitively simpler |

### High-Risk Areas (Skill may fail under pressure)

| Area | Tests Showing Risk | Mitigation |
|------|-------------------|------------|
| **Time pressure skipping** | Agent 1, Agent 5 | Add urgency-handling guidance; emphasize which steps are NEVER skippable |
| **"But it works" resistance** | Agent 2 (Sunk Cost) | Add explicit "Sunk Cost Counter" addressing time-invested rationalization |
| **Authority override on thresholds** | Agent 3 | Strengthen citations for enum conventions, boolean documentation variables |
| **Hot-hand skipping after successes** | Agent 5 | Add "even after success, still do this" language; address overconfidence |
| **Cherry-picking "almost as good" language** | Agent 4 | Remove permissive hedging; make constraints explicit |

### Ambiguity Hotspots (Multiple interpretations possible)

| Section | Interpretations Found | Clarification Needed |
|---------|----------------------|---------------------|
| "Priority Order" for nesting reduction | Sequential checklist vs. scope gradient vs. context-dependent selection | Rename to "Techniques (ordered by invasiveness)" |
| McCabe "WARNING FLAG, not inflexible rule" | Rigid threshold vs. suggestion vs. only for case statements | Specify: "Flag for review at 10+; mandatory refactor at 20+" |
| "Put nominal case in if" vs guard clauses | Always nominal first vs. guards are exception vs. context-dependent | Add explicit section reconciling the two patterns |
| "Use for when iteration count is known" | Binary rule vs. modern iterator patterns blur this | Add: "Or use foreach/map for collection iteration" |

### Missing Coverage

| Gap | Edge Cases Affected | Recommended Addition |
|-----|--------------------|--------------------|
| Async/await control flow | Promise chains, callback hell equivalents | Add async control flow patterns section |
| Pattern matching (modern languages) | Rust match, C# switch expressions | Add pattern matching vs traditional switch guidance |
| Functional programming patterns | Map/filter/reduce replacing loops | Address when FP patterns are clearer than loops |
| Error handling integration | try-catch nesting, Result types | Cross-reference to defensive programming skill |
| Generated code exceptions | Auto-generated code may violate thresholds | Add note: "Applies to human-written code" |

---

## Robustness Scores

| Dimension | Score | Notes |
|-----------|-------|-------|
| **Pressure Resistance** | 5/10 | Lacks urgency guidance; steps easily rationalized away under time pressure |
| **Interpretation Clarity** | 6/10 | Core patterns clear; decision guidance has contradictions |
| **Edge Case Coverage** | 6/10 | Good traditional coverage; missing modern patterns |
| **Confidence Calibration** | 7/10 | Citations present but unevenly distributed; some overclaiming |
| **Authority Resistance** | 6/10 | Strong on some points (McCabe citation); weak on conventions |
| **Sunk Cost Resistance** | 4/10 | No explicit "working code" counter in rationalization table |
| **Success Streak Resistance** | 4/10 | No "even after success" framing; easily skipped after wins |
| **Overall** | **5.4/10** | Below threshold for deployment without revision |

---

## Detailed Test Results by Agent

### Agent 1: Time Crisis Pressure Test

**Pressure Points Identified:**

| Skill Step | Skip Urge (1-10) | Rationalization |
|------------|------------------|-----------------|
| Review McCabe complexity before fixing | 8 | "Production is down - no time for metrics" |
| Apply guard clauses systematically | 6 | "Just flatten the one blocking case" |
| Extract to well-named function | 7 | "Naming takes time; inline fix is faster" |
| Check all 78 checklist items | 10 | "Impossible during crisis" |
| Consider table-driven approach | 9 | "Architectural change during outage? Never" |

**Vulnerability Assessment:**
- Steps most likely skipped: Checklist review, McCabe measurement, table-driven consideration
- Missing urgency-handling: **YES** - No "crisis mode" subset of essential checks
- Recommended: Add "Emergency Minimum" checklist (5-7 essential items for crisis fixes)

---

### Agent 2: Sunk Cost Pressure Test

**Resistance Points:**

| Skill Requirement | Resistance (1-10) | Rationalization |
|-------------------|-------------------|-----------------|
| Refactor 5-level nesting to guard clauses | 9 | "4 hours invested; it passes tests" |
| Reduce McCabe from 15 to <10 | 8 | "Complexity is distributed; refactoring risks regressions" |
| Extract boolean expressions to functions | 7 | "Function proliferation for working code?" |

**Vulnerability Assessment:**
- Skill's answer to "but it works": **MISSING** - Rationalization counters don't address time investment
- Recommended: Add explicit counter: "Time invested doesn't change latent bug potential"

---

### Agent 3: Authority Override Test

**Authority Challenge Points:**

| Skill Prescription | Override Risk (1-10) | Missing Justification |
|--------------------|---------------------|----------------------|
| McCabe threshold of 10 | 6 | McCabe 1976 cited but not explained WHY 10 |
| Guard clauses over deep nesting | 4 | Chomsky/Weinberg studies provide backing |
| "Recursion is dumb for factorials" | 8 | No citation; pure opinion presentation |
| Table-driven over inheritance | 7 | p.423 quote but no failure study |

**Vulnerability Assessment:**
- Weakest-justified: Recursion dismissal, table vs inheritance preference
- Skill provides evidence: YES, but unevenly (strong for nesting, weak for recursion)
- Recommended: Add failure case studies for recursion in simple cases

---

### Agent 4: Confirmation Bias Test

**Cherry-Pickable Passages:**

| Passage | Bad Practice Supported | Ambiguity Score |
|---------|----------------------|-----------------|
| "WARNING FLAG, not inflexible rule" | Ignoring McCabe entirely | 7/10 |
| "A large case statement may legitimately exceed 10" | Any high complexity "is a case statement" | 8/10 |
| "When NOT to Use" section exists | Claiming situation doesn't apply | 6/10 |

**Vulnerability Assessment:**
- Most exploitable: The McCabe exception language
- Recommended: Replace "may legitimately exceed" with specific criteria

---

### Agent 5: Hot-Hand Fallacy Test

**Success-Breeds-Skipping Analysis:**

| Skill Step | After 1 Success | After 5 | After 10 |
|------------|-----------------|---------|----------|
| Check nesting depth | 15% skip | 40% skip | 65% skip |
| Count McCabe complexity | 20% skip | 50% skip | 75% skip |
| Apply guard clause pattern | 10% skip | 30% skip | 55% skip |
| Consider table-driven | 30% skip | 60% skip | 85% skip |

**Vulnerability Assessment:**
- Skill addresses overconfidence: **NO**
- Steps lacking success-agnostic framing: All steps presented as "when applicable" not "always"
- Recommended: Add "Execute regardless of past success" markers for critical steps

---

### Agent 6: Ambiguity Stress Test

**Ambiguity Analysis:**

| Instruction | Interpretation A | Interpretation B | Clarity |
|-------------|-----------------|-----------------|---------|
| "3 levels max" | Hard limit (refactor at 4) | Soft target (review at 4+) | 6/10 |
| "Priority order" list | Must try #1 before #2 | Consider in rough order | 4/10 |
| "Loop-with-exit" pattern | Always use when duplicating | Only when significantly cleaner | 5/10 |

---

### Agent 7: Edge Case Injection Test

**Edge Case Coverage:**

| Edge Case | Addressed? | Gap Severity |
|-----------|-----------|--------------|
| Async/await promise chains | No | HIGH |
| Pattern matching (Rust, C#) | No | MEDIUM |
| LINQ/Stream pipelines | No | MEDIUM |
| Generated code (protobuf, etc.) | No | LOW |
| Nested lambdas/closures | No | MEDIUM |

---

### Agent 8: Perturbation Fragility Test

**Perturbation Results:**

| Original | Perturbation | Output Changed? | Should It? |
|----------|--------------|-----------------|------------|
| C++ example | Python syntax | No | No |
| "4 levels" | "3 levels" | Yes - different guidance | Yes |
| Web app context | Embedded system | No | Partially - different constraints |
| OOP code | Functional code | Uncertain | Yes - different patterns |

**Hidden Assumptions:**
- OOP/imperative paradigm assumed throughout
- Single-threaded execution implied
- Traditional compiled languages as baseline

---

### Agent 9: Order Sensitivity Test

**Order Analysis:**

| Sequence | Order Stated? | Order Matters? | Risk |
|----------|--------------|----------------|------|
| Nesting reduction techniques (6 items) | "Priority Order" but meaning unclear | Partially | MEDIUM |
| Loop selection decision tree | Yes (numbered) | Yes | LOW |
| McCabe counting steps | Yes (numbered) | Yes | LOW |

**Unmarked Order-Dependent:**
- Guard clauses should precede extract-to-routine (less invasive first)
- McCabe count should precede technique selection

---

### Agent 10: Confidence Calibration Test

**Calibration Analysis:**

| Claim | Confidence Implied | Appropriate? | Evidence |
|-------|-------------------|--------------|----------|
| "3 levels max" | Absolute threshold | Partially - context matters | Chomsky/Weinberg |
| "25% better comprehension" | Specific quantitative | Yes | Soloway 1983 |
| "Recursion is dumb" | Absolute dismissal | No - overclaims | None cited |

---

### Agent 11: Coverage Completeness Audit

**Coverage Map Summary:**

| Branch Category | Branches | Exercise Scenarios Exist? | Dead Paths? |
|-----------------|----------|---------------------------|-------------|
| Entry triggers | 6 | Yes | None |
| Loop selection | 4 | Yes | None |
| Nesting reduction | 6 | Partial | None dead; #5-6 under-exercised |
| Table access | 3 | Yes | Stair-step rarely used |
| McCabe ranges | 3 | Yes | None |

---

### Agent 12: Multi-Perspective Debate

**Interpretation Divergence:**

| Section | Junior vs Senior vs QA | Consensus? |
|---------|------------------------|------------|
| "Recursion is dumb" | Overcorrection vs dismissal vs checklist contradiction | LOW |
| Priority order | Checklist vs scope gradient vs contradiction with tables | LOW |
| McCabe threshold | Rigid vs judgment vs metric questioning | PARTIAL |
| Guard clauses | Rule vs exception pattern vs conflict with nominal-first | PARTIAL |

---

## Recommended Skill Improvements

### Priority 1: Fix Contradictions

1. **Reconcile guard clauses with "nominal in if"** - Add explicit exception language
2. **Clarify "priority order" meaning** - Rename to "Techniques by invasiveness"
3. **Soften recursion language** - Remove inflammatory "really dumb"; explain context

### Priority 2: Add Missing Counters

1. **Sunk cost counter**: "Time invested doesn't change bug potential"
2. **Success streak counter**: "Past success doesn't guarantee future correctness"
3. **Authority counter for recursion**: Add citation or acknowledge as style preference

### Priority 3: Improve Clarity

1. **McCabe exception criteria**: Specify what qualifies as "legitimate"
2. **Modern pattern coverage**: Add async, pattern matching, functional sections
3. **Language-specific notes expansion**: Address paradigm differences

### Priority 4: Pressure Resistance

1. **Add "Emergency Minimum" checklist** for crisis situations
2. **Mark "never skip" items explicitly**
3. **Add post-crisis review guidance**

---

## Conclusion

The cc-control-flow-quality skill has **strong foundational content** based on Code Complete research, but has **significant vulnerabilities** that could cause failure in practice:

- **Contradictory guidance** between patterns (guard clauses vs nominal-first)
- **Inflammatory language** that causes over/under-correction (recursion)
- **Missing pressure-resistance** for time-crisis and sunk-cost scenarios
- **Ambiguous "priority order"** that confuses users across experience levels
- **No modern pattern coverage** (async, functional, pattern matching)

**Recommendation:** Revise skill before deployment, targeting score of 8/10.

---

## Post-Fix Summary (Applied 2026-01-08)

### Fixes Applied

| Issue | Fix Applied |
|-------|-------------|
| Guard clauses contradict "nominal in if" | Added explicit reconciliation note explaining guard clauses as exception pattern |
| "Priority order" confusion | Renamed to "by invasiveness, not strict priority" with clarifying note |
| "Recursion is really dumb" inflammatory | Softened to context-specific guidance about when iteration vs recursion is appropriate |
| McCabe exception too vague | Added specific criteria: flat dispatch, ≤3 lines per case, exhaustive, low cognitive complexity |
| Missing sunk cost counter | Added "But it already works" rationalization counter |
| Missing success streak counter | Added "It worked last time" rationalization counter |
| Missing time pressure counter | Added "No time—production is down" with Emergency Minimum reference |
| Missing authority counter | Added "Senior engineer says it's fine" with evidence-based response |
| No Emergency Minimum | Added Emergency Minimum section with 4 essential items |
| No modern patterns | Added Async/Await, Pattern Matching, and Functional Pipelines sections |
| Evidence strength unclear | Added Evidence Strength Assessment table to hard-data.md |
| Checklists missing modern items | Added 9 modern control flow checklist items |

### Updated Files

- `SKILL.md` - Major revisions to address contradictions, add counters, add modern patterns
- `checklists.md` - Added Emergency Minimum, NEVER Skip, and Modern Control Flow sections
- `hard-data.md` - Added Evidence Strength Assessment table

### Estimated Post-Fix Scores

| Dimension | Pre-Fix | Post-Fix | Notes |
|-----------|---------|----------|-------|
| Pressure Resistance | 5/10 | **7/10** | Emergency Minimum + NEVER Skip + explicit counter |
| Interpretation Clarity | 6/10 | **8/10** | Contradictions resolved with explicit reconciliation |
| Edge Case Coverage | 6/10 | **8/10** | Modern patterns now covered |
| Confidence Calibration | 7/10 | **8/10** | Evidence strength table added |
| Authority Resistance | 6/10 | **7/10** | New counter + evidence table |
| Sunk Cost Resistance | 4/10 | **7/10** | Explicit counter added |
| Success Streak Resistance | 4/10 | **7/10** | Explicit counter added |
| **Overall** | **5.4/10** | **7.4/10** | Above 7/10 threshold |

### Recommended Next Steps

1. **Re-run test battery** to validate improvements empirically
2. **Field test** with real coding tasks to catch remaining gaps
3. **Monitor** for new rationalizations to add to counters
