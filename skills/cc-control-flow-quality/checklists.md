# Checklists: cc-control-flow-quality

Source: Code Complete 2nd Edition, Chapters 14-19

---

## Emergency Minimum (Crisis Mode)

**Use ONLY when production is down.** Return within 24 hours to apply full checklist.

- [ ] EM-1: "Nesting depth" - Fix does not add 4th+ nesting level → Red flag: 4+ levels = unreadable
- [ ] EM-2: "Loop exits" - All loops have reachable termination conditions → Red flag: infinite loop risk
- [ ] EM-3: "Variable names" - Any new variables have meaningful names (no `temp`, `fix`, `x`)
- [ ] EM-4: "Crisis comment" - One-line comment explaining WHY this fix was made

---

## NEVER Skip (regardless of circumstances)

These items must be checked even under maximum time pressure:

- [ ] NS-1: "Is nesting limited to three levels or less?" (Ch 16) → Red flag: 4+ levels
- [ ] NS-2: "Does the loop end under all possible conditions?" (Ch 16) → Red flag: missing exit
- [ ] NS-3: "Does the loop index have a meaningful name?" (Ch 16) (Good: customerIndex, Bad: i in outer loop)
- [ ] NS-4: "Is the termination condition obvious?" (Ch 16)
- [ ] NS-5: "Does recursive code include a path to stop recursion?" (Ch 17) → Red flag: unbounded recursion

---

## Organizing Sequential Code (Ch 14)

- [ ] SC-1: "Are dependencies among statements made obvious through code structure?"
- [ ] SC-2: "Do routine names make dependencies obvious?"
- [ ] SC-3: "Do parameters make dependencies obvious?"
- [ ] SC-4: "Do comments describe dependencies that would otherwise be unclear?"
- [ ] SC-5: "Are housekeeping variables used to check sequential dependencies in critical code?"
- [ ] SC-6: "Does code read from top to bottom?" (Good: linear flow, Bad: jumping around)
- [ ] SC-7: "Are related statements grouped together?"
- [ ] SC-8: "Have independent statement groups been moved into their own routines?"

---

## Using Conditionals (Ch 15)

### if-then Statements

- [ ] IT-1: "Is the nominal path through the code clear?" (Good: normal case first, Bad: error case first)
- [ ] IT-2: "Do if-then tests branch correctly on equality?"
- [ ] IT-3: "Is the else clause present and documented?"
- [ ] IT-4: "Is the else clause correct?"
- [ ] IT-5: "Are if and else clauses used correctly (not reversed)?" → Red flag: logic inverted
- [ ] IT-6: "Does the normal case follow the if rather than the else?"

### if-then-else-if Chains

- [ ] IC-1: "Are complicated tests encapsulated in boolean function calls?"
- [ ] IC-2: "Are the most common cases tested first?" (Good: frequent first, Bad: rare first)
- [ ] IC-3: "Are all cases covered?"
- [ ] IC-4: "Is the chain the best implementation vs. a case statement?"

### case Statements

- [ ] CS-1: "Are cases ordered meaningfully?"
- [ ] CS-2: "Are actions for each case simple (calling routines if necessary)?"
- [ ] CS-3: "Does the case test a real variable (not a manufactured one)?"
- [ ] CS-4: "Is the default clause used legitimately?"
- [ ] CS-5: "Is the default clause used to detect and report unexpected cases?"
- [ ] CS-6: "Does each case end with a break (in C, C++, Java)?" → Red flag: fall-through without comment

---

## Controlling Loops (Ch 16)

### Loop Selection and Creation

- [ ] LS-1: "Is a while loop used instead of for loop when appropriate?"
- [ ] LS-2: "Was the loop created from the inside out?"

### Entering the Loop

- [ ] LE-1: "Is the loop entered from the top?" → Red flag: mid-loop entry
- [ ] LE-2: "Is initialization code directly before the loop?"
- [ ] LE-3: "Is an infinite/event loop constructed cleanly (not with arbitrary limits)?"
- [ ] LE-4: "Is the for loop header reserved for loop-control code only?" (Good: simple counter, Bad: business logic)

### Inside the Loop

- [ ] LI-1: "Does the loop use braces to enclose the body?"
- [ ] LI-2: "Does the loop body have something in it (non-empty)?"
- [ ] LI-3: "Are housekeeping chores grouped at beginning or end?"
- [ ] LI-4: "Does the loop perform one and only one function?" (Good: single purpose, Bad: multiple unrelated actions)
- [ ] LI-5: "Is the loop short enough to view all at once?"
- [ ] LI-6: "Is nesting limited to three levels or less?" → Red flag: 4+ levels
- [ ] LI-7: "Have long loop contents been moved to their own routine?"
- [ ] LI-8: "If the loop is long, is it especially clear?"

### Loop Indexes

- [ ] LX-1: "Does code inside for loops avoid modifying the loop index?" → Red flag: index modification inside loop
- [ ] LX-2: "Is a variable used to save important index values (not the index itself outside the loop)?"
- [ ] LX-3: "Is the loop index an ordinal or enumerated type (not floating-point)?" → Red flag: floating-point loop index
- [ ] LX-4: "Does the loop index have a meaningful name?"
- [ ] LX-5: "Does the loop avoid index cross-talk?" → Red flag: reusing index variable

### Exiting the Loop

- [ ] LT-1: "Does the loop end under all possible conditions?" → Red flag: infinite loop possible
- [ ] LT-2: "Does the loop use safety counters if required by standards?"
- [ ] LT-3: "Is the termination condition obvious?"
- [ ] LT-4: "If break or continue are used, are they correct?"

---

## Unusual Control Structures (Ch 17)

### return

- [ ] RT-1: "Does each routine use return only when necessary?"
- [ ] RT-2: "Do returns enhance readability?" (Good: early exit for errors, Bad: multiple mid-function returns)

### Recursion

- [ ] RC-1: "Does recursive code include a path to stop recursion?" → Red flag: missing base case
- [ ] RC-2: "Does the routine use a safety counter to guarantee stopping?"
- [ ] RC-3: "Is recursion limited to one routine?"
- [ ] RC-4: "Is recursion depth within stack limits?"
- [ ] RC-5: "Is recursion better than simple iteration for this case?"

### goto

- [ ] GT-1: "Are gotos used only as a last resort?" → Red flag: goto usage
- [ ] GT-2: "If used for efficiency, has the gain been measured and documented?"
- [ ] GT-3: "Are gotos limited to one label per routine?"
- [ ] GT-4: "Do all gotos go forward, not backward?"
- [ ] GT-5: "Are all goto labels used?"

---

## Table-Driven Methods (Ch 18)

- [ ] TD-1: "Have table-driven methods been considered as an alternative to complicated logic?"
- [ ] TD-2: "Have table-driven methods been considered as an alternative to complicated inheritance?"
- [ ] TD-3: "Has storing table data externally been considered (for runtime modification)?"
- [ ] TD-4: "If table access requires key calculation, is it isolated in a routine?"

---

## Control-Structure Issues (Ch 19)

- [ ] CI-1: "Do expressions use true/false rather than 1/0?"
- [ ] CI-2: "Are boolean values compared implicitly (not to true/false explicitly)?" (Good: if(isReady), Bad: if(isReady == true))
- [ ] CI-3: "Are numeric values compared to test values explicitly?"
- [ ] CI-4: "Have expressions been simplified using boolean variables, functions, or decision tables?"
- [ ] CI-5: "Are boolean expressions stated positively?" (Good: if(isValid), Bad: if(!isInvalid))
- [ ] CI-6: "Do pairs of braces balance?"
- [ ] CI-7: "Are braces used everywhere needed for clarity?"
- [ ] CI-8: "Are logical expressions fully parenthesized?"
- [ ] CI-9: "Have tests been written in number-line order?" (Good: MIN <= x && x <= MAX, Bad: x <= MAX && MIN <= x)
- [ ] CI-10: "Do Java tests use a.equals(b) style when appropriate?"
- [ ] CI-11: "Are null statements obvious?"
- [ ] CI-12: "Have nested statements been simplified (retesting, if-then-else, case, routines, OO design)?"
- [ ] CI-13: "If routine has more than 10 decision points, is there good reason not to redesign?" → Red flag: >10 decision points

---

## Modern Control Flow (Beyond Code Complete)

### Async/Await

- [ ] AA-1: "Are nested callbacks flattened using async/await?"
- [ ] AA-2: "Do async functions have proper error handling (try/catch or .catch())?" → Red flag: unhandled promise rejection
- [ ] AA-3: "Is Promise.all used for parallel operations instead of sequential awaits?"

### Pattern Matching

- [ ] PM-1: "Does pattern matching handle all cases (exhaustiveness)?" → Red flag: missing match arm
- [ ] PM-2: "Are match arms kept simple (≤3 lines, ideally function calls)?"
- [ ] PM-3: "Is pattern matching preferred over if-else chains for type/variant dispatch?"

### Functional Pipelines

- [ ] FP-1: "Are map/filter/reduce preferred over explicit loops for simple transformations?"
- [ ] FP-2: "Is early exit needed? (If yes, use explicit loop instead)"
- [ ] FP-3: "Does the pipeline read clearly left-to-right or top-to-bottom?"

---

## Red Flags

- [ ] RF-1: "Deep nesting (4+ levels)?" - Code unreadable → Extract methods, use early returns, flatten structure
- [ ] RF-2: "Infinite loop possible?" - Missing/unreachable exit condition → Add safety counter, verify all paths exit
- [ ] RF-3: "Loop index modification inside loop?" - Unpredictable iteration → Use while loop or extract to function
- [ ] RF-4: "Floating-point loop index?" - Precision errors cause bugs → Use integer index, compute float in body
- [ ] RF-5: "Reversed if/else logic?" - Normal case in else clause → Swap branches, put normal case first
- [ ] RF-6: "Missing recursion base case?" - Stack overflow risk → Add explicit termination condition + safety counter
- [ ] RF-7: ">10 decision points in routine?" - Too complex to understand → Decompose into smaller routines or use table-driven method
- [ ] RF-8: "goto usage?" - Spaghetti code risk → Restructure with proper loops/conditionals or extract routine
- [ ] RF-9: "Unhandled promise rejection?" - Silent failure in async code → Add try/catch or .catch() handler
- [ ] RF-10: "switch fall-through without comment?" - Likely bug → Add break or explicit fall-through comment

---

Total items: 124
