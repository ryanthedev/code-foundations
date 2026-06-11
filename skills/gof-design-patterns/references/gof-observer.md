```yaml
---
name: gof-observer
classification: Behavioral / Object
description: Multiple objects need to stay synchronized with a source object's state changes; you find yourself manually propagating updates or creating tight coupling between data and its views.
---
```

## INTENT

Define a one-to-many dependency between objects so that when one object changes state, all its dependents are notified and updated automatically.

## ALSO KNOWN AS

Dependents, Publish-Subscribe

## PROBLEM INDICATORS

When you see:
- Multiple objects need to react to changes in another object's state
- Tight coupling between data sources and their displays/consumers
- Manual propagation of state changes across related objects
- An abstraction has two aspects, one dependent on the other
- A change to one object requires changing an unknown number of other objects
- Objects should notify others without knowing who they are
- Consistency between related objects is hard to maintain
- UI components need to stay synchronized with underlying data
- You need to add/remove interested parties dynamically at runtime

## KEY INSIGHT

The subject maintains a list of dependents and notifies them automatically of state changes, allowing loose coupling between the source of changes and the objects that react to those changes.

## PARTICIPANTS

| Role | Responsibility |
|------|---------------|
| Subject | Knows its observers; provides interface for attaching/detaching Observer objects; any number of Observers may observe a subject |
| Observer | Defines an updating interface for objects that should be notified of changes in a subject |
| ConcreteSubject | Stores state of interest to ConcreteObserver objects; sends notification to observers when state changes |
| ConcreteObserver | Maintains a reference to a ConcreteSubject object; stores state that should stay consistent with subject's; implements Observer updating interface to keep state consistent with subject's |

## CONSEQUENCES

**Benefits:**

1. Abstract coupling between Subject and Observer - The subject only knows it has a list of observers conforming to the abstract Observer interface; it doesn't know concrete classes. Subject and Observer can belong to different layers of abstraction, keeping system layering intact.

2. Support for broadcast communication - Unlike ordinary requests, notifications don't need to specify receivers. Notifications are broadcast automatically to all subscribed objects. The subject doesn't care how many interested objects exist; observers can be added/removed at any time.

3. Subjects and observers can be varied independently - You can reuse subjects without reusing their observers and vice versa. You can add observers without modifying the subject or other observers.

**Liabilities:**

1. Unexpected updates - Observers have no knowledge of each other's presence, so they can be blind to the ultimate cost of changing the subject. A seemingly innocuous operation may cause a cascade of updates to observers and their dependent objects.

2. Spurious updates - Dependency criteria that aren't well-defined or maintained can lead to spurious updates that are hard to track down.

3. Simple update protocol lacks detail - Without additional protocol to help observers discover what changed, observers may be forced to work hard to deduce the changes.

## WHEN NOT TO USE

- When changes are infrequent and polling would be simpler
- When there's only one dependent that will never change (direct call is cleaner)
- When update order matters critically and can't be managed
- When the cost of notification exceeds the benefit (very frequent, small changes)
- When observers need detailed change information and push/pull overhead is excessive
- When circular dependencies between subjects and observers could cause infinite loops
- When synchronous notification could cause performance issues (consider async alternatives)

## RELATED PATTERNS

| Pattern | Relationship |
|---------|-------------|
| Mediator | By encapsulating complex update semantics, the ChangeManager acts as mediator between subjects and observers |
| Singleton | The ChangeManager may use Singleton to make it unique and globally accessible |
| Template Method | Can be used to ensure subject state is self-consistent before notification by making Notify the last operation in the template method |

## MODERN CONTEXT

- **JavaScript/TypeScript**: EventEmitter, RxJS Observables, custom event systems, addEventListener/removeEventListener
- **React**: useState/useEffect hooks implement observer-like reactivity; Redux store subscriptions; Context API consumers
- **Vue**: Reactive data system with watchers and computed properties
- **Angular**: RxJS-based change detection, @Output EventEmitter decorators
- **Spring**: ApplicationEventPublisher, @EventListener annotations, reactive WebFlux
- **Java**: java.util.Observer (deprecated), PropertyChangeListener, Flow API (reactive streams)
- **.NET**: IObservable/IObserver interfaces, event delegates, Reactive Extensions (Rx.NET)
- **Message Brokers**: Kafka, RabbitMQ, Redis Pub/Sub implement publish-subscribe at system scale
- **State Management**: MobX, Vuex, NgRx all use observer patterns for reactive state
- **Push vs Pull**: Modern implementations often use push model with typed events (discriminated unions) for efficiency

## SKILL ACTIONS

```
TRIGGER: When multiple objects need to stay synchronized with a data source,
         or when you need loose coupling between state changes and reactions to those changes
ACTION: Define Subject interface (attach/detach/notify), Observer interface (update),
        have subject maintain observer list and broadcast changes automatically
COUNTER-INDICATOR: Single dependent that won't change; very frequent micro-updates where
                   notification overhead exceeds benefit; need for strict update ordering
```

