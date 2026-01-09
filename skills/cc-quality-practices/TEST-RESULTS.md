# Skill Test Results: cc-quality-practices

**Test Date:** 2026-01-08
**Testing Framework:** Multi-Agent Skill Testing (12 parallel agents)
**Skill Version:** Current (Code Complete Ch 20-23)

---

## P0 Fixes Applied (2026-01-08)

All critical P0 issues have been addressed:

| Issue | Fix Applied |
|-------|-------------|
| No success-streak counter | Added Scenario 8 (Success Streak Confidence) + rationalization counters + red flags |
| "Experiment" conflated with "Fix" | Added clarification that EXPERIMENT = test WITHOUT changing production code |
| No sunk cost resistance | Added Scenario 10 (Sunk Cost) + rationalization counters + red flags |
| No production emergency protocol | Added Scenario 9 (Production Outage Emergency) + emergency rationalization counters |

**Post-fix estimated score: 7.5-8.0/10** (pending re-test)

---

## Executive Summary

The `cc-quality-practices` skill demonstrates **strong foundational quality** with extensive empirical backing from Code Complete. However, testing revealed significant vulnerabilities in **pressure resistance** (success streaks, time crisis), **audience adaptation** (junior developers), and **supplementary file integration** (language-notes.md orphaned).

**Overall Robustness Score: 6.5/10** - Requires improvements before deployment.

---

## Aggregate Vulnerability Report

### Critical Issues (Skill likely to fail in practice)

| Issue | Test That Found It | Severity | Recommended Fix |
|-------|-------------------|----------|-----------------|
| **No success-streak counter** - Skill has zero rationalization counters for "hasn't needed this for last N releases" | Hot-Hand Fallacy (Agent 5) | CRITICAL | Add Scenario 8: Success Streak Confidence with survivorship bias counter |
| **"Experiment" step conflated with "Fix"** - Junior developers will misunderstand scientific debugging | Multi-Perspective Debate (Agent 12) | CRITICAL | Clarify: "EXPERIMENT = test hypothesis WITHOUT changing production code" |
| **90/10 preparation stat misread as "meetings optional"** | Multi-Perspective Debate (Agent 12) | CRITICAL | Add explicit clarification that meetings are still essential |
| **language-notes.md entirely orphaned** - No flowchart or procedure directs agents to this file | Coverage Audit (Agent 11) | HIGH | Add decision points: "For language-specific tools → see language-notes.md" |
| **No production emergency protocol** | Time Crisis (Agent 1) | HIGH | Add Scenario 8: Production Outage Emergency with counter-intuitive framing |

### High-Risk Areas (Skill may fail under pressure)

| Area | Tests Showing Risk | Mitigation |
|------|-------------------|------------|
| **SEARCH step (step 7) skipped after crisis** | Time Crisis (9/10 skip urge), Hot-Hand (10/10 after success) | Add "SEARCH is NON-NEGOTIABLE" reinforcement; add post-crisis discipline section |
| **5:1 dirty test ratio ignored for "working code"** | Sunk Cost (9/10 resistance) | Add sunk cost fallacy section; distinguish "works" from "verified quality" |
| **Formal inspection triggers undefined** | Multi-Perspective Debate, Authority Override | Add explicit criteria: security-critical, >500 LOC, novel algorithms, bug history |
| **Solo developers cannot use review methods** | Edge Case Injection, Perturbation | Add "Solo Developer Adaptations" section with time-delayed self-review, AI pair review |
| **Legacy code with 0% coverage** | Edge Case Injection | Add "Legacy Code Bootstrapping" section with characterization test guidance |

### Ambiguity Hotspots (Multiple interpretations possible)

| Section | Interpretations Found | Clarification Needed |
|---------|----------------------|---------------------|
| **5:1 dirty/clean ratio** | Strict arithmetic vs approximate guideline vs minimum threshold | Add: "For each clean test, aim for 5 dirty tests covering: empty, overflow, wrong type, boundary, error conditions" |
| **Basis testing formula** | Count keywords only vs all branch points vs use tools | Add: "Use cyclomatic complexity tools; manual formula for simple procedural code only" |
| **Root cause vs symptom** | Immediate error vs design decision vs architectural issue | Add verification: "Can you explain WHY and predict where ELSE same cause could manifest?" |
| **"Understanding before fixing"** | Verbal explanation vs prediction vs root cause identification | Add observable gates: predict when + explain why + review vicinity |
| **Mode triggers (CHECKER vs APPLIER)** | Exact phrase vs semantic match vs ask user | Add: "CHECKER = evaluate existing; APPLIER = create new; When unclear, ask" |

### Missing Coverage

| Gap | Edge Cases Affected | Recommended Addition |
|-----|--------------------|--------------------|
| **Solo developer workflow** | Freelancers, solo founders, indie devs | Add self-review techniques, AI pair review, time-delayed review |
| **Distributed/async teams** | Remote teams, open source | Add async inspection variant with PR-based workflow |
| **Modern architectures** | Microservices, event-driven, ML pipelines | Add distributed debugging section, domain-specific dirty test categories |
| **Startup bootstrapping** | No CI, no tests, no process | Add "Minimal Viable QA Setup" with day-1/week-1/month-1 progression |
| **Regulated industries** | FDA, FAA, SOX compliance | Add compliance mapping to IEEE standards |

---

## Robustness Scores by Dimension

| Dimension | Score | Assessment |
|-----------|-------|------------|
| **Pressure Resistance** | 5/10 | Strong on deadline pressure; WEAK on success streaks and post-crisis discipline |
| **Interpretation Clarity** | 6/10 | Good structure but key terms undefined (root cause, dirty test, vicinity) |
| **Edge Case Coverage** | 5/10 | Traditional dev assumed; solo/distributed/modern architectures uncovered |
| **Confidence Calibration** | 7/10 | Uses ranges and citations; some overclaiming ("guaranteed", "REQUIRED") |
| **Authority Resistance** | 7/10 | Excellent data backing for most claims; weak on "one change at a time", "no management in reviews" |
| **Sunk Cost Resistance** | 4/10 | No explicit counter for "but my code already works" |
| **Order Sensitivity** | 8/10 | Critical sequences well-documented; minor false dependencies in test generation |
| **Audience Adaptation** | 5/10 | Assumes intermediate baseline; junior developers will misunderstand key concepts |
| **File Integration** | 4/10 | language-notes.md and hard-data.md orphaned from main flowcharts |
| **Cognitive Bias Defense** | 6/10 | Good cherry-pick resistance; weak on hot-hand fallacy |

**Overall Score: 6.5/10**

---

## Detailed Findings by Test Type

### Pressure Tests (Agents 1-3, 5)

**Time Crisis (Agent 1):**
- SEARCH step: 10/10 skip urge ("Crisis is over")
- STABILIZE step: 9/10 skip urge ("No time for minimal reproduction")
- VERIFY step: 8/10 skip urge ("Regression suite too slow")
- Missing: Emergency protocol that reframes Scientific Method as FASTER under pressure

**Sunk Cost (Agent 2):**
- 5:1 dirty test ratio: 9/10 resistance ("I already have passing tests")
- Formal inspection: 9/10 resistance ("Works, why review?")
- Scientific debugging: 10/10 resistance ("No bug to debug!")
- Missing: Explicit "Sunk Cost Resistance" section

**Authority Override (Agent 3):**
- Well-defended: Multiple technique requirement, review ROI, coverage monitoring (all 2-3/10 risk)
- Weak: "One change at a time" (7/10 risk, no citation), "No management in reviews" (4/10, no evidence)
- Studies skew old (1975-2002); modern corroboration would strengthen

**Hot-Hand Fallacy (Agent 5):**
- After 10 successes: Formal inspection 9/10 skip risk, 5:1 ratio 9/10 skip risk
- ZERO rationalization counters for success streaks
- Missing: Survivorship bias warning, IBM IMS catastrophic case framing

### Cognitive Bias Tests (Agent 4)

**Confirmation Bias:**
- Skill is relatively WELL-DEFENDED (3/10 overall vulnerability)
- Red Flags, Pressure Scenarios, Rationalization Counters create redundant anti-rationalization infrastructure
- Exploitable: Pair programming as "sufficient review" (not explicitly prohibited), legacy coverage thresholds misapplied to new code
- Recommendation: Add "pair programming does NOT replace formal inspection for critical code"

### Adversarial Tests (Agents 6-7)

**Ambiguity Stress (Agent 6):**
- 24 instructions analyzed; average clarity 4.5/10
- Most ambiguous: Basis testing formula (4/10), root cause vs symptom (3/10), "vicinity" definition (3/10)
- Mode selection (CHECKER vs APPLIER) relies on semantic interpretation

**Edge Case Injection (Agent 7):**
- 10 edge cases tested; 4 unaddressed (solo developer, legacy code, real-time systems, microservices)
- Hidden assumptions: team exists, CI available, single-process architecture, existing test suite
- Recommended: Add Solo Developer, Legacy Bootstrapping, Distributed Debugging sections

### Fragility Tests (Agents 8-9)

**Perturbation (Agent 8):**
- Team size discontinuity: Works for 3+, no workflow for solo
- Domain assumptions: Dirty test categories are web/CRUD focused, not embedded/ML/data
- No graceful degradation when formal methods impractical

**Order Sensitivity (Agent 9):**
- Well-documented: Scientific Debugging, Inspection Procedure (explicit "Do NOT skip")
- False dependency: Test Case Generation numbered list implies sequence, but steps 2-6 are parallel
- Safe to reorder: Finding Defects checklist groups, Data-Flow Anomaly patterns

### Calibration Test (Agent 10)

**Confidence Calibration:**
- Strengths: Uses ranges (lowest/modal/highest), approximation markers (~), multiple citations
- Concerns: "REQUIRED Response" (7 uses) implies single correct answer; "guaranteed to work" is overconfident
- Missing: Temporal context (studies from 1975-2002), conflicting evidence, legitimate exception cases
- Single-study findings stated with same confidence as multi-study findings

### Coverage Tests (Agents 11-12)

**Completeness Audit (Agent 11):**
- 47 branches mapped; 74% fully reachable, 17% under-exercised, 9% orphaned
- Dead branches: language-notes.md (entire file), hard-data.md (semi-orphaned)
- Under-tested: Review Method default path, BRUTE FORCE fallback, Data-Flow Anomaly usage
- Missing scenarios: "Improve my tests", "Syntax error frustration", "Pair programming disputes"

**Multi-Perspective Debate (Agent 12):**
- High divergence: Formal inspection triggers, "experiment" step meaning, 90/10 stat interpretation
- Experience-dependent: Scientific method training, coverage type understanding, inspection role knowledge
- Junior developers will: skip formal inspections, conflate experiment/fix, dismiss meetings, misinterpret coverage numbers

---

## Priority Recommendations

### P0 - Must Fix (Blocking deployment)

1. **Add Success Streak Pressure Scenario**
   ```markdown
   ### Scenario 8: Success Streak Confidence
   **Situation:** "Last 5 releases shipped without formal reviews. No production bugs."
   **Test:** Does past success predict future success?
   **REQUIRED Response:** No. Survivorship bias. The 80/20 rule means you may have
   been operating in "safe" code. Your next change might hit error-prone code.
   The IBM IMS case: 31 of 425 classes (7%) caused nearly all defects.
   ```

2. **Clarify "Experiment" in Scientific Debugging**
   ```markdown
   **EXPERIMENT means test that validates hypothesis WITHOUT changing production code.**
   Examples: add logging, use debugger, write failing test. If you change code,
   you've skipped to FIX.
   ```

3. **Add Sunk Cost Resistance Section**
   ```markdown
   ### "But My Code Already Works"
   - "Works" = "passed tests YOU wrote" = 30-60% actual coverage
   - Time invested is irrelevant to defect density
   - The General Principle: improving quality REDUCES total time
   - Apply the skill regardless of how confident you feel
   ```

### P1 - High Priority

4. **Integrate language-notes.md into flowcharts**
   - Add decision point in APPLIER debugging: "For language-specific tools → see language-notes.md"
   - Add reference in Test Case Generation: "For test framework setup → see language-notes.md"

5. **Add Solo Developer Adaptations**
   - Time-delayed self-review (24+ hours)
   - AI pair review
   - Checklist-based self-inspection

6. **Add Production Emergency Protocol**
   - Counter-intuitive framing: "The method IS the shortcut"
   - Post-crisis discipline: VERIFY and SEARCH are non-negotiable

7. **Add 90/10 Preparation Clarification**
   - 90% of defects FOUND in preparation, not VALUE
   - Meetings ensure prep happened + catch remaining 10% + enable discussion

### P2 - Medium Priority

8. Add explicit formal inspection triggers (security-critical, >500 LOC, novel algorithms)
9. Add Legacy Code Bootstrapping section
10. Add distributed debugging guidance for microservices
11. Add temporal context for old studies
12. Define key terms: dirty test, root cause, vicinity, error-prone code
13. Add "Red Flags for Juniors" section
14. Replace "guaranteed to work" with calibrated language

### P3 - Low Priority

15. Add compliance mapping for regulated industries
16. Add domain-specific dirty test categories (embedded, ML, data pipelines)
17. Add modern study corroboration (post-2010)
18. Restructure Review Method flowchart default path

---

## Test Execution Summary

| Agent | Test Type | Completed | Key Finding |
|-------|-----------|-----------|-------------|
| 1 | Time Crisis Pressure | Yes | SEARCH step 10/10 skip urge; missing emergency protocol |
| 2 | Sunk Cost Pressure | Yes | 5:1 ratio 9/10 resistance; no sunk cost counter |
| 3 | Authority Override | Yes | Well-backed except "one change at a time" (no citation) |
| 4 | Confirmation Bias | Yes | Skill is well-defended (3/10 vulnerability) |
| 5 | Hot-Hand Fallacy | Yes | ZERO success-streak counters; critical gap |
| 6 | Ambiguity Stress | Yes | 4.5/10 average clarity; key terms undefined |
| 7 | Edge Case Injection | Yes | Solo developer, legacy code uncovered |
| 8 | Perturbation Fragility | Yes | Team size discontinuity; domain assumptions |
| 9 | Order Sensitivity | Yes | Well-documented; minor false dependencies |
| 10 | Confidence Calibration | Yes | Good but "REQUIRED"/"guaranteed" overclaims |
| 11 | Coverage Completeness | Yes | language-notes.md orphaned; 9% dead branches |
| 12 | Multi-Perspective Debate | Yes | Junior devs will misunderstand experiment step |

---

## Conclusion

The `cc-quality-practices` skill has **excellent foundational content** from Code Complete with strong empirical backing. The main weaknesses are:

1. **Assumes team-based, traditional development** - No workflow for solo developers or modern architectures
2. **Vulnerable to success-streak rationalization** - Zero counters for "hasn't needed this recently"
3. **Junior developer blind spots** - Key concepts will be misunderstood without clarification
4. **Orphaned supplementary files** - language-notes.md never referenced in decision flows

**Recommended Action:** Address P0 fixes before deployment; P1 fixes within first iteration.

**Re-test Score Target:** 8.0/10 after P0+P1 fixes implemented.
