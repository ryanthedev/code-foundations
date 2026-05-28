# Checklists: aposd-reviewing-module-design

Source: A Philosophy of Software Design (Ousterhout), Chapters 2, 4, 5, 7, 9

---

## Complexity Symptoms (Ch 2)

- [ ] CS-1: "Does a simple change require modifications in many places?" → Flag: Change Amplification
- [ ] CS-2: "Must developer know too much to work here?" → Flag: Cognitive Load
- [ ] CS-3: "Is it unclear what code/info is needed for changes?" → **CRITICAL**: Unknown Unknowns

---

## Module Depth (Ch 4)

- [ ] MD-1: "Is the interface much simpler than the implementation?" (Good: yes, Bad: interface rivals implementation)
- [ ] MD-2: "Are there few, powerful methods rather than many limited ones?" (Good: few powerful, Bad: many limited)
- [ ] MD-3: "Is information well hidden?" (Good: high, Bad: low)
- [ ] MD-4: "Is the common case simple to use?" (Good: simple, Bad: complex)

**Red flag:** If understanding the interface isn't much simpler than understanding the implementation, the module is shallow.

---

## Information Hiding (Ch 5)

- [ ] IH-1: "Is the same knowledge duplicated in multiple modules?" → High severity: Information Leakage
- [ ] IH-2: "Does structure mirror execution order rather than knowledge?" → Medium severity: Temporal Decomposition
- [ ] IH-3: "Is there shared knowledge not visible in interfaces?" → High severity: Back-Door Leakage
- [ ] IH-4: "Does common use force learning rare features?" → Medium severity: Overexposure

---

## Layer Abstraction (Ch 7)

- [ ] LA-1: "Does method only pass arguments to another with same API?" → High severity: Pass-Through Method
- [ ] LA-2: "Following operation through layers, do abstractions stay the same?" → High severity: Adjacent Similar Abstractions
- [ ] LA-3: "Is there large boilerplate for small functionality gain?" → Medium severity: Shallow Decorator

**Test:** Follow a single operation through layers. Does the abstraction change with each method call? If not, there's a layer problem.

---

## Together/Apart (Ch 9)

- [ ] TA-1: "Can't understand one method without another's implementation?" → High severity: Conjoined Methods
- [ ] TA-2: "Does general mechanism contain use-case specific code?" → High severity: Special-General Mixture
- [ ] TA-3: "Does same code appear in multiple places?" → Medium severity: Code Repetition
- [ ] TA-4: "Did method split result in interface equal to implementation?" → Medium severity: Shallow Split

---

## Quick Reference: Red Flags

- [ ] MD-S: "Shallow Module" - Interface as complex as implementation
- [ ] MD-C: "Classitis" - Many small classes, little functionality each
- [ ] IH-1: "Information Leakage" - Same knowledge in multiple modules
- [ ] IH-2: "Temporal Decomposition" - Structure follows execution order
- [ ] LA-1: "Pass-Through Method" - Method just delegates to another with same API
- [ ] TA-1: "Conjoined Methods" - Methods only understandable together
- [ ] TA-2: "Special-General Mixture" - General mechanism has use-case code
- [ ] TA-3: "Code Repetition" - Same code appears multiple places
- [ ] TA-4: "Shallow Split" - Method split resulted in interface equal to implementation
- [ ] SF-1: "Silent Failure" - Module swallows errors, returns defaults, or hides failure states from callers — operations can fail without the caller knowing

---

## Together/Apart Decision Procedure

- [ ] TAD-1: "Do pieces share information?" → Should probably be together
- [ ] TAD-2: "Would combining simplify the interface?" → Should probably be together
- [ ] TAD-3: "Is there repeated code?" → Extract shared method (if long snippet, simple signature)
- [ ] TAD-4: "Does module mix general-purpose with special-purpose?" → Should be separated

**Key principle:** Depth > Length. Never sacrifice depth for length.

---

## Depth vs Length

- [ ] DL-1: "Long method with clean abstraction?" → Keep together
- [ ] DL-2: "Short method requiring another's impl to understand?" → Combine them
- [ ] DL-3: "Method split creating conjoined pair?" → Undo the split
- [ ] DL-4: "Long method with extractable subtask?" → Extract subtask only

**Test for valid split:** Can the pieces be understood independently AND reused separately?

---

## Steel-Man Validation (Before Flagging)

- [ ] SM-1: "What's the best argument this design choice is intentional?"
- [ ] SM-2: "Is this an adapter, facade, or decorator where thinness is the point?"
- [ ] SM-3: "Is this 'leakage' actually a legitimate dependency injection point?"
- [ ] SM-4: "Can callers use this interface correctly without knowing implementation details?"

---

## Principle Conflicts

- [ ] PC-1: "Depth vs Cohesion" → Prefer cohesion. A focused shallow module beats a bloated deep one.
- [ ] PC-2: "Information Hiding vs Testability" → Testing seams (injectable dependencies) are acceptable "leakage"
- [ ] PC-3: "Simple Interface vs Configurability" → Real systems need configuration; penalize only unnecessary complexity

---

Total items: 37
