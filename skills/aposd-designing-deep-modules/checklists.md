# Checklists: aposd-designing-deep-modules

Source: A Philosophy of Software Design (Ousterhout), Chapter 4, 6, 9

---

## Design-It-Twice Workflow

- [ ] DT-1: "Did I define what I'm designing? (class, API, service)"
- [ ] DT-2: "Did I generate 2-3 RADICALLY different approaches?"
- [ ] DT-3: "Did I sketch each approach (important methods only, no implementation)?"
- [ ] DT-4: "Did I compare with pros/cons, especially ease of use for callers?"
- [ ] DT-5: "Is there a clear winner or hybrid?"
- [ ] DT-6: "Does the chosen design pass depth evaluation?"
- [ ] DT-7: "Am I implementing only AFTER completing steps 1-6?"

---

## Depth Evaluation

- [ ] DE-1: "Are there few methods in the interface?" (Good: few, Bad: many)
- [ ] DE-2: "Can methods be used for multiple use cases?" (Good: yes, Bad: single use case)
- [ ] DE-3: "Is information well hidden?" (Good: high, Bad: low)
- [ ] DE-4: "Is caller cognitive load low?" (Good: low, Bad: high)
- [ ] DE-5: "Is the common case simple?" (Good: simple, Bad: complex)

---

## Three Questions Framework

- [ ] TQ-1: "What is the simplest interface that covers all current needs?" → Red flag: "I need many methods"
- [ ] TQ-2: "In how many situations will this method be used?" → Red flag: "Just this one situation"
- [ ] TQ-3: "Is this easy to use for my current needs?" → Red flag: "I need lots of wrapper code"

---

## Information Hiding

- [ ] IH-1: "Do data structures and algorithms stay internal?"
- [ ] IH-2: "Are lower-level details (page sizes, buffer sizes) hidden?"
- [ ] IH-3: "Are higher-level assumptions (most files are small) hidden?"
- [ ] IH-4: "Is knowledge NOT shared across module boundaries unnecessarily?"
- [ ] IH-5: "Does common case require no knowledge of internal details?"

---

## Generality Sweet Spot

- [ ] GS-1: "Does functionality reflect current needs (not hypothetical)?"
- [ ] GS-2: "Does interface support multiple uses?"
- [ ] GS-3: "Is specialization pushed UP to callers OR DOWN into variants?"

---

## Red Flags

- [ ] RF-1: "Shallow Module?" - Interface complexity rivals implementation → Combine with related functionality
- [ ] RF-2: "Classitis?" - Many small classes with little functionality each → Consolidate related classes
- [ ] RF-3: "Single-Use Method?" - Method designed for exactly one caller → Generalize to handle multiple cases
- [ ] RF-4: "Information Leakage?" - Same knowledge in multiple modules → Consolidate in single module
- [ ] RF-5: "Temporal Decomposition?" - Structure mirrors execution order → Structure by knowledge encapsulation
- [ ] RF-6: "False Abstraction?" - Interface hides info caller actually needs → Expose necessary information
- [ ] RF-7: "Granularity Mismatch?" - Caller must do work that belongs in module → Move logic into module
- [ ] RF-8: "Module absorbs failures silently?" - Module handles errors internally but gives callers no way to know something went wrong (no error return, no observable state change, no logging) → Errors are implementation details that can be hidden; failures are not — surface failure states even when hiding the mechanism

---

## Process Integrity Checks

- [ ] PI-1: "Did I write out alternatives BEFORE evaluating them (not just 'thought through')?"
- [ ] PI-2: "Does my comparison have at least one criterion where my preferred option loses?"
- [ ] PI-3: "If I chose a hybrid, did I state what I'm sacrificing from each parent approach?"
- [ ] PI-4: "Could someone reasonably disagree with my choice based on the same comparison?"

---

## Emergency Bypass (ALL must be true)

- [ ] EB-1: "Is production down RIGHT NOW (not 'might break soon')?"
- [ ] EB-2: "Are users actively impacted, security breach in progress, OR data loss occurring?"
- [ ] EB-3: "Is the fix minimal (rollback or single-line change)?"
- [ ] EB-4: "Am I committing to return for proper implementation within 24 hours?"

---
