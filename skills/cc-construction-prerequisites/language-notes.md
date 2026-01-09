# Language Notes: cc-construction-prerequisites

## Language Expressiveness Ratios (Table 4-1)

| Language | Ratio to C | Notes |
|----------|-----------|-------|
| C | 1 | Baseline |
| C++ | 2.5 | Object-oriented features |
| Java | 2.5 | Platform independence |
| Fortran 95 | 2 | Scientific computing |
| Visual Basic | 4.5 | Rapid application development |
| Perl | 6 | String handling, scripting |
| Python | 6 | Scripting, readability |
| Smalltalk | 6 | Pure object-oriented |

Source: Adapted from Jones 1998, Boehm 2000, Prechelt 2000

## Technology Wave Positioning

| Wave Position | Characteristics | Construction Implications |
|---------------|-----------------|---------------------------|
| Early-wave | Few languages, buggy tools, poor docs, no debuggers | More time on workarounds; practices matter MORE |
| Late-wave | Many choices, mature tools, good docs | More time on new functionality |

## "Disguised Code" Anti-Pattern

Watch for programmers writing code patterns from their previous language:
- Fortran programmers in C++: excessive gotos, global data, ignoring OOP
- C programmers in Java: manual memory management patterns, avoiding collections

**Action:** Review code from language-transitioning teams for idiomatic usage of new language features.

## Programming "Into" vs "In" a Language

| Approach | Definition |
|----------|------------|
| Programming "in" | Limited to constructs language directly supports |
| Programming "into" | Decide what to express, then find expression mechanism |

If language lacks constructs you need, create compensating conventions, standards, or class libraries rather than accepting limitations.
