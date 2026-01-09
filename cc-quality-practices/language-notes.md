# Language Notes: cc-quality-practices

Quality practices from Chapters 20-23 are largely language-agnostic, but tool setup varies. This document provides concrete configurations.

---

## Universal Principles

These apply regardless of language:

| Practice | Language-Agnostic? |
|----------|-------------------|
| Inspection effectiveness | Yes - same process everywhere |
| Test-first development | Yes - concept universal |
| Scientific debugging | Yes - hypothesis → experiment → verify |
| 5:1 dirty/clean test ratio | Yes - same target everywhere |
| Coverage monitoring | Yes - tools vary, principle same |

---

## Test Framework Quick Setup

### Python (pytest)

```bash
# Install
pip install pytest pytest-cov

# Run tests
pytest

# Run with coverage
pytest --cov=myproject --cov-report=html

# Run specific test
pytest tests/test_module.py::test_function -v
```

**Coverage report location:** `htmlcov/index.html`

### JavaScript/TypeScript (Jest)

```bash
# Install
npm install --save-dev jest @types/jest ts-jest

# package.json script
"scripts": {
  "test": "jest",
  "test:coverage": "jest --coverage"
}

# Run
npm test
npm run test:coverage
```

**Coverage report location:** `coverage/lcov-report/index.html`

### Java (JUnit 5 + JaCoCo)

```xml
<!-- pom.xml dependencies -->
<dependency>
    <groupId>org.junit.jupiter</groupId>
    <artifactId>junit-jupiter</artifactId>
    <version>5.10.0</version>
    <scope>test</scope>
</dependency>

<!-- JaCoCo plugin for coverage -->
<plugin>
    <groupId>org.jacoco</groupId>
    <artifactId>jacoco-maven-plugin</artifactId>
    <version>0.8.10</version>
</plugin>
```

```bash
# Run tests with coverage
mvn test jacoco:report
```

**Coverage report location:** `target/site/jacoco/index.html`

### Go

```bash
# Run tests
go test ./...

# Run with coverage
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out

# Run specific test
go test -run TestFunctionName -v
```

### Rust

```bash
# Install coverage tool
cargo install cargo-tarpaulin

# Run tests
cargo test

# Run with coverage
cargo tarpaulin --out Html
```

---

## Strict Compiler/Linter Settings

### C/C++

```bash
# GCC/Clang - maximum warnings, treat as errors
gcc -Wall -Wextra -Werror -pedantic -std=c17 file.c
g++ -Wall -Wextra -Werror -pedantic -std=c++20 file.cpp

# Static analysis
cppcheck --enable=all --error-exitcode=1 src/
clang-tidy src/*.cpp -- -std=c++20
```

**Common flags explained:**
| Flag | Purpose |
|------|---------|
| `-Wall` | Enable most warnings |
| `-Wextra` | Enable additional warnings |
| `-Werror` | Treat warnings as errors |
| `-pedantic` | Strict ISO compliance |

### Java

```bash
# javac - enable all lint warnings
javac -Xlint:all -Werror *.java

# SpotBugs (formerly FindBugs)
mvn spotbugs:check

# PMD
mvn pmd:check
```

### Python

```bash
# pylint - comprehensive linting
pylint --max-line-length=100 myproject/

# mypy - type checking
mypy --strict myproject/

# Combined in pyproject.toml
[tool.pylint.messages_control]
max-line-length = 100
disable = ["C0114", "C0115", "C0116"]  # Disable docstring requirements if needed

[tool.mypy]
strict = true
```

### JavaScript/TypeScript

```javascript
// .eslintrc.js - strict configuration
module.exports = {
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/strict',
  ],
  rules: {
    'no-unused-vars': 'error',
    'no-console': 'warn',
    '@typescript-eslint/explicit-function-return-type': 'error',
  },
};

// tsconfig.json - strict mode
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true
  }
}
```

### Go

```bash
# Built-in vet
go vet ./...

# golangci-lint (comprehensive)
golangci-lint run

# staticcheck
staticcheck ./...
```

### Rust

```bash
# Clippy - comprehensive linting
cargo clippy -- -D warnings

# In Cargo.toml for CI
[lints.clippy]
all = "deny"
pedantic = "warn"
```

---

## Language-Specific Bug Patterns

### C/C++ - Memory Bugs

| Symptom | Likely Cause | Detection |
|---------|--------------|-----------|
| Intermittent crashes | Dangling pointer | Valgrind, AddressSanitizer |
| Different results each run | Uninitialized variable | `-Wuninitialized`, Valgrind |
| Corruption after free | Use-after-free | AddressSanitizer |
| Slow memory growth | Memory leak | Valgrind `--leak-check=full` |

**AddressSanitizer setup:**
```bash
gcc -fsanitize=address -g program.c -o program
./program  # Will report memory errors
```

### Java/C# - Reference Bugs

| Symptom | Likely Cause | Detection |
|---------|--------------|-----------|
| NullPointerException | Null reference | IDE null analysis, `@Nullable` annotations |
| ConcurrentModificationException | Modifying while iterating | Code review, thread analysis |
| Resource leak | Unclosed streams | try-with-resources, SpotBugs |

### Python - Type Bugs

| Symptom | Likely Cause | Detection |
|---------|--------------|-----------|
| AttributeError | Wrong type passed | mypy type checking |
| TypeError at runtime | Dynamic type mismatch | Unit tests with diverse inputs |
| Silent wrong results | Truthy/falsy confusion | Explicit boolean checks |

**Type hints example:**
```python
def process_user(user_id: int, name: str) -> dict[str, Any]:
    ...
```

### JavaScript/TypeScript - Async Bugs

| Symptom | Likely Cause | Detection |
|---------|--------------|-----------|
| Undefined instead of value | Missing await | ESLint `require-await` |
| Unhandled promise rejection | Missing catch | Node.js `--unhandled-rejections=strict` |
| Race condition | Parallel mutation | Careful async flow analysis |

---

## Debugging Tools by Language

### C/C++

```bash
# GDB basics
gdb ./program
(gdb) break main
(gdb) run
(gdb) next          # Step over
(gdb) step          # Step into
(gdb) print var     # Print variable
(gdb) backtrace     # Stack trace

# LLDB (macOS/Clang)
lldb ./program
(lldb) breakpoint set --name main
(lldb) run
```

### Python

```python
# Built-in debugger
import pdb; pdb.set_trace()  # Insert breakpoint

# Or use breakpoint() in Python 3.7+
breakpoint()

# Commands
# n = next, s = step, c = continue, p var = print var, bt = backtrace
```

```bash
# Run with debugger
python -m pdb script.py
```

### JavaScript/Node.js

```bash
# Chrome DevTools debugger
node --inspect-brk script.js
# Then open chrome://inspect

# Built-in debugger
node inspect script.js
```

```javascript
// Insert breakpoint in code
debugger;
```

### Java

```bash
# Remote debugging
java -agentlib:jdwp=transport=dt_socket,server=y,suspend=y,address=5005 -jar app.jar
# Then attach IDE debugger to port 5005
```

---

## Coverage Thresholds

Recommended minimum coverage by context:

| Context | Statement | Branch | Rationale |
|---------|-----------|--------|-----------|
| New code | 80% | 70% | Baseline for quality |
| Critical paths | 95% | 90% | Auth, payments, data integrity |
| Legacy code | 60% | 50% | Pragmatic improvement target |
| Generated code | Exclude | Exclude | Don't test generated code |

**Remember:** Developers believe 95% but achieve 30-60%. Always use a coverage monitor.

---

## CI Integration Examples

### GitHub Actions (Python)

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install pytest pytest-cov
      - run: pytest --cov=myproject --cov-fail-under=80
```

### GitHub Actions (Node.js)

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npm test -- --coverage --coverageThreshold='{"global":{"branches":70,"functions":80,"lines":80}}'
```

---

## Quick Reference Card

| Task | Python | JavaScript | Java | Go | Rust |
|------|--------|------------|------|-----|------|
| Run tests | `pytest` | `npm test` | `mvn test` | `go test ./...` | `cargo test` |
| Coverage | `pytest --cov` | `jest --coverage` | `mvn jacoco:report` | `go test -cover` | `cargo tarpaulin` |
| Lint | `pylint` | `eslint` | `spotbugs` | `golangci-lint` | `cargo clippy` |
| Type check | `mypy` | `tsc` | (built-in) | (built-in) | (built-in) |
| Debug | `pdb` | `node --inspect` | IDE/jdb | `dlv` | `rust-gdb` |
