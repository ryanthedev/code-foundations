---
name: gof-factory-method
classification: Creational / Class
description: "Use when a class cannot anticipate the class of objects it must create, or wants subclasses to specify the objects it creates; Symptoms: hard-coded class names in constructors, parallel class hierarchies requiring coordinated instantiation, framework code that must instantiate application-specific classes"
---

# FACTORY METHOD

## INTENT

Define an interface for creating an object, but let subclasses decide which class to instantiate. Factory Method lets a class defer instantiation to subclasses.

## ALSO KNOWN AS

Virtual Constructor

## PROBLEM INDICATORS

- A class cannot anticipate the class of objects it must create
- A class wants its subclasses to specify the objects it creates
- Classes delegate responsibility to one of several helper subclasses, and you want to localize the knowledge of which helper subclass is the delegate
- Framework code needs to create objects but only knows about abstract classes
- Hard-coded class names appear throughout instantiation code, making it inflexible
- Changing the class that gets instantiated requires modifying or overriding entire methods

## KEY INSIGHT

By replacing direct constructor calls with calls to an overridable factory method, you decouple the code that uses objects from the code that decides which concrete class to instantiate. The "decision" of which class to create moves from compile-time to runtime and from the calling code to a subclass, enabling frameworks to work with application-specific classes they cannot predict.

## PARTICIPANTS

| Role | Responsibility |
|------|----------------|
| Product | Defines the interface of objects the factory method creates |
| ConcreteProduct | Implements the Product interface |
| Creator | Declares the factory method, which returns an object of type Product; may define a default implementation; may call the factory method to create a Product object |
| ConcreteCreator | Overrides the factory method to return an instance of a ConcreteProduct |

## CONSEQUENCES

### Benefits

1. **Eliminates binding to application-specific classes** - The code only deals with the Product interface; therefore it can work with any user-defined ConcreteProduct classes
2. **Provides hooks for subclasses** - Creating objects inside a class with a factory method is always more flexible than creating an object directly; gives subclasses a hook for providing an extended version of an object
3. **Connects parallel class hierarchies** - Localizes knowledge of which classes belong together; clients can find factory methods useful when parallel hierarchies exist (e.g., Figure and Manipulator hierarchies)

### Liabilities

1. **May require subclassing Creator** - Clients might have to subclass the Creator class just to create a particular ConcreteProduct object; subclassing is fine when the client has to subclass Creator anyway, but otherwise adds complexity
2. **Requires parallel hierarchy maintenance** - When using parameterized factory methods, adding new product types may require modifying the factory method

## WHEN NOT TO USE

- When the class that is instantiated never changes and there is no need for extension
- When instantiation takes place in an operation that subclasses can easily override (such as an initialization operation)
- When you need to create families of related objects together (use Abstract Factory instead)
- When the construction process is complex and should be separated from representation (use Builder instead)
- When classes to create are determined at runtime by configuration or cloning (use Prototype instead)
- When you need a single, globally accessible instance (use Singleton instead)

## RELATED PATTERNS

| Pattern | Relationship |
|---------|--------------|
| Abstract Factory | Often implemented with factory methods; Abstract Factory classes are often implemented using Factory Method |
| Template Method | Factory methods are usually called within Template Methods; the template method defines the skeleton, factory method creates the objects needed |
| Prototype | Does not require subclassing Creator, but often requires an Initialize operation on the Product class; Factory Method does not require such an operation |
| Singleton | Concrete factories are often singletons |

## MODERN CONTEXT

### TypeScript Example

```typescript
// Product interface
interface Logger {
  log(message: string): void;
}

// Concrete Products
class ConsoleLogger implements Logger {
  log(message: string): void {
    console.log(`[Console] ${message}`);
  }
}

class FileLogger implements Logger {
  log(message: string): void {
    // Write to file
    console.log(`[File] ${message}`);
  }
}

// Creator with factory method
abstract class Application {
  // Factory Method
  abstract createLogger(): Logger;

  run(): void {
    const logger = this.createLogger();
    logger.log("Application started");
    // ... application logic
  }
}

// Concrete Creators
class DevelopmentApp extends Application {
  createLogger(): Logger {
    return new ConsoleLogger();
  }
}

class ProductionApp extends Application {
  createLogger(): Logger {
    return new FileLogger();
  }
}
```

### React Example

```tsx
// Factory method pattern for creating form field components
interface FieldProps {
  name: string;
  value: string;
  onChange: (value: string) => void;
}

// Product interface
type FieldComponent = React.FC<FieldProps>;

// Creator hook with factory method
function useFormFieldFactory(fieldType: string): FieldComponent {
  // Factory method - subcomponents/configurations determine concrete type
  const createField = (): FieldComponent => {
    switch (fieldType) {
      case 'text':
        return TextInput;
      case 'email':
        return EmailInput;
      case 'password':
        return PasswordInput;
      default:
        return TextInput;
    }
  };

  return createField();
}

// Usage in form component
function DynamicForm({ schema }: { schema: FieldSchema[] }) {
  return (
    <form>
      {schema.map(field => {
        const FieldComponent = useFormFieldFactory(field.type);
        return <FieldComponent key={field.name} {...field} />;
      })}
    </form>
  );
}
```

### Spring Framework Example

```java
// Product interface
public interface NotificationService {
    void send(String recipient, String message);
}

// Concrete Products
@Component("emailNotification")
public class EmailNotificationService implements NotificationService {
    @Override
    public void send(String recipient, String message) {
        // Send email
    }
}

@Component("smsNotification")
public class SmsNotificationService implements NotificationService {
    @Override
    public void send(String recipient, String message) {
        // Send SMS
    }
}

// Creator with factory method (using Spring's dependency injection)
@Component
public abstract class NotificationSender {

    // Factory method - implemented by configuration or subclass
    protected abstract NotificationService createNotificationService();

    public void notifyUser(String userId, String message) {
        NotificationService service = createNotificationService();
        String contact = lookupContact(userId);
        service.send(contact, message);
    }
}

// Alternative: Spring Factory Bean approach
@Component
public class NotificationServiceFactory {

    @Autowired
    private ApplicationContext context;

    // Parameterized factory method
    public NotificationService createService(String type) {
        return context.getBean(type + "Notification", NotificationService.class);
    }
}
```

## SKILL ACTIONS

### TRIGGER
- Code contains multiple `new ConcreteClass()` calls that may need to vary
- Framework or library code needs to create objects of application-specific classes
- Parallel class hierarchies exist where one hierarchy creates objects from another
- Client code uses conditional logic to decide which class to instantiate
- Need to provide extensibility points for object creation in a class hierarchy

### ACTION
1. Identify the Product (the common interface for created objects)
2. Create an abstract Creator class with a factory method returning Product type
3. Move object creation code into the factory method
4. For each ConcreteProduct, create a ConcreteCreator that overrides the factory method
5. Client code works with Creator and Product abstractions, not concrete classes
6. Consider providing a default implementation in Creator if a reasonable default exists

### COUNTER-INDICATOR
- Only one type of product will ever be created (no variation needed)
- Object creation is simple and does not benefit from encapsulation
- The cost of additional class hierarchy outweighs flexibility benefits
- Configuration-based or prototype-based creation would be simpler
- Products have many variations best handled by Abstract Factory

