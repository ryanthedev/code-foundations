# Code Complete Foundations Reference

> Shared vocabulary and metrics for all CC skills. Source: "Code Complete" 2nd Ed. (McConnell)

---

## Software's Primary Technical Imperative

**Managing Complexity** is the most important technical topic in software development.

> "The goal is to minimize the amount of a program you have to think about at any one time." — Ch 5

**Why it matters:** Software development is primarily a mental activity. Humans have limited working memory (~7±2 items). Every design decision should reduce cognitive load.

**Information Hiding:** The foundation of managing complexity. Hide implementation details so changes don't propagate.
- Korson/Vaishnavi 1986: Classes with good information hiding had **4× fewer faults** than those with poor hiding.

---

## Cohesion Spectrum

How well a routine's operations relate to each other. Higher = better.

| Level | Type | Definition | Quality |
|-------|------|------------|---------|
| 1 | **Functional** | Routine performs ONE operation | **Best** |
| 2 | **Sequential** | Operations must occur in specific order, sharing data | Good |
| 3 | **Communicational** | Operations use same data but no order dependency | Acceptable |
| 4 | **Temporal** | Operations grouped by when they happen (e.g., startup) | Marginal |
| 5 | **Procedural** | Operations in specified order but don't share data | Poor |
| 6 | **Logical** | Operations related by control flag selecting behavior | Bad |
| 7 | **Coincidental** | No meaningful relationship between operations | **Worst** |

**Empirical Evidence:**
- Card et al. 1986: **50% of high-cohesion routines** were fault-free vs **18% of low-cohesion** routines.

**Quick Test:** Can you describe what the routine does without using "and"? If not, cohesion is too low.

---

## Coupling Criteria

Degree of interdependence between modules. Lower = better.

| Criterion | Good | Bad |
|-----------|------|-----|
| **Size** | Few parameters, small interfaces | Many parameters, large interfaces |
| **Visibility** | Obvious connections (parameters) | Hidden connections (globals, side effects) |
| **Flexibility** | Can easily change one without affecting other | Changes cascade |

**Coupling Types (worst to best):**
1. **Content coupling** — Module modifies another's internal data → **Eliminate**
2. **Common coupling** — Shared global data → **Minimize**
3. **Control coupling** — One module controls flow of another → **Reduce**
4. **Stamp coupling** — Passing composite data, only some used → **Acceptable**
5. **Data coupling** — Only necessary data passed → **Goal**

---

## Key Metrics

Validated thresholds from empirical studies:

| Metric | Threshold | Source |
|--------|-----------|--------|
| **Parameters** | 7±2 maximum | Miller 1956; Basili/Perricone: routines with >5 params had more errors |
| **Inheritance depth** | ≤2 ideal, 3 warning, >3 violation | pp. 147-148 |
| **Routine length** | 100-200 lines optimal for comprehension | Basili/Perricone 1984 |
| **Fan-out** | ≤7 routines called | Card et al. — lower fan-out = fewer errors |
| **Complexity** | Low cyclomatic complexity | McCabe — high complexity = more defects |

**Debugging Performance:**
- Gould 1975, Gilb 1977, Curtis 1981: **20:1 performance variation** between best and worst debuggers.
- Yourdon 1986b: ~50% of bug fixes are **wrong the first time**.

---

## Information Hiding Principles

From Chapter 5 — the core technique for managing complexity:

1. **Secrets:** Every class/module should hide a design decision (a "secret")
2. **Interface:** Expose only what callers need to know
3. **Barriers:** Changes to implementation shouldn't affect callers

**Secrets to Hide:**
- Data structure implementation
- Algorithm details
- I/O formats
- Hardware dependencies
- Business rules likely to change

**Anti-Pattern:** "Convenience" functions that expose internal structure.

---

## Design Heuristics

Practical guidelines from Chapters 5-7:

| Heuristic | Application |
|-----------|-------------|
| **Find Real-World Objects** | Classes should correspond to real entities |
| **Consistent Abstraction** | All methods at same conceptual level |
| **Encapsulate Implementation** | Changes shouldn't cascade |
| **Minimize Accessibility** | Don't expose more than necessary |
| **Avoid Friend Classes** | Unless within same abstraction |
| **Favor Composition** | Inheritance depth < 3, prefer "has-a" over "is-a" |
| **Strong, Loose Coupling** | Modules dependent but changeable |

---

## CC ↔ APOSD Concept Mapping

| Code Complete | APOSD | Notes |
|---------------|-------|-------|
| **Managing complexity** | Complexity symptoms | Same goal, CC has metrics |
| **Information hiding** | Deep modules | Same principle—hide implementation |
| **High cohesion** | Single responsibility | CC has cohesion spectrum |
| **Loose coupling** | Minimize dependencies | CC has coupling types |
| **Routine length 100-200** | "Somewhat deep" | CC is metric; APOSD is principle |
| **7±2 parameters** | Simple interface | Same threshold reasoning |
| **Defensive programming** | — | CC unique—APOSD assumes correctness |
| **Pseudocode programming** | — | CC unique methodology |
| **— (not explicit)** | Unknown unknowns | APOSD frames complexity symptoms |
| **Debugging methodology** | — | CC unique—scientific debugging |

---

## Quick Reference

| Question | Look For |
|----------|----------|
| "Is this cohesive?" | Can describe without "and"? Functional = best |
| "Is coupling acceptable?" | Data coupling? Few params? No globals? |
| "Are metrics okay?" | ≤7 params, ≤2 inheritance, ≤7 fan-out |
| "Is complexity managed?" | Information hidden? Changes localized? |

---

*For application, see: cc-routine-and-class-design, cc-defensive-programming, cc-quality-practices, cc-debugging*
