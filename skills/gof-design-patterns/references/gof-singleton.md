---
name: gof-singleton
classification: Creational / Object
description: Use when exactly one instance of a class must exist system-wide with a well-known access point; Symptoms: multiple global variables storing sole instances, inconsistent state from duplicate instances, need for controlled access to shared resource
---

## INTENT

Ensure a class only has one instance, and provide a global point of access to it.

## ALSO KNOWN AS

(None specified in GoF)

## PROBLEM INDICATORS

- There must be exactly one instance of a class, and it must be accessible to clients from a well-known access point
- The sole instance should be extensible by subclassing, and clients should be able to use an extended instance without modifying their code
- Multiple printers in a system but only one printer spooler needed
- Single file system, window manager, or A/D converter required
- Accounting system dedicated to serving one company
- Global variables making objects accessible but not preventing multiple instantiation

## KEY INSIGHT

The class itself becomes responsible for keeping track of its sole instance by intercepting requests to create new objects and providing a way to access the single instance. This eliminates the need for global variables while guaranteeing exactly one instance exists.

## PARTICIPANTS

| Role | Responsibility |
|------|----------------|
| Singleton | Defines an Instance operation (class method/static member function) that lets clients access its unique instance. May be responsible for creating its own unique instance. |

## CONSEQUENCES

### Benefits

1. **Controlled access to sole instance** - Because the Singleton class encapsulates its sole instance, it can have strict control over how and when clients access it.

2. **Reduced name space** - The Singleton pattern is an improvement over global variables. It avoids polluting the name space with global variables that store sole instances.

3. **Permits refinement of operations and representation** - The Singleton class may be subclassed, and it's easy to configure an application with an instance of this extended class. You can configure the application with an instance of the class you need at run-time.

4. **Permits a variable number of instances** - The pattern makes it easy to change your mind and allow more than one instance of the Singleton class. Only the operation that grants access to the Singleton instance needs to change.

5. **More flexible than class operations** - Static member functions in C++ are never virtual, so subclasses cannot override them polymorphically. Singleton allows polymorphic behavior.

### Liabilities

1. **Subclassing complexity** - The main issue is not defining the subclass but installing its unique instance so that clients can use it. The variable referring to the singleton instance must be initialized with the subclass instance.

2. **Global state concerns** - While better than global variables, singletons still introduce global state into an application.

3. **Testing challenges** - Singletons can make unit testing difficult due to their global nature and persistent state between tests.

## WHEN NOT TO USE

- When multiple instances may be needed in the future (consider if the constraint is truly permanent)
- When the singleton would simply wrap static methods without needing instance state
- In highly concurrent systems where the singleton becomes a bottleneck
- When dependency injection can provide the same benefits with better testability
- When the "single instance" requirement is environment-specific rather than domain-inherent

## RELATED PATTERNS

| Pattern | Relationship |
|---------|--------------|
| Abstract Factory | Often implemented as a Singleton. A concrete factory is often a singleton. |
| Builder | Can be implemented using Singleton pattern. |
| Prototype | Can use Singleton in its implementation. |
| Facade | Often implemented as Singleton when only one Facade object is needed. |
| State | State objects are often Singletons. |

## MODERN CONTEXT

### TypeScript Example

```typescript
class ConfigurationManager {
  private static instance: ConfigurationManager;
  private config: Map<string, unknown> = new Map();

  private constructor() {
    // Private constructor prevents direct instantiation
  }

  public static getInstance(): ConfigurationManager {
    if (!ConfigurationManager.instance) {
      ConfigurationManager.instance = new ConfigurationManager();
    }
    return ConfigurationManager.instance;
  }

  public get<T>(key: string): T | undefined {
    return this.config.get(key) as T;
  }

  public set(key: string, value: unknown): void {
    this.config.set(key, value);
  }
}

// Usage
const config = ConfigurationManager.getInstance();
config.set('apiUrl', 'https://api.example.com');
```

### React Example (Context-based Singleton)

```typescript
import React, { createContext, useContext, useState, ReactNode } from 'react';

interface AuthState {
  user: User | null;
  login: (credentials: Credentials) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthState | undefined>(undefined);

// Singleton-like provider - only one instance in the component tree
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  const login = async (credentials: Credentials) => {
    const user = await authService.login(credentials);
    setUser(user);
  };

  const logout = () => {
    authService.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthState {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
```

### Spring Framework Example

```java
// Spring beans are singletons by default
@Service
public class UserService {
    private final UserRepository userRepository;

    @Autowired
    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    public User findById(Long id) {
        return userRepository.findById(id).orElse(null);
    }
}

// Explicit singleton scope (default behavior)
@Configuration
public class AppConfig {

    @Bean
    @Scope(ConfigurableBeanFactory.SCOPE_SINGLETON)
    public CacheManager cacheManager() {
        return new ConcurrentMapCacheManager();
    }
}

// Thread-safe eager initialization
@Component
public class ApplicationRegistry {
    private static final ApplicationRegistry INSTANCE = new ApplicationRegistry();

    private final Map<String, Object> registry = new ConcurrentHashMap<>();

    private ApplicationRegistry() {}

    public static ApplicationRegistry getInstance() {
        return INSTANCE;
    }
}
```

## SKILL ACTIONS

### Action 1: Identify Singleton Candidates

**TRIGGER:** Developer mentions needing "only one" of something, uses global variables for shared state, or describes resource managers (connection pools, caches, configuration)

**ACTION:** Evaluate if Singleton is appropriate:
1. Confirm the single-instance requirement is inherent to the domain
2. Check if the instance needs to be accessible from multiple places
3. Consider if subclassing/extension might be needed
4. Evaluate thread-safety requirements

**COUNTER-INDICATOR:** If the "single instance" is only for convenience or could legitimately have multiple instances in different contexts (testing, multi-tenancy), prefer dependency injection instead

### Action 2: Implement Thread-Safe Singleton

**TRIGGER:** Implementing Singleton in a multi-threaded environment or when lazy initialization is required

**ACTION:** Use appropriate thread-safe initialization:
- For Java: Use enum singleton or static holder pattern
- For TypeScript/JavaScript: Module-level instance (naturally singleton due to module caching)
- For C++: Use Meyers' Singleton (local static) or double-checked locking with memory barriers
- For Spring/frameworks: Leverage built-in singleton scope

**COUNTER-INDICATOR:** If initialization is simple and cheap, prefer eager initialization over lazy initialization to avoid synchronization complexity

### Action 3: Singleton with Subclassing

**TRIGGER:** Need to vary singleton behavior based on environment, configuration, or runtime conditions

**ACTION:** Implement registry-based or environment-driven subclass selection:
1. Define base Singleton class with protected constructor
2. Create subclasses with specific behaviors
3. Use Instance() method to select appropriate subclass based on configuration
4. Consider Abstract Factory if multiple related singletons need coordinated selection

**COUNTER-INDICATOR:** If subclass selection is complex or frequent, consider Strategy pattern with a singleton context instead

## CSO KEYWORDS

- singleton pattern
- single instance
- global access point
- lazy initialization
- eager initialization
- thread-safe singleton
- double-checked locking
- static instance
- getInstance method
- private constructor
- controlled instantiation
- unique instance
- registry pattern
- module pattern
- service locator
- dependency injection alternative
- singleton scope
- application context
- shared resource
- global state management
