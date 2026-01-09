# Checklists: cc-control-flow-quality

Source: Code Complete 2nd Edition, Chapters 14-19

---

## Emergency Minimum (Crisis Mode)

**Use ONLY when production is down.** Return within 24 hours to apply full checklist.

- [ ] **Nesting depth** - Fix does not add 4th+ nesting level
- [ ] **Loop exits** - All loops have reachable termination conditions
- [ ] **Variable names** - Any new variables have meaningful names (no `temp`, `fix`, `x`)
- [ ] **Crisis comment** - One-line comment explaining WHY this fix was made

---

## NEVER Skip (regardless of circumstances)

These items must be checked even under maximum time pressure:

- [ ] Is nesting limited to three levels or less? (Ch 16)
- [ ] Does the loop end under all possible conditions? (Ch 16)
- [ ] Does the loop index have a meaningful name? (Ch 16)
- [ ] Is the termination condition obvious? (Ch 16)
- [ ] Does recursive code include a path to stop recursion? (Ch 17)

---

## Organizing Sequential Code (Ch 14)

- [ ] Are dependencies among statements made obvious through code structure?
- [ ] Do routine names make dependencies obvious?
- [ ] Do parameters make dependencies obvious?
- [ ] Do comments describe dependencies that would otherwise be unclear?
- [ ] Are housekeeping variables used to check sequential dependencies in critical code?
- [ ] Does code read from top to bottom?
- [ ] Are related statements grouped together?
- [ ] Have independent statement groups been moved into their own routines?

## Using Conditionals (Ch 15)

### if-then Statements
- [ ] Is the nominal path through the code clear?
- [ ] Do if-then tests branch correctly on equality?
- [ ] Is the else clause present and documented?
- [ ] Is the else clause correct?
- [ ] Are if and else clauses used correctly (not reversed)?
- [ ] Does the normal case follow the if rather than the else?

### if-then-else-if Chains
- [ ] Are complicated tests encapsulated in boolean function calls?
- [ ] Are the most common cases tested first?
- [ ] Are all cases covered?
- [ ] Is the chain the best implementation vs. a case statement?

### case Statements
- [ ] Are cases ordered meaningfully?
- [ ] Are actions for each case simple (calling routines if necessary)?
- [ ] Does the case test a real variable (not a manufactured one)?
- [ ] Is the default clause used legitimately?
- [ ] Is the default clause used to detect and report unexpected cases?
- [ ] Does each case end with a break (in C, C++, Java)?

## Controlling Loops (Ch 16)

### Loop Selection and Creation
- [ ] Is a while loop used instead of for loop when appropriate?
- [ ] Was the loop created from the inside out?

### Entering the Loop
- [ ] Is the loop entered from the top?
- [ ] Is initialization code directly before the loop?
- [ ] Is an infinite/event loop constructed cleanly (not with arbitrary limits)?
- [ ] Is the for loop header reserved for loop-control code only?

### Inside the Loop
- [ ] Does the loop use braces to enclose the body?
- [ ] Does the loop body have something in it (non-empty)?
- [ ] Are housekeeping chores grouped at beginning or end?
- [ ] Does the loop perform one and only one function?
- [ ] Is the loop short enough to view all at once?
- [ ] Is nesting limited to three levels or less?
- [ ] Have long loop contents been moved to their own routine?
- [ ] If the loop is long, is it especially clear?

### Loop Indexes
- [ ] Does code inside for loops avoid modifying the loop index?
- [ ] Is a variable used to save important index values (not the index itself outside the loop)?
- [ ] Is the loop index an ordinal or enumerated type (not floating-point)?
- [ ] Does the loop index have a meaningful name?
- [ ] Does the loop avoid index cross-talk?

### Exiting the Loop
- [ ] Does the loop end under all possible conditions?
- [ ] Does the loop use safety counters if required by standards?
- [ ] Is the termination condition obvious?
- [ ] If break or continue are used, are they correct?

## Unusual Control Structures (Ch 17)

### return
- [ ] Does each routine use return only when necessary?
- [ ] Do returns enhance readability?

### Recursion
- [ ] Does recursive code include a path to stop recursion?
- [ ] Does the routine use a safety counter to guarantee stopping?
- [ ] Is recursion limited to one routine?
- [ ] Is recursion depth within stack limits?
- [ ] Is recursion better than simple iteration for this case?

### goto
- [ ] Are gotos used only as a last resort?
- [ ] If used for efficiency, has the gain been measured and documented?
- [ ] Are gotos limited to one label per routine?
- [ ] Do all gotos go forward, not backward?
- [ ] Are all goto labels used?

## Table-Driven Methods (Ch 18)

- [ ] Have table-driven methods been considered as an alternative to complicated logic?
- [ ] Have table-driven methods been considered as an alternative to complicated inheritance?
- [ ] Has storing table data externally been considered (for runtime modification)?
- [ ] If table access requires key calculation, is it isolated in a routine?

## Control-Structure Issues (Ch 19)

- [ ] Do expressions use true/false rather than 1/0?
- [ ] Are boolean values compared implicitly (not to true/false explicitly)?
- [ ] Are numeric values compared to test values explicitly?
- [ ] Have expressions been simplified using boolean variables, functions, or decision tables?
- [ ] Are boolean expressions stated positively?
- [ ] Do pairs of braces balance?
- [ ] Are braces used everywhere needed for clarity?
- [ ] Are logical expressions fully parenthesized?
- [ ] Have tests been written in number-line order?
- [ ] Do Java tests use a.equals(b) style when appropriate?
- [ ] Are null statements obvious?
- [ ] Have nested statements been simplified (retesting, if-then-else, case, routines, OO design)?
- [ ] If routine has more than 10 decision points, is there good reason not to redesign?

## Modern Control Flow (Beyond Code Complete)

### Async/Await
- [ ] Are nested callbacks flattened using async/await?
- [ ] Do async functions have proper error handling (try/catch or .catch())?
- [ ] Is Promise.all used for parallel operations instead of sequential awaits?

### Pattern Matching
- [ ] Does pattern matching handle all cases (exhaustiveness)?
- [ ] Are match arms kept simple (≤3 lines, ideally function calls)?
- [ ] Is pattern matching preferred over if-else chains for type/variant dispatch?

### Functional Pipelines
- [ ] Are map/filter/reduce preferred over explicit loops for simple transformations?
- [ ] Is early exit needed? (If yes, use explicit loop instead)
- [ ] Does the pipeline read clearly left-to-right or top-to-bottom?

---
Total items: 87 (78 original + 9 modern)
