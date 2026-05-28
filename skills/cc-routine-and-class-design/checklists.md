# Checklists: cc-routine-and-class-design

Source: Code Complete 2nd Edition, Chapters 5, 6, 7

---

## Design in Construction - Design Practices (p.118)

- [ ] DP-1: "Have you iterated, selecting the best of several attempts rather than the first attempt?" → Red flag: First solution shipped without exploration
- [ ] DP-2: "Have you tried decomposing the system in several different ways to see which way will work best?"
- [ ] DP-3: "Have you approached the design problem both from the top down and from the bottom up?"
- [ ] DP-4: "Have you prototyped risky or unfamiliar parts of the system, creating the absolute minimum amount of throwaway code needed to answer specific questions?"
- [ ] DP-5: "Has your design been reviewed, formally or informally, by others?"
- [ ] DP-6: "Have you driven the design to the point that its implementation seems obvious?" (Good: Implementation path clear, Bad: Multiple ways unclear)
- [ ] DP-7: "Have you captured your design work using an appropriate technique such as a Wiki, e-mail, flip charts, digital photography, UML, CRC cards, or comments in the code itself?"

---

## Design in Construction - Design Goals (p.119)

- [ ] DG-1: "Does the design adequately address issues that were identified and deferred at the architectural level?"
- [ ] DG-2: "Is the design stratified into layers?" (Good: Clear layer separation, Bad: Cross-layer coupling)
- [ ] DG-3: "Are you satisfied with the way the program has been decomposed into subsystems, packages, and classes?"
- [ ] DG-4: "Are you satisfied with the way the classes have been decomposed into routines?"
- [ ] DG-5: "Are classes designed for minimal interaction with each other?" → Red flag: High coupling between many classes
- [ ] DG-6: "Are classes and subsystems designed so that you can use them in other systems?"
- [ ] DG-7: "Will the program be easy to maintain?" (Good: Changes isolated, Bad: Change amplification)
- [ ] DG-8: "Is the design lean? Are all of its parts strictly necessary?" → Red flag: Speculative generality
- [ ] DG-9: "Does the design use standard techniques and avoid exotic, hard-to-understand elements?"
- [ ] DG-10: "Overall, does the design help minimize both accidental and essential complexity?"

---

## Class Quality (Ch 6, derived from boundaries/skill actions)

- [ ] CQ-1: "Does the class present a consistent abstraction level in its interface?" (Good: Single level, Bad: Mixed high/low level methods)
- [ ] CQ-2: "Is every public member consistent with the class's abstraction?"
- [ ] CQ-3: "Does the class hide its implementation details (encapsulation)?" → Red flag: Public fields or protected data
- [ ] CQ-4: "Is base class data private, not protected?" → Red flag: Protected fields break encapsulation
- [ ] CQ-5: "If using inheritance, does derived class truly 'is-a' base class (LSP)?"
- [ ] CQ-6: "Is inheritance depth less than 3 levels (and definitely less than 6)?" → Red flag: Deep inheritance hierarchies
- [ ] CQ-7: "Are there no empty overrides (overriding a routine to do nothing)?" → Red flag: Override to disable behavior
- [ ] CQ-8: "Does the class avoid chains like object.A().B().C() (Law of Demeter)?" → Red flag: Train wreck method chains
- [ ] CQ-9: "Does the class have 7 or fewer data members?" (Good: ≤7 members, Bad: >7 members)

---

## High-Quality Routines - Big-Picture Issues (p.181)

- [ ] RP-1: "Is the reason for creating the routine sufficient?"
- [ ] RP-2: "Have all parts of the routine that would benefit from being put into their own routines been put into their own routines?"
- [ ] RP-3: "Is the routine's name a strong, clear verb-plus-object for a procedure, or a description of the return value for a function?" (Good: calculateTotal(), Bad: process())
- [ ] RP-4: "Does the routine's name describe everything the routine does?" → Red flag: Side effects not in name
- [ ] RP-5: "Have you established naming conventions for common operations?"
- [ ] RP-6: "Does the routine have strong, functional cohesion—doing one and only one thing and doing it well?" → Red flag: Multiple unrelated operations
- [ ] RP-7: "Do the routines have loose coupling—are the routine's connections to other routines small, intimate, visible, and flexible?"
- [ ] RP-8: "Is the length of the routine determined naturally by its function and logic, rather than by an artificial coding standard?"

---

## High-Quality Routines - Parameter-Passing Issues (p.182)

- [ ] PP-1: "Does the routine's parameter list, taken as a whole, present a consistent interface abstraction?"
- [ ] PP-2: "Are the routine's parameters in a sensible order, including matching the order of parameters in similar routines?"
- [ ] PP-3: "Are interface assumptions documented?"
- [ ] PP-4: "Does the routine have seven or fewer parameters?" (Good: ≤7 params, Bad: >7 params) → Red flag: Long parameter lists
- [ ] PP-5: "Is each input parameter used?"
- [ ] PP-6: "Is each output parameter used?"
- [ ] PP-7: "Does the routine avoid using input parameters as working variables?" → Red flag: Modifying input parameters
- [ ] PP-8: "If the routine is a function, does it return a valid value under all possible circumstances?"

---

## Red Flags

- [ ] RF-1: "Protected or public data members?" - Breaks encapsulation → Make private with accessor methods only if needed
- [ ] RF-2: "Deep inheritance (>3 levels)?" - Excessive coupling and complexity → Favor composition over inheritance
- [ ] RF-3: "Empty override methods?" - Violates LSP → Rethink inheritance hierarchy or use composition
- [ ] RF-4: "Method chains (Law of Demeter)?" - `obj.getA().getB().getC()` → Add delegation methods to reduce coupling
- [ ] RF-5: "Routine does multiple things?" - Weak cohesion → Split into focused, single-purpose routines
- [ ] RF-6: "Routine name lies?" - Side effects not reflected in name → Rename to describe all effects or refactor
- [ ] RF-7: "Long parameter lists (>7)?" - High cognitive load → Introduce parameter object or builder pattern
- [ ] RF-8: "Input parameters modified?" - Confusing control flow → Use separate output variables or return values
- [ ] RF-9: "Many data members (>7)?" - Class doing too much → Split into cohesive classes with focused responsibilities
- [ ] RF-10: "First design shipped?" - Missed better alternatives → Always iterate and compare multiple design approaches
- [ ] RF-11: "Routine hides failure as default?" - Function returns neutral value (null, empty, zero) on error indistinguishable from a valid "no result" → Use Result type, throw, or distinct sentinel so callers can tell success from failure

---

Total items: 54
