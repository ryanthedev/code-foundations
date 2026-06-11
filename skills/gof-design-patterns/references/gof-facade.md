---
name: gof-facade
classification: Structural / Object
description: "Use when you need to provide a simple interface to a complex subsystem; Symptoms: clients coupled to many subsystem classes, complex initialization sequences, subsystem complexity leaking into client code"
---

## INTENT

Provide a unified interface to a set of interfaces in a subsystem. Facade defines a higher-level interface that makes the subsystem easier to use.

## ALSO KNOWN AS

None documented.

## PROBLEM INDICATORS

- You want to provide a simple interface to a complex subsystem that has evolved to contain many small classes
- There are many dependencies between clients and the abstraction's implementation classes
- You want to layer your subsystems, using a facade to define an entry point to each subsystem level
- Clients need to know about and interact with numerous subsystem classes to accomplish common tasks
- Subsystem complexity is leaking into client code through extensive imports and multi-step operations

## KEY INSIGHT

A Facade doesn't encapsulate subsystem classes or prevent direct access; it simply provides a convenient, simplified interface for the most common use cases while leaving the full power of the subsystem accessible when needed.

## PARTICIPANTS

| Role | Responsibility |
|------|----------------|
| **Facade** (e.g., Compiler) | Knows which subsystem classes are responsible for a request. Delegates client requests to appropriate subsystem objects. |
| **Subsystem classes** (e.g., Scanner, Parser, ProgramNode, BytecodeStream, ProgramNodeBuilder) | Implement subsystem functionality. Handle work assigned by the Facade object. Have no knowledge of the facade; keep no reference to it. |

## CONSEQUENCES

**Benefits:**

1. **Shields clients from subsystem components** - Reduces the number of objects that clients deal with and makes the subsystem easier to use.

2. **Promotes weak coupling between the subsystem and its clients** - Allows you to vary the components of the subsystem without affecting its clients. Reduces compilation dependencies in large software systems.

3. **Doesn't prevent applications from using subsystem classes if they need to** - You can choose between ease of use and generality; the facade doesn't lock you out of the subsystem's full functionality.

**Liabilities:**

4. **Can become a "god object" if not carefully designed** - May accumulate too many responsibilities if every subsystem operation is routed through it.

5. **Adds an extra layer of indirection** - For performance-critical paths, the additional delegation may be undesirable.

## WHEN NOT TO USE

- When clients genuinely need fine-grained control over subsystem components
- When the subsystem is simple enough that a facade adds unnecessary complexity
- When different clients need significantly different views of the subsystem (consider multiple facades instead)
- When the facade would become a maintenance bottleneck, requiring changes for every new subsystem feature
- When you want to enforce that clients cannot access subsystem classes directly (use other patterns like Abstract Factory for stricter encapsulation)

## RELATED PATTERNS

| Pattern | Relationship |
|---------|--------------|
| **Abstract Factory** | Can be used with Facade to provide an interface for creating subsystem objects in a subsystem-independent way. Abstract Factory can also be an alternative to Facade for hiding platform-specific classes. |
| **Mediator** | Similar to Facade in that it abstracts functionality of existing classes. However, Mediator's purpose is to abstract arbitrary communication between colleague objects (often centralizing functionality that doesn't belong in any one of them). Mediator's colleagues are aware of and communicate with the mediator. In contrast, a Facade merely abstracts the interface to subsystem objects to make them easier to use; it doesn't define new functionality, and subsystem classes don't know about it. |
| **Singleton** | Usually only one Facade object is required per subsystem, so Facade objects are often Singletons. |

## MODERN CONTEXT

**TypeScript Example - API Client Facade:**
```typescript
// Subsystem classes
class AuthService {
  async getToken(): Promise<string> { /* ... */ }
  async refreshToken(): Promise<string> { /* ... */ }
}

class HttpClient {
  async get<T>(url: string, headers: Record<string, string>): Promise<T> { /* ... */ }
  async post<T>(url: string, data: unknown, headers: Record<string, string>): Promise<T> { /* ... */ }
}

class CacheService {
  get<T>(key: string): T | null { /* ... */ }
  set<T>(key: string, value: T, ttl: number): void { /* ... */ }
}

class ErrorHandler {
  handle(error: Error): void { /* ... */ }
}

// Facade
class ApiClient {
  constructor(
    private auth: AuthService,
    private http: HttpClient,
    private cache: CacheService,
    private errorHandler: ErrorHandler
  ) {}

  async fetchUser(userId: string): Promise<User> {
    const cached = this.cache.get<User>(`user:${userId}`);
    if (cached) return cached;

    try {
      const token = await this.auth.getToken();
      const user = await this.http.get<User>(`/users/${userId}`, { Authorization: `Bearer ${token}` });
      this.cache.set(`user:${userId}`, user, 300);
      return user;
    } catch (error) {
      this.errorHandler.handle(error as Error);
      throw error;
    }
  }
}
```

**React Example - Complex State Facade:**
```typescript
// Facade hook that simplifies interaction with multiple contexts/stores
function useCheckout() {
  const cart = useCart();
  const user = useUser();
  const payment = usePayment();
  const shipping = useShipping();
  const analytics = useAnalytics();

  const processCheckout = async () => {
    analytics.trackCheckoutStart(cart.items);
    const shippingAddress = await shipping.validateAddress(user.address);
    const paymentResult = await payment.charge(cart.total, user.paymentMethod);
    await cart.clear();
    analytics.trackPurchase(paymentResult.orderId, cart.total);
    return paymentResult.orderId;
  };

  return {
    processCheckout,
    isReady: cart.hasItems && user.isLoggedIn && payment.isConfigured,
    total: cart.total + shipping.cost,
  };
}
```

**Spring Example - Service Facade:**
```java
@Service
public class OrderFacade {
    private final InventoryService inventoryService;
    private final PaymentService paymentService;
    private final ShippingService shippingService;
    private final NotificationService notificationService;

    public OrderFacade(InventoryService inventoryService,
                       PaymentService paymentService,
                       ShippingService shippingService,
                       NotificationService notificationService) {
        this.inventoryService = inventoryService;
        this.paymentService = paymentService;
        this.shippingService = shippingService;
        this.notificationService = notificationService;
    }

    @Transactional
    public OrderResult placeOrder(OrderRequest request) {
        inventoryService.reserve(request.getItems());
        PaymentResult payment = paymentService.process(request.getPaymentInfo());
        ShippingLabel label = shippingService.createLabel(request.getShippingAddress());
        notificationService.sendConfirmation(request.getCustomerEmail(), payment, label);
        return new OrderResult(payment.getOrderId(), label.getTrackingNumber());
    }
}
```

## SKILL ACTIONS

**TRIGGER:** Multiple classes from a subsystem imported into client code; complex multi-step initialization; clients need to understand subsystem internals to accomplish basic tasks; subsystem changes frequently break client code.

**ACTION:** Introduce a Facade class that provides simplified methods for common operations. The facade delegates to appropriate subsystem objects internally while presenting a cohesive, task-oriented interface to clients.

**COUNTER-INDICATOR:** Don't create a facade when clients legitimately need varied, fine-grained access patterns; when the "subsystem" is just one or two classes; or when the facade would simply mirror the subsystem interface without simplification.

