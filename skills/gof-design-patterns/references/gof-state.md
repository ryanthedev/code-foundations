---
name: gof-state
classification: Behavioral / Object
description: "Use when an object's behavior depends on its state and must change at runtime; Symptoms: large switch/if-else statements checking object state, operations scattered with same conditional structure, state represented by enumerated constants"
---

## INTENT

Allow an object to alter its behavior when its internal state changes. The object will appear to change its class.

## ALSO KNOWN AS

Objects for States

## PROBLEM INDICATORS

- An object's behavior depends on its state, and it must change its behavior at run-time depending on that state
- Operations have large, multipart conditional statements that depend on the object's state
- State is usually represented by one or more enumerated constants
- Several operations contain the same conditional structure checking state
- Adding a new state requires changing multiple operations, complicating maintenance
- Monolithic if or switch statements scattered throughout the codebase
- State transitions are implicit (just variable assignments) rather than explicit
- Need to treat an object's state as an object in its own right that can vary independently

## KEY INSIGHT

Instead of distributing state-dependent behavior across many conditional statements, encapsulate each state in its own class. The context delegates state-specific requests to the current state object, and state transitions become explicit by swapping one state object for another.

## PARTICIPANTS

| Role | Responsibility |
|------|----------------|
| Context (TCPConnection) | Defines the interface of interest to clients. Maintains an instance of a ConcreteState subclass that defines the current state. |
| State (TCPState) | Defines an interface for encapsulating the behavior associated with a particular state of the Context. |
| ConcreteState subclasses (TCPEstablished, TCPListen, TCPClosed) | Each subclass implements a behavior associated with a state of the Context. |

## CONSEQUENCES

### Benefits

1. **Localizes state-specific behavior and partitions behavior for different states** - The State pattern puts all behavior associated with a particular state into one object. Because all state-specific code lives in a State subclass, new states and transitions can be added easily by defining new subclasses.

2. **Makes state transitions explicit** - When an object defines its current state solely in terms of internal data values, its state transitions have no explicit representation. Introducing separate objects for different states makes the transitions more explicit.

3. **State objects can protect the Context from inconsistent internal states** - State transitions are atomic from the Context's perspective - they happen by rebinding one variable (the Context's State object variable), not several.

4. **State objects can be shared** - If State objects have no instance variables (the state they represent is encoded entirely in their type), then contexts can share a State object. When states are shared this way, they are essentially flyweights with no intrinsic state, only behavior.

### Liabilities

1. **Increases the number of classes** - The pattern distributes behavior for different states across several State subclasses. This increases the number of classes and is less compact than a single class. But such distribution is actually good if there are many states, which would otherwise necessitate large conditional statements.

2. **Decentralized transition logic introduces dependencies** - A disadvantage of decentralizing transition logic is that one State subclass will have knowledge of at least one other, which introduces implementation dependencies between subclasses.

3. **State creation/destruction trade-offs** - Must decide whether to create State objects only when needed and destroy them thereafter, or create them ahead of time and never destroy them. First approach avoids creating unused objects; second avoids destruction costs when state changes occur rapidly.

## WHEN NOT TO USE

- When there are only a few states with simple behavior - the overhead of multiple classes may not be justified
- When state transitions are extremely simple and unlikely to change
- When the state-dependent behavior is minimal and confined to a single method
- When a table-driven state machine would be more appropriate (focus on transitions rather than behavior)
- When the conditional logic is straightforward and easily understood
- When states share significant amounts of behavior (may indicate Strategy pattern instead)

## RELATED PATTERNS

| Pattern | Relationship |
|---------|--------------|
| Flyweight | Explains when and how State objects can be shared. If State objects have no instance variables, they are essentially flyweights. |
| Singleton | State objects are often Singletons - each ConcreteState subclass typically has only one instance. |
| Strategy | Both patterns use composition to change behavior. State allows the object to change its behavior when its state changes; Strategy allows a client to choose among alternative algorithms. |
| Interpreter | Can use State to define parsing contexts. |

## MODERN CONTEXT

### TypeScript Example

```typescript
// State interface
interface OrderState {
  cancel(order: Order): void;
  ship(order: Order): void;
  deliver(order: Order): void;
  getStatus(): string;
}

// Context
class Order {
  private state: OrderState;

  constructor() {
    this.state = new PendingState();
  }

  setState(state: OrderState): void {
    this.state = state;
  }

  cancel(): void {
    this.state.cancel(this);
  }

  ship(): void {
    this.state.ship(this);
  }

  deliver(): void {
    this.state.deliver(this);
  }

  getStatus(): string {
    return this.state.getStatus();
  }
}

// Concrete States
class PendingState implements OrderState {
  cancel(order: Order): void {
    console.log('Order cancelled');
    order.setState(new CancelledState());
  }

  ship(order: Order): void {
    console.log('Order shipped');
    order.setState(new ShippedState());
  }

  deliver(order: Order): void {
    console.log('Cannot deliver - order not shipped yet');
  }

  getStatus(): string {
    return 'Pending';
  }
}

class ShippedState implements OrderState {
  cancel(order: Order): void {
    console.log('Cannot cancel - order already shipped');
  }

  ship(order: Order): void {
    console.log('Order already shipped');
  }

  deliver(order: Order): void {
    console.log('Order delivered');
    order.setState(new DeliveredState());
  }

  getStatus(): string {
    return 'Shipped';
  }
}

class DeliveredState implements OrderState {
  cancel(order: Order): void {
    console.log('Cannot cancel - order already delivered');
  }

  ship(order: Order): void {
    console.log('Cannot ship - order already delivered');
  }

  deliver(order: Order): void {
    console.log('Order already delivered');
  }

  getStatus(): string {
    return 'Delivered';
  }
}

class CancelledState implements OrderState {
  cancel(order: Order): void {
    console.log('Order already cancelled');
  }

  ship(order: Order): void {
    console.log('Cannot ship cancelled order');
  }

  deliver(order: Order): void {
    console.log('Cannot deliver cancelled order');
  }

  getStatus(): string {
    return 'Cancelled';
  }
}
```

### React Example (useReducer as State Machine)

```typescript
import React, { useReducer } from 'react';

// States and actions as discriminated unions
type FetchState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: Error };

type FetchAction<T> =
  | { type: 'FETCH_START' }
  | { type: 'FETCH_SUCCESS'; payload: T }
  | { type: 'FETCH_ERROR'; error: Error }
  | { type: 'RESET' };

// State machine reducer - behavior depends on current state
function fetchReducer<T>(
  state: FetchState<T>,
  action: FetchAction<T>
): FetchState<T> {
  switch (state.status) {
    case 'idle':
      if (action.type === 'FETCH_START') {
        return { status: 'loading' };
      }
      return state;

    case 'loading':
      if (action.type === 'FETCH_SUCCESS') {
        return { status: 'success', data: action.payload };
      }
      if (action.type === 'FETCH_ERROR') {
        return { status: 'error', error: action.error };
      }
      return state;

    case 'success':
    case 'error':
      if (action.type === 'RESET') {
        return { status: 'idle' };
      }
      if (action.type === 'FETCH_START') {
        return { status: 'loading' };
      }
      return state;

    default:
      return state;
  }
}

// Usage in component
function useFetch<T>() {
  const [state, dispatch] = useReducer(fetchReducer<T>, { status: 'idle' });

  const fetch = async (url: string) => {
    dispatch({ type: 'FETCH_START' });
    try {
      const response = await globalThis.fetch(url);
      const data = await response.json();
      dispatch({ type: 'FETCH_SUCCESS', payload: data });
    } catch (error) {
      dispatch({ type: 'FETCH_ERROR', error: error as Error });
    }
  };

  return { state, fetch, reset: () => dispatch({ type: 'RESET' }) };
}
```

### Spring State Machine Example

```java
@Configuration
@EnableStateMachine
public class OrderStateMachineConfig
    extends StateMachineConfigurerAdapter<OrderStatus, OrderEvent> {

    @Override
    public void configure(StateMachineStateConfigurer<OrderStatus, OrderEvent> states)
        throws Exception {
        states
            .withStates()
            .initial(OrderStatus.PENDING)
            .state(OrderStatus.PROCESSING)
            .state(OrderStatus.SHIPPED)
            .end(OrderStatus.DELIVERED)
            .end(OrderStatus.CANCELLED);
    }

    @Override
    public void configure(StateMachineTransitionConfigurer<OrderStatus, OrderEvent> transitions)
        throws Exception {
        transitions
            .withExternal()
                .source(OrderStatus.PENDING).target(OrderStatus.PROCESSING)
                .event(OrderEvent.PROCESS)
            .and()
            .withExternal()
                .source(OrderStatus.PENDING).target(OrderStatus.CANCELLED)
                .event(OrderEvent.CANCEL)
            .and()
            .withExternal()
                .source(OrderStatus.PROCESSING).target(OrderStatus.SHIPPED)
                .event(OrderEvent.SHIP)
            .and()
            .withExternal()
                .source(OrderStatus.SHIPPED).target(OrderStatus.DELIVERED)
                .event(OrderEvent.DELIVER);
    }
}

// Service using the state machine
@Service
public class OrderService {

    private final StateMachine<OrderStatus, OrderEvent> stateMachine;

    public void processOrder(Order order) {
        stateMachine.sendEvent(OrderEvent.PROCESS);
        // State machine handles transition logic and guards
    }
}
```

### XState (Modern State Machine Library)

```typescript
import { createMachine, interpret } from 'xstate';

const orderMachine = createMachine({
  id: 'order',
  initial: 'pending',
  states: {
    pending: {
      on: {
        PROCESS: 'processing',
        CANCEL: 'cancelled'
      }
    },
    processing: {
      on: {
        SHIP: 'shipped',
        CANCEL: 'cancelled'
      }
    },
    shipped: {
      on: {
        DELIVER: 'delivered'
      }
    },
    delivered: {
      type: 'final'
    },
    cancelled: {
      type: 'final'
    }
  }
});

// Usage
const orderService = interpret(orderMachine)
  .onTransition((state) => console.log(state.value))
  .start();

orderService.send('PROCESS');  // -> 'processing'
orderService.send('SHIP');     // -> 'shipped'
orderService.send('DELIVER');  // -> 'delivered'
```

## SKILL ACTIONS

### Action 1: Identify State Pattern Candidates

**TRIGGER:** Developer has switch/if-else statements checking object state across multiple methods, or mentions behavior that varies based on "mode" or "status"

**ACTION:** Evaluate if State pattern is appropriate:
1. Identify all distinct states the object can be in
2. Map out which operations behave differently per state
3. Document the valid state transitions
4. Check if states have significant behavior (not just data)
5. Consider if new states are likely to be added

**COUNTER-INDICATOR:** If behavior differences are minimal, states are few and stable, or the logic is confined to one method, simple conditionals may be clearer

### Action 2: Implement State Transition Logic

**TRIGGER:** Implementing State pattern and need to decide where transition logic lives

**ACTION:** Choose transition responsibility:
- **Context-driven**: When transitions are simple and fixed, implement in Context
- **State-driven**: When transitions are complex or states know their successors, let ConcreteState classes trigger transitions via Context interface
- **Hybrid**: Context defines allowed transitions, States request them

Provide Context with `setState()` or `changeState()` method for States to use.

**COUNTER-INDICATOR:** If transition logic becomes a tangled web of inter-state dependencies, consider extracting to a separate transition table or state machine definition

### Action 3: Optimize State Object Lifecycle

**TRIGGER:** Performance concerns about State object creation/destruction

**ACTION:** Choose appropriate lifecycle strategy:
- **Lazy creation/destruction**: States created on demand, destroyed after transition. Use when states are heavyweight or rarely entered.
- **Eager creation/singleton**: All states created upfront and shared. Use when state changes are frequent and states are stateless (flyweight).
- **Pool/cache**: Reuse state objects. Use when states have some instance data but creation is expensive.

**COUNTER-INDICATOR:** Premature optimization - start with simplest approach (create on demand) unless profiling shows performance issues

