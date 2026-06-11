# Checklists: cc-refactoring-guidance

Source: Code Complete 2nd Edition, Chapter 24

---

## Safe Refactoring Process (pp. 579-581)

- [ ] SR-1: "Is the code saved in version control before starting?" → Red flag: refactoring without safety net
- [ ] SR-2: "Are refactorings kept small and atomic?" (Good: 1 technique at a time, Bad: changing multiple patterns simultaneously)
- [ ] SR-3: "Are refactorings done one at a time with retest after each?" → Red flag: batch changes without verification
- [ ] SR-4: "Is a list of planned steps documented before executing?"
- [ ] SR-5: "Is there a parking lot for deferred changes?" (Good: tracked separately, Bad: mixed with current work)
- [ ] SR-6: "Are frequent checkpoints made during the session?"
- [ ] SR-7: "Are regression tests run after changes?" → Red flag: skipping verification
- [ ] SR-8: "Are new test cases added to cover modified areas?"
- [ ] SR-9: "Have the changes been reviewed by another person?"
- [ ] SR-10: "Is the approach adjusted based on risk level?" (Good: high-risk gets more verification, Bad: one-size-fits-all)

---

## Refactoring Preconditions (derived from pp. 563-565)

- [ ] RP-1: "Does the code currently work and produce correct output?" → Red flag: refactoring broken code
- [ ] RP-2: "Is this refactoring (improving structure) not fixing (changing behavior)?"
- [ ] RP-3: "Are refactoring and fixing being done separately, not simultaneously?" → Red flag: mixing concerns
- [ ] RP-4: "Is the design fundamentally sound, not needing rewrite?" (Good: structure improvements, Bad: architectural overhaul disguised as refactoring)
- [ ] RP-5: "Are changes incremental rather than a 'big refactoring'?" → Red flag: multi-week refactoring sprints

---

## Code Smell Detection (pp. 564-569)

- [ ] CS-1: "Has duplicated code been detected and flagged for extraction?" → Red flag: copy-paste inheritance
- [ ] CS-2: "Is any routine too long to be easily readable?" (Good: < 50 lines, Bad: > 200 lines)
- [ ] CS-3: "Is any loop too long or too deeply nested?" (Good: 1-2 levels, Bad: 4+ levels)
- [ ] CS-4: "Does any class have poor cohesion?" → Red flag: classes doing unrelated things
- [ ] CS-5: "Does any interface fail to provide consistent level of abstraction?" (Good: all high-level or all low-level, Bad: mixed)
- [ ] CS-6: "Does any parameter list have too many parameters?" (Good: ≤ 7, Bad: > 7)
- [ ] CS-7: "Do changes require parallel modifications in multiple places?" → Red flag: shotgun surgery pattern
- [ ] CS-8: "Are related data items not organized into a class?" (Good: cohesive structures, Bad: parallel arrays/loose primitives)
- [ ] CS-9: "Does any routine use more features of another class than its own?" → Red flag: feature envy
- [ ] CS-10: "Is setup/takedown code required around routine calls?" (Good: encapsulated, Bad: manual caller responsibility)
- [ ] CS-11: "Is tramp data passed through routine chains?" → Red flag: middle-man parameters

---

## Small Change Discipline (p. 571)

- [ ] SC-1: "Has the change been desk-checked before testing?" → Red flag: test-driven debugging
- [ ] SC-2: "Has the change been reviewed, even for 1-line changes?" (Good: all changes reviewed, Bad: "too small to review" mindset)
- [ ] SC-3: "Have regression tests been run?"
- [ ] SC-4: "Has the same rigor been applied as for larger changes?" → Red flag: relaxed process for "quick fixes"

---

## Red Flags

- [ ] RF-1: "Refactoring without version control?" - No safety net for rollback → Commit before starting
- [ ] RF-2: "Big refactoring sessions?" - Multi-day/week efforts → Break into incremental steps
- [ ] RF-3: "Mixing refactoring and fixing?" - Behavior changes during restructuring → Separate concerns completely
- [ ] RF-4: "Shotgun surgery pattern?" - Same change repeated across files → Extract common abstraction
- [ ] RF-5: "Copy-paste inheritance?" - Duplicated blocks with minor variations → Extract method/class
- [ ] RF-6: "Feature envy detected?" - Routine uses another class's data more than its own → Move method to proper class
- [ ] RF-7: "Skipping tests after refactoring?" - No verification of behavior preservation → Run full regression suite
- [ ] RF-8: "Deep nesting (4+ levels)?" - Loops/conditionals nested deeply → Extract methods, invert conditions
- [ ] RF-9: "Parameter lists > 7?" - Too many inputs to routine → Introduce parameter object
- [ ] RF-10: "Tramp data chains?" - Parameters passed through multiple layers → Use object context or remove middle layers

---
