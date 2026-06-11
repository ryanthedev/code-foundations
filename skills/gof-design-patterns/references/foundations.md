# GoF Design Patterns: Foundations

Three operative principles that underpin all 23 patterns.

---

## "Program to an interface, not an implementation"

Clients depend on abstract interfaces, not concrete classes. Reduces coupling, enables substitution, facilitates testing.

```
// NOT THIS: Coupled to concrete class
const logger = new FileLogger();

// THIS: Depend on abstraction
const logger: Logger = createLogger(config);
```

Appears in: Abstract Factory, Bridge, Strategy, Observer

---

## "Favor object composition over class inheritance"

Inheritance creates tight coupling between parent and child. Composition offers runtime flexibility, avoids fragile-base-class problems, and makes individual components easier to test.

Patterns that exemplify this: Strategy, Decorator, Bridge, Composite, Chain of Responsibility

---

## Encapsulate What Varies

Identify what varies and separate it from what stays the same:
- **Creational patterns**: encapsulate object creation (Factory Method, Abstract Factory, Builder)
- **Structural patterns**: encapsulate composition (Adapter, Decorator, Proxy)
- **Behavioral patterns**: encapsulate algorithms and interaction (Strategy, Command, Observer)

---

## When NOT to Apply a Pattern

Every pattern adds indirection. Apply one only when the flexibility it provides outweighs the extra classes and interfaces needed to support it.
