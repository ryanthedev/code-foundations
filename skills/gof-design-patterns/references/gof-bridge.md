---
name: gof-bridge
classification: Structural / Object
description: |
  Applicability Trigger: You need to decouple an abstraction from its implementation so both can vary independently without affecting each other.

  Symptoms:
  - Permanent binding between abstraction and implementation at compile time
  - Need to extend both abstraction hierarchy and implementation hierarchy independently
  - Implementation changes should not require client recompilation
  - Class proliferation due to nested generalizations (one hierarchy for each combination)
  - Need to share an implementation among multiple objects
  - Need to switch implementations at runtime
---

## INTENT

Decouple an abstraction from its implementation so that the two can vary independently.

## ALSO KNOWN AS

Handle/Body

## PROBLEM INDICATORS

- You want to avoid a permanent binding between an abstraction and its implementation (e.g., when the implementation must be selected or switched at run-time)
- Both abstractions and their implementations should be extensible by subclassing, and you want to combine them independently
- Changes to the implementation of an abstraction should have no impact on clients (no recompilation needed)
- You have a proliferation of classes resulting from coupling interface to many implementations
- You have "nested generalizations" where a class hierarchy needs to be specialized along multiple dimensions
- You want to share an implementation among multiple objects (perhaps using reference counting) while hiding this from the client

## KEY INSIGHT

Instead of using inheritance to bind an abstraction to its implementation, the Bridge pattern uses object composition. The abstraction maintains a reference to an implementor object, allowing both hierarchies to evolve independently and enabling run-time binding between them.

## PARTICIPANTS

| Role | Responsibility |
|------|----------------|
| **Abstraction** | Defines the abstraction's interface; maintains a reference to an object of type Implementor |
| **RefinedAbstraction** | Extends the interface defined by Abstraction with additional operations |
| **Implementor** | Defines the interface for implementation classes; does not have to correspond exactly to Abstraction's interface (typically Implementor provides primitive operations, Abstraction defines higher-level operations) |
| **ConcreteImplementor** | Implements the Implementor interface and defines its concrete implementation |

## CONSEQUENCES

**Benefits:**

1. **Decoupling interface and implementation.** An implementation is not bound permanently to an interface. The implementation of an abstraction can be configured at run-time, and it's even possible for an object to change its implementation at run-time. Decoupling also eliminates compile-time dependencies on the implementation, encouraging layered architectures.

2. **Improved extensibility.** You can extend the Abstraction and Implementor hierarchies independently. You can introduce new abstractions without changing implementors and vice versa.

3. **Hiding implementation details from clients.** You can shield clients from implementation details, like the sharing of implementor objects and the accompanying reference count mechanism (if any).

**Liabilities:**

1. **Increased complexity.** The pattern adds another level of indirection, which can make the system slightly more complex to understand initially.

2. **Performance overhead.** The extra level of indirection can introduce a small performance cost due to delegation.

## WHEN NOT TO USE

- When you only have one implementation and it's unlikely to change
- When the abstraction and implementation are tightly coupled by design and should evolve together
- When the additional complexity of the pattern is not justified by the flexibility it provides
- When performance is critical and the indirection overhead is unacceptable
- When the system is simple enough that direct inheritance provides sufficient flexibility

## RELATED PATTERNS

| Pattern | Relationship |
|---------|--------------|
| **Abstract Factory** | Can create and configure a particular Bridge. Encapsulates the creation of the Implementor objects, allowing the abstraction to remain unaware of concrete implementor types. |
| **Adapter** | Adapter is used to make unrelated classes work together after they're designed; Bridge is used up-front in a design to let abstractions and implementations vary independently. |

## MODERN CONTEXT

**TypeScript Example:**
```typescript
// Implementor interface
interface RenderingEngine {
  renderShape(shape: string): void;
  renderText(text: string, x: number, y: number): void;
}

// Concrete Implementors
class CanvasRenderer implements RenderingEngine {
  renderShape(shape: string): void {
    console.log(`Canvas: Drawing ${shape}`);
  }
  renderText(text: string, x: number, y: number): void {
    console.log(`Canvas: Text "${text}" at (${x}, ${y})`);
  }
}

class SVGRenderer implements RenderingEngine {
  renderShape(shape: string): void {
    console.log(`SVG: Creating ${shape} element`);
  }
  renderText(text: string, x: number, y: number): void {
    console.log(`SVG: Text element "${text}" at (${x}, ${y})`);
  }
}

// Abstraction
abstract class UIComponent {
  constructor(protected renderer: RenderingEngine) {}
  abstract draw(): void;
}

// Refined Abstractions
class Button extends UIComponent {
  draw(): void {
    this.renderer.renderShape('rectangle');
    this.renderer.renderText('Click me', 10, 10);
  }
}

class Icon extends UIComponent {
  constructor(renderer: RenderingEngine, private iconPath: string) {
    super(renderer);
  }
  draw(): void {
    this.renderer.renderShape(`icon:${this.iconPath}`);
  }
}
```

**React Example:**
```tsx
// Bridge pattern separating UI components from rendering strategies
interface ThemeRenderer {
  buttonStyle: React.CSSProperties;
  containerStyle: React.CSSProperties;
}

const LightTheme: ThemeRenderer = {
  buttonStyle: { backgroundColor: '#fff', color: '#333' },
  containerStyle: { backgroundColor: '#f5f5f5' }
};

const DarkTheme: ThemeRenderer = {
  buttonStyle: { backgroundColor: '#333', color: '#fff' },
  containerStyle: { backgroundColor: '#1a1a1a' }
};

// Abstraction via Context
const ThemeContext = React.createContext<ThemeRenderer>(LightTheme);

// Refined Abstraction components
const ThemedButton: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const theme = useContext(ThemeContext);
  return <button style={theme.buttonStyle}>{children}</button>;
};

// Switch implementation at runtime
const App: React.FC = () => {
  const [theme, setTheme] = useState<ThemeRenderer>(LightTheme);
  return (
    <ThemeContext.Provider value={theme}>
      <ThemedButton>Click Me</ThemedButton>
      <button onClick={() => setTheme(theme === LightTheme ? DarkTheme : LightTheme)}>
        Toggle Theme
      </button>
    </ThemeContext.Provider>
  );
};
```

**Spring Example:**
```java
// Implementor interface
public interface MessageSender {
    void send(String message, String recipient);
}

// Concrete Implementors
@Component("emailSender")
public class EmailSender implements MessageSender {
    public void send(String message, String recipient) {
        // Send via email
    }
}

@Component("smsSender")
public class SmsSender implements MessageSender {
    public void send(String message, String recipient) {
        // Send via SMS
    }
}

// Abstraction
public abstract class Notification {
    protected final MessageSender sender;

    protected Notification(MessageSender sender) {
        this.sender = sender;
    }

    public abstract void notify(String recipient);
}

// Refined Abstraction
@Service
public class AlertNotification extends Notification {
    @Autowired
    public AlertNotification(@Qualifier("emailSender") MessageSender sender) {
        super(sender);
    }

    public void notify(String recipient) {
        sender.send("ALERT: System notification", recipient);
    }
}
```

## SKILL ACTIONS

**TRIGGER:** Developer mentions needing to support multiple implementations of an abstraction, or describes class explosion due to combining interface variations with implementation variations.

**ACTION:** Recommend the Bridge pattern. Guide the developer to:
1. Identify the abstraction (high-level interface clients use)
2. Identify the implementor (low-level operations interface)
3. Create an Implementor interface with primitive operations
4. Have the Abstraction hold a reference to Implementor
5. Implement ConcreteImplementors for each platform/variant
6. Create RefinedAbstractions for extended functionality

**COUNTER-INDICATOR:** If there's only one implementation and no foreseeable need for variation, or if the abstraction and implementation should be tightly coupled, suggest simpler direct inheritance or composition instead.

