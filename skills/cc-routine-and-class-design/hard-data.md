# Evidence: cc-routine-and-class-design

## Key Points (Author-Marked)

- [KEY POINT p.480] "Information hiding is a particularly valuable concept. Asking 'What should I hide?' settles many difficult design issues."
- [KEY POINT p.472] "Software's Primary Technical Imperative is managing complexity. This is greatly aided by a design focus on simplicity."
- [KEY POINT p.473] "Simplicity is achieved in two general ways: minimizing the amount of essential complexity that anyone's brain has to deal with at any one time, and keeping accidental complexity from proliferating needlessly."
- [KEY POINT p.476] "Good design is iterative; the more design possibilities you try, the better your final design will be."
- [KEY POINT p.473] "Design is heuristic. Dogmatic adherence to any single methodology hurts creativity and hurts your programs."
- [KEY POINT p.164] "The single most important reason to create a routine is to reduce a program's complexity."
- [KEY POINT p.171] "One of the strongest mental blocks to creating effective routines is a reluctance to create a simple routine for a simple purpose."
- [KEY POINT p.181] "Use a function if the primary purpose of the routine is to return the value indicated by the function name. Otherwise, use a procedure."
- [KEY POINT p.182] "Almost every macro demonstrates a flaw in the programming language, in the program, or in the programmer." (Stroustrup 1997)
- [KEY POINT p.175] "If a routine's name is bad, whether accurate or not, the program needs to change."

## Empirical Evidence

### Abstraction and ADTs
- [HARD DATA: Woodfield 1981, p.126] "Programs using ADTs had 30%+ better comprehension scores."
  - Context: Study on abstraction benefits for program understanding

### Information Hiding
- [HARD DATA: Korson and Vaishnavi 1986, p.95] "Large programs using information hiding were found to be easier to modify by a factor of 4."
  - Context: Maintainability study on information hiding effectiveness

### Inheritance and Class Complexity
- [HARD DATA: Basili 1996, p.126] "Deep inheritance significantly associated with fault rates; higher routines per class associated with higher faults; more routine calls correlated with fault rates."
  - Context: Study linking inheritance depth and class complexity to defects

- [HARD DATA: NASA 1989, p.126] "OO reuse: 70% vs 35% for functional decomposition."
  - Context: Comparative study on code reuse rates by paradigm

### Cohesion Studies
- [HARD DATA: Card, Church, and Agresti 1986, p.168-169] Study of 450 routines:
  - "50% of highly cohesive routines were fault free"
  - "Only 18% of routines with low cohesion were fault free"
  - "46% of routines with no unused variables had no errors"
  - "Only 17-29% of routines with more than one unreferenced variable had no errors"
  - Context: Correlating cohesion and parameter hygiene with reliability

- [HARD DATA: Card and Glass 1990, p.170] "Small routines (32 lines or fewer) were not correlated with lower cost or fault rate. Larger routines (65+ lines) were cheaper to develop per line of code."

- [HARD DATA: Card and Glass 1990, p.81] "High fan-out (more than about seven) indicates a class may be overly complex."
  - Context: Metric for class complexity threshold

### Coupling and Error Rates
- [HARD DATA: Selby and Basili 1991, p.168] "Routines with highest coupling-to-cohesion ratios had 7 times as many errors as those with lowest ratios, and were 20 times as costly to fix."

### Interface Errors
- [HARD DATA: Basili and Perricone 1984, p.174] "39% of all errors were internal interface errors - errors in communication between routines."
  - Context: Study highlighting parameter handling as major error source

### Cognitive Limits
- [HARD DATA: Miller 1956, p.126/174] "People generally cannot keep track of more than about seven chunks of information at once (7+/-2)."
  - Applied to: data members per class, parameters per routine

### Routine Length Studies
- [HARD DATA: Basili and Perricone 1984, p.170] "Routine size was inversely correlated with errors: as size increased (up to 200 lines), errors per line decreased."

- [HARD DATA: Shen et al. 1985, p.170] "Routine size was not correlated with errors, though structural complexity and amount of data were correlated with errors."

- [HARD DATA: Selby and Basili 1991, p.170] "Small routines (<143 source statements including comments) had 23% more errors per line but were 2.4 times less expensive to fix than larger routines."

- [HARD DATA: Lind and Vairavan 1989, p.170] "Code needed to be changed least when routines averaged 100 to 150 lines."

- [HARD DATA: Jones 1986a, p.170] "Most error-prone routines were larger than 500 lines. Beyond 500 lines, error rate was proportional to size."

## Anti-Patterns (CODING HORROR)

### Class Design Anti-Patterns

- [CODING HORROR p.125] Mixed Abstraction Levels
  - Description: AddEmployee/RemoveEmployee mixed with NextItemInList/FirstItem
  - Why it's wrong: Exposes container implementation; inconsistent abstraction
  - Fix: Hide container implementation completely

- [CODING HORROR p.127] Interface Erosion
  - Description: Employee class with IsZipCodeValid(Address) and GetQueryToCreateNewEmployee()
  - Why it's wrong: Not about employee abstraction; lower abstraction level
  - Fix: Move to appropriate class or lower-level module

- [CODING HORROR p.152] Empty Override
  - Description: ScratchlessCat overrides Scratch() to do nothing
  - Why it's wrong: Indicates error in base class design
  - Fix: Create Claws class, contain within Cat class

- [CODING HORROR p.136-137] Semantic Encapsulation Violations
  - Description: Skip calling InitializeOperations() because PerformFirstOperation() calls it automatically; skip calling database.Connect() because employee.Retrieve() will connect if needed
  - Why it's wrong: Client code depends on private implementation details
  - Fix: Always call required initialization; don't assume internal behavior

- [CODING HORROR p.146] God Classes
  - Description: All-knowing, all-powerful classes
  - Red flag: Class spends time calling Get()/Set() on other classes
  - Fix: Redistribute responsibilities; apply single responsibility principle

- [CODING HORROR p.143] Law of Demeter Violation
  - Description: Code like object.A().B().C()
  - Why it's wrong: Creates tight coupling across multiple objects
  - Fix: Only call routines on object itself or objects it directly instantiates

### Routine Design Anti-Patterns

- [CODING HORROR p.161] HandleStuff() Low-Quality Routine
  - Description: 11 parameters, bad name, unused parameters, no single purpose, magic numbers, global variable access
  - Why it's wrong: Violates nearly every routine quality principle
  - Problems identified: (1) Bad name, (2) Not documented, (3) Bad layout, (4) Input variable changed, (5) Reads/writes globals, (6) No single purpose, (7) No defense against bad data, (8) Magic numbers, (9) Unused parameters, (10) Incorrect parameter passing, (11) Too many parameters

- [CODING HORROR p.172] Numbered Routine Names
  - Description: Part1, Part2, OutputUser1, OutputUser2
  - Why it's wrong: Numbers provide no indication of different abstractions
  - Fix: Name routines by what they do differently

- [CODING HORROR p.172] Vague Verb Names
  - Description: HandleCalculation(), PerformServices(), OutputUser(), ProcessInput(), DealWithOutput()
  - Why it's wrong: Don't tell you what routines do
  - Exception: "Handle" in specific technical sense of handling an event

- [CODING HORROR p.167] Logical Cohesion
  - Description: Several operations stuffed into same routine, one selected by control flag; big if/case statement with unrelated operations
  - Why it's wrong: Operations aren't logically related
  - Exception: Event handlers that only dispatch commands are acceptable
  - Fix: Create separate routines for each operation

- [CODING HORROR p.167] Coincidental Cohesion
  - Description: Operations with no discernible relationship to each other ("chaotic cohesion")
  - Why it's wrong: Routine has no coherent purpose
  - Fix: Requires deeper redesign

- [CODING HORROR p.178] Multi-Statement Macros Without Braces (C++)
  - Description: Macro expands to multiple statements without enclosing braces
  - Why it's wrong: Only first statement executes in control structures
  - Fix: Wrap macro body in do { } while(0) or use inline function

- [CODING HORROR p.176] Using Input Parameters as Working Variables
  - Description: Modifying input parameter value within routine
  - Why it's wrong: Creates misleading variable names; loses original value
  - Fix: Copy to local working variable immediately

## Qualifiers and Scope

### When NOT to Apply Class Design Rigor
- **Scripting/automation code** - One-off scripts don't benefit from class design rigor (p.125)
- **Prototyping phase** - When exploring ideas before committing to design (p.125)
- **Simple data transfer objects** - Pure DTOs without behavior are exempt from ADT requirements (p.125)
- **Framework-mandated patterns** - When framework requires specific inheritance (e.g., Android Activity) (p.125)
- **Performance-critical inner loops** - Where accessor overhead matters (measure first) (p.125)

### When NOT to Use Information Hiding
- Excessive distribution is unavoidable (rare) (p.96)
- Performance measurement proves hiding creates bottleneck (measure first!) (p.96)
- Class is genuinely a simple data container with no behavior (p.96)

### When NOT to Use Design Patterns
- Code naturally fits simpler structure (p.104)
- Team unfamiliar with pattern (adds cognitive load) (p.104)
- Force-fitting required (symptom: "shifting code too far") (p.104)
- Using pattern for desire to try it rather than appropriateness (feature-itis) (p.104)

### Routine Length Qualifiers
- "The theoretical best maximum length is often described as one screen or one or two pages (approximately 50 to 150 lines)" - note "often described as" qualifier (p.170)
- "In object-oriented programs, routines should be allowed to grow organically up to 100-200 lines for complex algorithms" - scope limited to OOP (p.170)
- "Routines longer than 200 lines require care - no studies distinguished among sizes larger than 200 lines" (p.170)

### Design Methodology Boundaries
- "No single methodology is right for everything" - Plauger 1993 (p.118)
- "The more dogmatic you are about applying a design method, the fewer real-life problems you are going to solve" (p.118)
- "Two amounts of design are guaranteed to be wrong every time: designing every last detail AND not designing anything at all" (p.119)

## Cross-References

### To Other Code Complete Chapters
- [XREF] Chapter 5: Design in Construction (pp. 73-123) - Software design fundamentals, wicked problems, abstraction, encapsulation, information hiding, coupling/cohesion theory
- [XREF] Chapter 8: Defensive Programming - Error handling, assertions, input validation
- [XREF] Chapter 10: Variables - Data organization, scope, initialization
- [XREF] Chapter 11: Fundamental Data Types - Type selection, magic numbers
- [XREF] Chapter 19: Control Structures - Nesting depth, complexity metrics
- [XREF] Chapter 31: Layout and Style - Visual structure, naming conventions
- [XREF] Chapter 32: Self-Documenting Code - Documentation practices

### To APOSD Skills
- [XREF] aposd-designing-deep-modules - Complementary philosophy on interface depth
- [XREF] aposd-reviewing-module-design - Design review perspective
- [XREF] aposd-simplifying-complexity - Complexity reduction strategies

### To CC Skills
- [XREF] cc-defensive-programming - Error handling and input validation
- [XREF] cc-code-layout-and-style - Formatting and naming conventions
- [XREF] cc-quality-practices - Testing and review strategies
- [XREF] cc-pseudocode-programming - Routine design process

### Key Concept Relationships
- Abstraction enables Encapsulation enables Information Hiding (p.77-89)
- Cohesion (strength) opposes Coupling (dependencies) - optimize both (p.105-107)
- Design is heuristic, sloppy, nondeterministic, emergent (p.76)
- Wicked problems require solving to define, then solving again (Rittel and Webber 1973, p.74-75)