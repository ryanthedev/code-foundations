# Evidence: cc-integration-practices

## Key Points

- [KEY POINT p.694] "It doesn't matter that the stadium would have been strong enough by the time it was done; it needed to be strong enough at each step."

- [KEY POINT p.694] Benefits of careful integration: "Easier defect diagnosis, Fewer defects, Less scaffolding, Shorter time to first working product, Shorter overall development schedules, Better customer relations, Improved morale, Improved chance of project completion, More reliable schedule estimates, More accurate status reporting, Improved code quality, Less documentation"

## Empirical Findings

- [HARD DATA: Basili and Perricone 1984] "39 percent were intermodule interface errors"
  - Context: Study of defect origins showing integration boundaries are major error sources

- [HARD DATA: CC2 p.689] "Developers on many projects spend up to 50 percent of their time debugging"
  - Context: Motivation for incremental integration to reduce debugging time

- [HARD DATA: Zachary 1994] Windows 2000: "50 million lines of code... 19 hours on several machines, but... still managed to build every day"
  - Context: Daily builds scale to very large projects with proper infrastructure

- [HARD DATA: Cusumano et al. 2003] "Only 20–25 percent of projects used daily builds"
  - Context: Industry adoption rates lower than expected given proven benefits

- [HARD DATA: McConnell poll] Poll of tech executives (Amazon, Boeing, Expedia, Microsoft, Nordstrom): "none of them thought that continuous integration was superior to daily integration"
  - Context: Experienced practitioners see diminishing returns beyond daily frequency

## Anti-Patterns

- [ANTI-PATTERN p.691] Big Bang Integration
  - Description: "Integrate all components simultaneously at the end"
  - Why it's wrong: "All problems surface at once, interact, and mask each other"

- [ANTI-PATTERN p.695] Letting Low-Level Drive High-Level
  - Description: "Building system bottom-up, letting infrastructure dictate architecture"
  - Why it's wrong: "Contradicts information hiding and OO design principles"

- [ANTI-PATTERN p.702] Stale Smoke Test
  - Description: "Smoke test not updated as system evolves"
  - Why it's wrong: "Creates false sense of confidence, self-deception"
