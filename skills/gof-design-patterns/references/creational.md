# GoF Design Patterns — Pattern Selection & Creational

Practical decision-making guides for selecting and applying creational design patterns.

---

## Pattern Selection Checklist

Before applying any pattern, verify:

- [ ] **I've identified a recurring problem, not a one-off**
  - The same structural or behavioral issue appears multiple times in the codebase
  - Future code is likely to encounter the same problem
  - The pattern addresses a design smell, not just a single bug

- [ ] **The pattern's intent matches my problem**
  - I can clearly articulate which GoF intent applies
  - The problem indicators from the pattern match my symptoms
  - The pattern solves the root cause, not a surface symptom

- [ ] **Simpler solutions don't suffice**
  - Direct method calls or simple conditionals are inadequate
  - The complexity of the pattern is justified by the problem complexity
  - I've considered whether a language feature (lambdas, generics) already solves this

- [ ] **I understand the tradeoffs (consequences)**
  - I've reviewed both benefits AND liabilities of the pattern
  - The liabilities are acceptable in my context
  - I know what maintenance burden the pattern introduces

- [ ] **The indirection cost is worth the benefit**
  - Additional classes/interfaces provide meaningful flexibility
  - The pattern doesn't over-engineer a simple situation
  - Team members can understand and maintain the abstraction

---

## Creational Pattern Decision Tree

```
Need to create objects?
|
+-- Family of related objects that must be used together?
|   +-- YES --> Abstract Factory
|   |   - Products have compatibility constraints
|   |   - Switching product families should be easy
|   |   - Hide concrete product classes from clients
|   |
|   +-- NO --> Continue below
|
+-- Complex multi-step construction process?
|   +-- YES --> Builder
|   |   - Object requires many configuration options
|   |   - Same construction process creates different representations
|   |   - Construction algorithm should be reusable
|   |
|   +-- NO --> Continue below
|
+-- Class cannot anticipate which class to instantiate?
|   +-- YES --> Factory Method
|   |   - Framework needs to create application-specific objects
|   |   - Subclasses should decide which class to instantiate
|   |   - Parallel class hierarchies exist
|   |
|   +-- NO --> Continue below
|
+-- Need to create objects by copying existing instances?
|   +-- YES --> Prototype
|   |   - Classes determined at runtime
|   |   - Avoid parallel factory class hierarchy
|   |   - Objects have few state variations to pre-configure
|   |
|   +-- NO --> Continue below
|
+-- Exactly one instance needed system-wide?
    +-- YES --> Singleton
    |   - Single instance is domain-inherent (not just convenient)
    |   - Global access point is genuinely required
    |   - Consider DI frameworks as alternative
    |
    +-- NO --> Direct instantiation may suffice
```

### Creational Pattern Quick Reference

| Pattern | Use When | Avoid When |
|---------|----------|------------|
| **Abstract Factory** | Multiple related product families | Only one product type; products don't form families |
| **Builder** | Telescoping constructors; step-by-step construction | Simple objects; single-step creation |
| **Factory Method** | Subclasses specify which class to create | Class to instantiate never varies |
| **Prototype** | Runtime class specification; clone is cheaper than create | Objects have complex initialization; deep copy is problematic |
| **Singleton** | Exactly one instance required; global access needed | "Single instance" is environment-specific; testability matters |
