---
name: gof-interpreter
classification: Behavioral / Class
description: |
  When a particular kind of problem occurs often enough that instances can be expressed as sentences in a simple language, use Interpreter to define a grammar representation and an interpreter that uses it to interpret sentences in the language.
---

## INTENT

Given a language, define a represention for its grammar along with an interpreter that uses the representation to interpret sentences in the language.

## ALSO KNOWN AS

None

## PROBLEM INDICATORS

When you see:
- A recurring problem that can be expressed as sentences in a simple language
- The need to evaluate expressions or match patterns repeatedly
- Building custom algorithms for each variation of a problem instead of generalizing
- Domain-specific language requirements (DSL)
- Regular expressions, query languages, or rule-based systems
- Configuration or scripting needs that could benefit from a mini-language

## KEY INSIGHT

The Interpreter pattern uses a class to represent each grammar rule. Symbols on the right-hand side of the rule become instance variables of these classes. Every sentence defined by the grammar is represented by an abstract syntax tree made up of instances of these classes, and the Interpret operation on each class processes the input based on the current context.

## PARTICIPANTS

| Participant | Role | Example |
|------------|------|---------|
| AbstractExpression | Declares an abstract Interpret operation that is common to all nodes in the abstract syntax tree | RegularExpression, BooleanExp |
| TerminalExpression | Implements an Interpret operation associated with terminal symbols in the grammar; an instance is required for every terminal symbol in a sentence | LiteralExpression, VariableExp, Constant |
| NonterminalExpression | One such class is required for every rule R ::= R1 R2 ... Rn in the grammar; maintains instance variables of type AbstractExpression for each symbol R1 through Rn; implements Interpret for nonterminal symbols, typically calling itself recursively on subexpressions | AlternationExpression, SequenceExpression, RepetitionExpression, AndExp, OrExp, NotExp |
| Context | Contains information that's global to the interpreter | Input string and match state, variable bindings |
| Client | Builds (or is given) an abstract syntax tree representing a particular sentence in the language; invokes the Interpret operation | - |

## CONSEQUENCES

**Benefits:**

1. **It's easy to change and extend the grammar.** Because the pattern uses classes to represent grammar rules, you can use inheritance to change or extend the grammar. Existing expressions can be modified incrementally, and new expressions can be defined as variations on old ones.

2. **Implementing the grammar is easy, too.** Classes defining nodes in the abstract syntax tree have similar implementations. These classes are easy to write, and often their generation can be automated with a compiler or parser generator.

3. **Adding new ways to interpret expressions.** The Interpreter pattern makes it easier to evaluate an expression in a new way. For example, you can support pretty printing or type-checking an expression by defining a new operation on the expression classes. If you keep creating new ways of interpreting an expression, then consider using the Visitor pattern to avoid changing the grammar classes.

**Liabilities:**

4. **Complex grammars are hard to maintain.** The Interpreter pattern defines at least one class for every rule in the grammar (grammar rules defined using BNF may require multiple classes). Hence grammars containing many rules can be hard to manage and maintain. When the grammar is very complex, other techniques such as parser or compiler generators are more appropriate.

5. **Efficiency is not a critical concern.** The most efficient interpreters are usually not implemented by interpreting parse trees directly but by first translating them into another form. For example, regular expressions are often transformed into state machines. But even then, the translator can be implemented by the Interpreter pattern, so the pattern is still applicable.

## WHEN NOT TO USE

- When the grammar is complex with many rules (use parser generators instead)
- When efficiency is a critical concern (consider transforming to state machines or bytecode)
- When expressions don't naturally form a recursive tree structure
- When there's no recurring problem that warrants a mini-language
- When simple conditional logic or configuration would suffice
- When the language would rarely change (the extensibility benefit is wasted)

## RELATED PATTERNS

| Pattern | Relationship |
|---------|--------------|
| Composite | The abstract syntax tree is an instance of the Composite pattern |
| Flyweight | Shows how to share terminal symbols within the abstract syntax tree; terminal nodes generally don't store position information, so intrinsic/extrinsic state distinction applies |
| Iterator | The interpreter can use an Iterator to traverse the structure |
| Visitor | Can be used to maintain the behavior in each node in the abstract syntax tree in one class; useful when creating many ways of interpreting an expression |

## MODERN CONTEXT

### TypeScript Example
```typescript
// Context for expression evaluation
interface Context {
  variables: Map<string, number>;
}

// AbstractExpression
interface Expression {
  interpret(context: Context): number;
}

// TerminalExpression - Number literal
class NumberExpression implements Expression {
  constructor(private value: number) {}

  interpret(context: Context): number {
    return this.value;
  }
}

// TerminalExpression - Variable
class VariableExpression implements Expression {
  constructor(private name: string) {}

  interpret(context: Context): number {
    const value = context.variables.get(this.name);
    if (value === undefined) {
      throw new Error(`Undefined variable: ${this.name}`);
    }
    return value;
  }
}

// NonterminalExpression - Addition
class AddExpression implements Expression {
  constructor(private left: Expression, private right: Expression) {}

  interpret(context: Context): number {
    return this.left.interpret(context) + this.right.interpret(context);
  }
}

// NonterminalExpression - Multiplication
class MultiplyExpression implements Expression {
  constructor(private left: Expression, private right: Expression) {}

  interpret(context: Context): number {
    return this.left.interpret(context) * this.right.interpret(context);
  }
}

// Usage: (x + 5) * y
const expression = new MultiplyExpression(
  new AddExpression(
    new VariableExpression('x'),
    new NumberExpression(5)
  ),
  new VariableExpression('y')
);

const context: Context = {
  variables: new Map([['x', 3], ['y', 2]])
};

console.log(expression.interpret(context)); // (3 + 5) * 2 = 16
```

### React Example (Query Builder DSL)
```tsx
// Expression types for a filter DSL
type FilterExpression =
  | { type: 'equals'; field: string; value: any }
  | { type: 'and'; expressions: FilterExpression[] }
  | { type: 'or'; expressions: FilterExpression[] }
  | { type: 'not'; expression: FilterExpression };

// Interpreter function
function interpretFilter<T>(expr: FilterExpression, item: T): boolean {
  switch (expr.type) {
    case 'equals':
      return (item as any)[expr.field] === expr.value;
    case 'and':
      return expr.expressions.every(e => interpretFilter(e, item));
    case 'or':
      return expr.expressions.some(e => interpretFilter(e, item));
    case 'not':
      return !interpretFilter(expr.expression, item);
  }
}

// React hook for filtering
function useFilter<T>(items: T[], filter: FilterExpression): T[] {
  return useMemo(
    () => items.filter(item => interpretFilter(filter, item)),
    [items, filter]
  );
}

// Usage in component
const ProductList: React.FC = () => {
  const [filter, setFilter] = useState<FilterExpression>({
    type: 'and',
    expressions: [
      { type: 'equals', field: 'category', value: 'electronics' },
      { type: 'not', expression: { type: 'equals', field: 'outOfStock', value: true }}
    ]
  });

  const filteredProducts = useFilter(products, filter);
  // ...
};
```

### Spring Example (Specification Pattern as Interpreter)
```java
// AbstractExpression - Specification interface
public interface Specification<T> {
    boolean isSatisfiedBy(T candidate);

    default Specification<T> and(Specification<T> other) {
        return new AndSpecification<>(this, other);
    }

    default Specification<T> or(Specification<T> other) {
        return new OrSpecification<>(this, other);
    }

    default Specification<T> not() {
        return new NotSpecification<>(this);
    }
}

// NonterminalExpression - And
public class AndSpecification<T> implements Specification<T> {
    private final Specification<T> left;
    private final Specification<T> right;

    public AndSpecification(Specification<T> left, Specification<T> right) {
        this.left = left;
        this.right = right;
    }

    @Override
    public boolean isSatisfiedBy(T candidate) {
        return left.isSatisfiedBy(candidate) && right.isSatisfiedBy(candidate);
    }
}

// TerminalExpression - Concrete specifications
public class PriceRangeSpec implements Specification<Product> {
    private final BigDecimal min, max;

    public PriceRangeSpec(BigDecimal min, BigDecimal max) {
        this.min = min;
        this.max = max;
    }

    @Override
    public boolean isSatisfiedBy(Product product) {
        return product.getPrice().compareTo(min) >= 0
            && product.getPrice().compareTo(max) <= 0;
    }
}

// Usage with Spring Data
@Service
public class ProductService {
    public List<Product> findProducts(Specification<Product> spec) {
        return productRepository.findAll().stream()
            .filter(spec::isSatisfiedBy)
            .collect(Collectors.toList());
    }
}

// Client builds the expression tree
Specification<Product> spec = new PriceRangeSpec(10, 100)
    .and(new CategorySpec("electronics"))
    .and(new InStockSpec().not());
```

### Modern Use Cases
- **SQL-like query builders**: ORMs like TypeORM, Prisma use interpreter-like patterns for query construction
- **Validation rules engines**: Express complex validation as composable rule trees
- **Business rules engines**: Drools, Easy Rules interpret rule definitions
- **Expression languages**: Spring Expression Language (SpEL), JEXL
- **Template engines**: Handlebars, Mustache parse and interpret templates
- **Math expression evaluators**: Scientific calculators, spreadsheet formulas
- **Regular expression engines**: Pattern matching implementations
- **Configuration DSLs**: Terraform, Kubernetes YAML interpreted as infrastructure

## SKILL ACTIONS

```
TRIGGER: "recurring problem" AND ("express as sentences" OR "simple language" OR "grammar" OR "DSL")
ACTION: Apply Interpreter pattern with AbstractExpression, Terminal/Nonterminal classes, and recursive Interpret operation
COUNTER-INDICATOR: Grammar is complex (use parser generators); efficiency is critical (compile to bytecode/state machine)
```

```
TRIGGER: "evaluate expressions" AND ("abstract syntax tree" OR "parse tree" OR "expression tree")
ACTION: Map each grammar rule to a class; terminal symbols become leaves, nonterminal rules become composites with Interpret calling subexpressions recursively
COUNTER-INDICATOR: Expressions don't form recursive structure; problem doesn't recur enough to justify language
```

```
TRIGGER: "multiple interpretations" AND ("same grammar" OR "same AST")
ACTION: Consider using Visitor pattern to separate interpretation logic from grammar classes
COUNTER-INDICATOR: Only one interpretation needed; grammar classes change more often than interpretations
```

## CSO KEYWORDS

interpreter, grammar, abstract syntax tree, AST, parse tree, expression evaluation, domain-specific language, DSL, terminal expression, nonterminal expression, recursive descent, BNF, language processing, regular expression, pattern matching, rule engine, specification pattern, expression tree, context, evaluate, boolean expression, arithmetic expression, query builder, validation rules, business rules, template engine
