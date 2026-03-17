# GoF Design Patterns - Quick Reference Catalog

A comprehensive reference for the 23 Gang of Four design patterns.

---

## 1. Master Pattern Table

| Pattern | Category | Intent (1 sentence) | Key Participants |
|---------|----------|---------------------|------------------|
| Abstract Factory | Creational | Create families of related objects without specifying concrete classes | AbstractFactory, ConcreteFactory, AbstractProduct, ConcreteProduct, Client |
| Builder | Creational | Separate complex object construction from its representation | Builder, ConcreteBuilder, Director, Product |
| Factory Method | Creational | Define interface for object creation, letting subclasses decide which class to instantiate | Product, ConcreteProduct, Creator, ConcreteCreator |
| Prototype | Creational | Create new objects by copying a prototypical instance | Prototype, ConcretePrototype, Client |
| Singleton | Creational | Ensure a class has only one instance with global access point | Singleton |
| Adapter | Structural | Convert interface of a class into another interface clients expect | Target, Adapter, Adaptee, Client |
| Bridge | Structural | Decouple abstraction from implementation so both can vary independently | Abstraction, RefinedAbstraction, Implementor, ConcreteImplementor |
| Composite | Structural | Compose objects into tree structures to treat individual objects and compositions uniformly | Component, Leaf, Composite, Client |
| Decorator | Structural | Attach additional responsibilities to objects dynamically | Component, ConcreteComponent, Decorator, ConcreteDecorator |
| Facade | Structural | Provide unified interface to a set of interfaces in a subsystem | Facade, Subsystem classes |
| Flyweight | Structural | Use sharing to support large numbers of fine-grained objects efficiently | Flyweight, ConcreteFlyweight, FlyweightFactory, Client |
| Proxy | Structural | Provide surrogate or placeholder to control access to another object | Subject, RealSubject, Proxy |
| Chain of Responsibility | Behavioral | Avoid coupling sender to receiver by giving multiple objects a chance to handle request | Handler, ConcreteHandler, Client |
| Command | Behavioral | Encapsulate request as object to parameterize clients, queue requests, and support undo | Command, ConcreteCommand, Invoker, Receiver, Client |
| Interpreter | Behavioral | Define grammar representation and interpreter for a language | AbstractExpression, TerminalExpression, NonterminalExpression, Context, Client |
| Iterator | Behavioral | Provide way to access elements of aggregate sequentially without exposing representation | Iterator, ConcreteIterator, Aggregate, ConcreteAggregate |
| Mediator | Behavioral | Define object that encapsulates how a set of objects interact | Mediator, ConcreteMediator, Colleague |
| Memento | Behavioral | Capture and externalize object's internal state for later restoration without violating encapsulation | Memento, Originator, Caretaker |
| Observer | Behavioral | Define one-to-many dependency so dependents are notified automatically of state changes | Subject, Observer, ConcreteSubject, ConcreteObserver |
| State | Behavioral | Allow object to alter behavior when internal state changes (appear to change class) | Context, State, ConcreteState |
| Strategy | Behavioral | Define family of algorithms, encapsulate each, and make them interchangeable | Strategy, ConcreteStrategy, Context |
| Template Method | Behavioral | Define algorithm skeleton, deferring some steps to subclasses | AbstractClass, ConcreteClass |
| Visitor | Behavioral | Define new operation on object structure elements without changing their classes | Visitor, ConcreteVisitor, Element, ConcreteElement, ObjectStructure |

---

## 2. Creational Patterns (5)

Patterns that deal with object creation mechanisms.

| Pattern | One-liner | Use When... |
|---------|-----------|-------------|
| **Abstract Factory** | Creates families of related objects without specifying concrete classes | You need platform/family independence; products must be used together; you want to enforce family consistency |
| **Builder** | Constructs complex objects step-by-step with varying representations | Construction involves multiple steps; you need different representations from same process; telescoping constructors appear |
| **Factory Method** | Lets subclasses decide which class to instantiate | A class cannot anticipate object types it must create; framework code needs to create application-specific objects |
| **Prototype** | Creates objects by copying a prototypical instance | Classes are specified at runtime; you want to avoid parallel factory hierarchies; cloning is cheaper than construction |
| **Singleton** | Ensures exactly one instance exists with global access | Exactly one instance must exist system-wide; you need controlled access to a shared resource |

---

## 3. Structural Patterns (7)

Patterns that deal with object composition and relationships.

| Pattern | One-liner | Use When... |
|---------|-----------|-------------|
| **Adapter** | Converts one interface to another that clients expect | You need to use an existing class with incompatible interface; integrating legacy or third-party code |
| **Bridge** | Separates abstraction from implementation for independent variation | You need to avoid permanent binding between abstraction and implementation; both hierarchies should extend independently |
| **Composite** | Treats individual objects and compositions uniformly in tree structures | You need part-whole hierarchies; clients should ignore difference between leaf and composite objects |
| **Decorator** | Adds responsibilities to objects dynamically as flexible alternative to subclassing | You need to add behaviors dynamically; subclass explosion for feature combinations is impractical |
| **Facade** | Provides simplified interface to complex subsystem | You need to reduce coupling between clients and subsystem; subsystem complexity is leaking into client code |
| **Flyweight** | Shares objects to support large numbers of fine-grained objects efficiently | Application uses many similar objects; storage costs are high; most state can be made extrinsic |
| **Proxy** | Controls access to another object via surrogate | You need lazy loading, remote access, access control, or smart references; object creation is expensive |

---

## 4. Behavioral Patterns (11)

Patterns that deal with object communication and responsibility.

| Pattern | One-liner | Use When... |
|---------|-----------|-------------|
| **Chain of Responsibility** | Passes request along chain of handlers until one handles it | Multiple objects may handle request; handler not known a priori; request should pass through potential handlers |
| **Command** | Encapsulates request as object for parameterization, queuing, and undo | You need to decouple invoker from executor; support undo/redo; queue or log requests |
| **Interpreter** | Defines grammar representation and interpreter for a language | A problem occurs often enough to express as simple language; you need DSL or expression evaluation |
| **Iterator** | Provides sequential access to aggregate elements without exposing representation | You need uniform traversal interface; multiple traversals needed; hide internal collection structure |
| **Mediator** | Centralizes complex communications between objects | Objects communicate in complex ways; reuse is difficult due to inter-object references |
| **Memento** | Captures object state for later restoration without breaking encapsulation | You need undo/redo or checkpoints; object state must be saved externally; encapsulation must be preserved |
| **Observer** | Notifies dependents automatically when subject state changes | Multiple objects depend on one object's state; loose coupling between data source and consumers needed |
| **State** | Allows object to alter behavior when internal state changes | Behavior depends on state and must change at runtime; operations have large conditionals checking state |
| **Strategy** | Defines interchangeable algorithm family | You need different algorithm variants; conditional statements select behaviors; clients should choose algorithms |
| **Template Method** | Defines algorithm skeleton with steps deferred to subclasses | Subclasses share algorithm structure but differ in specific steps; you want to control extension points |
| **Visitor** | Defines new operations without changing element classes | Many distinct operations needed on stable object structure; adding operations is more common than adding elements |

---

## 5. Pattern Relationships

### Patterns That Work Together

| Pattern Combination | Relationship |
|---------------------|--------------|
| **Abstract Factory + Factory Method** | Abstract factories often use factory methods to create products |
| **Abstract Factory + Singleton** | Concrete factories are often singletons |
| **Builder + Composite** | Builder often constructs composite structures |
| **Composite + Iterator** | Iterator traverses composite structures |
| **Composite + Visitor** | Visitor operates over composite tree nodes |
| **Composite + Chain of Responsibility** | Parent links can form chain of responsibility |
| **Composite + Decorator** | Often share common parent class; can be combined |
| **Command + Memento** | Command uses memento to store state for undo |
| **Command + Composite** | MacroCommand is command composite pattern |
| **Factory Method + Template Method** | Factory methods often called within template methods |
| **Flyweight + Composite** | Flyweights share composite leaf nodes |
| **Flyweight + State/Strategy** | State and Strategy objects are often flyweights |
| **Iterator + Memento** | Iterator can use memento for traversal state |
| **Mediator + Observer** | Colleagues communicate with mediator via observer |
| **Observer + Mediator** | ChangeManager mediates between subjects and observers |
| **State + Singleton** | State objects are often singletons |
| **Template Method + Strategy** | Template uses inheritance; Strategy uses delegation for same goal |

### Alternative Patterns (Choose One)

| Problem Domain | Alternatives | Decision Criteria |
|----------------|--------------|-------------------|
| **Object Creation** | Factory Method vs Abstract Factory vs Prototype | Single product type vs product families vs runtime-specified classes |
| **Algorithm Variation** | Strategy vs Template Method | Composition vs inheritance; entire algorithm vs parts of algorithm |
| **Interface Incompatibility** | Adapter vs Facade | Single class adaptation vs subsystem simplification |
| **Behavior Extension** | Decorator vs Strategy | Add responsibilities vs replace algorithm |
| **State-Dependent Behavior** | State vs Strategy | State changes automatically vs client selects strategy |
| **Object Structure Operations** | Visitor vs Iterator | Multiple operations on elements vs sequential access |
| **Request Handling** | Chain of Responsibility vs Mediator | Pass along chain vs centralize in mediator |
| **Object Access Control** | Proxy vs Decorator | Control access vs add responsibilities |

---

## 6. Quick Lookup by Problem

| Problem | Consider These Patterns |
|---------|-------------------------|
| Object creation complexity | Factory Method, Abstract Factory, Builder |
| Creating families of related objects | Abstract Factory |
| Step-by-step construction | Builder |
| Copying existing objects | Prototype |
| Single instance requirement | Singleton |
| Interface incompatibility | Adapter, Facade |
| Decoupling abstraction from implementation | Bridge |
| Part-whole hierarchies | Composite |
| Adding behavior dynamically | Decorator, Strategy |
| Simplifying complex subsystem | Facade |
| Many similar objects (memory) | Flyweight |
| Lazy loading / access control | Proxy |
| Request routing to unknown handler | Chain of Responsibility |
| Undo/redo functionality | Command, Memento |
| Encapsulating requests | Command |
| DSL / expression evaluation | Interpreter |
| Collection traversal | Iterator |
| Complex object interactions | Mediator |
| State snapshots / checkpoints | Memento |
| Event notification / pub-sub | Observer |
| State-dependent behavior | State, Strategy |
| Interchangeable algorithms | Strategy |
| Algorithm skeleton with variants | Template Method |
| Operations on object structure | Visitor |
| Decoupling sender from receiver | Command, Chain of Responsibility, Mediator |
| Runtime behavior changes | State, Strategy, Decorator |
| Subclass explosion | Decorator, Strategy, Bridge |
| Tight coupling | Observer, Mediator, Facade |

---

## 7. Pattern Selection Guide

### By Symptom

| Symptom | Pattern to Consider |
|---------|---------------------|
| Switch/if-else chains on type | Strategy, State, Visitor |
| Switch/if-else on object state | State |
| Telescoping constructors | Builder |
| Subclass explosion | Decorator, Strategy, Bridge |
| Scattered concrete class instantiation | Factory Method, Abstract Factory |
| Hard-coded class names | Factory Method, Prototype |
| Tight coupling to subsystem | Facade |
| Many-to-many object relationships | Mediator |
| Manual state propagation | Observer |
| Duplicated algorithm structure | Template Method |
| Large conditional for request handling | Chain of Responsibility |
| High memory from many objects | Flyweight |

### By Design Goal

| Goal | Pattern |
|------|---------|
| Hide object creation | Factory Method, Abstract Factory, Builder, Prototype |
| Hide object structure | Composite, Decorator, Proxy |
| Hide platform dependencies | Abstract Factory, Bridge |
| Hide algorithms | Strategy, Template Method |
| Hide state | State, Memento |
| Hide traversal | Iterator |
| Hide object interactions | Mediator, Chain of Responsibility |
| Hide event notification | Observer |

---

## Quick Reference Notes

### Creational Pattern Selection
- **One product varying**: Factory Method
- **Product families**: Abstract Factory
- **Complex construction**: Builder
- **Expensive construction**: Prototype
- **Global single instance**: Singleton

### Structural Pattern Selection
- **Interface mismatch**: Adapter
- **Two varying dimensions**: Bridge
- **Tree/hierarchy**: Composite
- **Dynamic features**: Decorator
- **Subsystem complexity**: Facade
- **Memory optimization**: Flyweight
- **Access control**: Proxy

### Behavioral Pattern Selection
- **Request routing**: Chain of Responsibility
- **Encapsulate action**: Command
- **Mini-language**: Interpreter
- **Collection access**: Iterator
- **Object coordination**: Mediator
- **Snapshot/undo**: Memento
- **Event notification**: Observer
- **State machine**: State
- **Algorithm swap**: Strategy
- **Algorithm skeleton**: Template Method
- **Operations on structure**: Visitor
