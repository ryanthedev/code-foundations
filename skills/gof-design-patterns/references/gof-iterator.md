---
name: gof-iterator
classification: Behavioral / Object
description: |
  When you need to access elements of an aggregate object sequentially without exposing its internal representation, or when you need multiple traversals or a uniform interface for traversing different aggregate structures, use Iterator to encapsulate the traversal mechanism.
---

## INTENT

Provide a way to access the elements of an aggregate object sequentially without exposing its underlying representation.

## ALSO KNOWN AS

Cursor

## PROBLEM INDICATORS

When you see:
- Client code that needs to traverse a collection but shouldn't know about its internal structure (array, linked list, tree, etc.)
- The List/Aggregate interface is bloated with operations for different traversals
- Need for multiple simultaneous traversals on the same collection
- Client code commits to a specific aggregate structure, making it hard to change implementations
- Code that duplicates traversal logic across multiple clients
- Need to support different traversal algorithms (forward, backward, filtered, etc.) on the same aggregate

## KEY INSIGHT

The key idea is to take the responsibility for access and traversal out of the list object and put it into a separate iterator object. The iterator keeps track of the current element and knows which elements have been traversed already. This separation allows multiple traversals to be in progress simultaneously and enables different traversal policies without modifying the aggregate's interface.

## PARTICIPANTS

| Role | Responsibility |
|------|---------------|
| Iterator | Defines an interface for accessing and traversing elements (First, Next, IsDone, CurrentItem) |
| ConcreteIterator | Implements the Iterator interface; keeps track of the current position in the traversal of the aggregate |
| Aggregate | Defines an interface for creating an Iterator object (CreateIterator factory method) |
| ConcreteAggregate | Implements the Iterator creation interface to return an instance of the proper ConcreteIterator |

## CONSEQUENCES

**Benefits:**

1. It supports variations in the traversal of an aggregate. Complex aggregates may be traversed in many ways (inorder, preorder, filtered, etc.). Iterators make it easy to change the traversal algorithm: just replace the iterator instance with a different one. You can also define Iterator subclasses to support new traversals.

2. Iterators simplify the Aggregate interface. Iterator's traversal interface obviates the need for a similar interface in Aggregate, thereby simplifying the aggregate's interface.

3. More than one traversal can be pending on an aggregate. An iterator keeps track of its own traversal state. Therefore you can have more than one traversal in progress at once.

**Liabilities:**

1. External iterators vs. internal iterators trade-off. External iterators are more flexible (e.g., comparing two collections for equality) but require clients to advance the traversal explicitly. Internal iterators are easier to use but less flexible, especially in languages without closures.

2. Who defines the traversal algorithm. If the iterator is responsible for the traversal algorithm, it's easy to use different algorithms on the same aggregate. However, the traversal algorithm might need to access private variables of the aggregate, which violates encapsulation.

3. Robustness concerns. Modifying an aggregate while traversing it can be dangerous (accessing elements twice or missing them). Robust iterators require registering with the aggregate and being notified of changes.

4. Polymorphic iterators have costs. They require dynamic allocation by a factory method, and the client is responsible for deleting them (risk of memory leaks). A Proxy can help ensure proper cleanup.

## WHEN NOT TO USE

- When the collection is trivially small and a simple index-based loop suffices
- When you only ever need one type of traversal and the aggregate can expose it directly
- When the language provides built-in iteration mechanisms that meet all requirements (e.g., for-of loops, generators)
- When traversal logic is so tightly coupled to the aggregate's internal structure that separation provides no benefit
- When the overhead of creating iterator objects is unacceptable for performance-critical code

## RELATED PATTERNS

| Pattern | Relationship |
|---------|-------------|
| Composite | Iterators are often applied to recursive structures such as Composites. External iterators can be difficult to implement over recursive aggregates because a position may span many levels of nested aggregates. |
| Factory Method | Polymorphic iterators rely on factory methods (CreateIterator) to instantiate the appropriate Iterator subclass. The Factory Method approach gives rise to two class hierarchies: one for aggregates and another for iterators. |
| Memento | Often used in conjunction with Iterator. An iterator can use a memento to capture the state of an iteration. The iterator stores the memento internally. Cursors are a simple example of Memento. |

## MODERN CONTEXT

- **JavaScript/TypeScript**: The Iterator protocol and `Symbol.iterator` are built into the language. Generators (`function*`) provide an elegant way to implement iterators. The `for...of` loop works with any iterable.

- **Python**: The iterator protocol (`__iter__`, `__next__`) is fundamental. Generators and generator expressions are idiomatic. The `itertools` module provides powerful iterator combinators.

- **Java**: The `Iterator<E>` and `Iterable<E>` interfaces are core to the Collections Framework. Enhanced for-loops work with iterables. Streams provide functional-style iteration with lazy evaluation.

- **C#**: `IEnumerable<T>` and `IEnumerator<T>` with `yield return` for generator-style iterators. LINQ provides powerful query capabilities built on iterators.

- **Rust**: The `Iterator` trait with methods like `map`, `filter`, `fold`. Iterators are zero-cost abstractions due to compiler optimizations.

- **React**: The pattern appears in rendering lists with `map()`, custom hooks that iterate over data, and virtualized list components.

- **Modern streaming/pagination**: Async iterators for paginated API responses, cursor-based pagination, infinite scroll implementations.

## SKILL ACTIONS

```
TRIGGER: "traverse collection" AND ("hide internal structure" OR "multiple traversal methods" OR "polymorphic iteration")
ACTION: Create Iterator interface with First/Next/IsDone/CurrentItem; have Aggregate provide CreateIterator factory method
COUNTER-INDICATOR: Collection is trivially small or language provides sufficient built-in iteration
```

```
TRIGGER: "aggregate interface bloated" AND "traversal operations"
ACTION: Extract traversal responsibility into separate Iterator classes to simplify the Aggregate interface
COUNTER-INDICATOR: Only one traversal type is ever needed
```

```
TRIGGER: "multiple simultaneous traversals" OR "different traversal algorithms"
ACTION: Implement external iterators that maintain independent traversal state
COUNTER-INDICATOR: Internal iteration with callbacks/closures is sufficient
```

```
TRIGGER: "change aggregate implementation" AND "client code unchanged"
ACTION: Use abstract Aggregate with CreateIterator factory method; clients program to Iterator interface
COUNTER-INDICATOR: Aggregate implementation is stable and won't change
```

## CSO KEYWORDS

iterator, cursor, traversal, aggregate, collection, sequential access, external iterator, internal iterator, polymorphic iteration, CreateIterator, factory method, IsDone, CurrentItem, First, Next, robust iterator, null iterator, filtering iterator, tree traversal, composite traversal, iterable, generator, yield, for-of, enumerate, stream
