---
name: gof-decorator
classification: Structural / Object
description: Use when you need to add responsibilities to objects dynamically without affecting other objects; Symptoms: subclass explosion for optional features, rigid feature combinations, need to add/remove behaviors at runtime
---

# DECORATOR

## INTENT

Attach additional responsibilities to an object dynamically. Decorators provide a flexible alternative to subclassing for extending functionality.

## ALSO KNOWN AS

Wrapper

## PROBLEM INDICATORS

- You need to add responsibilities to individual objects dynamically and transparently, without affecting other objects
- You need responsibilities that can be withdrawn at runtime
- Extension by subclassing is impractical due to an explosion of subclasses or because the class definition is hidden or unavailable
- You have a proliferation of classes differing only in combinations of features
- You need to extend functionality of classes in ways that are impossible with static inheritance

## KEY INSIGHT

The Decorator pattern achieves flexibility by wrapping objects with other objects that have identical interfaces, allowing behaviors to be composed at runtime like layers of an onion rather than frozen at compile time through inheritance hierarchies.

## PARTICIPANTS

| Role | Responsibility |
|------|----------------|
| Component | Defines the interface for objects that can have responsibilities added to them dynamically |
| ConcreteComponent | Defines an object to which additional responsibilities can be attached |
| Decorator | Maintains a reference to a Component object and defines an interface that conforms to Component's interface |
| ConcreteDecorator | Adds responsibilities to the component; implements the added behavior and forwards requests to its Component |

## CONSEQUENCES

**Benefits:**

1. More flexibility than static inheritance - responsibilities can be added and removed at runtime by attaching and detaching decorators; combining decorators allows mixing and matching responsibilities
2. Avoids feature-laden classes high in the hierarchy - instead of trying to support all foreseeable features in a complex base class, you can define a simple class and add functionality incrementally with Decorator objects
3. Pay-as-you-go approach - rather than paying for features you don't need in a complex class, you can add only the functionality you require

**Liabilities:**

1. A decorator and its component aren't identical - a decorated component is not identical to the component itself; you shouldn't rely on object identity when using decorators
2. Lots of little objects - a design that uses Decorator often results in systems composed of many small objects that all look alike, making the system harder to learn and debug

## WHEN NOT TO USE

- When object identity is important and clients must distinguish the original object from its decorators
- When you need to access specific properties of concrete components through the decorator chain
- When the overhead of many small wrapper objects is unacceptable for performance-critical code
- When the component interface is large and most operations need forwarding (consider Strategy instead)
- When you need to modify the structure rather than just add behavior (consider Composite)

## RELATED PATTERNS

| Pattern | Relationship |
|---------|--------------|
| Adapter | Changes an object's interface; Decorator changes an object's responsibilities without changing its interface |
| Composite | Decorator can be viewed as a degenerate Composite with only one component; however, Decorator adds responsibilities while Composite focuses on structure |
| Strategy | Decorator changes the skin of an object (external behavior); Strategy changes the guts (internal algorithm). Decorators add behavior around existing operations; Strategy replaces the behavior entirely |

## MODERN CONTEXT

**TypeScript:**
```typescript
interface Coffee {
  cost(): number;
  description(): string;
}

class SimpleCoffee implements Coffee {
  cost() { return 2; }
  description() { return "Simple coffee"; }
}

abstract class CoffeeDecorator implements Coffee {
  constructor(protected coffee: Coffee) {}
  abstract cost(): number;
  abstract description(): string;
}

class MilkDecorator extends CoffeeDecorator {
  cost() { return this.coffee.cost() + 0.5; }
  description() { return this.coffee.description() + ", milk"; }
}

// Usage: new MilkDecorator(new SimpleCoffee())
```

**React (Higher-Order Components):**
```tsx
function withLogging<P>(WrappedComponent: React.ComponentType<P>) {
  return function LoggedComponent(props: P) {
    useEffect(() => {
      console.log('Component rendered');
    });
    return <WrappedComponent {...props} />;
  };
}

function withAuth<P>(WrappedComponent: React.ComponentType<P>) {
  return function AuthComponent(props: P & { isAuthenticated: boolean }) {
    if (!props.isAuthenticated) return <Login />;
    return <WrappedComponent {...props} />;
  };
}

// Compose decorators: withAuth(withLogging(MyComponent))
```

**Spring (Java Annotations):**
```java
// Spring uses decorator pattern extensively for AOP
@Service
public class UserService {
    @Transactional  // Decorates with transaction management
    @Cacheable("users")  // Decorates with caching behavior
    @Retryable(maxAttempts = 3)  // Decorates with retry logic
    public User findById(Long id) {
        return userRepository.findById(id);
    }
}

// Custom decorator via proxy
@Aspect
@Component
public class LoggingDecorator {
    @Around("@annotation(Logged)")
    public Object logExecution(ProceedingJoinPoint joinPoint) throws Throwable {
        log.info("Before: " + joinPoint.getSignature());
        Object result = joinPoint.proceed();
        log.info("After: " + joinPoint.getSignature());
        return result;
    }
}
```

## SKILL ACTIONS

**TRIGGER:** "We have an explosion of subclasses for different feature combinations" or "We need to add optional behaviors to objects at runtime"
**ACTION:** Apply Decorator pattern - create a component interface, implement concrete components, create an abstract decorator maintaining a component reference, implement concrete decorators that add specific behaviors
**COUNTER-INDICATOR:** If object identity matters or you need to access concrete component internals, reconsider; if most operations need forwarding, prefer Strategy

**TRIGGER:** "Different clients need different combinations of features on the same base object"
**ACTION:** Define each feature as a separate decorator; allow runtime composition of decorators to build customized object behavior
**COUNTER-INDICATOR:** If combinations are fixed and known at compile time, simple inheritance may be clearer

**TRIGGER:** "We can't modify this class but need to add behavior around its methods"
**ACTION:** Wrap the class in a decorator that implements the same interface, delegates to the original, and adds behavior before/after delegation
**COUNTER-INDICATOR:** If you need to change the interface itself, use Adapter instead

## CSO KEYWORDS

- dynamic behavior extension
- runtime composition
- transparent wrapping
- recursive composition
- single responsibility layering
- subclass explosion prevention
- flexible alternative to inheritance
- object augmentation
- behavior stacking
- transparent enclosure
