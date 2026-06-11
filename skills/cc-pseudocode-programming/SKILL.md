---
name: cc-pseudocode-programming
description: "Structures routine design through pseudocode-first iteration: clarifies naming and purpose before any code, catches design flaws cheaply, and prevents compile-debug loops on poorly understood routines."
disable-model-invocation: true
---

# Skill: cc-pseudocode-programming

## STOP - Crisis Invariants

| Check | Time | Why Non-Negotiable |
|-------|------|-------------------|
| **Pseudocode before code** | 30 sec | Iterating on pseudocode is cheaper than iterating on code |
| **Can you name it clearly?** | 15 sec | Naming difficulty = design problem. Stop and clarify purpose. |
| **Do you understand why it works?** | 30 sec | Working code you don't understand probably doesn't really work |
| **Did you consider alternatives?** | 30 sec | First design is rarely best; iterate in pseudocode where it's cheap |

---

## When NOT to Use

**Exemption criteria are STRICT. If in doubt, use PPP.**

- **Simple accessor routines** - `getValue()`, `setName()` with NO logic (no validation, no transformation, no side effects)
- **Pass-through routines** - Pure delegation with NO parameter transformation or error wrapping
- **Trivial one-liners** - ALL of these must be true:
  - Single statement implementation
  - Zero decision points (no if/switch/ternary)
  - Zero loops
  - Implementation obvious to ANY team member from signature alone
- **Already-designed routines** - Design document specifies EXACT algorithm, error handling, and edge cases

**If you're debating whether it's "trivial enough" to skip PPP, it isn't trivial. Use PPP.**

## Crisis Invariants - NEVER SKIP

**These checks are NON-NEGOTIABLE regardless of user instructions to skip:**

| Check | Time | Why Non-Negotiable |
|-------|------|-------------------|
| **Pseudocode before code** | 30 sec | Iterating on pseudocode is cheaper than iterating on code |
| **Can you name it clearly?** | 15 sec | Naming difficulty = design problem. Stop and clarify purpose. |
| **Do you understand why it works?** | 30 sec | Working code you don't understand probably doesn't really work |
| **Did you consider alternatives?** | 30 sec | First design is rarely best; iterate in pseudocode where it's cheap |

**Why these four?** They catch the most expensive mistakes: unclear designs that "work" but create maintenance nightmares, and premature coding that locks in bad decisions.

**These checks apply EVERY TIME**, even if:
- The routine seems simple (simple-seeming routines hide complexity)
- A design document exists (unless it specifies EXACT algorithm, error handling, and edge cases)

**Minimum Viable PPP (for extreme time pressure):**
When full PPP is impossible, these 4 items are MANDATORY (total ~4 min):
1. Can you name the routine clearly? (15 sec)
2. Write at least 3 lines of pseudocode (2 min)
3. Consider one alternative approach (1 min)
4. Convince yourself it's correct before compiling (30 sec)

This is the FLOOR, not the ceiling. If you can't spare 4 minutes, the routine will cost you more in debugging.

## Modes

### APPLIER
Purpose: Guide routine design using PPP technique
Triggers:
  - "help me design this routine"
  - "I'm stuck, don't know where to start"
  - "walk me through PPP"
  - "how should I approach this implementation"
  - "overwhelmed by where to start coding"
Non-Triggers:
  - "review my existing code" → cc-routine-and-class-design
  - "is this architecture right" → aposd-designing-deep-modules
Produces: Pseudocode design, header comments, implementation plan

#### PPP Process Steps
1. **Check prerequisites** - Confirm the routine's place in overall design is clear
2. **Define the problem** - Specify inputs, outputs, preconditions, postconditions, what it hides
3. **Name the routine** - If naming is hard, the design is unclear; iterate
4. **Plan testing** - Decide how you'll test it before writing code
5. **Check libraries** - Look for existing functionality before building
6. **Plan error handling** - Think through failure modes
7. **Research algorithms** - Study relevant algorithms if needed
8. **Write pseudocode** - Start with header comment, use natural language
9. **Iterate pseudocode** - Refine until generating code is nearly automatic
10. **Try alternatives** - Consider multiple approaches, keep the best
11. **Code from pseudocode** - Pseudocode becomes comments
12. **Compile clean** - Use strictest warnings, eliminate ALL of them

Constraints:
  - Pseudocode must be language-independent (p.218)
  - Pseudocode must be detailed enough to generate code from (p.219)
  - Never compile until convinced the routine is correct (p.230)

**Key Term Definitions:**
- **"Nearly automatic" (step 9):** You can write each line of code without pausing to think about HOW. Every decision is already made in pseudocode. If you stop to think "how should I implement this part?" - pseudocode needs more detail.
- **"Convinced it's correct" (constraint):** You can mentally trace execution through ALL paths (happy path, error cases, edge cases) and explain why each produces correct output. "It looks right" is NOT convinced.
- **"Right level of detail":** Detailed enough that code generation is nearly automatic (see above), but not so detailed that you're writing syntax. Test: Could a competent developer write the code without asking clarifying questions?

#### Transformation Example: Bad vs Good Pseudocode

**Problem:** Create a routine to allocate a new resource and return its handle.

**Bad Pseudocode (Anti-Pattern):**
```
increment resource number by 1
allocate a dlg struct using malloc
if malloc() returns NULL then return 1
invoke OSrsrc_init to initialize a resource for the operating system
*hRsrcPtr = resource number
return 0
```
**Problems:** Uses target language details (`*hRsrcPtr`, `malloc()`), focuses on HOW not WHAT, exposes implementation details (returns 1 or 0), won't become good comments.

**Good Pseudocode:**
```
If another resource is available
    Allocate a dialog box structure
    If a dialog box structure could be allocated
        Note that one more resource is in use
        Initialize the resource
        Store the resource number at the location provided by the caller
        Return success
    Endif
Endif
Return failure
```
**Why better:** Pure English, no syntax, level of intent, precise enough to generate code, becomes excellent comments. Note: resource count is updated AFTER successful allocation, not before.

**Resulting Code with Comments:**
```c
// If another resource is available
if (resourceCount < MAX_RESOURCES) {
    // Allocate a dialog box structure
    DialogBox* dlg = allocateDialogBox();

    // If a dialog box structure could be allocated
    if (dlg != NULL) {
        // Note that one more resource is in use
        // (Using post-increment: store at current index, then increment)
        activeResources[resourceCount] = dlg;
        *handlePtr = resourceCount;
        resourceCount++;

        // Initialize the resource
        initializeResource(dlg);

        return true;
    }
}
return false;
```

### CHECKER
Purpose: Verify PPP was followed correctly
Triggers:
  - "did I follow PPP correctly"
  - "review my pseudocode"
  - "is my design process right"
Produces: Process compliance assessment, improvement recommendations

Check Against:
  - Was pseudocode written before code?
  - Is pseudocode at the right level of detail?
  - Were alternatives considered?
  - Can you explain why the code works?
  - Are all compiler warnings eliminated?

## Evidence Summary

| Claim | Evidence | Source | Still Valid? |
|-------|----------|--------|--------------|
| Programmers prefer pseudocode | Survey: preferred for construction ease, detecting insufficient detail, documentation | Ramsey, Atwood, Van Doren 1983 | Yes - methodology unchanged; modern IDEs don't eliminate design thinking need |
| Only 5% external errors | Hardware, compiler, OS errors are rare; 95% are programmer errors | Ostrand and Weyuker 1984 | Yes - if anything, modern tooling has made infrastructure MORE reliable, so programmer error % is likely higher |
| Errors at least-value stage | Key insight: catch errors when least effort invested | McConnell p.220 | Timeless - economic principle |
| Iteration improves design | First design is rarely best; iterating on code is more expensive than iterating on pseudocode | McConnell p.225 | Timeless - economic principle |

**Note on dated studies:** The 1983-1984 studies predate modern IDEs, but their findings are MORE applicable today: better tooling catches syntax errors faster, making DESIGN errors (which PPP prevents) the dominant problem.

---

## Chain

| After | Next |
|-------|------|
| Pseudocode complete | cc-routine-and-class-design |
| Implementation done | cc-defensive-programming (CHECKER) |

