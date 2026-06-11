```yaml
---
name: gof-chain-of-responsibility
classification: Behavioral / Object
description: Use when requests need to pass through multiple potential handlers without the sender knowing which object will handle it, typically seen in event systems, middleware pipelines, or hierarchical UI components.
---
```

## INTENT

Avoid coupling the sender of a request to its receiver by giving more than one object a chance to handle the request. Chain the receiving objects and pass the request along the chain until an object handles it.

## ALSO KNOWN AS

None

## PROBLEM INDICATORS

When you see:
- A sender needs to issue a request but doesn't know which object should handle it
- Multiple objects may handle a request, and the handler isn't known a priori
- You want to issue a request to one of several objects without specifying the receiver explicitly
- The set of objects that can handle a request should be specified dynamically
- Large conditional logic (if/else or switch) determining which handler to invoke
- Context-sensitive behavior where handling depends on runtime context (e.g., help systems, event bubbling)
- Hierarchical structures where requests propagate from specific to general (child to parent)

## KEY INSIGHT

Decouple senders from receivers by letting multiple objects have a chance to handle the request. The request has an "implicit receiver" - it travels along the chain until someone handles it or it falls off the end.

## PARTICIPANTS

| Role | Responsibility |
|------|---------------|
| Handler (HelpHandler) | Defines an interface for handling requests; optionally implements the successor link |
| ConcreteHandler (PrintButton, PrintDialog) | Handles requests it is responsible for; can access its successor; if it can handle the request, it does so, otherwise forwards to successor |
| Client | Initiates the request to a ConcreteHandler object on the chain |

## CONSEQUENCES

**Benefits:**

1. Reduced coupling. The pattern frees an object from knowing which other object handles a request. An object only has to know that a request will be handled "appropriately." Both the receiver and the sender have no explicit knowledge of each other, and an object in the chain doesn't have to know about the chain's structure. Instead of objects maintaining references to all candidate receivers, they keep a single reference to their successor.

2. Added flexibility in assigning responsibilities to objects. Chain of Responsibility gives you added flexibility in distributing responsibilities among objects. You can add or change responsibilities for handling a request by adding to or otherwise changing the chain at run-time. You can combine this with subclassing to specialize handlers statically.

**Liabilities:**

1. Receipt isn't guaranteed. Since a request has no explicit receiver, there's no guarantee it'll be handled - the request can fall off the end of the chain without ever being handled. A request can also go unhandled when the chain is not configured properly.

## WHEN NOT TO USE

- When you need guaranteed handling of every request
- When the handler must be known explicitly by the sender
- When requests must be processed in a specific, fixed order that cannot change
- When the overhead of traversing the chain is unacceptable for performance-critical paths
- When debugging chain traversal would be too complex for your needs
- When a simple direct method call or Strategy pattern would suffice

## RELATED PATTERNS

| Pattern | Relationship |
|---------|-------------|
| Composite | Chain of Responsibility is often applied in conjunction with Composite. A component's parent can act as its successor in the chain. |

## MODERN CONTEXT

- **Express.js / Koa middleware**: HTTP request handling chains where each middleware can process or pass to `next()`
- **React event bubbling**: Events propagate up the component tree; any component can handle or let it bubble
- **DOM event propagation**: Native browser event bubbling and capturing phases
- **Spring Security filter chains**: Authentication/authorization filters process requests sequentially
- **Redux middleware**: Actions pass through middleware chain before reaching reducers
- **Node.js streams**: Piped streams form processing chains
- **Logging frameworks**: Log levels and appenders often use chain patterns
- **Exception handling**: Try-catch chains where exceptions propagate up the call stack
- **Validation pipelines**: Input validation through multiple validators
- **TypeScript/JavaScript**: Often implemented with arrays of handler functions and `.find()` or reduce patterns

## SKILL ACTIONS

```
TRIGGER: When a request could be handled by multiple objects and you don't want the sender to know which one handles it; when you need dynamic handler assignment; when building middleware or event systems
ACTION: Define a Handler interface with a handleRequest method and successor link. Create ConcreteHandlers that either handle the request or forward to successor. Chain handlers from most specific to most general.
COUNTER-INDICATOR: When every request MUST be handled (no fallthrough acceptable); when you need to know exactly which handler processed the request; when simple conditionals or Strategy pattern would be clearer
```

