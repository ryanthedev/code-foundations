---
name: gof-flyweight
classification: Structural / Object
description: |
  WHEN application uses large numbers of objects AND storage costs are high AND most object state can be made extrinsic AND many groups of objects may be replaced by relatively few shared objects once extrinsic state is removed AND application doesn't depend on object identity
  THEN use shared flyweight objects to support fine-grained objects efficiently by separating intrinsic (shareable) state from extrinsic (context-dependent) state
  SYMPTOMS: high memory consumption from many similar objects, storage costs from object quantity, performance degradation from object allocation overhead, need to treat many objects uniformly at fine granularity
---

## INTENT

Use sharing to support large numbers of fine-grained objects efficiently.

## ALSO KNOWN AS

(None listed in GoF)

## PROBLEM INDICATORS

- Application creates hundreds of thousands of similar objects (e.g., character objects in document editors)
- Storage costs are prohibitively expensive due to sheer quantity of objects
- Most object state can be extracted and passed in as context (extrinsic state)
- Many objects could be replaced by fewer shared objects once extrinsic state is removed
- Performance degrades due to memory allocation overhead
- Object identity is not required for correct application behavior
- Need to represent fine-grained elements (characters, particles, tiles) with objects

## KEY INSIGHT

Objects can be shared if their state is separated into intrinsic (stored in the flyweight, independent of context, shareable) and extrinsic (context-dependent, computed or stored by clients, passed to flyweight when needed). A document with 180,000 characters may only need 480 character objects when using flyweights.

## PARTICIPANTS

| Participant | Role | Example |
|-------------|------|---------|
| Flyweight | Declares interface through which flyweights receive and act on extrinsic state | Glyph |
| ConcreteFlyweight | Implements Flyweight interface; stores intrinsic state; must be sharable and context-independent | Character |
| UnsharedConcreteFlyweight | Not all Flyweight subclasses need to be shared; may have ConcreteFlyweights as children | Row, Column |
| FlyweightFactory | Creates and manages flyweight objects; ensures proper sharing; returns existing or creates new flyweight | GlyphFactory |
| Client | Maintains references to flyweights; computes or stores extrinsic state | Document, TextDocument |

## CONSEQUENCES

**Benefits:**

1. Reduces total number of instances through sharing
2. Reduces amount of intrinsic state per object
3. Extrinsic state can be computed rather than stored, saving additional space
4. Storage savings increase as more flyweights are shared
5. Greatest savings when objects have substantial intrinsic and extrinsic state

**Liabilities:**

1. Run-time costs for transferring, finding, and computing extrinsic state
2. Clients must pass extrinsic state to flyweight operations
3. Cannot rely on object identity for conceptually distinct objects
4. Flyweight leaf nodes cannot store parent pointers when combined with Composite
5. Complexity in managing the distinction between intrinsic and extrinsic state

## WHEN NOT TO USE

- When objects have little or no extrinsic state that can be removed
- When the number of different flyweights approaches the number of objects before sharing
- When object identity is required by the application
- When extrinsic state is too complex to compute or pass efficiently
- When storage costs are not a significant concern
- When objects are not numerous enough to justify the pattern's complexity
- When intrinsic state varies significantly between instances

## RELATED PATTERNS

| Pattern | Relationship |
|---------|--------------|
| Composite | Often combined with Flyweight to represent hierarchical structures as directed-acyclic graphs with shared leaf nodes; flyweight leaf nodes cannot store parent pointers (parent passed as extrinsic state) |
| State | State objects are often best implemented as flyweights |
| Strategy | Strategy objects are often best implemented as flyweights |

## MODERN CONTEXT

**TypeScript Example - React Virtual List with Flyweight Characters:**
```typescript
// Flyweight for shared character rendering
interface CharacterFlyweight {
  readonly code: string;
  render(context: RenderContext): JSX.Element;
}

interface RenderContext {
  x: number;
  y: number;
  font: string;
  color: string;
}

class CharacterFactory {
  private static flyweights = new Map<string, CharacterFlyweight>();

  static getCharacter(code: string): CharacterFlyweight {
    if (!this.flyweights.has(code)) {
      this.flyweights.set(code, {
        code,
        render: (ctx: RenderContext) => (
          <span style={{
            position: 'absolute',
            left: ctx.x,
            top: ctx.y,
            fontFamily: ctx.font,
            color: ctx.color
          }}>
            {code}
          </span>
        )
      });
    }
    return this.flyweights.get(code)!;
  }

  static get poolSize(): number {
    return this.flyweights.size;
  }
}
```

**Spring Boot Example - Cached Configuration Flyweights:**
```java
@Component
public class TenantConfigFlyweightFactory {
    private final Map<String, TenantConfig> configs = new ConcurrentHashMap<>();

    public TenantConfig getConfig(String configKey) {
        return configs.computeIfAbsent(configKey, this::loadConfig);
    }

    // Intrinsic: config values (shared)
    // Extrinsic: request-specific context passed to config.apply(request)
    private TenantConfig loadConfig(String key) {
        return configRepository.findByKey(key)
            .orElseThrow(() -> new ConfigNotFoundException(key));
    }
}
```

**Modern Applications:**
- String interning in JVM and JavaScript engines
- Icon/image caching in UI frameworks
- Game development (particle systems, tile maps, sprite sharing)
- Text rendering engines (glyph caching)
- Database connection pool objects
- React's reconciliation with stable element keys
- Immutable/value objects in functional programming

## SKILL ACTIONS

```
TRIGGER: "creating many similar objects" OR "high memory from object count" OR "fine-grained object representation"
ACTION: Identify intrinsic (shareable) vs extrinsic (context-dependent) state; create FlyweightFactory to manage shared instances; have clients pass extrinsic state to operations
COUNTER-INDICATOR: Object identity matters OR extrinsic state too complex OR few objects needed
```

```
TRIGGER: "document with character objects" OR "game with many sprites" OR "UI with repeated elements"
ACTION: Pool shared flyweight instances in factory; store only character code/sprite ID intrinsically; pass position, style, context extrinsically
COUNTER-INDICATOR: Each instance truly unique OR memory not constrained
```

```
TRIGGER: "combining with Composite pattern" OR "tree with shared leaves"
ACTION: Pass parent references as extrinsic state; use directed-acyclic graph instead of tree; flyweight leaves cannot store parent pointers
COUNTER-INDICATOR: Need bidirectional traversal with stored parent references
```

## CSO KEYWORDS

object sharing, intrinsic state, extrinsic state, fine-grained objects, memory optimization, flyweight pool, flyweight factory, shared objects, context-independent state, glyph, character objects, document editor, space efficiency, storage savings, object pooling, reference counting, immutable shared state
