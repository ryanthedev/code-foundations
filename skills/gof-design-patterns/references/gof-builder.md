---
name: gof-builder
classification: Creational / Object
description: "Use when constructing complex objects step-by-step with varying representations; Symptoms: telescoping constructors, multiple configuration options, need to create different representations from same construction process"
---

## INTENT

Separate the construction of a complex object from its representation so that the same construction process can create different representations.

## ALSO KNOWN AS

(No alternative names listed in GoF)

## PROBLEM INDICATORS

Use the Builder pattern when:

- The algorithm for creating a complex object should be independent of the parts that make up the object and how they're assembled
- The construction process must allow different representations for the object that's constructed

## KEY INSIGHT

The Builder pattern separates the "how" (construction algorithm) from the "what" (representation), allowing a single Director to orchestrate construction while different ConcreteBuilders produce entirely different products using the same step-by-step process.

## PARTICIPANTS

| Role | Responsibility |
|------|----------------|
| **Builder** (TextConverter) | Specifies an abstract interface for creating parts of a Product object |
| **ConcreteBuilder** (ASCIIConverter, TeXConverter, TextWidgetConverter) | Constructs and assembles parts of the product by implementing the Builder interface; defines and keeps track of the representation it creates; provides an interface for retrieving the product |
| **Director** (RTFReader) | Constructs an object using the Builder interface |
| **Product** (ASCIIText, TeXText, TextWidget) | Represents the complex object under construction; includes classes that define the constituent parts and interfaces for assembling them into the final result |

## CONSEQUENCES

### Benefits

1. **It lets you vary a product's internal representation.** The Builder object provides the director with an abstract interface for constructing the product. The interface lets the builder hide the representation and internal structure of the product. It also hides how the product gets assembled. Because the product is constructed through an abstract interface, all you have to do to change the product's internal representation is define a new kind of builder.

2. **It isolates code for construction and representation.** The Builder pattern improves modularity by encapsulating the way a complex object is constructed and represented. Clients needn't know anything about the classes that define the product's internal structure; such classes don't appear in Builder's interface. Each ConcreteBuilder contains all the code to create and assemble a particular kind of product. The code is written once; then different Directors can reuse it to build Product variants from the same set of parts.

3. **It gives you finer control over the construction process.** Unlike creational patterns that construct products in one shot, the Builder pattern constructs the product step by step under the director's control. Only when the product is finished does the director retrieve it from the builder. Hence the Builder interface reflects the process of constructing the product more than other creational patterns. This gives you finer control over the construction process and consequently the internal structure of the resulting product.

### Liabilities

1. **Requires creating separate ConcreteBuilder for each product type.** Each different product representation requires its own ConcreteBuilder implementation.

2. **Products may not share a common interface.** The products produced by concrete builders often differ so greatly in their representation that there is little to gain from giving different products a common parent class.

## WHEN NOT TO USE

- When the object being created is simple and can be constructed in a single step
- When all products share the same representation (no variation needed)
- When construction order is not important or there is no multi-step construction algorithm
- When you need to create families of related objects (use Abstract Factory instead)
- When the product is returned immediately rather than built incrementally (use Abstract Factory instead)

## RELATED PATTERNS

| Pattern | Relationship |
|---------|-------------|
| **Abstract Factory** | Similar in that both may construct complex objects. The primary difference is that Builder focuses on constructing a complex object step by step, while Abstract Factory's emphasis is on families of product objects. Builder returns the product as a final step; Abstract Factory returns the product immediately. |
| **Composite** | What the builder often builds. Complex recursive structures are commonly constructed using Builder. |

## MODERN CONTEXT

### TypeScript Example - Form Builder

```typescript
interface FormField {
  name: string;
  type: string;
  validation?: string[];
}

interface Form {
  fields: FormField[];
  submitUrl: string;
  method: 'GET' | 'POST';
}

// Builder interface
interface FormBuilder {
  addTextField(name: string): FormBuilder;
  addEmailField(name: string): FormBuilder;
  addPasswordField(name: string): FormBuilder;
  setSubmitUrl(url: string): FormBuilder;
  setMethod(method: 'GET' | 'POST'): FormBuilder;
  build(): Form;
}

// ConcreteBuilder
class HtmlFormBuilder implements FormBuilder {
  private form: Form = { fields: [], submitUrl: '', method: 'POST' };

  addTextField(name: string): FormBuilder {
    this.form.fields.push({ name, type: 'text' });
    return this;
  }

  addEmailField(name: string): FormBuilder {
    this.form.fields.push({ name, type: 'email', validation: ['email'] });
    return this;
  }

  addPasswordField(name: string): FormBuilder {
    this.form.fields.push({ name, type: 'password', validation: ['minLength:8'] });
    return this;
  }

  setSubmitUrl(url: string): FormBuilder {
    this.form.submitUrl = url;
    return this;
  }

  setMethod(method: 'GET' | 'POST'): FormBuilder {
    this.form.method = method;
    return this;
  }

  build(): Form {
    const result = this.form;
    this.form = { fields: [], submitUrl: '', method: 'POST' };
    return result;
  }
}

// Usage with fluent interface (modern variation)
const form = new HtmlFormBuilder()
  .addTextField('username')
  .addEmailField('email')
  .addPasswordField('password')
  .setSubmitUrl('/api/register')
  .setMethod('POST')
  .build();
```

### React Example - Component Builder

```tsx
interface DialogConfig {
  title: string;
  content: React.ReactNode;
  actions: React.ReactNode[];
  size: 'sm' | 'md' | 'lg';
}

class DialogBuilder {
  private config: Partial<DialogConfig> = {};

  setTitle(title: string): DialogBuilder {
    this.config.title = title;
    return this;
  }

  setContent(content: React.ReactNode): DialogBuilder {
    this.config.content = content;
    return this;
  }

  addAction(action: React.ReactNode): DialogBuilder {
    this.config.actions = [...(this.config.actions || []), action];
    return this;
  }

  setSize(size: 'sm' | 'md' | 'lg'): DialogBuilder {
    this.config.size = size;
    return this;
  }

  build(): React.FC {
    const { title, content, actions, size } = this.config as DialogConfig;
    return () => (
      <Dialog size={size}>
        <DialogTitle>{title}</DialogTitle>
        <DialogContent>{content}</DialogContent>
        <DialogActions>{actions}</DialogActions>
      </Dialog>
    );
  }
}

// Director function
function createConfirmationDialog(message: string, onConfirm: () => void) {
  return new DialogBuilder()
    .setTitle('Confirm Action')
    .setContent(<p>{message}</p>)
    .addAction(<Button onClick={onConfirm}>Confirm</Button>)
    .addAction(<Button variant="secondary">Cancel</Button>)
    .setSize('sm')
    .build();
}
```

### Spring Boot Example - Request Builder

```java
@Component
public class HttpRequestBuilder {
    private HttpMethod method;
    private String url;
    private HttpHeaders headers;
    private Object body;
    private Map<String, String> queryParams;

    public HttpRequestBuilder() {
        this.headers = new HttpHeaders();
        this.queryParams = new HashMap<>();
    }

    public HttpRequestBuilder get(String url) {
        this.method = HttpMethod.GET;
        this.url = url;
        return this;
    }

    public HttpRequestBuilder post(String url) {
        this.method = HttpMethod.POST;
        this.url = url;
        return this;
    }

    public HttpRequestBuilder withHeader(String name, String value) {
        this.headers.add(name, value);
        return this;
    }

    public HttpRequestBuilder withBearerToken(String token) {
        this.headers.setBearerAuth(token);
        return this;
    }

    public HttpRequestBuilder withBody(Object body) {
        this.body = body;
        return this;
    }

    public HttpRequestBuilder withQueryParam(String name, String value) {
        this.queryParams.put(name, value);
        return this;
    }

    public <T> ResponseEntity<T> execute(Class<T> responseType, RestTemplate restTemplate) {
        UriComponentsBuilder uriBuilder = UriComponentsBuilder.fromHttpUrl(url);
        queryParams.forEach(uriBuilder::queryParam);

        HttpEntity<?> entity = new HttpEntity<>(body, headers);
        return restTemplate.exchange(
            uriBuilder.toUriString(),
            method,
            entity,
            responseType
        );
    }
}

// Usage
@Service
public class ApiService {
    private final RestTemplate restTemplate;

    public UserDto getUser(String userId, String token) {
        return new HttpRequestBuilder()
            .get("https://api.example.com/users/" + userId)
            .withBearerToken(token)
            .withHeader("Accept", "application/json")
            .execute(UserDto.class, restTemplate)
            .getBody();
    }
}
```

## SKILL ACTIONS

### TRIGGER
- Constructors with many parameters (telescoping constructor anti-pattern)
- Need to create different representations of a complex object
- Object construction involves multiple steps that should be reusable
- Parsing/conversion scenarios where input is processed step-by-step to produce different outputs
- Configuration objects with many optional settings

### ACTION
1. Identify the construction algorithm (the steps) and extract into Director
2. Define Builder interface with methods for each construction step
3. Create ConcreteBuilder classes for each product representation
4. Builder methods should return `this` for fluent interface (modern convention)
5. Product retrieval method (e.g., `build()`, `getResult()`) returns and resets builder state
6. Consider making Director optional - clients can drive builders directly

### COUNTER-INDICATOR
- Simple objects that can be constructed in one step
- No variation in product representation needed
- Performance-critical code where builder overhead matters
- When Abstract Factory is more appropriate (families of related objects)
- When immutable objects with all-args constructor suffice

