---
name: gof-prototype
classification: Creational / Object
description: Use when classes to instantiate are specified at run-time or to avoid parallel factory hierarchies; Symptoms: excessive subclassing for object creation, class explosion from factory hierarchies, need to configure objects dynamically by copying pre-configured instances
---

# PROTOTYPE

## INTENT

Specify the kinds of objects to create using a prototypical instance, and create new objects by copying this prototype.

## ALSO KNOWN AS

None documented in GoF.

## PROBLEM INDICATORS

Use the Prototype pattern when a system should be independent of how its products are created, composed, and represented; and:

- When the classes to instantiate are specified at run-time (e.g., by dynamic loading)
- To avoid building a class hierarchy of factories that parallels the class hierarchy of products
- When instances of a class can have one of only a few different combinations of state (more convenient to install prototypes and clone them rather than instantiating manually with appropriate state each time)

## KEY INSIGHT

Instead of creating objects through constructors or factories, you clone a pre-configured prototype instance. This shifts the burden of object creation from knowing "which class to instantiate" to knowing "which prototype to copy," enabling run-time flexibility and eliminating the need for parallel factory class hierarchies.

## PARTICIPANTS

| Role | Responsibility |
|------|----------------|
| Prototype (Graphic) | Declares an interface for cloning itself |
| ConcretePrototype (Staff, WholeNote, HalfNote) | Implements an operation for cloning itself |
| Client (GraphicTool) | Creates a new object by asking a prototype to clone itself |

## CONSEQUENCES

### Benefits

1. **Adding and removing products at run-time** - Prototypes let you incorporate a new concrete product class into a system simply by registering a prototypical instance with the client. Clients can install and remove prototypes at run-time.

2. **Specifying new objects by varying values** - You can define new kinds of objects by instantiating existing classes and registering the instances as prototypes of client objects. A client can exhibit new behavior by delegating responsibility to the prototype. Cloning a prototype is similar to instantiating a class.

3. **Specifying new objects by varying structure** - Many applications build objects from parts and subparts. The Prototype pattern supports this by allowing complex, user-defined structures to be added as prototypes. As long as the composite object implements Clone as a deep copy, circuits/structures with different configurations can be prototypes.

4. **Reduced subclassing** - Factory Method often produces a hierarchy of Creator classes that parallels the product class hierarchy. The Prototype pattern lets you clone a prototype instead of asking a factory method to make a new object. Hence you don't need a Creator class hierarchy at all.

5. **Configuring an application with classes dynamically** - Some run-time environments let you load classes dynamically. The Prototype pattern is the key to exploiting such facilities in languages like C++, where you can't reference a dynamically loaded class's constructor statically.

### Liabilities

1. **Each subclass of Prototype must implement Clone** - This may be difficult when classes under consideration already exist. Implementing Clone can be difficult when internals include objects that don't support copying or have circular references.

## WHEN NOT TO USE

- When object creation is simple and constructors suffice
- When the cost of cloning is higher than direct instantiation
- When objects have complex initialization that cannot be captured in a prototype
- When objects contain references to external resources that cannot be meaningfully copied
- When deep copy semantics are unclear or impractical (circular references, shared state)
- When the prototype registry would become unwieldy or hard to maintain

## RELATED PATTERNS

| Pattern | Relationship |
|---------|--------------|
| Abstract Factory | Competing patterns in some ways; can also be used together. An Abstract Factory might store a set of prototypes from which to clone and return product objects. Prototype-based approach eliminates need for new concrete factory class for each new product family. |
| Composite | Designs that make heavy use of Composite often can benefit from Prototype as well |
| Decorator | Designs that make heavy use of Decorator often can benefit from Prototype as well |
| Factory Method | Prototype doesn't require subclassing Creator. However, prototypes often require an Initialize operation on the Product class. Factory Method doesn't require such an operation. |

## MODERN CONTEXT

### TypeScript Example

```typescript
// Prototype interface
interface Prototype<T> {
  clone(): T;
}

// Concrete prototype
class UserSettings implements Prototype<UserSettings> {
  constructor(
    public theme: string,
    public language: string,
    public notifications: { email: boolean; push: boolean }
  ) {}

  clone(): UserSettings {
    // Deep copy for nested objects
    return new UserSettings(
      this.theme,
      this.language,
      { ...this.notifications }
    );
  }
}

// Prototype registry/manager
class SettingsPrototypeRegistry {
  private prototypes: Map<string, UserSettings> = new Map();

  register(name: string, prototype: UserSettings): void {
    this.prototypes.set(name, prototype);
  }

  create(name: string): UserSettings | undefined {
    const prototype = this.prototypes.get(name);
    return prototype?.clone();
  }
}

// Usage
const registry = new SettingsPrototypeRegistry();
registry.register('default', new UserSettings('light', 'en', { email: true, push: false }));
registry.register('power-user', new UserSettings('dark', 'en', { email: true, push: true }));

const newUserSettings = registry.create('default');
```

### React Example

```tsx
// Prototype pattern for component configurations
interface ComponentConfig {
  style: React.CSSProperties;
  className: string;
  props: Record<string, unknown>;
}

const configPrototypes: Record<string, ComponentConfig> = {
  primaryButton: {
    style: { backgroundColor: 'blue', color: 'white' },
    className: 'btn btn-primary',
    props: { type: 'button' }
  },
  dangerButton: {
    style: { backgroundColor: 'red', color: 'white' },
    className: 'btn btn-danger',
    props: { type: 'button' }
  }
};

function cloneConfig(name: string): ComponentConfig {
  const proto = configPrototypes[name];
  return {
    style: { ...proto.style },
    className: proto.className,
    props: { ...proto.props }
  };
}

// React hook for prototype-based state initialization
function usePrototypeState<T>(prototype: T): [T, React.Dispatch<React.SetStateAction<T>>] {
  return React.useState(() => structuredClone(prototype));
}
```

### Spring/Java Example

```java
// Spring supports prototype scope natively
@Component
@Scope("prototype")
public class ShoppingCart implements Cloneable {
    private List<Item> items = new ArrayList<>();
    private UserPreferences preferences;

    @Override
    public ShoppingCart clone() {
        try {
            ShoppingCart cloned = (ShoppingCart) super.clone();
            // Deep copy mutable fields
            cloned.items = new ArrayList<>(this.items);
            cloned.preferences = this.preferences.clone();
            return cloned;
        } catch (CloneNotSupportedException e) {
            throw new RuntimeException(e);
        }
    }
}

// Prototype registry using Spring
@Component
public class DocumentPrototypeRegistry {
    private final Map<String, Document> prototypes = new ConcurrentHashMap<>();

    public void registerPrototype(String key, Document prototype) {
        prototypes.put(key, prototype);
    }

    public Document createDocument(String key) {
        Document prototype = prototypes.get(key);
        if (prototype == null) {
            throw new IllegalArgumentException("Unknown prototype: " + key);
        }
        return prototype.clone();
    }
}

// Modern Java with Records (immutable, so "cloning" is just copying with modifications)
public record ImmutableConfig(String name, Map<String, String> settings) {
    public ImmutableConfig withSetting(String key, String value) {
        var newSettings = new HashMap<>(settings);
        newSettings.put(key, value);
        return new ImmutableConfig(name, Map.copyOf(newSettings));
    }
}
```

## SKILL ACTIONS

### TRIGGER
- "Need to create objects whose type is determined at runtime"
- "Factory hierarchy is mirroring product hierarchy"
- "Want to avoid subclassing just to change instantiation"
- "Need to create pre-configured object variants"
- "Classes loaded dynamically need instantiation"
- "Object creation is expensive but copying is cheap"

### ACTION
1. Define a Prototype interface with a `clone()` method
2. Implement clone in each ConcretePrototype (handle deep vs shallow copy)
3. Create a prototype registry/manager if prototypes need to be looked up by key
4. Initialize prototypes with desired state
5. Client requests clones from prototypes rather than using constructors
6. Add Initialize operation if clones need post-copy configuration

### COUNTER-INDICATOR
- Object creation is trivial (no complex initialization)
- Deep copying is problematic (circular refs, external resources)
- Objects are immutable (just share references instead)
- Prototype management overhead exceeds benefits
- Clone semantics are unclear for the domain

## CSO KEYWORDS

- prototype pattern
- clone method
- object cloning
- deep copy vs shallow copy
- prototype registry
- prototype manager
- runtime object creation
- dynamic instantiation
- copy constructor
- creational pattern
- avoid factory subclassing
- prototype-based creation
- cloneable interface
- object copying
- pre-configured instances
- prototype scope (Spring)
- structuredClone (JavaScript)
