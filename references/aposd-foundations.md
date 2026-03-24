# Software Design Foundations Reference

> Shared vocabulary for APOSD design skills. Source: "A Philosophy of Software Design" (Ousterhout)

---

## Complexity Definition

**Complexity:** Anything related to the structure of a software system that makes it hard to understand and modify.

**Obvious System (Goal):** Developer quickly understands existing code and confidently knows what changes require.

---

## Three Symptoms of Complexity

How complexity manifests. Use for diagnosis.

| Symptom | Definition | Severity |
|---------|------------|----------|
| **Change Amplification** | Simple change requires modifications in many places | Moderate |
| **Cognitive Load** | Developer must know too much to complete a task | Moderate |
| **Unknown Unknowns** | Not obvious what code/information is needed | **Worst** |

**Why Unknown Unknowns is worst:** You don't know what you don't know. No amount of effort reveals the problem until something breaks.

---

## Two Causes of Complexity

Why complexity exists. Use for root cause analysis.

| Cause | Definition | Constraint |
|-------|------------|------------|
| **Dependencies** | Code cannot be understood/modified in isolation | Cannot eliminate—only minimize and make obvious |
| **Obscurity** | Important information is not obvious | Primary source of unknown unknowns |

---

## Key Relationships

```
Dependencies + Obscurity → Symptoms
       ↓
Obscurity → Unknown Unknowns (worst symptom)
       ↓
Small increments → Large accumulation
```

---

## Counterintuitive Insight

**Lines of Code ≠ Complexity**

More lines may mean *less* cognitive load, therefore *less* complexity. A 10-line function with clear variable names and comments can be simpler than a 3-line function requiring mental gymnastics to understand.

---

## Quick Reference

| Question | Look For |
|----------|----------|
| "Is this complex?" | Three symptoms present? |
| "Why is it complex?" | Dependencies? Obscurity? |
| "How bad is it?" | Unknown unknowns = worst |
| "Can we fix it?" | Reduce/clarify dependencies, eliminate obscurity |

---

## Cross-References to Code Complete

| APOSD Concept | CC Equivalent | Notes |
|---------------|---------------|-------|
| Complexity symptoms | Cognitive load (cc-routine-and-class-design) | CC uses cohesion/coupling metrics |
| Information hiding | Information hiding (cc-routine-and-class-design Ch 5) | Same concept, different framing |
| Deep modules | High cohesion (cc-routine-and-class-design) | APOSD emphasizes interface simplicity |
| Obviousness | Readability (code-clarity-and-docs) | CC focuses on formatting; APOSD on semantics |

---

*For application, see: aposd-designing-deep-modules, aposd-reviewing-module-design, aposd-simplifying-complexity*
