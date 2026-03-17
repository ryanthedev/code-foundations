# GoF Design Patterns - Decision Checklists

Practical decision-making guides for selecting and applying the 23 Gang of Four design patterns.

---

## 1. Pattern Selection Checklist

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

## 2. Creational Pattern Decision Tree

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

---

## 3. Structural Pattern Decision Tree

```
Need to compose objects or adapt interfaces?
|
+-- Interface mismatch between existing and expected?
|   +-- YES --> Adapter
|   |   - Legacy system integration
|   |   - Third-party library with incompatible interface
|   |   - Wrap existing class without modifying it
|   |
|   +-- NO --> Continue below
|
+-- Need to vary abstraction and implementation independently?
|   +-- YES --> Bridge
|   |   - Avoid permanent binding at compile time
|   |   - Both hierarchies need independent extension
|   |   - Class explosion from combinations
|   |
|   +-- NO --> Continue below
|
+-- Part-whole hierarchy with uniform treatment?
|   +-- YES --> Composite
|   |   - Tree structure of objects
|   |   - Clients should ignore leaf vs. composite distinction
|   |   - Recursive composition needed
|   |
|   +-- NO --> Continue below
|
+-- Add responsibilities dynamically without subclassing?
|   +-- YES --> Decorator
|   |   - Optional features that can be combined
|   |   - Responsibilities can be withdrawn
|   |   - Subclass explosion for feature combinations
|   |
|   +-- NO --> Continue below
|
+-- Simplify interface to complex subsystem?
|   +-- YES --> Facade
|   |   - Clients coupled to many subsystem classes
|   |   - Complex initialization sequences
|   |   - Need layered subsystem entry points
|   |
|   +-- NO --> Continue below
|
+-- Share fine-grained objects efficiently?
|   +-- YES --> Flyweight
|   |   - Large number of similar objects
|   |   - Storage costs are high
|   |   - Most state can be made extrinsic
|   |   - Object identity not required
|   |
|   +-- NO --> Continue below
|
+-- Control access to an object?
    +-- YES --> Proxy
    |   - Lazy loading (Virtual Proxy)
    |   - Remote object access (Remote Proxy)
    |   - Access control (Protection Proxy)
    |   - Smart references (caching, counting, locking)
    |
    +-- NO --> Direct references may suffice
```

### Structural Pattern Quick Reference

| Pattern | Use When | Avoid When |
|---------|----------|------------|
| **Adapter** | Interface incompatibility; legacy integration | Interfaces can be easily refactored to match |
| **Bridge** | Abstraction and implementation vary independently | Only one implementation; no foreseeable variation |
| **Composite** | Tree structures; uniform leaf/composite treatment | No natural hierarchy; interfaces fundamentally differ |
| **Decorator** | Dynamic, combinable responsibilities | Object identity matters; large interface to forward |
| **Facade** | Complex subsystem needs simple interface | Clients need fine-grained control; subsystem is simple |
| **Flyweight** | Many similar objects; high storage costs | Object identity required; extrinsic state complex |
| **Proxy** | Lazy loading, access control, remote access | Object creation is cheap; no access control needed |

---

## 4. Behavioral Pattern Decision Tree

```
Need to define object behavior or communication?
|
+-- Request handling by one of several objects?
|   +-- YES --> Chain of Responsibility
|   |   - Handler not known a priori
|   |   - Dynamic handler assignment
|   |   - Middleware/event bubbling scenarios
|   |
|   +-- NO --> Continue below
|
+-- Encapsulate request as object (queue, log, undo)?
|   +-- YES --> Command
|   |   - Parameterize objects with operations
|   |   - Queue or schedule requests
|   |   - Support undo/redo
|   |
|   +-- NO --> Continue below
|
+-- Define grammar for a simple language?
|   +-- YES --> Interpreter
|   |   - Simple, recurring grammar
|   |   - Expressions as abstract syntax tree
|   |   - DSL or rule engine needed
|   |
|   +-- NO --> Continue below
|
+-- Access collection elements without exposing structure?
|   +-- YES --> Iterator
|   |   - Multiple traversal methods needed
|   |   - Uniform interface for different collections
|   |   - Simultaneous traversals required
|   |
|   +-- NO --> Continue below
|
+-- Centralize complex communication between objects?
|   +-- YES --> Mediator
|   |   - Many-to-many relationships create tangled web
|   |   - Objects hard to reuse due to interconnections
|   |   - Interaction logic should vary independently
|   |
|   +-- NO --> Continue below
|
+-- Capture and restore object state (undo, checkpoint)?
|   +-- YES --> Memento
|   |   - Need undo/redo or checkpoints
|   |   - State must be saved without exposing internals
|   |   - Originator shouldn't manage storage
|   |
|   +-- NO --> Continue below
|
+-- Notify multiple objects of state changes?
|   +-- YES --> Observer
|   |   - One-to-many dependency
|   |   - Loose coupling between subject and observers
|   |   - Dynamic observer subscription
|   |
|   +-- NO --> Continue below
|
+-- Object behavior depends on state (changes at runtime)?
|   +-- YES --> State
|   |   - Large conditionals checking state
|   |   - State transitions should be explicit
|   |   - Operations vary by state across methods
|   |
|   +-- NO --> Continue below
|
+-- Interchangeable algorithms/strategies?
|   +-- YES --> Strategy
|   |   - Multiple algorithm variants
|   |   - Switch/case selecting between behaviors
|   |   - Algorithm should vary independently from client
|   |
|   +-- NO --> Continue below
|
+-- Algorithm skeleton with customizable steps?
|   +-- YES --> Template Method
|   |   - Subclasses share algorithm structure
|   |   - Only specific steps vary
|   |   - Parent controls invariant sequence
|   |
|   +-- NO --> Continue below
|
+-- Operations on elements of stable object structure?
    +-- YES --> Visitor
    |   - Many distinct operations on structure
    |   - Operations change; element classes stable
    |   - Accumulate state during traversal
    |
    +-- NO --> Direct implementation may suffice
```

### Behavioral Pattern Quick Reference

| Pattern | Use When | Avoid When |
|---------|----------|------------|
| **Chain of Responsibility** | Dynamic handler selection; middleware | Guaranteed handling required; fixed order |
| **Command** | Queue, log, undo operations; decouple invoker/receiver | Simple direct calls suffice; no undo needed |
| **Interpreter** | Simple grammar; DSL; recurring language problem | Complex grammar (use parser generators) |
| **Iterator** | Sequential access; hide collection structure | Built-in iteration is sufficient |
| **Mediator** | Complex interconnections; many-to-many communication | Mediator becomes god object; simple interactions |
| **Memento** | Undo/redo; checkpoints; externalize state | State is trivially small; inverse operations work |
| **Observer** | Broadcast state changes; loose coupling | Single dependent; very frequent micro-updates |
| **State** | Behavior varies by state; eliminate state conditionals | Few stable states; minimal state-dependent behavior |
| **Strategy** | Interchangeable algorithms; eliminate algorithm conditionals | Single algorithm; no variants needed |
| **Template Method** | Shared algorithm skeleton; varying steps | Entire algorithm varies (use Strategy) |
| **Visitor** | Many operations on stable structure | Element classes change frequently |

---

## 5. Implementation Checklist (Per Pattern)

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

## 6. Code Review Checklist

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

## 7. Quick Decision Matrix

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

## 8. Pattern Relationship Guide

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

## Summary

Effective pattern selection requires:

1. **Understand the problem deeply** before selecting a pattern
2. **Know the pattern's intent** and verify it matches your need
3. **Consider the consequences** - both benefits and liabilities
4. **Start simple** - add patterns when complexity justifies them
5. **Review pattern usage** to ensure proper application
6. **Document pattern choices** for team understanding

Remember: Patterns are tools, not goals. The best code uses patterns where they solve real problems and avoids them where they add unnecessary complexity.
