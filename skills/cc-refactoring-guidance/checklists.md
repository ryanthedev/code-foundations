# Checklists: cc-refactoring-guidance

Source: Code Complete 2nd Edition, Chapter 24

## Safe Refactoring Process (pp. 579-581)

Verify each step before and during refactoring:

- [ ] Is the code saved in version control before starting?
- [ ] Are refactorings kept small and atomic?
- [ ] Are refactorings done one at a time with retest after each?
- [ ] Is a list of planned steps documented before executing?
- [ ] Is there a parking lot for deferred changes?
- [ ] Are frequent checkpoints made during the session?
- [ ] Are regression tests run after changes?
- [ ] Are new test cases added to cover modified areas?
- [ ] Have the changes been reviewed by another person?
- [ ] Is the approach adjusted based on risk level?

## Refactoring Preconditions (derived from pp. 563-565)

Verify BEFORE starting any refactoring:

- [ ] Does the code currently work and produce correct output?
- [ ] Is this refactoring (improving structure) not fixing (changing behavior)?
- [ ] Are refactoring and fixing being done separately, not simultaneously?
- [ ] Is the design fundamentally sound, not needing rewrite?
- [ ] Are changes incremental rather than a "big refactoring"?

## Code Smell Detection (pp. 564-569)

Look for these refactoring candidates:

- [ ] Has duplicated code been detected and flagged for extraction?
- [ ] Is any routine too long to be easily readable?
- [ ] Is any loop too long or too deeply nested?
- [ ] Does any class have poor cohesion?
- [ ] Does any interface fail to provide consistent level of abstraction?
- [ ] Does any parameter list have too many parameters?
- [ ] Do changes require parallel modifications in multiple places?
- [ ] Are related data items not organized into a class?
- [ ] Does any routine use more features of another class than its own?
- [ ] Is setup/takedown code required around routine calls?
- [ ] Is tramp data passed through routine chains?

## Small Change Discipline (p. 571)

For ANY change, especially small ones:

- [ ] Has the change been desk-checked before testing?
- [ ] Has the change been reviewed, even for 1-line changes?
- [ ] Have regression tests been run?
- [ ] Has the same rigor been applied as for larger changes?

---
Total items: 30
