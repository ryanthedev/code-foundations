---
name: gof-template-method
classification: Behavioral / Class
description: Multiple subclasses implement similar algorithms with duplicated code structure, differing only in specific steps. The overall algorithm sequence is the same but certain operations vary by subclass.
---

## INTENT

Define the skeleton of an algorithm in an operation, deferring some steps to subclasses. Template Method lets subclasses redefine certain steps of an algorithm without changing the algorithm's structure.

## ALSO KNOWN AS

None

## PROBLEM INDICATORS

When you see:
- Multiple subclasses implementing similar algorithms with duplicated structure
- Copy-paste code where only certain steps differ between implementations
- Algorithms that share the same sequence of steps but vary in specific operations
- Subclasses that need to extend parent behavior but often forget to call the parent method
- Need to control which parts of an algorithm subclasses can customize
- Common behavior scattered across subclasses instead of localized in a parent class
- Difficulty enforcing invariants across subclass implementations

## KEY INSIGHT

By defining the algorithm skeleton in a parent class and deferring only the variable steps to subclasses, you fix the ordering of operations while allowing customization. This inverts control - the parent calls subclass operations ("Hollywood principle: Don't call us, we'll call you"), rather than subclasses calling parent operations.

## PARTICIPANTS

| Role | Responsibility |
|------|---------------|
| AbstractClass | Defines abstract primitive operations that concrete subclasses must implement; implements the template method defining the skeleton of the algorithm; the template method calls primitive operations, hook operations, and concrete operations |
| ConcreteClass | Implements the primitive operations to carry out subclass-specific steps of the algorithm |
| Primitive Operations | Abstract operations that subclasses must override to provide concrete behavior |
| Hook Operations | Operations with default (often empty) behavior that subclasses may optionally override to extend behavior at specific points |

## CONSEQUENCES

**Benefits:**

1. Template methods are a fundamental technique for code reuse, particularly important in class libraries for factoring out common behavior
2. Leads to an inverted control structure ("Hollywood principle") where the parent class controls the algorithm flow and calls subclass operations
3. Lets you implement the invariant parts of an algorithm once while leaving variable parts to subclasses
4. Factors and localizes common behavior in a single class, avoiding code duplication
5. Controls subclass extensions by defining hook operations at specific points, permitting customization only at those points
6. Enforces invariants that subclasses might otherwise forget (e.g., setup/teardown sequences)

**Liabilities:**

1. Relies on inheritance, which creates tight coupling between abstract and concrete classes
2. The more primitive operations that need overriding, the more tedious it becomes for clients
3. Subclass writers must understand which operations are hooks (may be overridden) versus abstract operations (must be overridden)
4. Can lead to confusion if the distinction between hooks and required overrides is unclear
5. Violates the Liskov Substitution Principle if subclasses must override methods to work correctly

## WHEN NOT TO USE

- When algorithms vary entirely, not just in specific steps (use Strategy instead)
- When you need to vary behavior at runtime rather than compile time
- When inheritance hierarchies are already deep or complex
- When subclasses need to change the order of algorithm steps, not just the step implementations
- When composition would be simpler than inheritance for the variation needed
- In languages or codebases that favor composition over inheritance

## RELATED PATTERNS

| Pattern | Relationship |
|---------|-------------|
| Factory Method | Factory Methods are often called by template methods. In the Motivation example, DoCreateDocument (factory method) is called by OpenDocument (template method) |
| Strategy | Template methods use inheritance to vary part of an algorithm; Strategies use delegation to vary the entire algorithm. Strategy is more flexible but requires more objects |

## MODERN CONTEXT

- **React Class Components**: Lifecycle methods (componentDidMount, componentDidUpdate, render) form a template method pattern where React controls the sequence and components override specific hooks
- **React Hooks**: The useEffect hook with cleanup functions follows a similar template (setup, optional cleanup) but using composition
- **Angular**: Component lifecycle hooks (ngOnInit, ngOnDestroy, ngOnChanges) follow the template method pattern
- **Spring Framework**: JdbcTemplate, RestTemplate, and TransactionTemplate define algorithm skeletons for database access, REST calls, and transactions
- **JUnit/Testing Frameworks**: Test lifecycle with @Before, @Test, @After hooks; the framework controls execution order
- **Express/Koa Middleware**: Middleware chains where each handler calls next() follow a similar inversion of control
- **TypeScript Abstract Classes**: Abstract methods and protected hooks map directly to the pattern
- **Python ABCs**: Abstract Base Classes with @abstractmethod decorators implement template methods
- **ASP.NET Core**: Controller action filters (OnActionExecuting, OnActionExecuted) provide hooks around the template
- **Django Class-Based Views**: Methods like get_queryset(), get_context_data() are hooks in the view rendering template

## SKILL ACTIONS

```
TRIGGER: Multiple classes share the same algorithm structure but differ in specific steps; duplicated code with only certain operations varying; need to enforce an invariant sequence across subclasses
ACTION: Extract the algorithm skeleton into an abstract class template method; identify primitive operations (must override) and hook operations (may override); use naming conventions like "do" prefix for overridable operations
COUNTER-INDICATOR: The entire algorithm varies (use Strategy); need runtime flexibility; inheritance hierarchy is already complex; steps need to be reordered by subclasses
```

