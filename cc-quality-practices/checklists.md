# Checklists: cc-quality-practices

Source: Code Complete 2nd Edition, Chapters 20-23

---

## Quick Reference: Which Checklist When?

| Situation | Use Checklist |
|-----------|---------------|
| Starting a project | A Quality-Assurance Plan |
| Setting up code review | Effective Inspections |
| Pairing on code | Effective Pair Programming |
| Writing tests | Test Cases |
| Bug won't reproduce | Techniques for Finding Defects |
| Compiler errors confusing | Techniques for Syntax Errors |
| Found the bug, fixing it | Techniques for Fixing Defects |
| Stuck debugging | Brute-Force Debugging Techniques |
| Reviewing overall approach | General Debugging Approach |

---

## A Quality-Assurance Plan (p.603-644)

Use when: Starting a project or reviewing QA strategy

- [ ] Have you identified specific quality characteristics important to this project?
- [ ] Have you communicated quality objectives to all team members?
- [ ] Have you differentiated between external and internal quality characteristics?
- [ ] Have you analyzed which characteristics compete vs complement?
- [ ] Have you selected several different error-detection techniques?
- [ ] Have you included quality assurance at each development stage?
- [ ] Have you established metrics to measure quality trends?

**Key insight:** No single technique exceeds 75% detection. Plan for multiple techniques.

---

## Effective Inspections (p.485-492)

Use when: Setting up formal code review process

### Before the Inspection
- [ ] Do you have checklists focused on past problem areas?
- [ ] Are reviewers given enough time to prepare? (90% of defects found here)
- [ ] Does each participant have a distinct role (moderator, reader, scribe)?
- [ ] Has the author distributed materials with line numbers?

### During the Inspection
- [ ] Is focus on defect detection rather than correction?
- [ ] Is the meeting limited to two hours?
- [ ] Does management understand it should NOT attend?
- [ ] Is the author listening without defending?

### After the Inspection
- [ ] Is there follow-up to assure fixes are correct?
- [ ] Are defects logged with type and severity?
- [ ] Is data collected for process improvement?

**Key insight:** Preparation finds 90% of defects; the meeting finds only 10% more [Votta 1991].

---

## Effective Pair Programming (p.483-484)

Use when: Deciding to pair or improving pairing practice

- [ ] Do you have a coding standard?
- [ ] Are both partners participating actively? (Non-typing partner must analyze, plan, think ahead)
- [ ] Are you selecting assignments that benefit from pairing? (Complex code, learning opportunities)
- [ ] Are you rotating pair assignments regularly?
- [ ] Are pairs matched in pace and personality?
- [ ] Is there a team leader for coordination?
- [ ] Is at least one partner experienced? (Don't pair two novices)

**Key insight:** 40-60% detection rate with real-time feedback and 45% schedule reduction potential.

---

## Test Cases (p.532-533)

Use when: Designing test suite for a class or routine

### Requirements and Design Coverage
- [ ] Does each requirement that applies have its own test case?
- [ ] Does each design element that applies have its own test case?

### Code Coverage
- [ ] Has each line of code been tested with at least one test case?
- [ ] Have you computed minimum tests needed? (1 + count of if/while/for/and/or)
- [ ] Have all defined-used data-flow paths been tested?
- [ ] Has code been checked for anomalous data-flow patterns?

### Boundary Testing
- [ ] Have all simple boundaries been tested: maximum, minimum, and off-by-one?
- [ ] Have compound boundaries been tested? (Combinations that produce edge values)

### Dirty Tests (aim for 5:1 ratio vs clean tests)
- [ ] Do test cases check for too little data (or no data)?
- [ ] Do test cases check for too much data?
- [ ] Do test cases check for the wrong kind of data?
- [ ] Do test cases check for the wrong size of data?
- [ ] Do test cases check for uninitialized data?

### Clean Tests
- [ ] Are representative, middle-of-the-road values tested?
- [ ] Is the minimum normal configuration tested?
- [ ] Is the maximum normal configuration tested?
- [ ] Is compatibility with old data tested?

### Test Quality
- [ ] Has a list of common errors been used to write test cases?
- [ ] Do the test cases make hand-checks easy?
- [ ] Are you using a coverage monitor? (Developers believe 95%, achieve 30-60%)

**Key insight:** Mature organizations have 5 dirty tests for every 1 clean test.

---

## Data-Flow Anomaly Patterns (p.509-510)

Use when: Reviewing code for data-related bugs before testing

Check for these suspicious patterns:

| Pattern | Meaning | Likely Problem |
|---------|---------|----------------|
| Defined-Defined | Variable assigned twice without use | Redundant or missing code |
| Defined-Exited | Variable assigned then routine exits | Dead code or missing use |
| Defined-Killed | Variable assigned then freed/invalidated | Missing use or wrong order |
| Entered-Killed | Variable killed without being defined | Logic error |
| Entered-Used | Variable used without being defined | Uninitialized variable |
| Killed-Killed | Variable killed twice | Double-free, logic error |
| Killed-Used | Variable used after being killed | Use-after-free |
| Used-Defined | Variable used then assigned | Check for prior definition |

**Note:** Some patterns are acceptable for global variables or parameters. Focus on local variables.

---

## Techniques for Finding Defects (p.559)

Use when: Debugging and need systematic approaches

### Gather Data
- [ ] Use all the data available to make your hypothesis
- [ ] Refine the test cases that produce the error
- [ ] Reproduce the error several different ways
- [ ] Generate more data to generate more hypotheses
- [ ] Use the results of negative tests (what DOESN'T trigger it?)

### Narrow the Search
- [ ] Exercise the code in your unit test suite
- [ ] Narrow the suspicious region of the code (binary search)
- [ ] Be suspicious of classes and routines that have had defects before
- [ ] Check code that's changed recently
- [ ] Expand the suspicious region if narrowing fails

### Use Tools and Techniques
- [ ] Use available tools (debugger, profiler, lint)
- [ ] Integrate incrementally to isolate the problem
- [ ] Check for common defects (off-by-one, null, uninitialized)

### Get Help
- [ ] Brainstorm for possible hypotheses
- [ ] Keep a notepad and make a list of things to try
- [ ] Talk to someone else about the problem (rubber duck debugging)
- [ ] Take a break from the problem (let subconscious work)

### Time Management
- [ ] Set a maximum time for quick and dirty debugging (then switch to brute-force)

---

## Techniques for Syntax Errors (p.557-558)

Use when: Compiler errors are confusing or misleading

- [ ] Don't trust line numbers in compiler messages (look before AND after)
- [ ] Don't trust compiler messages (read between the lines)
- [ ] Don't trust the compiler's second message (fix first error, recompile)
- [ ] Divide and conquer (remove half the code, see if error remains)
- [ ] Find misplaced comments and quotation marks

### Comment/Quote Finder Trick
Insert this sequence to find unbalanced comments or quotes:
```
/*"/**/
```
If this causes new errors, you have mismatched comments or quotes.

### Common Misleading Errors

| Compiler Says | Often Means |
|---------------|-------------|
| "Unexpected token" on line N | Missing semicolon or brace on line N-1 |
| "Undefined variable" | Typo in variable name, or scope issue |
| Multiple cascading errors | Fix only the FIRST error, recompile |
| Error in header/import | Problem in the imported file, not this one |

---

## Techniques for Fixing Defects (p.560)

Use when: You've found the bug and are about to fix it

### Before Fixing
- [ ] Understand the problem before you fix it
- [ ] Understand the program, not just the problem (vicinity = hundreds of lines)
- [ ] Confirm the defect diagnosis (can you predict when it occurs?)
- [ ] Relax (pressure causes errors; take a break if rushing)
- [ ] Save the original source code

### The Fix
- [ ] Fix the problem, not the symptom (no special-case workarounds)
- [ ] Change the code only for good reason
- [ ] Make one change at a time
- [ ] Be confident the change will work BEFORE making it

### After Fixing
- [ ] Check your fix (or have someone else check)
- [ ] Add a unit test that exposes the defect
- [ ] Look for similar defects (same file, same developer, same pattern)

**Key insight:** ~50% of fixes are wrong the first time [Yourdon 1986b]. Always verify.

---

## Brute-Force Debugging Techniques (p.552-553)

Use when: Stuck debugging, need guaranteed (if tedious) approaches

These techniques are time-consuming but guaranteed to work:

### Code Review Approaches
- [ ] Perform a full design and/or code review on the broken code
- [ ] Throw away the section of code and redesign/recode from scratch
- [ ] Throw away the whole program and redesign/recode from scratch

### Build Configuration
- [ ] Compile code with full debugging information
- [ ] Compile code at pickiest warning level and fix ALL warnings
- [ ] Compile the code with a different compiler
- [ ] Compile and run the program in a different environment

### Testing Approaches
- [ ] Strap on a unit test harness and test the new code in isolation
- [ ] Create an automated test suite and run it all night
- [ ] Step through a big loop in the debugger manually until error condition

### Instrumentation
- [ ] Instrument the code with print, display, or other logging statements
- [ ] Link or run against special libraries that warn when code is misused

### Environment
- [ ] Replicate the end-user's full machine configuration
- [ ] Integrate new code in small pieces, fully testing each piece

**When to use:** Set a time limit for "quick" debugging (15-30 min). If exceeded, switch to brute-force.

---

## General Debugging Approach (p.560)

Use when: Evaluating your overall debugging practice

### Mindset
- [ ] Do you use debugging as an opportunity to learn more about your program?
- [ ] Do you avoid the trial-and-error, superstitious approach to debugging?
- [ ] Do you assume that errors are your fault? (95%+ are)

### Method
- [ ] Do you use the scientific method to stabilize intermittent errors?
- [ ] Do you use the scientific method to find defects? (Hypothesize → Experiment → Verify)
- [ ] Do you use several different techniques to find defects?

### Verification
- [ ] Do you verify that the fix is correct?
- [ ] Do you search for similar defects after fixing one?

### Tools
- [ ] Do you use compiler warning messages (at pickiest level)?
- [ ] Do you use execution profiling?
- [ ] Do you use a test framework?
- [ ] Do you use scaffolding (isolated test code)?
- [ ] Do you use interactive debugging?

---

## Inspection Roles Reference

| Role | Responsibility |
|------|----------------|
| **Moderator** | Distributes materials, runs meeting, produces report, verifies fixes |
| **Author** | Wrote the code; answers questions but does NOT defend |
| **Reader** | Paraphrases/reads code aloud (NOT the author) |
| **Scribe** | Records defects during meeting |
| **Reviewer** | Finds defects during preparation; participates in meeting |

**Critical:** Author should NEVER moderate their own inspection.

---

## Quick Counts

| Checklist | Items |
|-----------|-------|
| Quality-Assurance Plan | 7 |
| Effective Inspections | 11 |
| Effective Pair Programming | 7 |
| Test Cases | 20 |
| Data-Flow Anomalies | 8 patterns |
| Finding Defects | 17 |
| Syntax Errors | 5 + table |
| Fixing Defects | 12 |
| Brute-Force Techniques | 13 |
| General Debugging | 12 |

**Total actionable items: 112+**
