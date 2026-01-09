# Evidence: cc-quality-practices

Source: Code Complete 2nd Edition, Chapters 20-23

## Key Points (Author's Emphasis)

| Key Point | Page | Implication |
|-----------|------|-------------|
| "The General Principle of Software Quality is that improving quality reduces development costs." | p.519 | Quality is not a cost center; it's a time/money saver |
| "Defect-detection methods work better in combination than they do singly." | p.480 | Never rely on a single technique |
| "Writing test cases before the code takes the same amount of time and effort as writing the test cases after the code, but it shortens defect-detection-debug-correction cycles." | p.506 | Test-first is free; only the sequence changes |
| "Debugging performance varies 20-to-1 between programmers." | p.536 | Systematic debugging is a learnable, high-leverage skill |
| "Errors tend to cluster in a few error-prone classes and routines." | p.512 | Focus quality efforts on the troubled 20% |

---

## Defect Detection Rates by Technique

### Table 20-2: Defect-Detection Rates [Jones 1986a, Jones 1996, Shull et al. 2002]

| Removal Step | Lowest | Modal | Highest |
|--------------|--------|-------|---------|
| Informal design reviews | 25% | 35% | 40% |
| **Formal design inspections** | 45% | 55% | 65% |
| Informal code reviews | 20% | 25% | 35% |
| **Formal code inspections** | 45% | 60% | 70% |
| Modeling or prototyping | 35% | 65% | 80% |
| Personal desk-checking of code | 20% | 40% | 60% |
| Unit test | 15% | 30% | 50% |
| New function (component) test | 20% | 30% | 35% |
| Integration test | 25% | 35% | 40% |
| Regression test | 15% | 25% | 30% |
| System test | 25% | 40% | 55% |
| Low-volume beta test (<10 sites) | 25% | 35% | 40% |
| High-volume beta test (>1,000 sites) | 60% | 75% | 85% |

**Key insights:**
- No single technique exceeds 75% modal rate
- Techniques average about 40% detection
- Unit + integration testing modal rates are only 30-35%
- Typical test-heavy organizations achieve only ~85% total removal
- Leading organizations use multiple techniques for 95%+

### Extreme Programming Estimated Detection [Table 20-3]

| XP Practice | Lowest | Modal | Highest |
|-------------|--------|-------|---------|
| Informal design reviews (pair programming) | 25% | 35% | 40% |
| Informal code reviews (pair programming) | 20% | 25% | 35% |
| Personal desk-checking | 20% | 40% | 60% |
| Unit test | 15% | 30% | 50% |
| Integration test | 25% | 35% | 40% |
| Regression test | 15% | 25% | 30% |
| **Expected cumulative efficiency** | ~74% | ~90% | ~97% |

XP achieves ~90% through combination of practices, not special synergy. Other combinations can work equally well.

---

## Review Method Comparison

### Effectiveness Comparison [Multiple sources]

| Property | Pair Programming | Formal Inspection | Walk-Through |
|----------|------------------|-------------------|--------------|
| Typical detection rate | 40-60% | 45-70% | 20-40% |
| Defined participant roles | Yes | Yes | No |
| Who "drives" | Keyboard holder | Moderator | Author |
| Process improvement data | No | Yes | No |
| Best for | Real-time feedback | Highest detection | Diverse viewpoints |

### Inspection ROI Data

| Finding | Source | Data |
|---------|--------|------|
| Time savings | Holland 1999, IBM | 1 hour inspection = 100 hours saved |
| Rework reduction | Haley 1996, Raytheon | Rework cost reduced from 40% to 20% |
| Annual savings | Grady/Van Slack 1994, HP | $21.5M/year saved |
| Maintenance savings | Russell 1991 | 1 hour inspection = 33 hours maintenance saved |
| Efficiency vs testing | Russell 1991 | Inspections 20x more efficient than testing |
| One-line changes | Freedman/Weinberg 1990 | Error rate reduced from 55% to 2% |
| ROI comparison | Collofello/Woodfield 1989 | Code reviews: 1.38 ROI vs testing: 0.17 ROI |

### 99% Defect Removal Correlation [Jones 2000]

- **All** projects achieving 99%+ defect removal used formal inspections
- **None** achieving <75% removal used formal inspections

### Where Defects Are Found [Votta 1991, AT&T]

| Phase | Defects Found |
|-------|---------------|
| Preparation (individual review) | 90% |
| Meeting | 10% |

**Implication:** Emphasize preparation time; the meeting itself is less critical.

---

## Cost of Finding and Fixing Defects

### Finding Defects

| Finding | Source | Data |
|---------|--------|------|
| Code reading vs testing | Basili/Selby 1987 | Code reading finds 80% more faults per hour |
| Design defects | Ackerman et al. 1989 | Testing costs 6x more than inspections |
| Hours per error (inspections) | Kaplan 1995, IBM | 3.5 staff hours |
| Hours per error (testing) | Kaplan 1995, IBM | 15-25 hours |
| One-step vs two-step | Moore 1992, Microsoft | Inspection: 3 hours; Testing: 12 hours to find AND fix |

### Fixing Defects

- Longer defects remain → more expensive to remove
- Inspections find symptom AND cause (one-step)
- Testing finds symptom only, requires diagnosis (two-step)
- One-step techniques substantially cheaper overall

---

## Error Distribution and Clustering

### The 80/20 Rule for Defects

| Finding | Source |
|---------|--------|
| 80% of errors in 20% of classes/routines | Endres 1975, Gremillion 1984, Boehm 1987b, Shull et al. 2002 |
| 50% of errors in 5% of classes | Jones 2000 |
| 20% of routines = 80% of development cost | Boehm 1987b |
| Error-prone routines: up to 50 defects/1000 LOC | Jones 1986a, IBM OS/360 |

### IBM IMS Case Study [Jones 2000]

- 31 of 425 classes identified as error-prone
- Classes repaired or completely redeveloped
- Results in less than one year:
  - Customer-reported defects reduced **10-to-1**
  - Total maintenance costs reduced **~45%**
  - Customer satisfaction improved from "unacceptable" to "good"
  - Productivity improved **~15%**

**Implication:** Find and fix (or rewrite) error-prone code rather than patching.

---

## Error Types Breakdown [Beizer 1990]

| Error Category | Percentage |
|----------------|------------|
| Structural | 25.18% |
| Data | 22.44% |
| Functionality as implemented | 16.19% |
| Construction | 9.88% |
| Integration | 8.98% |
| Functional requirements | 8.12% |
| Test definition or execution | 2.76% |
| System, software architecture | 1.74% |
| Unspecified | 4.71% |

**Caveat:** Different studies report wildly different results (differences of 50%+, not hundredths of a percent). Use as rough guidance only.

### Error Sources

| Finding | Source |
|---------|--------|
| 85% of errors correctable without modifying more than one routine | Endres 1975 |
| ~95% of errors are programmer's fault | Brown/Sampson 1973, Ostrand/Weyuker 1984 |
| ~2% caused by compiler/OS | Brown/Sampson 1973 |
| ~2% caused by other software | Brown/Sampson 1973 |
| ~1% caused by hardware | Brown/Sampson 1973 |
| 18-36% of errors are clerical (typos) | Weiss 1975, Card 1987 |
| 16-19% from misunderstood design | Beizer 1990, Weiss 1975 |

### Most Expensive Single-Character Errors [Weinberg 1983]

| Cost | Description |
|------|-------------|
| $1.6 billion | Single character change in previously correct program |
| $900 million | Single character change in previously correct program |
| $245 million | Single character change in previously correct program |

**Implication:** Clerical errors are not "minor." Treat typos seriously.

---

## Expected Error Rates

### By Development Approach

| Approach | In-House Testing | Released Product | Source |
|----------|------------------|------------------|--------|
| Industry average (hodgepodge) | 1-25 defects/KLOC | - | Multiple |
| Microsoft Applications Division | 10-20 defects/KLOC | 0.5 defects/KLOC | Moore 1992 |
| Cleanroom development | 3 defects/KLOC | 0.1 defects/KLOC | Cobb/Mills 1990 |
| Team Software Process (TSP) | - | 0.06 defects/KLOC | Weber 2003 |
| Space shuttle software | - | 0 defects/500KLOC | Fishman 1996 |

### Productivity Impact

| Approach | Productivity | Notes |
|----------|--------------|-------|
| Industry average | 250-300 LOC/work-month | Fully checked-out code, all overhead included |
| Cleanroom (80KLOC project) | 740 LOC/work-month | 2.5-3x industry average |

**Why the difference:** Virtually no time spent debugging in TSP/cleanroom projects.

---

## Debugging Performance

### 20:1 Variation Study [Gould 1975]

| Group | Avg Debug Time | Defects Not Found | New Defects Introduced |
|-------|----------------|-------------------|------------------------|
| Best 3 programmers | 5.0 min | 0.7 | 3.0 |
| Slowest 3 programmers | 14.1 min | 1.7 | 7.7 |

**Extreme cases:**
- Best programmer: Found all defects, introduced 0 new defects
- Worst programmer: Missed 4 of 12 defects, introduced 11 new defects while fixing 8

**Author's extrapolation:** Slowest group would take ~13x as long to fully debug as fastest group.

### Fix Success Rate [Yourdon 1986b]

- Defect corrections have **>50% chance of being wrong** the first time
- **Implication:** Always verify fixes; expect initial failure

### Program Understanding and Success [Littman et al. 1986]

- Programmers with **global understanding** of program behavior modify code more successfully
- Study with 280-line programs
- "Vicinity" of understanding = few hundred lines, not just the bug site

### Debugging Blindness [Basili, Selby, Hutchens 1986]

- Effective debuggers mentally "slice away" irrelevant code
- Risk: Sometimes the defect is in the sliced-away portion
- Good practices (formatting, comments, naming) help anomalies stand out

---

## Test Coverage Reality

### Coverage Gap [Beizer, reported in Johnson 1994]

| Metric | Developer Belief | Actual Achievement |
|--------|------------------|-------------------|
| Test coverage | 95% | 30-60% (avg 50-60%) |

### Without Coverage Monitor [Wiegers 2002]

- Testing without measurement typically exercises only **50-60%** of code

### Manual Testing Error Rate [Beizer, Johnson 1994]

- Error rate in manual testing is **comparable to bug rate in code being tested**
- Only about **half of all manual tests** are executed properly

**Implication:** Automate testing; use coverage monitors.

---

## Clean vs Dirty Test Ratio [Beizer]

| Organization Maturity | Clean:Dirty Ratio |
|----------------------|-------------------|
| Immature | 5:1 (5 clean per 1 dirty) |
| Mature | 1:5 (1 clean per 5 dirty) |

**How to improve:** Don't reduce clean tests; create **25x more dirty tests**.

Dirty tests check:
- Too little data (or no data)
- Too much data
- Wrong kind of data (invalid)
- Wrong size of data
- Uninitialized data

---

## Anti-Patterns (Documented Failures)

### Special-Case Fix [CODING HORROR, p.553]

```java
// BAD: Symptom fix, not root cause
for (claimNumber = 0; claimNumber < numClaims[client]; claimNumber++) {
    sum[client] = sum[client] + claimAmount[claimNumber];
}
if (client == 45) {
    sum[45] = sum[45] + 3.45;  // "Fix" for client 45
}
```

**Why it fails:**
1. Initialization defects are unpredictable - $3.45 today, $10,000.02 tomorrow
2. Special cases become barnacles that sink the code
3. Uses computer for something better done by hand (whiteout)

### Debug by Superstition [p.540]

Blaming compiler, machine, moon phase, or external factors.

**Reality:** If you wrote the program, it's your fault. The program doesn't do something different every time. Take responsibility.

### Voodoo Programming [p.546]

Making random changes until something seems to work.

**Reality:** You learn nothing. The more different you make it without understanding, the less confidence you'll have that it works.

---

## Quality and Schedule Relationship

### General Principle Validation

| Finding | Source |
|---------|--------|
| Increased QA = decreased errors, **no increased cost** | Card 1987, NASA (50 projects, 400 work-years, 3M LOC) |
| Lowest defects = shortest schedules, highest productivity | Jones 2000, IBM |
| Programmers taking **less than median time** had fewer errors | DeMarco/Lister 1985 |
| Programmers taking **more than median time** also had fewer errors | DeMarco/Lister 1985 |
| Median-time programmers had **most errors** | DeMarco/Lister 1985 |

**Conclusion:** Writing software without defects can take **less time**, not more. Quality and speed are not opposites.

### Time Spent on Debugging

- Debugging + rework consumes **~50%** of time on traditional/naive development [Section 3.1]
- Reducing debugging by preventing errors improves productivity
- Most obvious way to shorten schedule: improve quality → reduce debugging/rework

---

## Relevant Standards

- IEEE Std 730-2002, Standard for Software Quality Assurance Plans
- IEEE Std 1061-1998, Standard for Software Quality Metrics Methodology
- IEEE Std 1028-1997, Standard for Software Reviews
- IEEE Std 1008-1987 (R1993), Standard for Software Unit Testing
- IEEE Std 829-1998, Standard for Software Test Documentation
