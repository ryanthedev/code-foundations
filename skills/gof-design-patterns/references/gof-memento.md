---
name: gof-memento
classification: Behavioral / Object
description: Need to implement undo/redo, checkpoints, or state recovery without exposing internal object structure; objects encapsulate state that must be saved externally.
---

## INTENT

Without violating encapsulation, capture and externalize an object's internal state so that the object can be restored to this state later.

## ALSO KNOWN AS

Token

## PROBLEM INDICATORS

When you see:
- Need to implement undo/redo functionality for complex objects
- Requirement to save checkpoints or snapshots of object state
- Objects that encapsulate state which must be saved externally for recovery
- Direct state access would expose implementation details and break encapsulation
- Constraint solvers or editors where simple reversal operations are insufficient
- Need to restore objects to previous states after tentative operations or errors
- Storage management burden on originators becoming unwieldy

## KEY INSIGHT

A memento is an opaque object that stores a snapshot of another object's internal state. Only the originator can store and retrieve information from the memento, keeping the state hidden from all other objects while still allowing external storage and restoration.

## PARTICIPANTS

| Role | Responsibility |
|------|---------------|
| Memento (SolverState) | Stores internal state of the Originator object (as much or as little as necessary). Protects against access by objects other than the originator. Has two interfaces: narrow (for Caretaker - can only pass memento around) and wide (for Originator - full data access). |
| Originator (ConstraintSolver) | Creates a memento containing a snapshot of its current internal state. Uses the memento to restore its internal state. |
| Caretaker (undo mechanism) | Responsible for the memento's safekeeping. Never operates on or examines the contents of a memento. |

## CONSEQUENCES

**Benefits:**

1. Preserving encapsulation boundaries - Memento avoids exposing information that only an originator should manage but that must be stored nevertheless outside the originator. The pattern shields other objects from potentially complex Originator internals, thereby preserving encapsulation boundaries.

2. It simplifies Originator - In other encapsulation-preserving designs, Originator keeps the versions of internal state that clients have requested. That puts all the storage management burden on Originator. Having clients manage the state they ask for simplifies Originator and keeps clients from having to notify originators when they're done.

**Liabilities:**

1. Using mementos might be expensive - Mementos might incur considerable overhead if Originator must copy large amounts of information to store in the memento or if clients create and return mementos to the originator often enough. Unless encapsulating and restoring Originator state is cheap, the pattern might not be appropriate.

2. Defining narrow and wide interfaces - It may be difficult in some languages to ensure that only the originator can access the memento's state.

3. Hidden costs in caring for mementos - A caretaker is responsible for deleting the mementos it cares for. However, the caretaker has no idea how much state is in the memento. Hence an otherwise lightweight caretaker might incur large storage costs when it stores mementos.

## WHEN NOT TO USE

- When the state to be saved is very large and copying would be prohibitively expensive
- When state changes are frequent and creating mementos would cause performance issues
- When the language does not support two levels of interface visibility (narrow/wide)
- When simple inverse operations can reliably restore previous state
- When state versioning can be handled entirely within the originator without external storage

## RELATED PATTERNS

| Pattern | Relationship |
|---------|-------------|
| Command | Commands can use mementos to maintain state for undoable operations. The command stores a memento before executing to enable undo. |
| Iterator | Mementos can be used for iteration - the iteration state object is a memento representing the current position in a collection, completely hidden from clients. |

## MODERN CONTEXT

- **TypeScript/JavaScript**: Use private fields (`#state`) or closures to implement narrow/wide interfaces. Libraries like Immer provide immutable state snapshots naturally suited for mementos.
- **React/Redux**: Redux time-travel debugging is essentially a Memento implementation - each state snapshot is a memento, the store is the originator, and Redux DevTools is the caretaker.
- **Java**: Use nested classes where the Memento is a private inner class of the Originator, providing natural access control.
- **Event Sourcing**: Modern alternative where state changes are stored as events rather than snapshots; can reconstruct any previous state by replaying events.
- **Serialization**: JSON.stringify/parse or structured cloning can create simple mementos, but may expose more state than intended.
- **Undo Libraries**: Libraries like `use-undo` in React or `undo-manager` implement caretaker functionality with memento stacks.
- **Database Transactions**: Savepoints in databases are a form of memento for transaction state.
- **Git**: Each commit is effectively a memento of the entire repository state.

## SKILL ACTIONS

```
TRIGGER: Need to save and restore object state without exposing internal structure; implementing undo/redo, checkpoints, or rollback functionality
ACTION: Create a Memento class that only the Originator can fully access; have Originator create mementos with CreateMemento() and restore via SetMemento(); Caretaker stores mementos but never examines contents
COUNTER-INDICATOR: State is trivially small, inverse operations are reliable, or memento creation would be too expensive for the use case
```

## CSO KEYWORDS

memento, token, undo, redo, checkpoint, snapshot, state restoration, encapsulation, originator, caretaker, rollback, history, save state, restore state, internal state, state management, undo mechanism, constraint solver, time travel, versioning, state snapshot, opaque object
