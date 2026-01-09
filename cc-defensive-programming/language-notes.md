# Language Notes: Defensive Programming

## Exception Handling by Language (Table 8-1)

| Attribute | C++ | Java | Visual Basic |
|-----------|-----|------|--------------|
| Try-catch-finally | No | Yes | Yes |
| What can be thrown | Exception, pointer, reference, primitives | Exception objects | Exception objects |
| Uncaught exception effect | `std::unexpected()` then `abort()` | Terminates thread | Terminates program |
| Exceptions in interface required | No | Yes (checked) | No |

## C / C++

### Assertions
- Custom assertion macro with message support:
  ```cpp
  #define ASSERT( condition, message ) { \
      if ( !(condition) ) { \
          LogError( "Assertion failed: ", #condition, message ); \
          exit( EXIT_FAILURE ); \
      } \
  }
  ```

### Debug Code Control
- Preprocessor-based debug code:
  ```cpp
  #define DEBUG
  #if defined( DEBUG )
  #define DebugCode( code_fragment ) { code_fragment }
  #else
  #define DebugCode( code_fragment )
  #endif
  ```
- Debug stub pattern: Replace debug routines with empty stubs for production

### Exception Handling
- No `finally` block - use RAII for cleanup
- Can throw anything: Exception objects, pointers, references, primitives (string, int)
- **Recommendation:** Standardize on throwing only Exception-derived objects
- **Warning:** Destructors aren't called unless object is fully constructed - potential resource leaks if exceptions thrown in constructors

## Java

### Assertions
- Built-in `assert` keyword with optional message
- Can be enabled/disabled at runtime via `-ea` flag

### Exception Handling
- Full try-catch-finally support
- Can only throw Exception objects or derived classes
- **Checked exceptions:** Must declare in method signature (`throws`)
- **Caught exceptions:** Must be declared in interface
- Uncaught exceptions terminate only the current thread

## Visual Basic

### Assertions
- `Debug.Assert` for preconditions/postconditions:
  ```vb
  Debug.Assert ( -90 <= latitude And latitude <= 90 )
  Debug.Assert ( 0 <= longitude And longitude < 360 )
  ```

### Exception Handling
- Full try-catch-finally support
- Can only throw Exception objects
- No interface declaration requirement for exceptions
- **Pattern:** Centralized exception reporter for consistent error handling

## Cross-Language Recommendations

### Exception Strategy
- Document exceptions at abstraction boundaries
- Prefer returning status for expected failures
- Reserve exceptions for truly exceptional conditions
- Standardize project-wide exception hierarchy

### Assertion Strategy
- Use assertions for conditions that should never occur
- Use error handling for conditions that might occur
- Keep assertions enabled during development
- Consider keeping critical assertions in production
