```yaml
---
name: gof-mediator
classification: Behavioral / Object
description: Many objects communicate in complex, unstructured ways creating tight coupling; objects refer to each other explicitly making reuse difficult and behavior changes require extensive subclassing.
---
```

## INTENT

Define an object that encapsulates how a set of objects interact. Mediator promotes loose coupling by keeping objects from referring to each other explicitly, and it lets you vary their interaction independently.

## ALSO KNOWN AS

None

## PROBLEM INDICATORS

When you see:
- A set of objects communicating in well-defined but complex ways with unstructured, difficult-to-understand interdependencies
- Objects that are difficult to reuse because they refer to and communicate with many other objects
- Behavior distributed between several classes that should be customizable without extensive subclassing
- Many-to-many relationships between objects creating a tangled web of connections
- System acting monolithic despite being partitioned into many objects
- Widgets or components in a UI with complex interdependencies (e.g., buttons disabled based on field contents, selections affecting other fields)
- Changes to one object requiring updates to many other objects

## KEY INSIGHT

Instead of having objects communicate directly with each other (creating N-to-N connections), introduce a central mediator that all objects communicate through, reducing connections to N-to-1 and localizing interaction logic in a single place.

## PARTICIPANTS

| Role | Responsibility |
|------|---------------|
| Mediator (DialogDirector) | Defines an interface for communicating with Colleague objects |
| ConcreteMediator (FontDialogDirector) | Implements cooperative behavior by coordinating Colleague objects; knows and maintains its colleagues |
| Colleague classes (ListBox, EntryField) | Each Colleague class knows its Mediator object; each colleague communicates with its mediator whenever it would have otherwise communicated with another colleague |

## CONSEQUENCES

**Benefits:**

1. It limits subclassing. A mediator localizes behavior that otherwise would be distributed among several objects. Changing this behavior requires subclassing Mediator only; Colleague classes can be reused as is.

2. It decouples colleagues. A mediator promotes loose coupling between colleagues. You can vary and reuse Colleague and Mediator classes independently.

3. It simplifies object protocols. A mediator replaces many-to-many interactions with one-to-many interactions between the mediator and its colleagues. One-to-many relationships are easier to understand, maintain, and extend.

4. It abstracts how objects cooperate. Making mediation an independent concept and encapsulating it in an object lets you focus on how objects interact apart from their individual behavior. That can help clarify how objects interact in a system.

**Liabilities:**

1. It centralizes control. The Mediator pattern trades complexity of interaction for complexity in the mediator. Because a mediator encapsulates protocols, it can become more complex than any individual colleague. This can make the mediator itself a monolith that's hard to maintain.

## WHEN NOT TO USE

- When interactions between objects are simple and well-defined without complex interdependencies
- When the mediator would become a "god object" that knows too much and does too much
- When objects need to communicate with many different groups (multiple mediators become unwieldy)
- When the coordination logic is trivial and doesn't justify the extra indirection
- When you need maximum performance and the indirection overhead is unacceptable
- When colleague objects naturally form a hierarchy (consider Composite or Chain of Responsibility instead)

## RELATED PATTERNS

| Pattern | Relationship |
|---------|-------------|
| Facade | Differs from Mediator in that it abstracts a subsystem of objects to provide a more convenient interface. Its protocol is unidirectional (Facade objects make requests of the subsystem classes but not vice versa). In contrast, Mediator enables cooperative behavior that colleague objects don't or can't provide, and the protocol is multidirectional. |
| Observer | Colleagues can communicate with the mediator using the Observer pattern. Colleague classes act as Subjects, sending notifications to the mediator whenever they change state. The mediator responds by propagating the effects of the change to other colleagues. |

## MODERN CONTEXT

- **Event Bus / Message Broker**: Modern event-driven architectures use mediators (e.g., Redux store, RxJS Subject, EventEmitter) to coordinate state changes across components
- **React Context + useReducer**: Acts as a mediator for component state coordination without prop drilling
- **Angular Services**: Injectable services often serve as mediators between components
- **Spring ApplicationEventPublisher**: Mediates between beans through application events
- **MediatR (.NET)**: Library implementing the mediator pattern for CQRS and request/response communication
- **Vue.js Event Bus**: Central event hub for component communication (though composition API now preferred)
- **WebSocket/SignalR Hubs**: Server-side mediators coordinating real-time client communication
- **Microservices**: Message queues (RabbitMQ, Kafka) act as mediators between services
- **State Management Libraries**: Vuex, MobX, Zustand all implement mediator-like coordination
- **TypeScript**: Interface-based mediator contracts enable strong typing of colleague-mediator communication

## SKILL ACTIONS

```
TRIGGER: When multiple objects have complex, interconnected communication creating a web of dependencies; when objects cannot be reused because they reference too many peers; when UI components have intricate interdependencies
ACTION: Introduce a Mediator that encapsulates interaction logic; have colleagues communicate only through the mediator; implement WidgetChanged/Notify pattern for colleague-to-mediator communication
COUNTER-INDICATOR: When the mediator becomes a god object; when interactions are simple; when performance overhead of indirection is unacceptable; when only 2-3 objects interact
```

