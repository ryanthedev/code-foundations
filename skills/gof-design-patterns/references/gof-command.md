---
name: gof-command
classification: Behavioral / Object
description: Use when you need to decouple the object that invokes an operation from the one that performs it, or when you need to queue, log, or undo requests.
---

## INTENT

Encapsulate a request as an object, thereby letting you parameterize clients with different requests, queue or log requests, and support undoable operations.

## ALSO KNOWN AS

Action, Transaction

## PROBLEM INDICATORS

When you see:
- UI elements (buttons, menus) that need to trigger operations on unknown targets
- Need to parameterize objects with actions to perform at runtime
- Operations that need to be queued and executed at different times
- Requirements for undo/redo functionality
- Need to log changes for crash recovery or audit trails
- System needs to be structured around high-level operations built on primitives (transactions)
- Tight coupling between request invokers and request handlers
- Callback functions proliferating throughout the codebase
- Difficulty sharing the same action between multiple UI elements (menu + toolbar button)
- Need to support command scripting or macro recording

## KEY INSIGHT

By turning a request into a standalone object, you gain the ability to pass, store, queue, and manipulate requests as first-class entities, enabling undo/redo, logging, and decoupling invokers from receivers.

## PARTICIPANTS

| Role | Responsibility |
|------|---------------|
| Command | Declares an interface for executing an operation (Execute) |
| ConcreteCommand (PasteCommand, OpenCommand) | Defines a binding between a Receiver object and an action; implements Execute by invoking the corresponding operation(s) on Receiver |
| Client (Application) | Creates a ConcreteCommand object and sets its receiver |
| Invoker (MenuItem) | Asks the command to carry out the request |
| Receiver (Document, Application) | Knows how to perform the operations associated with carrying out a request; any class may serve as a Receiver |

## CONSEQUENCES

**Benefits:**

1. Command decouples the object that invokes the operation from the one that knows how to perform it
2. Commands are first-class objects that can be manipulated and extended like any other object
3. You can assemble commands into a composite command (MacroCommand) using the Composite pattern
4. It is easy to add new Commands because you do not have to change existing classes
5. Commands can have a lifetime independent of the original request, enabling transfer across processes
6. Supports unlimited-level undo and redo via a history list
7. Supports logging changes for crash recovery by augmenting the Command interface with load and store operations
8. Enables command scripting by composing commands into larger ones
9. Menu and push button can share the same concrete Command instance for the same feature

**Liabilities:**

1. Proliferation of command classes - each distinct action requires a ConcreteCommand subclass
2. Hysteresis/error accumulation in undo process - errors can accumulate as commands are repeatedly executed and unexecuted
3. Undoable commands may need to be copied before being placed on the history list if their state varies across invocations
4. Commands that store undo state require additional memory
5. Complexity in determining how "intelligent" a command should be (simple receiver binding vs. self-contained logic)

## WHEN NOT TO USE

- Simple direct method calls suffice and no decoupling is needed
- Operations are trivial and do not need to be queued, logged, or undone
- The overhead of creating command objects is not justified by the flexibility gained
- Single, one-off operations that will never be reused or composed
- When callbacks or lambdas provide sufficient decoupling without the ceremony of command objects
- When the receiver is always known at compile time and will never change

## RELATED PATTERNS

| Pattern | Relationship |
|---------|-------------|
| Composite | Can be used to implement MacroCommands (commands that execute a sequence of other commands) |
| Memento | Can keep state the command requires to undo its effect, giving access to information without exposing object internals |
| Prototype | A command that must be copied before being placed on the history list acts as a Prototype |
| Chain of Responsibility | Commands in THINK library are passed along a Chain of Responsibility for consumption |

## MODERN CONTEXT

- **TypeScript/JavaScript**: Commands naturally map to function objects, closures, or classes implementing an execute interface; Redux actions are a form of Command pattern
- **React**: useReducer hook dispatch actions that are essentially commands; state management libraries (Redux, MobX) use command-like action objects
- **Event Sourcing**: Commands represent intent to change state; the pattern is foundational to CQRS (Command Query Responsibility Segregation)
- **Task Queues**: Message brokers (RabbitMQ, Kafka) and job queues (Celery, Bull) treat work items as serializable command objects
- **Spring Framework**: Spring's CommandLineRunner and ApplicationRunner interfaces; transaction management follows command semantics
- **Undo Libraries**: Libraries like Immer for immutable state, or dedicated undo libraries, implement sophisticated command history
- **CLI Tools**: Command-line applications often use command pattern for subcommands (git commit, git push are commands)
- **Game Development**: Input handling, replay systems, and AI action queues commonly use Command pattern
- **Microservices**: API requests encapsulated as command DTOs for service orchestration

## SKILL ACTIONS

```
TRIGGER: When you need to decouple request invocation from execution, support undo/redo, queue operations, or log changes for recovery
ACTION: Encapsulate requests as Command objects with Execute (and optionally Unexecute) methods; create ConcreteCommand classes that bind receivers to actions; use Invoker to trigger commands
COUNTER-INDICATOR: When direct method calls suffice, operations are trivial, or the overhead of command objects is not justified by flexibility needs
```

## CSO KEYWORDS

command, action, transaction, request encapsulation, undo, redo, history list, execute, unexecute, invoker, receiver, callback replacement, queue requests, log requests, macro command, composite command, undoable operations, decouple invocation, parameterize actions, first-class request, command history, reversible operations, transaction modeling, menu actions, button actions, event sourcing, CQRS, task queue, job queue, redux actions, dispatch
