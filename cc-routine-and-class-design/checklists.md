# Checklists: cc-routine-and-class-design

Source: Code Complete 2nd Edition, Chapters 5, 6, 7

## Design in Construction - Design Practices (p.118)

- [ ] "Have you iterated, selecting the best of several attempts rather than the first attempt?"
- [ ] "Have you tried decomposing the system in several different ways to see which way will work best?"
- [ ] "Have you approached the design problem both from the top down and from the bottom up?"
- [ ] "Have you prototyped risky or unfamiliar parts of the system, creating the absolute minimum amount of throwaway code needed to answer specific questions?"
- [ ] "Has your design been reviewed, formally or informally, by others?"
- [ ] "Have you driven the design to the point that its implementation seems obvious?"
- [ ] "Have you captured your design work using an appropriate technique such as a Wiki, e-mail, flip charts, digital photography, UML, CRC cards, or comments in the code itself?"

## Design in Construction - Design Goals (p.119)

- [ ] "Does the design adequately address issues that were identified and deferred at the architectural level?"
- [ ] "Is the design stratified into layers?"
- [ ] "Are you satisfied with the way the program has been decomposed into subsystems, packages, and classes?"
- [ ] "Are you satisfied with the way the classes have been decomposed into routines?"
- [ ] "Are classes designed for minimal interaction with each other?"
- [ ] "Are classes and subsystems designed so that you can use them in other systems?"
- [ ] "Will the program be easy to maintain?"
- [ ] "Is the design lean? Are all of its parts strictly necessary?"
- [ ] "Does the design use standard techniques and avoid exotic, hard-to-understand elements?"
- [ ] "Overall, does the design help minimize both accidental and essential complexity?"

## Class Quality (Ch 6, derived from boundaries/skill actions)

- [ ] "Does the class present a consistent abstraction level in its interface?"
- [ ] "Is every public member consistent with the class's abstraction?"
- [ ] "Does the class hide its implementation details (encapsulation)?"
- [ ] "Is base class data private, not protected?"
- [ ] "If using inheritance, does derived class truly 'is-a' base class (LSP)?"
- [ ] "Is inheritance depth less than 3 levels (and definitely less than 6)?"
- [ ] "Are there no empty overrides (overriding a routine to do nothing)?"
- [ ] "Does the class avoid chains like object.A().B().C() (Law of Demeter)?"
- [ ] "Does the class have 7 or fewer data members?"

## High-Quality Routines - Big-Picture Issues (p.181)

- [ ] "Is the reason for creating the routine sufficient?"
- [ ] "Have all parts of the routine that would benefit from being put into their own routines been put into their own routines?"
- [ ] "Is the routine's name a strong, clear verb-plus-object for a procedure, or a description of the return value for a function?"
- [ ] "Does the routine's name describe everything the routine does?"
- [ ] "Have you established naming conventions for common operations?"
- [ ] "Does the routine have strong, functional cohesion—doing one and only one thing and doing it well?"
- [ ] "Do the routines have loose coupling—are the routine's connections to other routines small, intimate, visible, and flexible?"
- [ ] "Is the length of the routine determined naturally by its function and logic, rather than by an artificial coding standard?"

## High-Quality Routines - Parameter-Passing Issues (p.182)

- [ ] "Does the routine's parameter list, taken as a whole, present a consistent interface abstraction?"
- [ ] "Are the routine's parameters in a sensible order, including matching the order of parameters in similar routines?"
- [ ] "Are interface assumptions documented?"
- [ ] "Does the routine have seven or fewer parameters?"
- [ ] "Is each input parameter used?"
- [ ] "Is each output parameter used?"
- [ ] "Does the routine avoid using input parameters as working variables?"
- [ ] "If the routine is a function, does it return a valid value under all possible circumstances?"

---
Total items: 43
