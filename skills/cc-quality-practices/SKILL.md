---
name: cc-quality-practices
description: "Use when planning QA, choosing review methods, designing tests, or debugging fails. Triggers on: defects found late, tests pass but production bugs, coverage disputes, review ineffective, spending excessive time debugging."
---

# Skill: cc-quality-practices

## STOP - The Quality Principle

**Improving quality reduces development costs.** No single defect-detection technique exceeds 75% effectiveness. Combining techniques nearly doubles detection rates.

**Critical ratio:** Mature organizations have 5 dirty tests for every 1 clean test.

**Debugging rule:** Do NOT skip to FIX without completing STABILIZE → HYPOTHESIZE → EXPERIMENT. ~50% of defect corrections are wrong the first time.

---

## Key Definitions

### External vs Internal Quality
- **External** (users care about): Correctness, usability, efficiency, reliability, integrity, robustness
- **Internal** (developers care about): Maintainability, flexibility, portability, reusability, readability, testability

Internal quality enables external quality. Poor maintainability → can't fix defects → poor reliability.

### Defect Detection Techniques
- **Formal Inspection**: Structured review with roles, checklists, preparation. 45-70% detection rate.
- **Walk-Through**: Author-led review, less structured. 20-40% detection rate.
- **Pair Programming**: Real-time collaborative development. 40-60% detection rate.
- **Code Reading**: Individual review emphasizing preparation. 20-35% detection rate.
- **Unit Testing**: Developer tests of individual components. 15-50% detection rate.

### Clean vs Dirty Tests
- **Clean tests**: Verify code works correctly (happy path)
- **Dirty tests**: Verify code handles failures gracefully (error paths, bad data, edge cases)

**Critical ratio:** Mature organizations have 5 dirty tests for every 1 clean test. Immature organizations have the inverse.

### Psychological Set
The tendency to see what you expect to see. Causes "debugging blindness" where programmers overlook defects because they expect code to work. Good formatting, naming, and comments help break psychological set by making anomalies stand out.

## Modes

### CHECKER
Purpose: Execute quality, review, and testing checklists against code/process
Triggers:
  - "review this code"
  - "check quality practices"
  - "are my test cases adequate"
Non-Triggers:
  - "how do I debug this" → APPLIER
  - "write tests for this" → APPLIER
Checklists:
  - **[QA & Testing]($CLAUDE_PLUGIN_ROOT/skills/cc-quality-practices/checklists/qa-and-testing.md)** — QA plan, inspections, test cases, data-flow
  - **[Debugging]($CLAUDE_PLUGIN_ROOT/skills/cc-quality-practices/checklists/debugging.md)** — finding, fixing, brute-force, general approach
Output Format:
  | Item | Status | Evidence | Location |
  |------|--------|----------|----------|
Severity:
  - VIOLATION: Fails checklist item
  - WARNING: Partial compliance
  - PASS: Meets requirement

### APPLIER
Purpose: Apply testing techniques, inspection procedures, and debugging method
Triggers:
  - "debug this issue"
  - "design test cases for"
  - "how should we review this"
Non-Triggers:
  - "check my test coverage" → CHECKER
  - "review my QA plan" → CHECKER
Produces: Test cases, debugging hypotheses, review procedures, quality plans

**Test Case Generation (output: test case list):**
1. Identify requirements → write test per requirement
2. Compute minimum tests: 1 + count(if/while/for/and/or)
3. Add data-flow tests: cover all defined-used paths
4. Add boundary tests: below, at, above each boundary
5. Add dirty tests (5:1 ratio): bad data, wrong size, uninitialized
6. Add nominal tests: middle-of-road expected values

**Debugging Method (Scientific) - output: hypothesis + fix:**
1. STABILIZE - Narrow to simplest failing test case
2. HYPOTHESIZE - Form theory from all available data
3. EXPERIMENT - Design test to prove/disprove hypothesis **WITHOUT changing production code**
4. PROVE/DISPROVE - Run test; refine hypothesis if disproved
5. FIX - Only after predicting defect occurrence correctly
6. VERIFY - Re-run original test + regression suite
7. SEARCH - Check same file, same developer, same pattern for similar defects

**Critical clarification on EXPERIMENT:** EXPERIMENT means a test that validates or invalidates your hypothesis WITHOUT changing production code. Examples: add logging/print statements, use a debugger to inspect state, write a failing unit test that exposes the suspected bug, inspect code to verify your theory. If you change production code, you've skipped to FIX—which has a >50% failure rate when done without understanding [Yourdon]. The experiment confirms your understanding; the fix applies it.

**Inspection Procedure (output: defect list) - see [Effective Inspections checklist]($CLAUDE_PLUGIN_ROOT/skills/cc-quality-practices/checklists/qa-and-testing.md):**
1. PLANNING - Moderator distributes materials with line numbers + checklist
2. PREPARATION - Each reviewer works alone using checklist (90% defects found here)
3. MEETING - Reader paraphrases code; scribe records defects (≤2 hours)
4. REPORT - Moderator lists each defect with type and severity
5. REWORK - Author fixes defects
6. FOLLOW-UP - Moderator verifies all fixes complete

## Decision Flowcharts

### Choosing a Review Method

```dot
digraph review_method {
    rankdir=TB;
    node [shape=box];

    START [label="Need to review code" shape=doublecircle];
    formal [label="Need highest\ndefect detection?\n(45-70%)" shape=diamond];
    inspection [label="FORMAL INSPECTION\n• Defined roles\n• Checklists required\n• Preparation mandatory" style=filled fillcolor=lightblue];
    dispersed [label="Team geographically\ndispersed?" shape=diamond];
    codereading [label="CODE READING\n• Individual preparation\n• Minimal meeting\n• Async-friendly" style=filled fillcolor=lightgreen];
    schedule [label="Schedule pressure\n+ need quality?" shape=diamond];
    pairing [label="PAIR PROGRAMMING\n• Real-time review\n• 45% schedule reduction\n• Continuous feedback" style=filled fillcolor=lightyellow];
    diverse [label="Need diverse\nviewpoints?" shape=diamond];
    walkthrough [label="WALK-THROUGH\n• Author-led\n• Larger groups OK\n• Less structured" style=filled fillcolor=lightyellow];
    default [label="Default:\nFORMAL INSPECTION" style=filled fillcolor=lightblue];

    START -> formal;
    formal -> inspection [label="yes"];
    formal -> dispersed [label="no"];
    dispersed -> codereading [label="yes"];
    dispersed -> schedule [label="no"];
    schedule -> pairing [label="yes"];
    schedule -> diverse [label="no"];
    diverse -> walkthrough [label="yes"];
    diverse -> default [label="no"];
}
```

**Key data:** Inspections find 45-70% of defects; walk-throughs find 20-40%. Preparation finds 90% of inspection defects; the meeting only finds 10% more [Votta 1991].

### Test Strategy Selection

```dot
digraph test_strategy {
    rankdir=TB;
    node [shape=box];

    START [label="Design test cases" shape=doublecircle];
    reqs [label="Requirements\ntests defined?" shape=diamond];
    reqstep [label="1. REQUIREMENTS TESTS\nOne test per requirement\nInclude security, storage,\ninstallation, reliability" style=filled fillcolor=lightcoral];
    design [label="Design tests\ndefined?" shape=diamond];
    designstep [label="2. DESIGN TESTS\nOne test per design element\nTest interfaces, data flows" style=filled fillcolor=lightyellow];
    basis [label="Basis testing\ncomputed?" shape=diamond];
    basisstep [label="3. BASIS TESTING\nMinimum = 1 + count of:\nif, while, for, and, or\nPlus case branches" style=filled fillcolor=lightgreen];
    dataflow [label="Data-flow paths\ncovered?" shape=diamond];
    dataflowstep [label="4. DATA-FLOW TESTS\nTest all defined-used paths\nCheck: defined-defined,\ndefined-exited, killed-used" style=filled fillcolor=lightblue];
    dirty [label="Dirty tests\nadded? (5:1 ratio)" shape=diamond];
    dirtystep [label="5. DIRTY TESTS\n• Too little/much data\n• Wrong kind/size\n• Uninitialized data\n• Boundary violations" style=filled fillcolor=plum];
    complete [label="TEST SUITE COMPLETE\nRun with coverage monitor\nActual vs believed coverage" style=filled fillcolor=lightgray];

    START -> reqs;
    reqs -> reqstep [label="no"];
    reqs -> design [label="yes"];
    reqstep -> design;
    design -> designstep [label="no"];
    design -> basis [label="yes"];
    designstep -> basis;
    basis -> basisstep [label="no"];
    basis -> dataflow [label="yes"];
    basisstep -> dataflow;
    dataflow -> dataflowstep [label="no"];
    dataflow -> dirty [label="yes"];
    dataflowstep -> dirty;
    dirty -> dirtystep [label="no"];
    dirty -> complete [label="yes"];
    dirtystep -> complete;
}
```

**Basis testing formula:** Minimum test cases = `1 + count(if) + count(while) + count(for) + count(and) + count(or) + count(case branches)`. If no default case, add 1 more.

### Scientific Debugging Method

```dot
digraph debugging {
    rankdir=TB;
    node [shape=box];

    START [label="Error reported" shape=doublecircle];
    intermittent [label="Error occurs\nreliably?" shape=diamond];
    stabilize [label="1. STABILIZE\n• Find simplest failing case\n• Remove irrelevant factors\n• Make 100% reproducible" style=filled fillcolor=lightcoral];
    hypothesis [label="2. HYPOTHESIZE\n• Use ALL available data\n• What could cause this?\n• Check recent changes" style=filled fillcolor=lightyellow];
    experiment [label="3. DESIGN EXPERIMENT\n• How to prove/disprove?\n• WITHOUT changing code\n• Add logging/debugger/test" style=filled fillcolor=lightgreen];
    test [label="4. RUN TEST" style=filled fillcolor=lightblue];
    proved [label="Hypothesis\nproved?" shape=diamond];
    fix [label="5. FIX DEFECT\n• Fix root cause, not symptom\n• One change at a time\n• Be confident before changing" style=filled fillcolor=plum];
    verify [label="6. VERIFY FIX\n• Re-run original test\n• Run regression suite\n• Add test to prevent regression" style=filled fillcolor=lightblue];
    search [label="7. SEARCH FOR SIMILAR\n• Same file\n• Same developer\n• Same pattern\n• Same assumption" style=filled fillcolor=lightgray];
    refine [label="Refine hypothesis\nwith new data" style=filled fillcolor=lightyellow];
    timelimit [label="Time limit\nexceeded?" shape=diamond];
    bruteforce [label="BRUTE FORCE\n• Full code review\n• Rewrite section\n• Binary search\n• Instrument heavily" style=filled fillcolor=lightcoral];

    START -> intermittent;
    intermittent -> stabilize [label="no"];
    intermittent -> hypothesis [label="yes"];
    stabilize -> hypothesis;
    hypothesis -> experiment;
    experiment -> test;
    test -> proved;
    proved -> fix [label="yes"];
    proved -> timelimit [label="no"];
    timelimit -> bruteforce [label="yes"];
    timelimit -> refine [label="no"];
    refine -> hypothesis;
    fix -> verify;
    verify -> search;
}
```

**Critical:** Do NOT skip to FIX without completing steps 1-4. ~50% of defect corrections are wrong the first time [Yourdon 1986b]. Understand the problem before fixing.

**Debugging blindness:** Programmers mentally "slice away" code they think is irrelevant. Sometimes the defect is in the sliced-away portion. If stuck, expand your search area.

---

## Chain

| After | Next |
|-------|------|
| Defect found | cc-refactoring-guidance |
| Design issues | cc-routine-and-class-design (CHECKER) |
| Fix verified | SEARCH for similar defects, then done |

