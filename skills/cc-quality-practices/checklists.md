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

- [ ] QA-1: "Have you identified specific quality characteristics important to this project?" (Good: Maintainability, performance, security prioritized; Bad: Vague "high quality" goal)
- [ ] QA-2: "Have you communicated quality objectives to all team members?"
- [ ] QA-3: "Have you differentiated between external and internal quality characteristics?" (External: End-user visible; Internal: Developer concerns)
- [ ] QA-4: "Have you analyzed which characteristics compete vs complement?" → Red flag: Optimizing performance while ignoring maintainability
- [ ] QA-5: "Have you selected several different error-detection techniques?" → Red flag: Relying on testing alone
- [ ] QA-6: "Have you included quality assurance at each development stage?" (Good: QA gates per phase; Bad: Final QA only)
- [ ] QA-7: "Have you established metrics to measure quality trends?" (Good: Defect density, code coverage tracked; Bad: No measurement)

**Key insight:** No single technique exceeds 75% detection. Plan for multiple techniques.

---

## Effective Inspections (p.485-492)

Use when: Setting up formal code review process

### Before the Inspection

- [ ] EI-1: "Do you have checklists focused on past problem areas?" (Good: Tailored to project defects; Bad: Generic checklist)
- [ ] EI-2: "Are reviewers given enough time to prepare?" → Red flag: Meeting scheduled without prep time (90% of defects found in preparation)
- [ ] EI-3: "Does each participant have a distinct role (moderator, reader, scribe)?" → Red flag: Author moderating their own inspection
- [ ] EI-4: "Has the author distributed materials with line numbers?" (Good: Numbered diffs/code; Bad: Raw code dump)

### During the Inspection

- [ ] EI-5: "Is focus on defect detection rather than correction?" → Red flag: Design discussions during inspection
- [ ] EI-6: "Is the meeting limited to two hours?" → Red flag: Marathon inspection sessions
- [ ] EI-7: "Does management understand it should NOT attend?" → Red flag: Managers present (creates defensiveness)
- [ ] EI-8: "Is the author listening without defending?" → Red flag: Author arguing about defects

### After the Inspection

- [ ] EI-9: "Is there follow-up to assure fixes are correct?" → Red flag: No verification of corrections
- [ ] EI-10: "Are defects logged with type and severity?" (Good: Categorized data; Bad: Simple list)
- [ ] EI-11: "Is data collected for process improvement?" (Good: Trend analysis; Bad: One-off metrics)

**Key insight:** Preparation finds 90% of defects; the meeting finds only 10% more [Votta 1991].

---

## Effective Pair Programming (p.483-484)

Use when: Deciding to pair or improving pairing practice

- [ ] PP-1: "Do you have a coding standard?" → Red flag: Pairing without agreed conventions
- [ ] PP-2: "Are both partners participating actively?" → Red flag: Non-typing partner disengaged (must analyze, plan, think ahead)
- [ ] PP-3: "Are you selecting assignments that benefit from pairing?" (Good: Complex code, learning opportunities; Bad: Simple CRUD pairing)
- [ ] PP-4: "Are you rotating pair assignments regularly?" → Red flag: Same pairs for months
- [ ] PP-5: "Are pairs matched in pace and personality?" (Good: Compatible work styles; Bad: Constant friction)
- [ ] PP-6: "Is there a team leader for coordination?" → Red flag: No one tracking pair assignments
- [ ] PP-7: "Is at least one partner experienced?" → Red flag: Two novices pairing without guidance

**Key insight:** 40-60% detection rate with real-time feedback and 45% schedule reduction potential.

---

## Test Cases (p.532-533)

Use when: Designing test suite for a class or routine

### Requirements and Design Coverage

- [ ] TC-1: "Does each requirement that applies have its own test case?"
- [ ] TC-2: "Does each design element that applies have its own test case?"

### Code Coverage

- [ ] TC-3: "Has each line of code been tested with at least one test case?"
- [ ] TC-4: "Have you computed minimum tests needed?" (Formula: 1 + count of if/while/for/and/or)
- [ ] TC-5: "Have all defined-used data-flow paths been tested?" → Red flag: Skipping data-flow testing
- [ ] TC-6: "Has code been checked for anomalous data-flow patterns?" (See Data-Flow Anomaly Patterns)

### Boundary Testing

- [ ] TC-7: "Have all simple boundaries been tested: maximum, minimum, and off-by-one?" → Red flag: Testing only middle values
- [ ] TC-8: "Have compound boundaries been tested?" (Good: Combinations that produce edge values; Bad: Simple boundaries only)

### Dirty Tests (aim for 5:1 ratio vs clean tests)

- [ ] TC-9: "Do test cases check for too little data (or no data)?" → Red flag: No empty input tests
- [ ] TC-10: "Do test cases check for too much data?" (Good: Buffer overflow tests; Bad: Only normal-sized data)
- [ ] TC-11: "Do test cases check for the wrong kind of data?" (Good: String when expecting number; Bad: Only correct types)
- [ ] TC-12: "Do test cases check for the wrong size of data?" (Good: 1000-char string in 100-char field; Bad: Perfect fits only)
- [ ] TC-13: "Do test cases check for uninitialized data?" → Red flag: Assuming initialization

### Clean Tests

- [ ] TC-14: "Are representative, middle-of-the-road values tested?" (Good: Normal user behavior; Bad: Only edge cases)
- [ ] TC-15: "Is the minimum normal configuration tested?" (Good: Single item in list; Bad: Only large datasets)
- [ ] TC-16: "Is the maximum normal configuration tested?" (Good: Full capacity; Bad: Only partial load)
- [ ] TC-17: "Is compatibility with old data tested?" → Red flag: No migration tests

### Test Quality

- [ ] TC-18: "Has a list of common errors been used to write test cases?" (Good: Off-by-one, null, uninitialized checked; Bad: Random test ideas)
- [ ] TC-19: "Do the test cases make hand-checks easy?" (Good: Verifiable expected values; Bad: Complex calculations)
- [ ] TC-20: "Are you using a coverage monitor?" → Red flag: Believing 95% coverage, achieving 30-60%

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

- [ ] DF-1: "Have you checked for Defined-Defined patterns?" → Red flag: Variable assigned twice without use
- [ ] DF-2: "Have you checked for Defined-Exited patterns?" → Red flag: Assignment before return (dead code)
- [ ] DF-3: "Have you checked for Defined-Killed patterns?" → Red flag: Assign then immediately free
- [ ] DF-4: "Have you checked for Entered-Killed patterns?" → Red flag: Free uninitialized resource
- [ ] DF-5: "Have you checked for Entered-Used patterns?" → Red flag: Uninitialized variable read
- [ ] DF-6: "Have you checked for Killed-Killed patterns?" → Red flag: Double-free
- [ ] DF-7: "Have you checked for Killed-Used patterns?" → Red flag: Use-after-free
- [ ] DF-8: "Have you checked for Used-Defined patterns?" (Acceptable for parameters, suspicious for locals)

**Note:** Some patterns are acceptable for global variables or parameters. Focus on local variables.

---

## Techniques for Finding Defects (p.559)

Use when: Debugging and need systematic approaches

### Gather Data

- [ ] FD-1: "Are you using all the data available to make your hypothesis?" (Good: Stack traces, logs, user reports; Bad: Guessing from one symptom)
- [ ] FD-2: "Have you refined the test cases that produce the error?" (Good: Minimal reproduction; Bad: Full app execution required)
- [ ] FD-3: "Can you reproduce the error several different ways?" (Good: Multiple triggers found; Bad: Single flaky reproduction)
- [ ] FD-4: "Are you generating more data to generate more hypotheses?" (Good: Instrumentation added; Bad: Staring at same output)
- [ ] FD-5: "Are you using the results of negative tests?" (Good: Know what DOESN'T trigger it; Bad: Only positive tests)

### Narrow the Search

- [ ] FD-6: "Have you exercised the code in your unit test suite?" → Red flag: Debugging in full app without isolating
- [ ] FD-7: "Are you narrowing the suspicious region of the code?" (Good: Binary search approach; Bad: Reading entire codebase)
- [ ] FD-8: "Are you checking classes and routines that have had defects before?" → Red flag: Ignoring defect history
- [ ] FD-9: "Have you checked code that's changed recently?" (Good: Check last week's commits; Bad: Assuming old code is correct)
- [ ] FD-10: "Will you expand the suspicious region if narrowing fails?" (Good: Broaden search; Bad: Fixating on wrong area)

### Use Tools and Techniques

- [ ] FD-11: "Are you using available tools?" (Good: Debugger, profiler, lint, sanitizers; Bad: Print statements only)
- [ ] FD-12: "Are you integrating incrementally to isolate the problem?" (Good: Add one change at a time; Bad: Big-bang integration)
- [ ] FD-13: "Are you checking for common defects?" → Red flag: Not checking off-by-one, null, uninitialized

### Get Help

- [ ] FD-14: "Have you brainstormed for possible hypotheses?" (Good: List 5+ theories; Bad: First theory only)
- [ ] FD-15: "Are you keeping a notepad and making a list of things to try?" → Red flag: Trying random fixes without recording
- [ ] FD-16: "Have you talked to someone else about the problem?" (Good: Rubber duck debugging; Bad: Struggling alone)
- [ ] FD-17: "Have you taken a break from the problem?" (Good: Let subconscious work; Bad: 8-hour debug session)

### Time Management

- [ ] FD-18: "Have you set a maximum time for quick debugging?" → Red flag: 2+ hours on trial-and-error (switch to brute-force)

---

## Techniques for Syntax Errors (p.557-558)

Use when: Compiler errors are confusing or misleading

- [ ] SE-1: "Are you checking lines BEFORE and AFTER the compiler's line number?" → Red flag: Trusting line numbers exactly
- [ ] SE-2: "Are you reading between the lines of compiler messages?" (Good: Understand root cause; Bad: Taking message literally)
- [ ] SE-3: "Are you fixing only the FIRST error, then recompiling?" → Red flag: Fixing cascading errors
- [ ] SE-4: "Are you using divide and conquer?" (Good: Comment out half the code; Bad: Reading entire file)
- [ ] SE-5: "Have you checked for misplaced comments and quotation marks?" (Trick: Insert `/*"/**/` to find unbalanced)

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

- [ ] FX-1: "Do you understand the problem before fixing it?" → Red flag: Guessing at a fix
- [ ] FX-2: "Do you understand the program, not just the problem?" (Good: Understand hundreds of lines of vicinity; Bad: Fixing one line in isolation)
- [ ] FX-3: "Can you confirm the defect diagnosis?" (Good: Can predict when it occurs; Bad: Uncertain about trigger)
- [ ] FX-4: "Are you relaxed?" → Red flag: Rushing under pressure (pressure causes errors; take a break)
- [ ] FX-5: "Have you saved the original source code?" (Good: Version control commit/branch; Bad: Overwriting immediately)

### The Fix

- [ ] FX-6: "Are you fixing the problem, not the symptom?" → Red flag: Special-case workarounds
- [ ] FX-7: "Are you changing the code only for good reason?" (Good: Justified change; Bad: "While I'm here" changes)
- [ ] FX-8: "Are you making one change at a time?" → Red flag: Multiple unrelated fixes together
- [ ] FX-9: "Are you confident the change will work BEFORE making it?" (Good: Predicted effect; Bad: Trial and error)

### After Fixing

- [ ] FX-10: "Have you checked your fix (or had someone else check)?" → Red flag: No verification (~50% of fixes are wrong first time)
- [ ] FX-11: "Have you added a unit test that exposes the defect?" → Red flag: Fixing without test
- [ ] FX-12: "Have you looked for similar defects?" (Good: Check same file, same developer, same pattern; Bad: One-off fix)

**Key insight:** ~50% of fixes are wrong the first time [Yourdon 1986b]. Always verify.

---

## Brute-Force Debugging Techniques (p.552-553)

Use when: Stuck debugging, need guaranteed (if tedious) approaches

These techniques are time-consuming but guaranteed to work:

### Code Review Approaches

- [ ] BF-1: "Can you perform a full design and/or code review on the broken code?" (Good: Systematic review; Bad: More random debugging)
- [ ] BF-2: "Can you throw away the section of code and redesign/recode from scratch?" → Red flag: Keeping obviously broken design
- [ ] BF-3: "Can you throw away the whole program and redesign/recode from scratch?" (Last resort for fundamentally broken architecture)

### Build Configuration

- [ ] BF-4: "Are you compiling code with full debugging information?" (Good: Debug symbols enabled; Bad: Optimized release build)
- [ ] BF-5: "Are you compiling at pickiest warning level and fixing ALL warnings?" → Red flag: Ignoring warnings
- [ ] BF-6: "Can you compile the code with a different compiler?" (Good: Cross-compiler check; Bad: Single compiler only)
- [ ] BF-7: "Can you compile and run in a different environment?" (Good: Different OS/architecture; Bad: Single environment)

### Testing Approaches

- [ ] BF-8: "Can you strap on a unit test harness and test the new code in isolation?" (Good: Isolated test; Bad: Full integration only)
- [ ] BF-9: "Can you create an automated test suite and run it all night?" (Good: Stress testing; Bad: Manual testing only)
- [ ] BF-10: "Can you step through a big loop in the debugger manually until error condition?" (Tedious but guaranteed)

### Instrumentation

- [ ] BF-11: "Can you instrument the code with print, display, or other logging statements?" (Good: Strategic logging; Bad: No visibility)
- [ ] BF-12: "Can you link or run against special libraries that warn when code is misused?" (Good: Sanitizers, debug malloc; Bad: Standard libs only)

### Environment

- [ ] BF-13: "Can you replicate the end-user's full machine configuration?" (Good: Exact environment; Bad: "Works on my machine")
- [ ] BF-14: "Can you integrate new code in small pieces, fully testing each piece?" (Good: Incremental integration; Bad: Big-bang integration)

**When to use:** Set a time limit for "quick" debugging (15-30 min). If exceeded, switch to brute-force.

---

## General Debugging Approach (p.560)

Use when: Evaluating your overall debugging practice

### Mindset

- [ ] GD-1: "Do you use debugging as an opportunity to learn more about your program?" (Good: Learning mindset; Bad: Just fixing symptoms)
- [ ] GD-2: "Do you avoid the trial-and-error, superstitious approach to debugging?" → Red flag: Random code changes hoping for fix
- [ ] GD-3: "Do you assume that errors are your fault?" (95%+ are developer errors, not compiler/hardware/framework)

### Method

- [ ] GD-4: "Do you use the scientific method to stabilize intermittent errors?" (Good: Hypothesize → Experiment → Verify; Bad: Guessing)
- [ ] GD-5: "Do you use the scientific method to find defects?" → Red flag: Skipping hypothesis step
- [ ] GD-6: "Do you use several different techniques to find defects?" (Good: Multiple approaches; Bad: One technique only)

### Verification

- [ ] GD-7: "Do you verify that the fix is correct?" → Red flag: No verification after fix
- [ ] GD-8: "Do you search for similar defects after fixing one?" (Good: Pattern search; Bad: One-off fix)

### Tools

- [ ] GD-9: "Do you use compiler warning messages (at pickiest level)?" → Red flag: Warnings disabled or ignored
- [ ] GD-10: "Do you use execution profiling?" (Good: Data-driven optimization; Bad: Guessing at performance)
- [ ] GD-11: "Do you use a test framework?" → Red flag: Manual testing only
- [ ] GD-12: "Do you use scaffolding (isolated test code)?" (Good: Unit test harnesses; Bad: Integration tests only)
- [ ] GD-13: "Do you use interactive debugging?" (Good: Debugger proficiency; Bad: Print statements only)

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

## Red Flags

- [ ] RF-1: "Relying on testing alone?" - Single error-detection technique → Select multiple techniques (no technique exceeds 75% detection)
- [ ] RF-2: "Author moderating their own inspection?" - Conflict of interest → Assign independent moderator
- [ ] RF-3: "No preparation time before inspection?" - 90% of defects found in preparation → Schedule prep time before meeting
- [ ] RF-4: "Only clean tests?" - No dirty tests → Aim for 5:1 ratio of dirty to clean tests
- [ ] RF-5: "Skipping data-flow testing?" - Missing common defects → Check all 8 anomaly patterns
- [ ] RF-6: "Trial-and-error debugging?" - Superstitious code changes → Use scientific method (hypothesize → experiment → verify)
- [ ] RF-7: "No verification after fix?" - ~50% of fixes wrong first time → Always verify fix is correct
- [ ] RF-8: "Ignoring compiler warnings?" - Missing early defect detection → Enable pickiest warnings and fix ALL
- [ ] RF-9: "Debugging 2+ hours without progress?" - Stuck on inefficient approach → Switch to brute-force techniques
- [ ] RF-10: "No unit tests for defects?" - Regression risk → Add test that exposes defect before fixing

---

Total items: 115
