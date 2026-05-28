# Checklists: Control Flow — Loops & Advanced

Source: Code Complete 2nd Edition, Chapters 16-18 + Modern Additions

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
- [ ] RF-11: "Silent catch-continue in loop?" - Error inside loop caught and `continue`d, failed items silently skipped → Log each failure with context, track failure count, fail the batch if threshold exceeded
- [ ] RF-12: "Default/else branch does nothing?" - `default:` case or final `else` is empty or just breaks on unexpected values → Unexpected cases should log or throw, not pass silently
