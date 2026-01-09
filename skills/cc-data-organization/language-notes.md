# Language Notes: cc-data-organization

## C / C++

- **String declarations**: Declare as `CONSTANT+1` for null terminator; use `strncpy()` not `strcpy()`
- **String initialization**: Initialize to NULL to avoid endless strings; use `calloc()` over `malloc()`
- **Pointer vs array naming**: Use `ps` prefix for pointer-to-string, `ach` for char array
- **Enum values**: Explicitly define First/Last for iteration; reserve 0 for invalid
- **Type casting**: Avoid - turns off compiler type checking; many casts indicate architectural problems
- **sizeof()**: Always use for memory allocation - portable, no performance penalty, self-maintaining
- **Pointer initialization**: Declare and initialize at same time; set to NULL after free
- **Smart pointers**: Use auto_ptr (C++98) or unique_ptr/shared_ptr (C++11+) to avoid memory leaks

## C++ Specific

- **References vs pointers**: Use reference when null is invalid; pointer when null is valid state
- **Parameter passing**: `const LARGE_OBJECT&` for read-only; `LARGE_OBJECT*` for modifiable
- **Global initialization order**: Undefined across translation units; use explicit initialization

## Java / C#

- **Enums**: Use built-in enum support directly; can add methods to enums
- **Constants**: Use `static final` (Java) or `const` (C#) for named constants
- **Decimal types**: Use `BigDecimal` (Java) or `decimal` (C#) for currency, not float/double
- **No pointers**: These languages eliminated pointer type due to error-proneness

## General OOP

- **Custom types**: Create wrapper classes when primitives represent domain concepts
- **Type safety**: Prefer strong typing to catch errors at compile time
- **Access routines**: Hide data behind methods even for simple values

## Dynamic Languages (Python, JavaScript, etc.)

- **Named constants**: Use UPPER_CASE convention since language may lack const
- **Type hints**: Use type annotations where available for documentation
- **Enum emulation**: Use frozen objects or dedicated enum libraries
