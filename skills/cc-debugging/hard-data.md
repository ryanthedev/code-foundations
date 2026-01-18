# cc-debugging - Evidence and Hard Data

Source: Code Complete 2nd Edition, Chapter 23 (pp. 535-562)

---

## Key Points (Author-Marked)

1. **Debugging performance varies 20-to-1** between programmers (p.536)
   - Best programmers found defects fastest, introduced fewest new bugs
   - Worst programmer missed 4 of 12 defects, introduced 11 new ones

2. **Assume errors are your fault** - helps debugging effectiveness and credibility (p.540)
   - Programs don't do something different every time
   - "Demon machines" don't exist

3. **Scientific method for debugging:** stabilize, locate, fix, test, look for similar (p.541)
   - Same method scientists use: hypothesis, experiment, prove/disprove

4. **Understand the problem before you fix it** (p.550)
   - Simply finding the defect is not enough
   - Must understand root cause

5. **Set compiler warning to pickiest level** and fix all errors (p.557)
   - "Setting a switch to turn off warnings doesn't make errors go away any more than closing your eyes makes an adult go away"

6. **Good thinking + good debugger = most effective combination** (p.559)
   - Tools are powerful aids but don't replace systematic thinking

---

## Empirical Evidence

### Gould 1975 - Debugging Performance Study
**Citation:** Gould, J. (1975). "Some Psychological Evidence on How People Debug Computer Programs." *International Journal of Man-Machine Studies*, 7, pp. 151-82.

**Key Findings:**
- Roughly 20:1 difference in time experienced programmers take to find same defects
- Best three programmers: avg 5.0 min debug time, 0.7 defects not found, 3.0 new defects introduced
- Slowest three: avg 14.1 min debug time, 1.7 defects not found, 7.7 new defects introduced
- Best programmer found ALL defects and introduced NO new defects
- Worst missed 4 of 12 defects and introduced 11 new defects while fixing 8

**Author Extrapolation:** Slowest group would take ~13x as long to fully debug as fastest group (noted as "not statistically valid" extrapolation)

### Gilb 1977, Curtis 1981 - Confirmed Performance Variation
**Citations:**
- Gilb, T. (1977). *Software Metrics*. Cambridge, MA: Winthrop.
- Curtis, B. (1981). "Substantiating Programmer Variability." *Proceedings of the IEEE*, 69(7), pp. 846.

**Key Finding:** Confirmed Gould's finding of wide variation in debugging performance across programmers.

### Yourdon 1986b - Defect Correction Error Rate
**Citation:** Yourdon, E. (1986b). *Managing the Structured Techniques*, 3d Ed. New York: Yourdon Press.

**Key Finding:** Defect corrections have more than a 50 percent chance of being wrong the first time.

**Qualifier:** "at least one study found"

**Implication:** Always verify fixes before committing. Never assume fix is correct without testing.

### Littman et al. 1986 - Program Understanding
**Citation:** Littman, D.C., et al. (1986). "Mental Models and Software Maintenance." *Proceedings of the First Workshop on Empirical Studies of Programmers*. Norwood, NJ: Ablex.

**Key Finding:** Programmers who achieve a global understanding of program behavior have better chance of modifying it successfully than those who focus on local behavior.

**Study Details:**
- Conducted with 280-line programs
- "Vicinity" of defect = ~hundreds of lines, not just the bug site

**Qualifier:** Small study - doesn't prove need to understand entire 50,000-line program

### Basili, Selby, and Hutchens 1986 - Mental Slicing
**Citation:** Basili, V.R., R.W. Selby, and D.H. Hutchens (1986). "Experimentation in Software Engineering." *IEEE Transactions on Software Engineering*, SE-12(7), pp. 733-43.

**Key Finding:** Programmers who debug most effectively mentally slice away parts of program that aren't relevant during debugging.

**Caveat:** Sometimes the part containing the defect is mistakenly sliced away.

**Good practices help:** Formatting, commenting, variable names help structure code so likely defects appear as variations and stand out.

### Weinberg 1998 - Variable Confusion
**Citation:** Weinberg, Gerald M. (1998). *The Psychology of Computer Programming*, Silver Anniversary Ed. New York: Dorset House.

**Key Finding:** A programmer unintentionally used both SYSTSTS and SYSSTSTS thinking it was single variable. Problem wasn't discovered until program had run hundreds of times and a book was written containing erroneous results.

**Implication:** Psychological distance matters in variable naming.

### Curtis et al. 1986 - While Loop Misconception
**Citation:** Curtis, B., et al. (1986). "On Building Software Process Models Under the Lamppost." *Proceedings of the 9th International Conference on Software Engineering*. Los Alamitos, CA: IEEE Computer Society.

**Key Finding:** In one study, students expected while loops to be continuously evaluated.

**Implication:** Programmers have mental models that may not match actual program execution.

---

## Anti-Patterns (CODING HORROR)

### Find Defect by Guessing
- Scatter print statements randomly throughout program
- Try changing things without backing up or keeping record
- **Why it fails:** Programming by trial and error guarantees defects

### Don't Waste Time Understanding
- Assume problem is trivial, don't need to understand it
- **Why it fails:** Simply finding a defect is not enough to fix it correctly

### Fix with Most Obvious Fix (CODING HORROR)
**Example Code:**
```java
for (claimNumber = 0; claimNumber < numClaims[client]; claimNumber++) {
    sum[client] = sum[client] + claimAmount[claimNumber];
}
// "Fix" for client 45 being off by $3.45
if (client == 45) {
    sum[45] = sum[45] + 3.45;
}
```

**Why it fails:**
1. Won't work - initialization defects are unpredictable, $3.45 today could be $10,000.02 tomorrow
2. Unmaintainable - special cases become prominent feature, barnacles sink the code
3. Wrong tool - humans are better at fudging data creatively

### Debug by Superstition
- Blame demon machines, mysterious compiler defects, hidden language defects
- **Why it fails:** If you have a problem with a program you've written, it's your fault

### Random Changes (Voodoo Programming)
- "I'll just put a -1 here and try it" without understanding why
- **Why it fails:** You learn nothing, lose confidence in the code

---

## Qualifiers and Scope

| Claim | Qualifier | Context |
|-------|-----------|---------|
| 90% of work is finding/understanding | "usually" | May vary for trivial bugs |
| Intermittent = initialization/timing/pointer | "usually" | Other causes exist |
| Defects occur in groups | "tend to" | Statistical tendency |
| 13x time difference | "not statistically valid" | Author's extrapolation |
| Littman study | Small (280 lines) | May not scale to large programs |
| 50% fixes wrong | "at least one study" | Single citation |

---

## Cross-References

| Topic | Reference | Notes |
|-------|-----------|-------|
| Pointers and dangling pointers | Section 13.2 | Common cause of intermittent bugs |
| General Principle of Software Quality | Section 20.5 | Quality reduces costs |
| Compiler warning levels | Ch 23 | Set to pickiest |
| Code reviews | Ch 21 | Alternative defect detection |
| Testing strategies | Ch 22 | Testing vs debugging distinction |
| Defensive programming | Ch 8 | Prevention is better than debugging |

---

## Debugging Performance Comparison

| Metric | Best 3 | Slowest 3 | Ratio |
|--------|--------|-----------|-------|
| Avg debug time | 5.0 min | 14.1 min | 2.8x |
| Defects not found | 0.7 | 1.7 | 2.4x |
| New defects introduced | 3.0 | 7.7 | 2.6x |

| Metric | Best Individual | Worst Individual |
|--------|-----------------|------------------|
| Defects not found | 0 | 4 of 12 |
| New defects introduced | 0 | 11 |

---

## Key Quotes

> "Debugging is twice as hard as writing the code in the first place. Therefore, if you write the code as cleverly as possible, you are, by definition, not smart enough to debug it." — Brian W. Kernighan

> "Programmers do not always use available data to constrain their reasoning. They carry out minor and irrational repairs, and they often don't undo the incorrect repairs." — Iris Vessey

> "Never debug standing up." — Gerald Weinberg

> "An interactive debugger is an outstanding example of what is not needed—it encourages trial-and-error hacking rather than systematic design, and also hides marginal people barely qualified for precision programming." — Harlan Mills
