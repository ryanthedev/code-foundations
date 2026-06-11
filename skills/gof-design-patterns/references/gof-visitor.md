---
name: gof-visitor
classification: Behavioral / Object
description: Need to perform many distinct operations on objects in a complex structure without modifying the element classes; operations keep changing while the object structure remains stable
---

## INTENT

Represent an operation to be performed on the elements of an object structure. Visitor lets you define a new operation without changing the classes of the elements on which it operates.

## ALSO KNOWN AS

None

## PROBLEM INDICATORS

When you see:
- Multiple unrelated operations need to be performed on objects in an object structure
- Operations are frequently added or changed, but the element classes are stable
- Type-checking, code optimization, pretty-printing, and similar operations scattered across node classes
- Adding a new operation requires modifying many classes
- Related behavior is spread across multiple classes instead of being localized
- You need to accumulate state while traversing a complex object structure
- Operations depend on the concrete classes of elements in the structure

## KEY INSIGHT

By using double-dispatch (element accepts visitor, then calls back with its concrete type), you can add new operations to a stable class hierarchy without modifying those classes - the operation that executes depends on both the visitor type and the element type.

## PARTICIPANTS

| Role | Responsibility |
|------|---------------|
| Visitor (NodeVisitor) | Declares a Visit operation for each class of ConcreteElement in the object structure. The operation's name and signature identifies the class that sends the Visit request to the visitor, letting the visitor determine the concrete class of the element being visited and access it through its particular interface |
| ConcreteVisitor (TypeCheckingVisitor) | Implements each operation declared by Visitor. Each operation implements a fragment of the algorithm defined for the corresponding class of object in the structure. Provides the context for the algorithm and stores its local state. This state often accumulates results during the traversal |
| Element (Node) | Defines an Accept operation that takes a visitor as an argument |
| ConcreteElement (AssignmentNode, VariableRefNode) | Implements an Accept operation that takes a visitor as an argument |
| ObjectStructure (Program) | Can enumerate its elements. May provide a high-level interface to allow the visitor to visit its elements. May either be a composite or a collection such as a list or a set |

## CONSEQUENCES

**Benefits:**

1. Visitor makes adding new operations easy. You can define a new operation over an object structure simply by adding a new visitor. In contrast, if you spread functionality over many classes, then you must change each class to define a new operation.

2. A visitor gathers related operations and separates unrelated ones. Related behavior isn't spread over the classes defining the object structure; it's localized in a visitor. Unrelated sets of behavior are partitioned in their own visitor subclasses. That simplifies both the classes defining the elements and the algorithms defined in the visitors. Any algorithm-specific data structures can be hidden in the visitor.

3. Visiting across class hierarchies. An iterator can't work across object structures with different types of elements. Visitor does not have this restriction. It can visit objects that don't have a common parent class. You can add any type of object to a Visitor interface.

4. Accumulating state. Visitors can accumulate state as they visit each element in the object structure. Without a visitor, this state would be passed as extra arguments to the operations that perform the traversal, or they might appear as global variables.

**Liabilities:**

1. Adding new ConcreteElement classes is hard. Each new ConcreteElement gives rise to a new abstract operation on Visitor and a corresponding implementation in every ConcreteVisitor class. Sometimes a default implementation can be provided in Visitor that can be inherited by most of the ConcreteVisitors, but this is the exception rather than the rule.

2. Breaking encapsulation. Visitor's approach assumes that the ConcreteElement interface is powerful enough to let visitors do their job. As a result, the pattern often forces you to provide public operations that access an element's internal state, which may compromise its encapsulation.

## WHEN NOT TO USE

- The object structure classes change frequently (adding new ConcreteElement classes requires updating all visitors)
- The Element class hierarchy is unstable
- Elements need to keep their internal state private (Visitor requires exposing state)
- You only have one or two operations to perform (overhead not justified)
- Operations are simple and unlikely to change
- You need strong encapsulation of element internals
- The cost of redefining the interface to all visitors when adding elements is prohibitive

## RELATED PATTERNS

| Pattern | Relationship |
|---------|-------------|
| Composite | Visitors can be used to apply an operation over an object structure defined by the Composite pattern |
| Interpreter | Visitor may be applied to do the interpretation |
| Iterator | Both traverse structures, but Iterator requires elements to have a common parent class; Visitor can visit objects without a common parent and enables double-dispatch |

## MODERN CONTEXT

- TypeScript discriminated unions with exhaustive switch statements provide compile-time visitor-like behavior
- Pattern matching in functional languages (Scala, Kotlin, Rust) often replaces Visitor
- AST traversal in compilers (Babel, ESLint, TypeScript) heavily uses Visitor pattern
- React's reconciliation algorithm uses visitor-like traversal of component trees
- Redux reducers can be seen as visitors over action types
- GraphQL query execution uses visitors for query validation and execution
- Java's javax.lang.model.element.ElementVisitor for annotation processing
- ANTLR generates visitor interfaces for parse tree traversal
- Spring's BeanDefinitionVisitor for bean definition inspection
- DOM tree walkers (TreeWalker, NodeIterator) implement visitor-like traversal

## SKILL ACTIONS

```
TRIGGER: Need to add many distinct operations to a stable object structure without modifying element classes
ACTION: Define Visitor interface with visit method per element type; elements implement accept(visitor) that calls visitor.visitConcreteType(this); create ConcreteVisitors for each operation
COUNTER-INDICATOR: Element hierarchy changes frequently; only a few simple operations needed; strong encapsulation required
```

