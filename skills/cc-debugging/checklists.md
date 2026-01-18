# cc-debugging - Checklists

Source: Code Complete 2nd Edition, Chapter 23 (pp. 559-560)

---

## Techniques for Finding Defects

- [ ] Use all the data available to make your hypothesis
- [ ] Refine the test cases that produce the error
- [ ] Exercise the code in your unit test suite
- [ ] Use available tools (debugger, profiler, lint)
- [ ] Reproduce the error several different ways
- [ ] Generate more data to generate more hypotheses
- [ ] Use the results of negative tests (what DOESN'T cause it?)
- [ ] Brainstorm for possible hypotheses
- [ ] Keep a notepad by your desk, and make a list of things to try
- [ ] Narrow the suspicious region of the code (binary search)
- [ ] Be suspicious of classes and routines that have had defects before
- [ ] Check code that's changed recently
- [ ] Expand the suspicious region of the code (if narrowing fails)
- [ ] Integrate incrementally (isolate the change that broke it)
- [ ] Check for common defects (off-by-one, null pointer, etc.)
- [ ] Talk to someone else about the problem (confessional debugging)
- [ ] Take a break from the problem
- [ ] Set a maximum time for quick and dirty debugging
- [ ] Make a list of brute-force techniques, and use them

---

## Techniques for Syntax Errors

- [ ] Don't trust line numbers in compiler messages
- [ ] Don't trust compiler messages (read between the lines)
- [ ] Don't trust the compiler's second message (fix first error, recompile)
- [ ] Divide and conquer (remove part of code, compile again)
- [ ] Use a syntax-directed editor to find misplaced comments and quotation marks

---

## Techniques for Fixing Defects

- [ ] Understand the problem before you fix it
- [ ] Understand the program, not just the problem (vicinity = hundreds of lines)
- [ ] Confirm the defect diagnosis (rule out competing hypotheses)
- [ ] Relax (take a break if rushing)
- [ ] Save the original source code
- [ ] Fix the problem, not the symptom (no special-case workarounds)
- [ ] Change the code only for good reason (be confident it will work)
- [ ] Make one change at a time
- [ ] Check your fix (test triangulation cases)
- [ ] Add a unit test that exposes the defect (prevents regression)
- [ ] Look for similar defects (defects cluster)

---

## General Approach to Debugging

- [ ] Do you use debugging as an opportunity to learn more about your program, mistakes, code quality, and problem-solving approach?
- [ ] Do you avoid the trial-and-error, superstitious approach to debugging?
- [ ] Do you assume that errors are your fault?
- [ ] Do you use the scientific method to stabilize intermittent errors?
- [ ] Do you use the scientific method to find defects?
- [ ] Rather than using the same approach every time, do you use several different techniques to find defects?
- [ ] Do you verify that the fix is correct?
- [ ] Do you use compiler warning messages, execution profiling, a test framework, scaffolding, and interactive debugging?

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

- [ ] Perform a full design and/or code review on the broken code
- [ ] Throw away the section of code and redesign/recode from scratch
- [ ] Throw away the whole program and redesign/recode from scratch
- [ ] Compile code with full debugging information
- [ ] Compile code at pickiest warning level and fix all picky warnings
- [ ] Strap on a unit test harness and test the new code in isolation
- [ ] Create an automated test suite and run it all night
- [ ] Step through a big loop in the debugger manually until you get to the error condition
- [ ] Instrument the code with print, display, or other logging statements
- [ ] Compile the code with a different compiler
- [ ] Compile and run the program in a different environment
- [ ] Link or run against special libraries that produce warnings when code is used incorrectly
- [ ] Replicate the end-user's full machine configuration
- [ ] Integrate new code in small pieces, fully testing each piece

---

## Common Defect Checklist

Quick checks for common bugs:

- [ ] Off-by-one errors (loop bounds, array indices)
- [ ] Null/undefined references
- [ ] Uninitialized variables
- [ ] Use-after-free / dangling pointers
- [ ] Race conditions (timing-dependent behavior)
- [ ] Integer overflow/underflow
- [ ] Incorrect operator precedence
- [ ] String encoding issues (UTF-8, etc.)
- [ ] Floating-point comparison (use epsilon)
- [ ] Incorrect type conversions
- [ ] Resource leaks (memory, file handles, connections)
- [ ] Logic inversion (wrong branch taken)

---

## Debugging Time Limits

| Phase | Max Time | Action If Exceeded |
|-------|----------|-------------------|
| Quick-and-dirty | 15-30 min | Switch to systematic |
| Single hypothesis | 30-60 min | Generate new hypotheses |
| Systematic debugging | 2-4 hours | Take break, talk to colleague |
| Same bug, multiple days | N/A | Consider brute-force rewrite |
