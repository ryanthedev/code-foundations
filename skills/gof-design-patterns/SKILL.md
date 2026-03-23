---
name: gof-design-patterns
description: Use when designing object-oriented systems, refactoring code structure, or recognizing design pattern opportunities. Triggers on: "which pattern", "how to decouple", "too many conditionals", "object creation", "interface mismatch", "notify observers", "undo/redo", "state machine", "algorithm varies", "traverse collection".
---

# GoF Design Patterns Skill

This skill helps identify and apply the 23 Gang of Four design patterns. Use this router to find the right pattern for your problem.

## Quick Reference: Symptom to Pattern

| Symptom | Pattern | Category |
|---------|---------|----------|
| Need single instance globally | [Singleton]($CLAUDE_PLUGIN_ROOT/skills/gof-design-patterns/references/gof-singleton.md) | Creational |
| Complex object construction with many parameters | [Builder]($CLAUDE_PLUGIN_ROOT/skills/gof-design-patterns/references/gof-builder.md) | Creational |
| Need families of related objects | [Abstract Factory]($CLAUDE_PLUGIN_ROOT/skills/gof-design-patterns/references/gof-abstract-factory.md) | Creational |
| Class cannot anticipate objects to create | [Factory Method]($CLAUDE_PLUGIN_ROOT/skills/gof-design-patterns/references/gof-factory-method.md) | Creational |
| Need to copy/clone existing objects | [Prototype]($CLAUDE_PLUGIN_ROOT/skills/gof-design-patterns/references/gof-prototype.md) | Creational |
| Interface mismatch between classes | [Adapter]($CLAUDE_PLUGIN_ROOT/skills/gof-design-patterns/references/gof-adapter.md) | Structural |
| Need to decouple abstraction from implementation | [Bridge]($CLAUDE_PLUGIN_ROOT/skills/gof-design-patterns/references/gof-bridge.md) | Structural |
| Part-whole hierarchies, tree structures | [Composite]($CLAUDE_PLUGIN_ROOT/skills/gof-design-patterns/references/gof-composite.md) | Structural |
| Add responsibilities dynamically | [Decorator]($CLAUDE_PLUGIN_ROOT/skills/gof-design-patterns/references/gof-decorator.md) | Structural |
| Simplify complex subsystem interface | [Facade]($CLAUDE_PLUGIN_ROOT/skills/gof-design-patterns/references/gof-facade.md) | Structural |
| Many similar objects consuming memory | [Flyweight]($CLAUDE_PLUGIN_ROOT/skills/gof-design-patterns/references/gof-flyweight.md) | Structural |
| Control access to an object | [Proxy]($CLAUDE_PLUGIN_ROOT/skills/gof-design-patterns/references/gof-proxy.md) | Structural |
| Pass request along handler chain | [Chain of Responsibility]($CLAUDE_PLUGIN_ROOT/skills/gof-design-patterns/references/gof-chain-of-responsibility.md) | Behavioral |
| Encapsulate request as object, undo/redo | [Command]($CLAUDE_PLUGIN_ROOT/skills/gof-design-patterns/references/gof-command.md) | Behavioral |
| Define grammar for simple language | [Interpreter]($CLAUDE_PLUGIN_ROOT/skills/gof-design-patterns/references/gof-interpreter.md) | Behavioral |
| Traverse collection without exposing internals | [Iterator]($CLAUDE_PLUGIN_ROOT/skills/gof-design-patterns/references/gof-iterator.md) | Behavioral |
| Reduce chaotic object interconnections | [Mediator]($CLAUDE_PLUGIN_ROOT/skills/gof-design-patterns/references/gof-mediator.md) | Behavioral |
| Save/restore object state (undo/checkpoint) | [Memento]($CLAUDE_PLUGIN_ROOT/skills/gof-design-patterns/references/gof-memento.md) | Behavioral |
| Notify dependents of state changes | [Observer]($CLAUDE_PLUGIN_ROOT/skills/gof-design-patterns/references/gof-observer.md) | Behavioral |
| Object behavior changes with state | [State]($CLAUDE_PLUGIN_ROOT/skills/gof-design-patterns/references/gof-state.md) | Behavioral |
| Swap algorithms at runtime | [Strategy]($CLAUDE_PLUGIN_ROOT/skills/gof-design-patterns/references/gof-strategy.md) | Behavioral |
| Define algorithm skeleton, defer steps | [Template Method]($CLAUDE_PLUGIN_ROOT/skills/gof-design-patterns/references/gof-template-method.md) | Behavioral |
| Operations on object structure without modification | [Visitor]($CLAUDE_PLUGIN_ROOT/skills/gof-design-patterns/references/gof-visitor.md) | Behavioral |

---

## Pattern Categories

### Creational Patterns (5)
**Purpose:** Abstract the instantiation process, making systems independent of how objects are created.

| Pattern | When to Use |
|---------|-------------|
| **Abstract Factory** | Create families of related objects without specifying concrete classes |
| **Builder** | Construct complex objects step-by-step with varying representations |
| **Factory Method** | Let subclasses decide which class to instantiate |
| **Prototype** | Clone pre-configured objects instead of constructing from scratch |
| **Singleton** | Ensure exactly one instance exists with global access |

### Structural Patterns (7)
**Purpose:** Compose classes and objects into larger structures while keeping them flexible and efficient.

| Pattern | When to Use |
|---------|-------------|
| **Adapter** | Make incompatible interfaces work together |
| **Bridge** | Separate abstraction from implementation for independent variation |
| **Composite** | Treat individual objects and compositions uniformly |
| **Decorator** | Add responsibilities to objects dynamically |
| **Facade** | Provide simple interface to complex subsystem |
| **Flyweight** | Share common state among many fine-grained objects |
| **Proxy** | Control access to an object (lazy load, remote, protection) |

### Behavioral Patterns (11)
**Purpose:** Define how objects interact and distribute responsibilities.

| Pattern | When to Use |
|---------|-------------|
| **Chain of Responsibility** | Pass request along chain until handled |
| **Command** | Encapsulate requests for queuing, logging, undo |
| **Interpreter** | Define grammar representation for simple language |
| **Iterator** | Access collection elements without exposing structure |
| **Mediator** | Centralize complex object communications |
| **Memento** | Capture and restore object state without exposing internals |
| **Observer** | Notify multiple objects of state changes |
| **State** | Alter behavior when internal state changes |
| **Strategy** | Encapsulate interchangeable algorithms |
| **Template Method** | Define algorithm skeleton, let subclasses fill steps |
| **Visitor** | Add operations to object structure without modifying it |

---

## Decision Trees

### "How should I create objects?"

```
Need to create objects?
|
+-- Need families of related objects?
|   YES --> Abstract Factory
|
+-- Construction is complex/multi-step?
|   YES --> Builder
|
+-- Want subclasses to specify type?
|   YES --> Factory Method
|
+-- Want to copy existing configured objects?
|   YES --> Prototype
|
+-- Need exactly one instance?
    YES --> Singleton
```

### "How should I structure my classes?"

```
Need to structure classes?
|
+-- Incompatible interface to integrate?
|   YES --> Adapter
|
+-- Abstraction and implementation vary independently?
|   YES --> Bridge
|
+-- Part-whole hierarchy (tree)?
|   YES --> Composite
|
+-- Add optional behaviors dynamically?
|   YES --> Decorator
|
+-- Complex subsystem needs simple entry point?
|   YES --> Facade
|
+-- Many similar objects wasting memory?
|   YES --> Flyweight
|
+-- Need to control object access?
    YES --> Proxy
```

### "How should objects communicate?"

```
Need to define object interaction?
|
+-- Multiple potential handlers for request?
|   YES --> Chain of Responsibility
|
+-- Need to queue/undo/log operations?
|   YES --> Command
|
+-- Recurring problem expressible as grammar?
|   YES --> Interpreter
|
+-- Traverse collection without exposing structure?
|   YES --> Iterator
|
+-- Too many object interconnections?
|   YES --> Mediator
|
+-- Need to save/restore state?
|   YES --> Memento
|
+-- Objects must react to state changes?
|   YES --> Observer
|
+-- Behavior changes based on state?
|   YES --> State
|
+-- Need to swap algorithms at runtime?
|   YES --> Strategy
|
+-- Algorithm varies only in specific steps?
|   YES --> Template Method
|
+-- Add operations to stable structure?
    YES --> Visitor
```

---

## Common Problem-to-Pattern Mapping

### Object Creation Problems

| Problem | Consider |
|---------|----------|
| "Telescoping constructor" (many params) | Builder |
| "Hard-coded class names everywhere" | Factory Method, Abstract Factory |
| "Need platform/theme independence" | Abstract Factory |
| "Object creation is expensive, copying is cheap" | Prototype |
| "Need single shared resource" | Singleton |

### Structural Problems

| Problem | Consider |
|---------|----------|
| "Legacy API doesn't match what I need" | Adapter |
| "Class explosion from orthogonal variations" | Bridge |
| "Need to treat files and folders uniformly" | Composite |
| "Subclass explosion for feature combinations" | Decorator |
| "Clients coupled to too many subsystem classes" | Facade |
| "Creating thousands of similar objects" | Flyweight |
| "Need lazy loading / access control" | Proxy |

### Behavioral Problems

| Problem | Consider |
|---------|----------|
| "Don't know which handler should process request" | Chain of Responsibility |
| "Need undo/redo functionality" | Command + Memento |
| "Large switch statements on object type" | State, Strategy, or Visitor |
| "UI needs to update when model changes" | Observer |
| "Objects communicate in complex web" | Mediator |
| "Algorithm skeleton is same, steps differ" | Template Method |
| "Need many operations on stable structure" | Visitor |

---

## Pattern Relationships

```
Creational         Structural              Behavioral
---------         ----------              ----------
Abstract Factory   Adapter                Chain of Resp.
     |                |                        |
     +--- creates --> Bridge                   |
     |                |                        v
Builder              Composite <-------- Visitor
     |                |    ^                   |
     v                v    |                   v
Prototype            Decorator          Iterator
     |                |                        |
     +--- clones --> Flyweight                 |
     |                |                        v
Singleton <--------- Facade              Observer
                      |                        |
                      v                        v
                    Proxy <------------- Mediator
                                               |
                                               v
                                         Command <---> Memento
                                               |
                                               v
                                         State <---> Strategy
                                               |
                                               v
                                         Template Method
                                               |
                                               v
                                         Interpreter
```

### Key Relationships:
- **Abstract Factory** often implemented with Factory Methods; factories often Singletons
- **Builder** products frequently Composites
- **Composite** often used with Iterator, Visitor, and Decorator
- **Decorator** and Proxy have similar structures but different intents
- **State** and Strategy both delegate to encapsulated objects but for different reasons
- **Command** uses Memento for undo state
- **Observer** uses Mediator for complex update semantics
- **Visitor** adds operations to Composite structures

---

## Usage Notes

1. **Start with the problem, not the pattern.** Identify what's changing, what's stable, and where flexibility is needed.

2. **Patterns are not mutually exclusive.** Real systems combine multiple patterns. A UI might use Composite for structure, Decorator for scrolling, Strategy for layout, and Observer for updates.

3. **Patterns evolve with languages.** Modern TypeScript, React, and Spring often have idiomatic ways to implement patterns that differ from the original GoF book.

4. **Pattern names are a vocabulary.** Use them in code reviews, documentation, and discussions. "This is an Adapter for the legacy API" communicates more than pages of explanation.

5. **Don't force patterns.** If a direct solution is clearer and the problem is unlikely to evolve, simplicity wins. Patterns add value when they solve real problems.

---

## Reference Files

All 23 pattern reference files are available in `$CLAUDE_PLUGIN_ROOT/skills/gof-design-patterns/references/`:

**Creational:**
- `gof-abstract-factory.md` - Families of related objects
- `gof-builder.md` - Step-by-step complex construction
- `gof-factory-method.md` - Subclass instantiation
- `gof-prototype.md` - Clone-based creation
- `gof-singleton.md` - Single instance

**Structural:**
- `gof-adapter.md` - Interface conversion
- `gof-bridge.md` - Abstraction/implementation separation
- `gof-composite.md` - Part-whole hierarchies
- `gof-decorator.md` - Dynamic responsibilities
- `gof-facade.md` - Subsystem simplification
- `gof-flyweight.md` - Shared fine-grained objects
- `gof-proxy.md` - Access control

**Behavioral:**
- `gof-chain-of-responsibility.md` - Handler chains
- `gof-command.md` - Request encapsulation
- `gof-interpreter.md` - Grammar representation
- `gof-iterator.md` - Collection traversal
- `gof-mediator.md` - Interaction encapsulation
- `gof-memento.md` - State snapshots
- `gof-observer.md` - Change notification
- `gof-state.md` - State-based behavior
- `gof-strategy.md` - Interchangeable algorithms
- `gof-template-method.md` - Algorithm skeletons
- `gof-visitor.md` - Operations on structures
