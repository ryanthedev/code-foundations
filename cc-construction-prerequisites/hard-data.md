# Evidence: cc-construction-prerequisites

## Key Points

- [KEY POINT p.31] "The overarching goal of preparation is risk reduction. A good project planner clears major risks out of the way as early as possible so that the bulk of the project can proceed smoothly."
- [KEY POINT p.28] "Quality at the beginning has greater influence than quality at the end."
- [KEY POINT p.54] "The quality of the architecture determines the conceptual integrity of the system. That in turn determines the ultimate quality of the system."
- [KEY POINT p.66] "Establish programming conventions before you begin programming. It's nearly impossible to change code to match them later."
- [KEY POINT p.68] "Program into the language, rather than programming in it."

## Empirical Findings

| Finding | Data | Source |
|---------|------|--------|
| Defect correction cost multiplier | 10-100x higher when found late vs early | Fagan 1976; Boehm and Turner 2004 |
| Debugging time in typical project | ~50% of development time | Mills 1983; Jones 1998; Shull et al. 2002 |
| Requirements change during development | ~25% average | Boehm 1981; Jones 1994, 2000 |
| Rework from requirements changes | 70-85% of total rework | Leffingwell 1997; Wiegers 2003 |
| Prerequisites time investment | 10-20% effort, 20-30% schedule | McConnell 1998; Kruchten 2000 |
| Language familiarity productivity boost | ~30% more productive with 3+ years experience | Cocomo II, Boehm et al. 2000 |
| High-level vs low-level language productivity | 5-15x improvement | Brooks 1987; Jones 1998; Boehm 2000 |

## Defect Cost by Phase (Table 3-1)

| Time Introduced | Requirements | Architecture | Construction | System Test | Post-Release |
|-----------------|--------------|--------------|--------------|-------------|--------------|
| Requirements    | 1            | 3            | 5-10         | 10          | 10-100       |
| Architecture    | -            | 1            | 10           | 15          | 25-100       |
| Construction    | -            | -            | 1            | 10          | 10-25        |

Source: Boehm and Turner 2004
