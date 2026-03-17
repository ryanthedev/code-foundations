---
name: gof-strategy
classification: Behavioral / Object
description: Multiple conditional statements selecting behavior variants, or related classes differing only in their algorithms - encapsulate interchangeable algorithms in separate classes.
---

## INTENT

Define a family of algorithms, encapsulate each one, and make them interchangeable. Strategy lets the algorithm vary independently from clients that use it.

## ALSO KNOWN AS

Policy

## PROBLEM INDICATORS

When you see:
- Many related classes that differ only in their behavior
- Multiple conditional statements (switch/if-else chains) selecting different algorithms or behaviors
- A class defines many behaviors that appear as multiple conditional branches in its operations
- You need different variants of an algorithm with different time/space trade-offs
- An algorithm uses data that clients shouldn't know about (complex, algorithm-specific data structures)
- Hard-wired algorithm code making classes bigger, harder to maintain, and impossible to vary dynamically
- Need to add new algorithms or vary existing ones without modifying client code

## KEY INSIGHT

Instead of embedding algorithm selection logic (conditionals) in a class, extract each algorithm variant into its own class with a common interface. The context delegates to a strategy object, making algorithms independently variable, testable, and extensible.

## PARTICIPANTS

| Role | Responsibility |
|------|---------------|
| Strategy (Compositor) | Declares an interface common to all supported algorithms. Context uses this interface to call the algorithm defined by a ConcreteStrategy. |
| ConcreteStrategy (SimpleCompositor, TeXCompositor, ArrayCompositor) | Implements the algorithm using the Strategy interface. |
| Context (Composition) | Is configured with a ConcreteStrategy object. Maintains a reference to a Strategy object. May define an interface that lets Strategy access its data. |

## CONSEQUENCES

**Benefits:**

1. Families of related algorithms - Hierarchies of Strategy classes define a family of algorithms or behaviors for contexts to reuse. Inheritance can help factor out common functionality of the algorithms.

2. An alternative to subclassing - Encapsulating the algorithm in separate Strategy classes lets you vary the algorithm independently of its context, making it easier to switch, understand, and extend. Avoids hard-wiring behavior into Context and mixing algorithm implementation with Context's code.

3. Strategies eliminate conditional statements - The Strategy pattern offers an alternative to conditional statements for selecting desired behavior. Encapsulating the behavior in separate Strategy classes eliminates switch/case and if-else chains.

4. A choice of implementations - Strategies can provide different implementations of the same behavior. The client can choose among strategies with different time and space trade-offs.

**Liabilities:**

1. Clients must be aware of different Strategies - A client must understand how Strategies differ before it can select the appropriate one. Clients might be exposed to implementation issues. Use the Strategy pattern only when the variation in behavior is relevant to clients.

2. Communication overhead between Strategy and Context - The Strategy interface is shared by all ConcreteStrategy classes whether the algorithms they implement are trivial or complex. Some ConcreteStrategies won't use all the information passed to them; simple ones may use none of it. The context may create and initialize parameters that never get used.

3. Increased number of objects - Strategies increase the number of objects in an application. This can be reduced by implementing strategies as stateless objects that contexts can share (see Flyweight pattern).

## WHEN NOT TO USE

- When you have only one algorithm and no foreseeable need for variants
- When the variation in behavior is not relevant to clients
- When algorithm selection is truly static and determined at compile-time (consider template parameters instead)
- When the overhead of object creation and delegation outweighs the benefits (very performance-critical code with simple algorithms)
- When the Strategy interface would need to change with every new subclass
- When tight coupling between algorithm and context data is acceptable and beneficial

## RELATED PATTERNS

| Pattern | Relationship |
|---------|-------------|
| Flyweight | Strategy objects often make good flyweights. Shared strategies should not maintain state across invocations - residual state is maintained by the context, which passes it in each request. |
| State | Both patterns delegate behavior to associated objects, but State changes behavior based on internal state while Strategy is typically set once by the client. |
| Template Method | Template Method uses inheritance to vary parts of an algorithm; Strategy uses composition/delegation to vary the entire algorithm. |
| Decorator | Both modify behavior, but Decorator wraps objects to add responsibilities while Strategy replaces the algorithm entirely. |

## MODERN CONTEXT

- **TypeScript/JavaScript**: Strategy is often implemented with functions or lambdas passed as arguments rather than full class hierarchies. Callback functions and higher-order functions are lightweight strategies.
- **React**: Custom hooks and render props can serve as strategies. Sorting/filtering functions passed to components are strategy patterns.
- **Spring Framework**: `@Qualifier` annotations select between multiple strategy implementations. `ApplicationContext` can inject the appropriate strategy bean.
- **Dependency Injection**: Strategy pattern is foundational to DI - services inject their dependencies (strategies) rather than creating them.
- **Functional Programming**: First-class functions make Strategy trivial - pass a function instead of creating a strategy object.
- **Java Streams/Collections**: `Comparator` interface is a classic Strategy. `sort()` accepts different comparison strategies.
- **Validation frameworks**: Validators (as in ObjectWindows example) remain common - form validation strategies, data validation rules.
- **Cloud/Microservices**: Different deployment strategies, retry strategies, load balancing strategies are configured via strategy pattern.

## SKILL ACTIONS

```
TRIGGER: When you see switch/case or if-else chains selecting between algorithm variants, or related classes differing only in their behavior
ACTION: Extract each algorithm into a ConcreteStrategy class implementing a common Strategy interface. Have the Context delegate to the Strategy object.
COUNTER-INDICATOR: When there's only one algorithm with no variants, when algorithm selection overhead exceeds benefits, or when variation is not client-relevant
```

## CSO KEYWORDS

strategy pattern, policy pattern, algorithm encapsulation, interchangeable algorithms, behavioral pattern, eliminate conditionals, switch statement refactoring, algorithm family, composition over inheritance, delegation, pluggable behavior, runtime algorithm selection, open-closed principle, dependency injection, validator, compositor, configurable behavior, algorithm variation, decoupled algorithms
