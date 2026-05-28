# Checklists: Quality Practices — QA & Testing

Source: Code Complete 2nd Edition, Chapters 20-22

---

## Quick Reference: Which Checklist When?

| Situation | Use Checklist |
|-----------|---------------|
| Starting a project | A Quality-Assurance Plan |
| Setting up code review | Effective Inspections |
| Pairing on code | Effective Pair Programming |
| Writing tests | Test Cases |
| Bug won't reproduce | Techniques for Finding Defects (see debugging.md) |
| Compiler errors confusing | Techniques for Syntax Errors (see debugging.md) |
| Found the bug, fixing it | Techniques for Fixing Defects (see debugging.md) |
| Stuck debugging | Brute-Force Debugging Techniques (see debugging.md) |
| Reviewing overall approach | General Debugging Approach (see debugging.md) |

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
