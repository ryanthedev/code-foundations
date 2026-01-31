# Checklists: Pseudocode Programming Process

Source: Code Complete 2nd Edition, pp. 233-234

---

## Prerequisites

- [ ] PR-1: "Have you checked that the prerequisites have been satisfied?"
- [ ] PR-2: "Have you defined the problem that the class will solve?" → Red flag: Fuzzy requirements

---

## Design Quality

- [ ] DQ-1: "Is the high-level design clear enough to give the class and each of its routines a good name?" → Red flag: If naming is hard, design is unclear
- [ ] DQ-2: "Have you thought about how to test the class and each of its routines?" (Good: Test plan exists, Bad: "I'll figure it out later")
- [ ] DQ-3: "Have you checked the standard libraries and other code libraries for applicable routines or components?" → Red flag: Reinventing the wheel
- [ ] DQ-4: "Have you checked reference books for helpful algorithms?" → Red flag: Guessing at approach

---

## Pseudocode Quality

- [ ] PQ-1: "Have you designed each routine by using detailed pseudocode?"
- [ ] PQ-2: "Have you mentally checked the pseudocode? Is it easy to understand?"
- [ ] PQ-3: "Is the pseudocode at the right level of detail?" (Good: Level of intent, Bad: Too high-level or language-specific)
- [ ] PQ-4: "Is the pseudocode language-independent?" → Red flag: Target language syntax in pseudocode

---

## Implementation

- [ ] IM-1: "Did you translate the pseudocode to code accurately?" (Good: Pseudocode becomes comments, Bad: Comments diverge from code)
- [ ] IM-2: "Did you apply the PPP recursively, breaking routines into smaller routines when needed?"
- [ ] IM-3: "Have you chosen the best of several iterations?" → Red flag: Stopping after first iteration only
- [ ] IM-4: "Did you compile clean with ALL warnings eliminated?" → Red flag: "Warnings don't matter" attitude

---

## Understanding

- [ ] UN-1: "Do you thoroughly understand your code? Is it easy to understand?"
- [ ] UN-2: "Can you explain WHY the code works, not just that it works?" → Red flag: Works but mysterious

---

## Quick Reference: PPP Process Steps

| Step | Key Question | Red Flag |
|------|--------------|----------|
| 1. Check prerequisites | Is routine's place in design clear? | Vague responsibilities |
| 2. Define problem | Inputs, outputs, pre/postconditions? | Fuzzy requirements |
| 3. Name routine | Is naming easy? | Naming is hard → design unclear |
| 4. Plan testing | How will you verify? | "I'll figure it out later" |
| 5. Check libraries | Does this exist already? | Reinventing the wheel |
| 6. Plan error handling | What can go wrong? | No failure modes identified |
| 7. Research algorithms | Is algorithm well understood? | Guessing at approach |
| 8. Write pseudocode | English-like, level of intent? | Target language syntax |
| 9. Iterate pseudocode | Is code generation automatic? | Too high-level |
| 10. Try alternatives | Did you consider other approaches? | First design only |
| 11. Code from pseudocode | Pseudocode becomes comments? | Comments diverge from code |
| 12. Compile clean | ALL warnings eliminated? | "Warnings don't matter" |

---

## Warning Signs That PPP Would Help

Use PPP when you experience any of these symptoms:

| Symptom | What It Means |
|---------|---------------|
| **Coded into a corner** | Logic is tangled, hard to extend - design wasn't thought through |
| **Lost train of thought** | Forgot where you were going - pseudocode would have kept you on track |
| **Forgot to write part** | Missing functionality discovered later - incomplete design |
| **Staring at screen** | Don't know where to start - need to define problem first |
| **Just One More Compile** | Endless compile-debug loop - coding before understanding |
| **Can't name it** | No clear, simple name works - routine has unclear purpose |
| **Works but mysterious** | Don't understand why it works - probably doesn't really work |
| **Too many warnings** | Compiler complaints piling up - hasty, unconsidered code |

---

## Minimum Viable PPP (Time-Constrained)

When full PPP is impractical, these 4 items are MANDATORY:

| # | Check | Time |
|---|-------|------|
| 1 | Can you name the routine clearly? | 15 sec |
| 2 | Write at least 3 lines of pseudocode | 2 min |
| 3 | Consider one alternative approach | 1 min |
| 4 | Convince yourself it's correct before compiling | 30 sec |

**Total: ~4 minutes** - This is the floor, not the ceiling.

---

## Red Flags

- [ ] RF-1: "Coded into a corner?" - Logic tangled, hard to extend → Design wasn't thought through
- [ ] RF-2: "Endless compile-debug loop?" - Just One More Compile syndrome → Coding before understanding
- [ ] RF-3: "Mysterious code?" - Works but you don't know why → Probably doesn't really work
- [ ] RF-4: "Can't name routine?" - No clear name works → Routine has unclear purpose
- [ ] RF-5: "Pseudocode has target language syntax?" - `for i in range()` instead of `for each item` → Too low-level
- [ ] RF-6: "Skipped alternative approaches?" - First design only → Missing potentially better solutions
- [ ] RF-7: "Comments diverge from code?" - Pseudocode comments don't match implementation → Translation failed
- [ ] RF-8: "Ignoring compiler warnings?" - "Warnings don't matter" attitude → Hasty, unconsidered code
- [ ] RF-9: "No test plan?" - "I'll figure it out later" → Will lead to untestable code
- [ ] RF-10: "Reinventing the wheel?" - Didn't check libraries → Wasting time on solved problems

---

Total items: 26
