---
name: gof-proxy
classification: Structural / Object
description: "Use when you need to control access to an object—whether for lazy loading expensive resources, remote communication, access control, or smart reference counting; Symptoms: direct object creation is costly or constrained, clients need transparent access to remote or protected objects, resource management requires additional actions on access"
---

# PROXY

## INTENT

Provide a surrogate or placeholder for another object to control access to it.

## ALSO KNOWN AS

Surrogate

## PROBLEM INDICATORS

- **Expensive object creation**: Creating a resource-intensive object (large image, database connection, complex calculation) that may not be needed immediately or at all
- **Remote object access**: Needing to access objects in different address spaces while hiding the complexity of remote communication
- **Access control requirements**: Objects require protection or permission checks before allowing operations
- **Smart reference needs**: Additional actions needed when accessing an object (reference counting, loading on first access, locking for exclusive access, checking validity)
- **On-demand instantiation**: Full object creation should be deferred until the object is actually used
- **Copy-on-write optimization**: Multiple clients share an object until one needs to modify it

## KEY INSIGHT

A proxy provides a level of indirection that lets you intercept and control access to another object while maintaining the same interface—enabling lazy loading, remote communication, access control, and smart references without clients knowing they are not dealing with the real object.

## PARTICIPANTS

| Role | Responsibility |
|------|----------------|
| **Proxy** | Maintains a reference to the real subject; provides an interface identical to Subject so it can substitute for the real subject; controls access to the real subject and may be responsible for creating and deleting it; forwards requests to RealSubject when appropriate |
| **Subject** | Defines the common interface for RealSubject and Proxy so that a Proxy can be used anywhere a RealSubject is expected |
| **RealSubject** | Defines the real object that the proxy represents |

## CONSEQUENCES

### Benefits

1. **Remote proxy hides location**: Clients remain unaware that an object resides in a different address space
2. **Virtual proxy optimizes resources**: Expensive objects are created only on demand, improving startup time and memory usage
3. **Protection proxy enables access control**: Additional housekeeping tasks can be performed when an object is accessed
4. **Smart references add functionality**: Reference counting, first-access loading, object locking, and validity checks happen transparently
5. **Copy-on-write reduces costs**: Large objects can be shared until modification is needed, deferring expensive copying

### Liabilities

1. **Indirection overhead**: An additional level of indirection may introduce latency
2. **Implementation complexity**: Proxy must implement the full Subject interface
3. **Synchronization challenges**: Virtual proxies may face thread-safety issues during lazy instantiation
4. **Transparency illusion**: Clients may make assumptions about immediate availability or local access that don't hold

## WHEN NOT TO USE

- **Simple, cheap objects**: When object creation is inexpensive and immediate access is needed
- **Performance-critical paths**: When the indirection overhead is unacceptable
- **No access control needed**: When all clients have equal, unrestricted access
- **Interface instability**: When the Subject interface changes frequently, requiring parallel Proxy updates
- **Direct manipulation required**: When clients need to distinguish between proxy and real object

## RELATED PATTERNS

| Pattern | Relationship |
|---------|--------------|
| **Adapter** | Adapter provides a different interface to the object it adapts; Proxy provides the same interface as its subject |
| **Decorator** | Decorator adds responsibilities to an object; Proxy controls access to an object. Decorators can have similar implementations but different purposes |
| **Facade** | Facade provides a simplified interface to a subsystem; Proxy provides the same interface to control access to a single object |

## MODERN CONTEXT

### TypeScript: Virtual Proxy with Lazy Loading

```typescript
// Subject interface
interface Image {
  display(): void;
  getExtent(): { width: number; height: number };
}

// RealSubject - expensive to create
class HighResolutionImage implements Image {
  private data: ArrayBuffer;

  constructor(private filename: string) {
    // Expensive operation: load from disk/network
    console.log(`Loading image: ${filename}`);
    this.data = this.loadImageData(filename);
  }

  private loadImageData(filename: string): ArrayBuffer {
    // Simulate expensive loading
    return new ArrayBuffer(1024 * 1024 * 10); // 10MB
  }

  display(): void {
    console.log(`Displaying ${this.filename}`);
  }

  getExtent(): { width: number; height: number } {
    return { width: 1920, height: 1080 };
  }
}

// Proxy - defers loading until needed
class ImageProxy implements Image {
  private realImage: HighResolutionImage | null = null;
  private cachedExtent: { width: number; height: number } | null = null;

  constructor(private filename: string) {
    // Lightweight: only store filename, don't load image
  }

  private ensureLoaded(): HighResolutionImage {
    if (!this.realImage) {
      this.realImage = new HighResolutionImage(this.filename);
    }
    return this.realImage;
  }

  display(): void {
    this.ensureLoaded().display();
  }

  getExtent(): { width: number; height: number } {
    // Can return cached extent without loading full image
    if (this.cachedExtent) {
      return this.cachedExtent;
    }
    // In real implementation, might read just metadata
    return this.ensureLoaded().getExtent();
  }
}

// Usage
const images: Image[] = [
  new ImageProxy('photo1.jpg'),
  new ImageProxy('photo2.jpg'),
  new ImageProxy('photo3.jpg'),
];
// No images loaded yet

images[0].display(); // Now photo1.jpg loads and displays
```

### React: Protection Proxy with Access Control

```tsx
import React, { ComponentType, useContext } from 'react';

// Auth context
interface User {
  id: string;
  roles: string[];
}

const AuthContext = React.createContext<User | null>(null);

// Protection proxy HOC
function withAuthorization<P extends object>(
  WrappedComponent: ComponentType<P>,
  requiredRoles: string[]
) {
  return function AuthorizedComponent(props: P) {
    const user = useContext(AuthContext);

    if (!user) {
      return <div>Please log in to access this content.</div>;
    }

    const hasAccess = requiredRoles.some(role =>
      user.roles.includes(role)
    );

    if (!hasAccess) {
      return <div>You do not have permission to view this content.</div>;
    }

    return <WrappedComponent {...props} />;
  };
}

// Real component
function AdminDashboard({ title }: { title: string }) {
  return <div>Admin Dashboard: {title}</div>;
}

// Protected proxy component
const ProtectedAdminDashboard = withAuthorization(
  AdminDashboard,
  ['admin', 'superuser']
);

// Usage
function App() {
  return (
    <AuthContext.Provider value={{ id: '1', roles: ['user'] }}>
      <ProtectedAdminDashboard title="System Settings" />
      {/* Renders: "You do not have permission..." */}
    </AuthContext.Provider>
  );
}
```

### Spring: Remote Proxy with REST Client

```java
// Subject interface
public interface UserService {
    User findById(Long id);
    List<User> findAll();
    User save(User user);
}

// Remote proxy using Spring's RestTemplate
@Service
public class UserServiceProxy implements UserService {

    private final RestTemplate restTemplate;
    private final String baseUrl;

    public UserServiceProxy(
            RestTemplate restTemplate,
            @Value("${user-service.url}") String baseUrl) {
        this.restTemplate = restTemplate;
        this.baseUrl = baseUrl;
    }

    @Override
    public User findById(Long id) {
        return restTemplate.getForObject(
            baseUrl + "/users/{id}",
            User.class,
            id
        );
    }

    @Override
    public List<User> findAll() {
        User[] users = restTemplate.getForObject(
            baseUrl + "/users",
            User[].class
        );
        return Arrays.asList(users);
    }

    @Override
    public User save(User user) {
        return restTemplate.postForObject(
            baseUrl + "/users",
            user,
            User.class
        );
    }
}

// Spring also provides declarative remote proxies via Feign
@FeignClient(name = "user-service", url = "${user-service.url}")
public interface UserServiceClient extends UserService {

    @GetMapping("/users/{id}")
    User findById(@PathVariable Long id);

    @GetMapping("/users")
    List<User> findAll();

    @PostMapping("/users")
    User save(@RequestBody User user);
}

// Smart proxy with caching
@Service
public class CachingUserServiceProxy implements UserService {

    private final UserService delegate;
    private final Cache<Long, User> cache;

    public CachingUserServiceProxy(
            @Qualifier("remoteUserService") UserService delegate) {
        this.delegate = delegate;
        this.cache = Caffeine.newBuilder()
            .expireAfterWrite(Duration.ofMinutes(5))
            .maximumSize(1000)
            .build();
    }

    @Override
    public User findById(Long id) {
        return cache.get(id, delegate::findById);
    }

    @Override
    public List<User> findAll() {
        return delegate.findAll();
    }

    @Override
    public User save(User user) {
        User saved = delegate.save(user);
        cache.put(saved.getId(), saved);
        return saved;
    }
}
```

## SKILL ACTIONS

### TRIGGER
- Detect expensive object creation (database connections, large files, complex computations)
- Identify remote service calls that need local interface
- Spot access control scattered across client code
- Find reference counting or lifecycle management duplicated
- Notice copy-on-write optimization opportunities

### ACTION
1. Define Subject interface matching RealSubject's interface
2. Implement Proxy with same interface
3. Add control logic appropriate to proxy type:
   - Virtual: lazy instantiation in accessor methods
   - Remote: network communication and marshalling
   - Protection: access checks before delegation
   - Smart: reference counting, caching, or validation
4. Ensure Proxy forwards requests to RealSubject when appropriate
5. Consider thread safety for lazy instantiation

### COUNTER-INDICATOR
- Object creation is cheap and fast
- No access control or lifecycle management needed
- Indirection overhead unacceptable for performance
- Subject interface too unstable for parallel maintenance
- Clients need to distinguish proxy from real object

