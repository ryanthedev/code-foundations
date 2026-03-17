---
name: gof-abstract-factory
classification: Creational / Object
description: Use when system needs platform/family independence for object creation; Symptoms: scattered concrete class instantiation, inconsistent product mixing, hard-coded class names throughout codebase
---

# ABSTRACT FACTORY

## INTENT

Provide an interface for creating families of related or dependent objects without specifying their concrete classes.

## ALSO KNOWN AS

Kit

## PROBLEM INDICATORS

- A system should be independent of how its products are created, composed, and represented
- A system should be configured with one of multiple families of products
- A family of related product objects is designed to be used together, and you need to enforce this constraint
- You want to provide a class library of products, and you want to reveal just their interfaces, not their implementations

## KEY INSIGHT

The pattern decouples client code from concrete product classes by introducing an abstract factory interface. The factory creates entire families of related objects, ensuring that products from different families are never mixed - the whole product family changes at once simply by switching the concrete factory.

## PARTICIPANTS

| Role | Responsibility |
|------|----------------|
| AbstractFactory (WidgetFactory) | Declares an interface for operations that create abstract product objects |
| ConcreteFactory (MotifWidgetFactory, PMWidgetFactory) | Implements the operations to create concrete product objects |
| AbstractProduct (Window, ScrollBar) | Declares an interface for a type of product object |
| ConcreteProduct (MotifWindow, MotifScrollBar) | Defines a product object to be created by the corresponding concrete factory; implements the AbstractProduct interface |
| Client | Uses only interfaces declared by AbstractFactory and AbstractProduct classes |

## CONSEQUENCES

### Benefits

1. **It isolates concrete classes.** The Abstract Factory pattern helps you control the classes of objects that an application creates. Because a factory encapsulates the responsibility and the process of creating product objects, it isolates clients from implementation classes. Clients manipulate instances through their abstract interfaces. Product class names are isolated in the implementation of the concrete factory; they do not appear in client code.

2. **It makes exchanging product families easy.** The class of a concrete factory appears only once in an application - where it's instantiated. This makes it easy to change the concrete factory an application uses. It can use different product configurations simply by changing the concrete factory. Because an abstract factory creates a complete family of products, the whole product family changes at once.

3. **It promotes consistency among products.** When product objects in a family are designed to work together, it's important that an application use objects from only one family at a time. AbstractFactory makes this easy to enforce.

### Liabilities

4. **Supporting new kinds of products is difficult.** Extending abstract factories to produce new kinds of Products isn't easy. That's because the AbstractFactory interface fixes the set of products that can be created. Supporting new kinds of products requires extending the factory interface, which involves changing the AbstractFactory class and all of its subclasses.

## WHEN NOT TO USE

- When products do not form natural families or have no dependencies between them
- When the system only needs one type of product (use Factory Method instead)
- When the product hierarchy is unlikely to change but new concrete products are frequently added (Prototype may be more suitable)
- When the overhead of creating factory hierarchies outweighs the flexibility benefits (simple applications)
- When clients need fine-grained control over product creation beyond what factory methods provide (Builder may be more appropriate)

## RELATED PATTERNS

| Pattern | Relationship |
|---------|--------------|
| Factory Method | AbstractFactory classes are often implemented with factory methods. Each factory method in the abstract factory creates one product type. |
| Prototype | Can be used to implement concrete factories. The factory stores prototypical instances of each product and creates new products by cloning. |
| Singleton | A concrete factory is often a singleton since an application typically needs only one instance of a ConcreteFactory per product family. |
| Builder | Similar in that it constructs complex objects, but Builder focuses on step-by-step construction while Abstract Factory emphasizes families of products. |

## MODERN CONTEXT

### TypeScript Example

```typescript
// Abstract products
interface Button {
  render(): void;
  onClick(handler: () => void): void;
}

interface TextField {
  render(): void;
  getValue(): string;
}

// Abstract factory
interface UIComponentFactory {
  createButton(): Button;
  createTextField(): TextField;
}

// Concrete products - Material Design
class MaterialButton implements Button {
  render(): void { console.log('Rendering Material button'); }
  onClick(handler: () => void): void { /* Material click handling */ }
}

class MaterialTextField implements TextField {
  render(): void { console.log('Rendering Material text field'); }
  getValue(): string { return 'material-value'; }
}

// Concrete factory - Material Design
class MaterialUIFactory implements UIComponentFactory {
  createButton(): Button { return new MaterialButton(); }
  createTextField(): TextField { return new MaterialTextField(); }
}

// Concrete products - iOS
class IOSButton implements Button {
  render(): void { console.log('Rendering iOS button'); }
  onClick(handler: () => void): void { /* iOS click handling */ }
}

class IOSTextField implements TextField {
  render(): void { console.log('Rendering iOS text field'); }
  getValue(): string { return 'ios-value'; }
}

// Concrete factory - iOS
class IOSUIFactory implements UIComponentFactory {
  createButton(): Button { return new IOSButton(); }
  createTextField(): TextField { return new IOSTextField(); }
}

// Client code
function buildForm(factory: UIComponentFactory) {
  const button = factory.createButton();
  const textField = factory.createTextField();
  button.render();
  textField.render();
}
```

### React Example

```tsx
// Abstract factory as a context provider
interface ThemeComponents {
  Button: React.FC<{ onClick: () => void; children: React.ReactNode }>;
  Card: React.FC<{ title: string; children: React.ReactNode }>;
  Input: React.FC<{ value: string; onChange: (v: string) => void }>;
}

// Light theme factory
const LightThemeComponents: ThemeComponents = {
  Button: ({ onClick, children }) => (
    <button className="bg-white text-black border" onClick={onClick}>
      {children}
    </button>
  ),
  Card: ({ title, children }) => (
    <div className="bg-gray-100 p-4 rounded">
      <h3 className="text-black">{title}</h3>
      {children}
    </div>
  ),
  Input: ({ value, onChange }) => (
    <input
      className="border bg-white text-black"
      value={value}
      onChange={(e) => onChange(e.target.value)}
    />
  ),
};

// Dark theme factory
const DarkThemeComponents: ThemeComponents = {
  Button: ({ onClick, children }) => (
    <button className="bg-gray-800 text-white" onClick={onClick}>
      {children}
    </button>
  ),
  Card: ({ title, children }) => (
    <div className="bg-gray-900 p-4 rounded">
      <h3 className="text-white">{title}</h3>
      {children}
    </div>
  ),
  Input: ({ value, onChange }) => (
    <input
      className="border-gray-600 bg-gray-800 text-white"
      value={value}
      onChange={(e) => onChange(e.target.value)}
    />
  ),
};

// Context for the factory
const ThemeContext = React.createContext<ThemeComponents>(LightThemeComponents);

// Client component uses factory products without knowing concrete types
function UserForm() {
  const { Button, Card, Input } = React.useContext(ThemeContext);
  const [name, setName] = React.useState('');

  return (
    <Card title="User Registration">
      <Input value={name} onChange={setName} />
      <Button onClick={() => console.log(name)}>Submit</Button>
    </Card>
  );
}
```

### Spring (Java) Example

```java
// Abstract products
public interface DataSource {
    Connection getConnection();
}

public interface TransactionManager {
    void begin();
    void commit();
    void rollback();
}

// Abstract factory
public interface PersistenceFactory {
    DataSource createDataSource();
    TransactionManager createTransactionManager();
}

// Concrete factory for MySQL
@Configuration
@Profile("mysql")
public class MySQLPersistenceFactory implements PersistenceFactory {

    @Bean
    @Override
    public DataSource createDataSource() {
        return DataSourceBuilder.create()
            .driverClassName("com.mysql.cj.jdbc.Driver")
            .url("jdbc:mysql://localhost:3306/mydb")
            .build();
    }

    @Bean
    @Override
    public TransactionManager createTransactionManager() {
        return new DataSourceTransactionManager(createDataSource());
    }
}

// Concrete factory for PostgreSQL
@Configuration
@Profile("postgres")
public class PostgreSQLPersistenceFactory implements PersistenceFactory {

    @Bean
    @Override
    public DataSource createDataSource() {
        return DataSourceBuilder.create()
            .driverClassName("org.postgresql.Driver")
            .url("jdbc:postgresql://localhost:5432/mydb")
            .build();
    }

    @Bean
    @Override
    public TransactionManager createTransactionManager() {
        return new DataSourceTransactionManager(createDataSource());
    }
}

// Client service - unaware of concrete database
@Service
public class UserRepository {
    private final DataSource dataSource;
    private final TransactionManager transactionManager;

    public UserRepository(DataSource dataSource, TransactionManager transactionManager) {
        this.dataSource = dataSource;
        this.transactionManager = transactionManager;
    }

    // Uses abstract products...
}
```

## SKILL ACTIONS

### TRIGGER
- Multiple families or variants of related objects exist (themes, platforms, databases)
- Client code instantiates concrete classes directly throughout the codebase
- Switching between product variants requires widespread code changes
- Products have implicit compatibility constraints that are not enforced

### ACTION
1. Identify the product families and the abstract product interfaces
2. Create an AbstractFactory interface with create methods for each product type
3. Implement ConcreteFactory classes for each product family
4. Refactor client code to depend only on abstract interfaces
5. Inject the appropriate factory at configuration/startup time

### COUNTER-INDICATOR
- Only one product family will ever exist
- Products have no meaningful relationships or compatibility constraints
- The system is simple and unlikely to require platform/variant abstraction
- Adding new product types is more common than adding new product families

## CSO KEYWORDS

- product family
- platform independence
- kit
- widget factory
- look and feel
- cross-platform
- theme switching
- database abstraction
- UI component library
- dependency injection
- configuration-based instantiation
- encapsulated instantiation
- family consistency
- variant isolation
