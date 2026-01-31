# cc-debugging - Checklists

Source: Code Complete 2nd Edition, Chapter 23 (pp. 559-560)

---

## Techniques for Finding Defects

- [ ] FD-1: "Did you use all available data to make your hypothesis?" → Red flag: Guessing without examining logs, variables, stack traces
- [ ] FD-2: "Did you refine the test cases that produce the error?" (Good: Minimal repro case, Bad: Only testing in full app context)
- [ ] FD-3: "Did you exercise the code in your unit test suite?"
- [ ] FD-4: "Did you use available tools?" (debugger, profiler, lint)
- [ ] FD-5: "Did you reproduce the error several different ways?" → Reveals root cause vs symptoms
- [ ] FD-6: "Did you generate more data to generate more hypotheses?"
- [ ] FD-7: "Did you use the results of negative tests?" (what DOESN'T cause it?)
- [ ] FD-8: "Did you brainstorm for possible hypotheses?"
- [ ] FD-9: "Did you keep a notepad and make a list of things to try?" → Prevents circular debugging
- [ ] FD-10: "Did you narrow the suspicious region of the code?" (binary search)
- [ ] FD-11: "Were you suspicious of classes and routines that have had defects before?" → Defects cluster
- [ ] FD-12: "Did you check code that's changed recently?"
- [ ] FD-13: "Did you expand the suspicious region if narrowing failed?"
- [ ] FD-14: "Did you integrate incrementally to isolate the change that broke it?"
- [ ] FD-15: "Did you check for common defects?" (off-by-one, null pointer, etc.)
- [ ] FD-16: "Did you talk to someone else about the problem?" (confessional debugging)
- [ ] FD-17: "Did you take a break from the problem?" → Fresh eyes prevent tunnel vision
- [ ] FD-18: "Did you set a maximum time for quick and dirty debugging?" (Good: 15-30 min limit, Bad: Hours of random changes)
- [ ] FD-19: "Did you make a list of brute-force techniques and use them?"

---

## Techniques for Syntax Errors

- [ ] SE-1: "Did you distrust line numbers in compiler messages?" → Error often 1-5 lines earlier
- [ ] SE-2: "Did you read between the lines of compiler messages?" (Good: Understand root cause, Bad: Trust cryptic message literally)
- [ ] SE-3: "Did you fix only the first error and recompile?" → Later errors often spurious cascades
- [ ] SE-4: "Did you divide and conquer?" (remove part of code, compile again)
- [ ] SE-5: "Did you use a syntax-directed editor to find misplaced comments and quotation marks?"

---

## Techniques for Fixing Defects

- [ ] FF-1: "Did you understand the problem before fixing it?" → Red flag: Applying fixes without diagnosis
- [ ] FF-2: "Did you understand the program vicinity?" (hundreds of lines, not just the error line)
- [ ] FF-3: "Did you confirm the defect diagnosis?" (rule out competing hypotheses)
- [ ] FF-4: "Did you relax if you were rushing?" → Red flag: Panic-driven debugging
- [ ] FF-5: "Did you save the original source code?"
- [ ] FF-6: "Did you fix the problem, not the symptom?" (Good: Root cause fix, Bad: Special-case workarounds)
- [ ] FF-7: "Did you change the code only for good reason?" → Red flag: Superstitious changes
- [ ] FF-8: "Did you make one change at a time?" (Good: Single variable experiment, Bad: Shotgun debugging)
- [ ] FF-9: "Did you check your fix with triangulation test cases?"
- [ ] FF-10: "Did you add a unit test that exposes the defect?" → Prevents regression
- [ ] FF-11: "Did you look for similar defects?" → Defects cluster; if one bug exists, similar ones likely nearby

---

## General Approach to Debugging

- [ ] GA-1: "Do you use debugging as an opportunity to learn?" (program structure, mistakes, code quality, problem-solving)
- [ ] GA-2: "Do you avoid the trial-and-error, superstitious approach?" → Red flag: Random code changes hoping something works
- [ ] GA-3: "Do you assume that errors are your fault?" (Good: Own the bug, Bad: Blame compiler/library/hardware)
- [ ] GA-4: "Do you use the scientific method to stabilize intermittent errors?"
- [ ] GA-5: "Do you use the scientific method to find defects?" (hypothesis → experiment → prove/disprove)
- [ ] GA-6: "Do you use several different techniques?" → Red flag: Using same failed approach repeatedly
- [ ] GA-7: "Do you verify that the fix is correct?" (triangulation + regression tests)
- [ ] GA-8: "Do you use all available tools?" (compiler warnings, execution profiling, test framework, scaffolding, interactive debugging)

---

## Quick Reference: Scientific Debugging Steps

| Step | Action | Checkpoint |
|------|--------|------------|
| 1 | **STABILIZE** the error | Can reproduce reliably? |
| 2 | Form **HYPOTHESIS** | Based on actual data? |
| 3 | Design **EXPERIMENT** | How will you prove/disprove? |
| 4 | **PROVE/DISPROVE** | Run experiment, record result |
| 5 | **FIX** the defect | Root cause, not symptom? |
| 6 | **TEST** the fix | Triangulation + regression? |
| 7 | **SEARCH** for similar | Check clusters? |

---

## Brute-Force Techniques Checklist

When systematic approaches fail, use these guaranteed (but tedious) methods:

- [ ] BF-1: "Did you perform a full design and/or code review on the broken code?"
- [ ] BF-2: "Did you consider throwing away the section and redesigning/recoding from scratch?"
- [ ] BF-3: "Did you consider throwing away the whole program and redesigning/recoding from scratch?"
- [ ] BF-4: "Did you compile code with full debugging information?"
- [ ] BF-5: "Did you compile at pickiest warning level and fix all warnings?"
- [ ] BF-6: "Did you strap on a unit test harness and test the code in isolation?"
- [ ] BF-7: "Did you create an automated test suite and run it extensively?"
- [ ] BF-8: "Did you step through a big loop in the debugger manually?"
- [ ] BF-9: "Did you instrument the code with print, display, or other logging statements?"
- [ ] BF-10: "Did you try compiling the code with a different compiler?"
- [ ] BF-11: "Did you compile and run the program in a different environment?"
- [ ] BF-12: "Did you link or run against special libraries that produce warnings?"
- [ ] BF-13: "Did you replicate the end-user's full machine configuration?"
- [ ] BF-14: "Did you integrate new code in small pieces, fully testing each piece?"

---

## Common Defect Checklist

Quick checks for common bugs:

- [ ] CD-1: "Off-by-one errors?" (loop bounds, array indices) → Red flag: Using `<=` where `<` is correct
- [ ] CD-2: "Null/undefined references?" → Red flag: Missing null checks before dereferencing
- [ ] CD-3: "Uninitialized variables?"
- [ ] CD-4: "Use-after-free / dangling pointers?"
- [ ] CD-5: "Race conditions?" (timing-dependent behavior)
- [ ] CD-6: "Integer overflow/underflow?"
- [ ] CD-7: "Incorrect operator precedence?" (Good: Use parentheses for clarity, Bad: Rely on memorized precedence)
- [ ] CD-8: "String encoding issues?" (UTF-8, etc.)
- [ ] CD-9: "Floating-point comparison?" → Red flag: Using `==` instead of epsilon comparison
- [ ] CD-10: "Incorrect type conversions?"
- [ ] CD-11: "Resource leaks?" (memory, file handles, connections)
- [ ] CD-12: "Logic inversion?" (wrong branch taken) → Red flag: Inverted conditional logic

---

## Debugging Time Limits

| Phase | Max Time | Action If Exceeded |
|-------|----------|-------------------|
| Quick-and-dirty | 15-30 min | Switch to systematic |
| Single hypothesis | 30-60 min | Generate new hypotheses |
| Systematic debugging | 2-4 hours | Take break, talk to colleague |
| Same bug, multiple days | N/A | Consider brute-force rewrite |

---

## Red Flags

- [ ] RF-1: "Shotgun debugging?" - Random code changes without hypothesis → Use scientific method: stabilize, hypothesize, experiment
- [ ] RF-2: "Superstitious debugging?" - Trying same failed approach repeatedly → Switch techniques, use different tools
- [ ] RF-3: "Symptom fixing?" - Special-case workarounds instead of root cause → Understand the problem before fixing
- [ ] RF-4: "Panic debugging?" - Rushing, making multiple changes at once → Take a break, make one change at a time
- [ ] RF-5: "Compiler blame?" - Assuming bug is in compiler/library/hardware → Assume errors are your fault first
- [ ] RF-6: "No reproduction case?" - Can't reproduce error reliably → Stabilize error with minimal test case
- [ ] RF-7: "Circular debugging?" - Revisiting same code without new data → Keep notepad of attempts, generate more hypotheses
- [ ] RF-8: "Unfixed clusters?" - Fixed one bug without checking for similar defects → Search for related bugs in vicinity
- [ ] RF-9: "No regression test?" - Fixed bug without adding test → Add unit test that exposes the defect
- [ ] RF-10: "Incomplete diagnosis?" - Fixing without understanding program vicinity → Study hundreds of lines, not just error location

---

Total items: 99
