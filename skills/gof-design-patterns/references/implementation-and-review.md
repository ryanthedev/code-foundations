# GoF Design Patterns — Implementation & Review

---

## Implementation Checklist (Per Pattern)

Use this checklist when implementing any design pattern:

### Design Phase

- [ ] **Define interfaces/abstract classes first**
  - Identify the abstract participant roles from the pattern
  - Define contracts before implementations
  - Use meaningful names that reflect the pattern's vocabulary

- [ ] **Identify all participants**
  - Map your domain classes to pattern participants
  - Document which class plays which role
  - Verify all required participants are identified

### Implementation Phase

- [ ] **Implement concrete classes**
  - Start with the simplest ConcreteX implementation
  - Follow the Single Responsibility Principle per class
  - Each concrete class should be independently testable

- [ ] **Wire up client code**
  - Client depends only on abstractions, not concretions
  - Use dependency injection where appropriate
  - Configuration/factory code is separate from business logic

### Verification Phase

- [ ] **Test pattern behavior**
  - Unit tests for each participant in isolation
  - Integration tests for participant interactions
  - Test edge cases specific to the pattern

- [ ] **Verify consequences match expectations**
  - Benefits listed in pattern are actually realized
  - Liabilities are acceptable and manageable
  - No unexpected side effects or performance issues

### Pattern-Specific Considerations

#### Creational Patterns
- [ ] Object creation is properly encapsulated
- [ ] Clients are decoupled from concrete classes
- [ ] New product types can be added without client changes

#### Structural Patterns
- [ ] Interface relationships are clear and well-defined
- [ ] Composition/aggregation is used appropriately
- [ ] Transparency to clients is maintained where expected

#### Behavioral Patterns
- [ ] Responsibilities are distributed appropriately
- [ ] Communication protocols are well-defined
- [ ] State changes and transitions are handled correctly

---

## Code Review Checklist

Use during code reviews to evaluate pattern application:

### Problem Fit

- [ ] **Pattern applied to correct problem?**
  - The problem matches the pattern's intent
  - Problem indicators from GoF are present
  - Alternative patterns were considered

- [ ] **Not over-engineered?**
  - Simpler solutions were genuinely insufficient
  - Pattern complexity is justified by problem complexity
  - YAGNI principle considered (You Aren't Gonna Need It)

### Implementation Quality

- [ ] **Participants properly separated?**
  - Each class has a single, clear responsibility
  - Abstractions don't leak into concrete implementations
  - Pattern vocabulary is used in naming

- [ ] **Client code decoupled appropriately?**
  - Clients depend on interfaces, not implementations
  - Concrete classes are hidden behind factories/abstractions
  - Changes to one participant don't ripple to others

### Maintainability

- [ ] **Easy to extend?**
  - New variants can be added without modifying existing code
  - Open/Closed Principle is respected
  - Extension points are clear and documented

- [ ] **Easy to understand?**
  - Pattern usage is documented or obvious
  - Team members can recognize the pattern
  - Participant roles are clear from class names

### Common Anti-Patterns to Watch For

- [ ] **No "pattern mania"** - Using patterns for their own sake
- [ ] **No "abstract everything"** - Over-abstracting simple code
- [ ] **No "mega-class"** - Mediator/Facade becoming a god object
- [ ] **No "leaky abstraction"** - Implementation details exposed
- [ ] **No "pattern mixing confusion"** - Multiple patterns tangled together
- [ ] **No "premature patterning"** - Applying before the need is clear

---

## Quick Decision Matrix

When you're unsure which pattern to use, find your primary concern:

| Primary Concern | Consider These Patterns |
|-----------------|------------------------|
| **Object creation complexity** | Factory Method, Abstract Factory, Builder |
| **Object creation flexibility** | Prototype, Factory Method |
| **Single instance requirement** | Singleton |
| **Interface incompatibility** | Adapter |
| **Varying abstraction/implementation** | Bridge |
| **Tree/hierarchy structures** | Composite |
| **Adding behavior dynamically** | Decorator |
| **Simplifying complex systems** | Facade |
| **Memory optimization (many objects)** | Flyweight |
| **Controlling object access** | Proxy |
| **Request routing** | Chain of Responsibility |
| **Encapsulating requests** | Command |
| **Language/grammar processing** | Interpreter |
| **Collection traversal** | Iterator |
| **Object communication** | Mediator, Observer |
| **State snapshots/undo** | Memento |
| **State-dependent behavior** | State |
| **Algorithm selection** | Strategy |
| **Algorithm skeleton** | Template Method |
| **Operations on structures** | Visitor |

---

## Pattern Relationship Guide

Understanding how patterns work together:

### Patterns Often Used Together

| Pattern | Frequently Combined With |
|---------|-------------------------|
| Abstract Factory | Factory Method, Singleton, Prototype |
| Builder | Composite (builds complex composites) |
| Factory Method | Template Method, Abstract Factory |
| Composite | Iterator, Visitor, Decorator, Chain of Responsibility |
| Decorator | Composite, Strategy |
| Facade | Singleton, Abstract Factory |
| Command | Memento (for undo), Composite (macros) |
| Iterator | Composite, Factory Method |
| Mediator | Observer, Singleton |
| Observer | Mediator, Singleton |
| State | Singleton (shared states), Flyweight |
| Strategy | Flyweight (shared strategies) |
| Visitor | Composite, Iterator |

### Pattern Alternatives

| If Considering... | Also Consider... | Choose Based On... |
|-------------------|------------------|-------------------|
| Strategy | State | Strategy: one algorithm; State: behavior varies by state |
| Strategy | Template Method | Strategy: vary whole algorithm; Template: vary steps |
| Decorator | Strategy | Decorator: add behavior; Strategy: replace behavior |
| Adapter | Bridge | Adapter: retrofit; Bridge: design upfront |
| Adapter | Facade | Adapter: interface conversion; Facade: simplification |
| Facade | Mediator | Facade: unidirectional; Mediator: multidirectional |
| Proxy | Decorator | Proxy: control access; Decorator: add responsibilities |
| Command | Strategy | Command: encapsulate request; Strategy: encapsulate algorithm |
| Factory Method | Abstract Factory | Factory Method: one product; Abstract Factory: families |

---

Effective pattern selection requires:

1. **Understand the problem deeply** before selecting a pattern
2. **Know the pattern's intent** and verify it matches your need
3. **Consider the consequences** — both benefits and liabilities
4. **Start simple** — add patterns when complexity justifies them
5. **Review pattern usage** to ensure proper application
6. **Document pattern choices** for team understanding

Patterns are tools, not goals. The best code uses patterns where they solve real problems and avoids them where they add unnecessary complexity.
