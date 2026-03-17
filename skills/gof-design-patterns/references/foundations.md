# GoF Design Patterns: Foundations

## Core Philosophy

### What Design Patterns ARE

Design patterns are **proven solutions to recurring problems** in software design. They represent the collective wisdom of experienced object-oriented developers, distilled into reusable templates that address common challenges in software construction.

Key characteristics:
- **Named solutions**: Each pattern has a name that becomes part of a design vocabulary, enabling efficient communication among developers
- **Problem-solution pairs**: Patterns describe both the problem context and the solution structure
- **Documented trade-offs**: Every pattern comes with known consequences, both benefits and liabilities
- **Language-independent**: Patterns express design ideas that transcend specific programming languages

### What Design Patterns Are NOT

- **Rigid templates**: Patterns must be adapted to your specific context. The GoF explicitly states that patterns are not finished designs that can be transformed directly into code.
- **Silver bullets**: No pattern solves every problem. Misapplied patterns add unnecessary complexity.
- **Replacements for thinking**: Patterns are tools, not substitutes for understanding the problem domain.
- **Copy-paste code snippets**: Each application requires thoughtful implementation tailored to the situation.

### Gang of Four Principles

The Gang of Four (Erich Gamma, Richard Helm, Ralph Johnson, John Vlissides) established foundational principles that underpin all 23 patterns:

1. **Design for change**: Anticipate what aspects of your design are likely to vary and encapsulate those aspects
2. **Favor flexibility**: Prefer designs that support extension without modification
3. **Reduce dependencies**: Minimize coupling between components to improve maintainability

---

## Key Principles

### "Program to an interface, not an implementation"

Clients should depend on abstract interfaces rather than concrete classes. This principle:
- Reduces coupling between components
- Enables substitution of different implementations
- Facilitates testing through mocking and stubbing
- Appears in patterns like: Abstract Factory, Bridge, Strategy, Observer

```
// NOT THIS: Coupled to concrete class
const logger = new FileLogger();

// THIS: Depend on abstraction
const logger: Logger = createLogger(config);
```

### "Favor object composition over class inheritance"

Inheritance creates tight coupling between parent and child classes. Composition offers:
- Runtime flexibility to change behavior
- Avoidance of fragile base class problems
- Better encapsulation of implementation details
- Easier testing of individual components

Patterns that exemplify this: Strategy, Decorator, Bridge, Composite, Chain of Responsibility

### Encapsulate What Varies

Identify aspects of your application that vary and separate them from what stays the same:
- **Creational patterns**: Encapsulate object creation (Factory Method, Abstract Factory, Builder)
- **Structural patterns**: Encapsulate object composition (Adapter, Decorator, Proxy)
- **Behavioral patterns**: Encapsulate algorithms and object interaction (Strategy, Command, Observer)

### Loose Coupling

Minimize dependencies between components:
- Objects should know as little as possible about each other
- Use intermediaries (Mediator) to reduce direct connections
- Prefer observer/event patterns over direct callbacks
- Design for independent evolution of components

---

## Pattern Classification

### Creational Patterns
**Purpose**: Abstract the instantiation process, making systems independent of how objects are created, composed, and represented.

| Pattern | Scope | Core Problem |
|---------|-------|--------------|
| Abstract Factory | Object | Creating families of related objects without specifying concrete classes |
| Builder | Object | Constructing complex objects step-by-step with varying representations |
| Factory Method | Class | Letting subclasses decide which class to instantiate |
| Prototype | Object | Creating objects by cloning prototypical instances |
| Singleton | Object | Ensuring a class has only one instance with global access |

**Key insight**: These patterns give flexibility in *what* gets created, *who* creates it, *how* it gets created, and *when*.

### Structural Patterns
**Purpose**: Compose classes and objects into larger structures while keeping these structures flexible and efficient.

| Pattern | Scope | Core Problem |
|---------|-------|--------------|
| Adapter | Class/Object | Making incompatible interfaces work together |
| Bridge | Object | Separating abstraction from implementation for independent variation |
| Composite | Object | Treating individual objects and compositions uniformly |
| Decorator | Object | Adding responsibilities to objects dynamically |
| Facade | Object | Providing a unified interface to a subsystem |
| Flyweight | Object | Sharing state efficiently among many fine-grained objects |
| Proxy | Object | Controlling access to an object through a surrogate |

**Key insight**: Structural patterns use inheritance and composition to realize new functionality through object relationships.

### Behavioral Patterns
**Purpose**: Define algorithms and the assignment of responsibilities between objects, describing patterns of communication.

| Pattern | Scope | Core Problem |
|---------|-------|--------------|
| Chain of Responsibility | Object | Passing requests along a chain of potential handlers |
| Command | Object | Encapsulating requests as objects for queuing, logging, or undo |
| Interpreter | Class | Defining a grammar representation and interpreter |
| Iterator | Object | Accessing elements of a collection sequentially |
| Mediator | Object | Centralizing complex communications between objects |
| Memento | Object | Capturing and restoring object state without violating encapsulation |
| Observer | Object | Notifying dependents automatically when state changes |
| State | Object | Altering behavior when internal state changes |
| Strategy | Object | Encapsulating interchangeable algorithms |
| Template Method | Class | Defining algorithm skeleton with subclass-specific steps |
| Visitor | Object | Adding operations to object structures without modifying them |

**Key insight**: Behavioral patterns characterize complex control flow that is difficult to follow at runtime, shifting focus from flow of control to object interconnections.

---

## When to Use Patterns

### Recognize the Problem First

Patterns are solutions to specific problems. Before applying a pattern:

1. **Identify the problem clearly**: What is causing friction in your design?
2. **Understand the forces at play**: What constraints and requirements must be balanced?
3. **Consider the context**: Is this a recurring problem or a one-off situation?

### Problem Indicators (from GoF patterns)

Look for these symptoms that suggest pattern application:

- **Creational**: Hard-coded class names, inflexible object creation, scattered `new` statements
- **Structural**: Interface mismatches, rigid class hierarchies, feature explosion via inheritance
- **Behavioral**: Complex conditional logic selecting behavior, tight coupling between sender and receiver

### Don't Force Patterns Where Simple Code Works

Not every problem needs a pattern:

- **YAGNI (You Aren't Gonna Need It)**: Don't add flexibility you don't need yet
- **Simple is better**: If a straightforward solution works, use it
- **Premature abstraction**: Adding patterns "just in case" creates unnecessary complexity

### Patterns Add Indirection - Ensure Benefit > Cost

Every pattern introduces some level of indirection:

| Pattern | Indirection Cost | Justified When |
|---------|-----------------|----------------|
| Strategy | Extra classes for each algorithm | Algorithm selection varies at runtime |
| Decorator | Multiple wrapper objects | Combinations of behaviors are needed |
| Observer | Notification overhead | Multiple dependents need updates |
| Abstract Factory | Factory hierarchy | Multiple product families exist |

**Ask yourself**: Does the flexibility this pattern provides outweigh the complexity it introduces?

---

## Common Misconceptions

| Myth | Reality |
|------|---------|
| "Use patterns everywhere" | Use patterns when they solve a real problem you actually have |
| "More patterns = better code" | The simplest solution that meets requirements wins |
| "Patterns are for architecture only" | Patterns apply at all scales, from local code to system design |
| "You must use the exact structure from the book" | Adapt patterns to your language, framework, and context |
| "Knowing patterns makes you a good designer" | Knowing when NOT to use a pattern is equally important |
| "Patterns are only for object-oriented languages" | Many patterns translate to functional and other paradigms |
| "Modern frameworks eliminate the need for patterns" | Frameworks often implement patterns internally; understanding them helps you use frameworks effectively |

---

## Applying These Foundations

When evaluating whether to use a pattern:

1. **Is there a recurring problem?** Patterns solve problems that appear repeatedly, not one-time issues.

2. **Does the pattern address your specific problem?** Read the "Problem Indicators" section of each pattern carefully.

3. **Do the consequences align with your needs?** Every pattern has trade-offs. Ensure the benefits outweigh the liabilities for your situation.

4. **Is the indirection justified?** Patterns add layers. Make sure the flexibility gained is worth the added complexity.

5. **Does your team understand it?** A pattern only helps if the team can maintain the code that uses it.

The goal is not to use patterns, but to create software that is **maintainable**, **extensible**, and **understandable**. Patterns are one tool among many to achieve that goal.
