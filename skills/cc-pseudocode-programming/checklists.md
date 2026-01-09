# Checklists: Pseudocode Programming Process

Source: Code Complete 2nd Edition, pp. 233-234

---

## Checklist: The Pseudocode Programming Process

### Prerequisites
- [ ] Have you checked that the prerequisites have been satisfied?
- [ ] Have you defined the problem that the class will solve?

### Design Quality
- [ ] Is the high-level design clear enough to give the class and each of its routines a good name?
- [ ] Have you thought about how to test the class and each of its routines?
- [ ] Have you checked the standard libraries and other code libraries for applicable routines or components?
- [ ] Have you checked reference books for helpful algorithms?

### Pseudocode Quality
- [ ] Have you designed each routine by using detailed pseudocode?
- [ ] Have you mentally checked the pseudocode? Is it easy to understand?
- [ ] Is the pseudocode at the right level of detail (not too high, not language-specific)?
- [ ] Is the pseudocode language-independent (no target language syntax)?

### Implementation
- [ ] Did you translate the pseudocode to code accurately?
- [ ] Did you apply the PPP recursively, breaking routines into smaller routines when needed?
- [ ] Have you chosen the best of several iterations, rather than merely stopping after your first iteration?

### Understanding
- [ ] Do you thoroughly understand your code? Is it easy to understand?
- [ ] Can you explain why the code works (not just that it works)?

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

Total checklist items: 15
