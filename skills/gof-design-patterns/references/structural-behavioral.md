# GoF Design Patterns — Structural & Behavioral Decision Trees

---

## Structural Pattern Decision Tree

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

## Behavioral Pattern Decision Tree

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
