---
name: gof-composite
classification: Structural / Object
description: |
  When you want to represent part-whole hierarchies of objects, or when clients should be able to ignore the difference between compositions of objects and individual objects, use Composite to compose objects into tree structures and let clients treat individual objects and compositions uniformly.
---

## INTENT

Compose objects into tree structures to represent part-whole hierarchies. Composite lets clients treat individual objects and compositions of objects uniformly.

## ALSO KNOWN AS

(None specified in GoF)

## PROBLEM INDICATORS

- Code must distinguish between primitive and container objects, even when the user treats them identically
- You need to represent part-whole hierarchies of objects
- Clients should treat composite structures and individual objects uniformly
- Having to write tag-and-case-statement-style functions over classes that define a composition
- You want to build complex structures from simple components recursively

## KEY INSIGHT

The key to the Composite pattern is an abstract class that represents both primitives and their containers. This class declares operations specific to the domain objects (like `Draw` for graphical objects) as well as operations that all composite objects share, such as operations for accessing and managing children. By conforming to the same interface, both leaf objects and composite objects can be treated uniformly by clients.

## PARTICIPANTS

| Participant | Role | Example |
|------------|------|---------|
| Component | Declares the interface for objects in the composition; implements default behavior for the interface common to all classes; declares an interface for accessing and managing child components; optionally defines an interface for accessing a component's parent | Graphic |
| Leaf | Represents leaf objects in the composition (has no children); defines behavior for primitive objects | Rectangle, Line, Text |
| Composite | Defines behavior for components having children; stores child components; implements child-related operations in the Component interface | Picture |
| Client | Manipulates objects in the composition through the Component interface | - |

## CONSEQUENCES

### Benefits

1. **Defines class hierarchies consisting of primitive objects and composite objects.** Primitive objects can be composed into more complex objects, which in turn can be composed, and so on recursively. Wherever client code expects a primitive object, it can also take a composite object.

2. **Makes the client simple.** Clients can treat composite structures and individual objects uniformly. Clients normally don't know (and shouldn't care) whether they're dealing with a leaf or a composite component. This simplifies client code, because it avoids having to write tag-and-case-statement-style functions over the classes that define the composition.

3. **Makes it easier to add new kinds of components.** Newly defined Composite or Leaf subclasses work automatically with existing structures and client code. Clients don't have to be changed for new Component classes.

### Liabilities

4. **Can make your design overly general.** The disadvantage of making it easy to add new components is that it makes it harder to restrict the components of a composite. Sometimes you want a composite to have only certain components. With Composite, you can't rely on the type system to enforce those constraints for you. You'll have to use run-time checks instead.

## WHEN NOT TO USE

- When there is no natural part-whole hierarchy in your domain
- When leaf and composite objects have fundamentally different interfaces that cannot be reasonably unified
- When you need strict type-checking to enforce constraints on which objects can be children of which composites
- When the overhead of the uniform interface (child management operations on leaves) is unacceptable
- When operations differ significantly between leaves and composites, making a common interface awkward

## RELATED PATTERNS

| Pattern | Relationship |
|---------|--------------|
| Chain of Responsibility | Often the component-parent link is used for a Chain of Responsibility |
| Decorator | Often used with Composite; when used together, they usually have a common parent class, so decorators must support the Component interface with operations like Add, Remove, and GetChild |
| Flyweight | Lets you share components, but they can no longer refer to their parents |
| Iterator | Can be used to traverse composites |
| Visitor | Localizes operations and behavior that would otherwise be distributed across Composite and Leaf classes |

## MODERN CONTEXT

### TypeScript Example
```typescript
// Component interface
interface FileSystemNode {
  getName(): string;
  getSize(): number;
  print(indent?: string): void;
}

// Leaf
class File implements FileSystemNode {
  constructor(private name: string, private size: number) {}

  getName(): string { return this.name; }
  getSize(): number { return this.size; }
  print(indent = ''): void {
    console.log(`${indent}- ${this.name} (${this.size}KB)`);
  }
}

// Composite
class Directory implements FileSystemNode {
  private children: FileSystemNode[] = [];

  constructor(private name: string) {}

  getName(): string { return this.name; }

  getSize(): number {
    return this.children.reduce((sum, child) => sum + child.getSize(), 0);
  }

  add(node: FileSystemNode): void { this.children.push(node); }
  remove(node: FileSystemNode): void {
    this.children = this.children.filter(c => c !== node);
  }

  print(indent = ''): void {
    console.log(`${indent}+ ${this.name}/`);
    this.children.forEach(child => child.print(indent + '  '));
  }
}
```

### React Example
```tsx
// Composite pattern is fundamental to React's component model
interface MenuItemProps {
  label: string;
  onClick?: () => void;
  children?: React.ReactNode;
}

// Can be both leaf (no children) or composite (with children)
const MenuItem: React.FC<MenuItemProps> = ({ label, onClick, children }) => {
  const hasChildren = React.Children.count(children) > 0;

  return (
    <li>
      <span onClick={onClick}>{label}</span>
      {hasChildren && <ul>{children}</ul>}
    </li>
  );
};

// Usage - uniform treatment of leaves and composites
const Menu = () => (
  <ul>
    <MenuItem label="File">
      <MenuItem label="New" onClick={() => newFile()} />
      <MenuItem label="Open" onClick={() => openFile()} />
      <MenuItem label="Recent">
        <MenuItem label="document1.txt" />
        <MenuItem label="document2.txt" />
      </MenuItem>
    </MenuItem>
  </ul>
);
```

### Spring Example
```java
// Component
public interface OrganizationUnit {
    String getName();
    BigDecimal getBudget();
    void print(int indent);
}

// Leaf
@Component
public class Employee implements OrganizationUnit {
    private String name;
    private BigDecimal salary;

    public String getName() { return name; }
    public BigDecimal getBudget() { return salary; }
    public void print(int indent) {
        System.out.println(" ".repeat(indent) + "- " + name);
    }
}

// Composite
@Component
public class Department implements OrganizationUnit {
    private String name;
    private List<OrganizationUnit> members = new ArrayList<>();

    public void add(OrganizationUnit unit) { members.add(unit); }
    public void remove(OrganizationUnit unit) { members.remove(unit); }

    public String getName() { return name; }

    public BigDecimal getBudget() {
        return members.stream()
            .map(OrganizationUnit::getBudget)
            .reduce(BigDecimal.ZERO, BigDecimal::add);
    }

    public void print(int indent) {
        System.out.println(" ".repeat(indent) + "+ " + name);
        members.forEach(m -> m.print(indent + 2));
    }
}
```

## SKILL ACTIONS

```
TRIGGER: "part-whole hierarchy" OR "tree structure" OR "treat uniformly" OR "recursive composition"
ACTION: Apply Composite pattern with Component interface, Leaf implementations, and Composite containers
COUNTER-INDICATOR: No natural hierarchy exists; leaf and composite behaviors are fundamentally incompatible
```

```
TRIGGER: "clients distinguish between" AND ("primitive" OR "container" OR "leaf" OR "composite")
ACTION: Unify interfaces so clients can treat all objects polymorphically through Component
COUNTER-INDICATOR: The distinction is essential to correctness and should not be hidden
```

```
TRIGGER: "add/remove children" AND "common interface"
ACTION: Place child management operations in Component (transparency) or only in Composite (safety)
COUNTER-INDICATOR: Safety is paramount and type-unsafe operations are unacceptable
```

## CSO KEYWORDS

composite, tree structure, part-whole hierarchy, recursive composition, uniform treatment, component, leaf, container, child management, transparency vs safety, graphics system, file system, organization hierarchy, menu structure, DOM tree, AST, parse tree
