---
name: gof-adapter
classification: Structural / Class, Object
description: Convert the interface of a class into another interface clients expect. Adapter lets classes work together that couldn't otherwise because of incompatible interfaces.
---

## INTENT

Convert the interface of a class into another interface clients expect. Adapter lets classes work together that couldn't otherwise because of incompatible interfaces.

## ALSO KNOWN AS

Wrapper

## PROBLEM INDICATORS

- You want to use an existing class, and its interface does not match the one you need
- You want to create a reusable class that cooperates with unrelated or unforeseen classes, that is, classes that don't necessarily have compatible interfaces
- (object adapter only) You need to use several existing subclasses, but it's impractical to adapt their interface by subclassing every one. An object adapter can adapt the interface of its parent class

## KEY INSIGHT

Adapters work by creating an intermediary abstraction that translates (or maps) the old interface to the new. Class adapters inherit from both interfaces while object adapters compose the adaptee and delegate calls to it, providing a trade-off between inheritance-based tight coupling and composition-based flexibility.

## PARTICIPANTS

| Role | Responsibility |
|------|----------------|
| Target | Defines the domain-specific interface that Client uses |
| Client | Collaborates with objects conforming to the Target interface |
| Adaptee | Defines an existing interface that needs adapting |
| Adapter | Adapts the interface of Adaptee to the Target interface |

## CONSEQUENCES

**Benefits:**

1. Class adapters let Adapter override some of Adaptee's behavior, since Adapter is a subclass of Adaptee
2. Class adapters introduce only one object, and no additional pointer indirection is needed to get to the adaptee
3. Object adapters let a single Adapter work with many Adaptees—the Adaptee itself and all of its subclasses. The Adapter can also add functionality to all Adaptees at once
4. Adapters decouple clients from the concrete classes they use, promoting loose coupling

**Liabilities:**

1. Class adapters won't work when we want to adapt a class and all its subclasses
2. Object adapters make it harder to override Adaptee behavior. It will require subclassing Adaptee and making Adapter refer to the subclass rather than the Adaptee itself
3. Class adapters require multiple inheritance which may not be available in all languages
4. Additional level of indirection can introduce slight overhead

## WHEN NOT TO USE

- When the interfaces are already compatible or can be made compatible with minimal changes
- When the adaptee's interface is likely to change frequently, causing ripple effects through the adapter
- When you need bidirectional adaptation and transparency would be compromised
- When a simple interface change or refactoring of the original class is feasible and preferred
- When the overhead of an additional abstraction layer isn't justified for simple, one-off integrations

## RELATED PATTERNS

| Pattern | Relationship |
|---------|--------------|
| Bridge | Has a structure similar to an object adapter, but Bridge has a different intent: it is meant to separate an interface from its implementation so that they can be varied easily and independently. An adapter is meant to change the interface of an existing object |
| Decorator | Is more transparent than an adapter. As a consequence, Decorator supports recursive composition, which isn't possible with pure adapters. A decorator enhances another object without changing its interface |
| Proxy | Defines a representative or surrogate for another object and does not change its interface |

## MODERN CONTEXT

**TypeScript Example:**
```typescript
// Target interface expected by the client
interface PaymentProcessor {
  processPayment(amount: number, currency: string): Promise<PaymentResult>;
}

// Adaptee - legacy or third-party payment system
class LegacyStripeGateway {
  charge(cents: number, curr: string, callback: (err: Error | null, result: any) => void): void {
    // Legacy callback-based implementation
  }
}

// Object Adapter
class StripePaymentAdapter implements PaymentProcessor {
  constructor(private legacyGateway: LegacyStripeGateway) {}

  async processPayment(amount: number, currency: string): Promise<PaymentResult> {
    return new Promise((resolve, reject) => {
      this.legacyGateway.charge(amount * 100, currency, (err, result) => {
        if (err) reject(err);
        else resolve({ success: true, transactionId: result.id });
      });
    });
  }
}
```

**React Example:**
```tsx
// Adapting a legacy class-based component API to modern hooks
interface LegacyDataSource {
  subscribe(callback: () => void): void;
  unsubscribe(callback: () => void): void;
  getData(): any;
}

// Hook adapter for legacy data sources
function useLegacyDataSource<T>(dataSource: LegacyDataSource): T {
  const [data, setData] = useState<T>(dataSource.getData());

  useEffect(() => {
    const handleChange = () => setData(dataSource.getData());
    dataSource.subscribe(handleChange);
    return () => dataSource.unsubscribe(handleChange);
  }, [dataSource]);

  return data;
}

// Usage adapts legacy API to React's reactive model
const MyComponent: React.FC = () => {
  const userData = useLegacyDataSource<User>(legacyUserStore);
  return <UserProfile user={userData} />;
};
```

**Spring Example:**
```java
// Target interface for modern logging
public interface LoggingService {
    void log(LogLevel level, String message, Map<String, Object> context);
}

// Adaptee - legacy logging framework
public class LegacyLogger {
    public void writeLog(int severity, String msg) { /* ... */ }
}

// Adapter using Spring's dependency injection
@Component
public class LegacyLoggerAdapter implements LoggingService {

    private final LegacyLogger legacyLogger;

    @Autowired
    public LegacyLoggerAdapter(LegacyLogger legacyLogger) {
        this.legacyLogger = legacyLogger;
    }

    @Override
    public void log(LogLevel level, String message, Map<String, Object> context) {
        int severity = mapLevelToSeverity(level);
        String formattedMsg = formatWithContext(message, context);
        legacyLogger.writeLog(severity, formattedMsg);
    }

    private int mapLevelToSeverity(LogLevel level) {
        return switch (level) {
            case ERROR -> 1;
            case WARN -> 2;
            case INFO -> 3;
            case DEBUG -> 4;
        };
    }
}
```

## SKILL ACTIONS

| TRIGGER | ACTION | COUNTER-INDICATOR |
|---------|--------|-------------------|
| "incompatible interface" | Suggest creating an Adapter to wrap the incompatible class | Interfaces can be easily refactored to match |
| "integrate legacy system" | Propose object adapter to wrap legacy API without modification | Legacy system is being replaced soon |
| "third-party library mismatch" | Recommend adapter layer to isolate external dependencies | Library provides official adapters |
| "callback to promise conversion" | Use adapter to translate callback-based APIs to Promise/async | Native async version available |
| "need to wrap multiple implementations" | Apply object adapter pattern to compose rather than inherit | All implementations share common base class |
| "class hierarchy integration" | Consider class adapter if language supports multiple inheritance | Single inheritance language or need to adapt subclasses |

## CSO KEYWORDS

- adapter pattern
- wrapper pattern
- interface adapter
- legacy integration
- API compatibility
- interface conversion
- class adapter
- object adapter
- interface translation
- pluggable adapter
- two-way adapter
- structural pattern
- incompatible interfaces
- interface mismatch
- third-party integration
