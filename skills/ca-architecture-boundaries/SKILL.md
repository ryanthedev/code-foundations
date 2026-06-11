---
name: ca-architecture-boundaries
description: "Applies Clean Architecture's dependency-direction and SRP-by-actor rules to system-level boundary design: separates business logic from infrastructure, identifies actor-coupling risks, and enforces inward-pointing dependency arrows."
disable-model-invocation: true
---

# Architecture Boundaries (Clean Architecture)

Operates at SYSTEM level (layers, boundaries, components). For MODULE level (interface depth, information hiding), use aposd-designing-deep-modules.

---

## SRP Is About Actors, Not "Doing One Thing"

"A module should be responsible to one, and only one, actor."

An actor is a group of users/stakeholders who request changes. If two actors share a class, a change for one can break the other.

```java
// BEFORE: One class serves three actors
class Employee {
    Money calculatePay() { }      // CFO's accounting team
    String reportHours() { }      // COO's HR team
    void save() { }               // CTO's DBA team
}

// AFTER: Separate class per actor
class EmployeeData { /* just data */ }

class PayCalculator {
    Money calculatePay(EmployeeData e) { /* CFO */ }
}
class HourReporter {
    String reportHours(EmployeeData e) { /* COO */ }
}
class EmployeeSaver {
    void saveEmployee(EmployeeData e) { /* CTO */ }
}

// Optional: Facade for convenience
class EmployeeFacade {
    // Delegates to actor-specific classes
}
```

**Test:** For each class, ask "who requests changes to this?" If the answer is more than one actor, split.

---

## DRY Within Actor Boundaries Only

Duplication across actor boundaries is safer than coupling.

If CFO's calculatePay and COO's reportHours both use the same regularHours helper, they appear duplicated — but they change for different reasons. Merging them couples two actors. When CFO's accounting rules change, COO's reports break.

**Rule:** DRY applies within a single actor's code. Across actors, prefer duplication over coupling.

---

## Dependency Rule

Dependencies point inward: Frameworks → Adapters → Use Cases → Entities.

Nothing in an inner circle can know anything about an outer circle. Business rules never import database, UI, or framework code. If business logic needs to call infrastructure, define an interface in the business layer and implement it in the infrastructure layer (dependency inversion).

---

## Separate Business Rules from Infrastructure

```java
// 1. Interface defined in business layer (where it's USED, not implemented)
public interface OrderRepository {
    Order findById(String id);
    void save(Order order);
}

// 2. Entity with Critical Business Rules (pure, no dependencies)
public class Order {
    private Money total;
    public Money calculateDiscount() {
        if (total.isGreaterThan(1000))
            return total.multiply(0.1);
        return Money.ZERO;
    }
}

// 3. Use Case orchestrates (does NOT contain business rules)
public class ProcessOrderUseCase {
    private OrderRepository repository;
    public OrderResponse execute(OrderRequest request) {
        Order order = repository.findById(request.orderId);
        Money discount = order.calculateDiscount();
        order.applyDiscount(discount);
        repository.save(order);
        return new OrderResponse(order.getId(), order.getTotal());
    }
}

// 4. Infrastructure implements interface (dependency inverted)
public class SqlOrderRepository implements OrderRepository {
    public Order findById(String id) { /* SQL */ }
    public void save(Order order) { /* SQL */ }
}
```

---

## Integration Checklist

When applying to an existing system:

### Phase 1: Identify
- [ ] Map actors (who requests changes?) → find SRP violations
- [ ] Identify Critical Business Rules (what makes/saves money?) → Entities
- [ ] List application workflows → Use Cases
- [ ] Find technical dependencies (DB, UI, frameworks) → Details to isolate

### Phase 2: Draw Boundaries
- [ ] Dependencies all point toward business rules?
- [ ] Can business logic run without infrastructure?
- [ ] Are changes proportional to scope, not shape?

### Phase 3: Verify
- [ ] SRP: Classes serving multiple actors?
- [ ] OCP: Simple extensions require modifying existing code?
- [ ] DIP: Business logic importing concrete infrastructure?

---

## Boundary Violation Detection

```bash
# Framework coupling in business logic
grep -r "import.*servlet\|import.*spring.*web\|import.*express" src/domain/
grep -r "import.*sql\|import.*mongoose\|import.*prisma" src/entities/

# ORM annotations in domain
grep -r "@Entity\|@Table\|@Column" src/domain/

# Type checking instead of polymorphism
grep -r "instanceof\|getType()\|typeof.*===" src/
```

---

## Chain

| After | Next |
|-------|------|
| Boundaries drawn | aposd-designing-deep-modules (module-level design) |
| SOLID violations found | cc-refactoring-guidance (safe restructuring) |
