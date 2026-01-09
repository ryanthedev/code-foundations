# Checklists: cc-data-organization

Source: Code Complete 2nd Edition, Chapters 10-13

## Initializing Variables (p.257)

- [ ] "Does each routine check input parameters for validity?"
- [ ] "Does the code declare variables close to where they're first used?"
- [ ] "Does the code initialize variables as they're declared, if possible?"
- [ ] "Are counters and accumulators initialized properly and reinitialized each time they are used?"
- [ ] "Are variables reinitialized properly in code that's executed repeatedly?"
- [ ] "Does the code compile with no warnings from the compiler?"
- [ ] "If your language uses implicit declarations, have you compensated for the problems they cause?"

## Scope and Purpose (p.258-259)

- [ ] "Do all variables have the smallest scope possible?"
- [ ] "Are references to variables as close together as possible?"
- [ ] "Are all the declared variables being used?"
- [ ] "Does each variable have one and only one purpose?"
- [ ] "Is each variable's meaning explicit, with no hidden meanings?"
- [ ] "Are you striking a conscious balance between flexibility and complexity in binding times?"

## Numbers in General (p.316)

- [ ] "Does the code avoid magic numbers?"
- [ ] "Does the code anticipate divide-by-zero errors?"
- [ ] "Are type conversions obvious?"
- [ ] "If variables with two different types are used in the same expression, will the expression be evaluated as you intend it to be?"
- [ ] "Does the code avoid mixed-type comparisons?"
- [ ] "Does the program compile with no warnings?"

## Integers (p.316)

- [ ] "Do expressions that use integer division work the way they're meant to?"
- [ ] "Do integer expressions avoid integer-overflow problems?"

## Floating-Point Numbers (p.317)

- [ ] "Does the code avoid additions and subtractions on numbers with greatly different magnitudes?"
- [ ] "Does the code systematically prevent rounding errors?"
- [ ] "Does the code avoid comparing floating-point numbers for equality?"

## Characters and Strings (p.317)

- [ ] "Does the code avoid magic characters and strings?"
- [ ] "Are references to strings free of off-by-one errors?"
- [ ] "Does C code treat string pointers and character arrays differently?"
- [ ] "Does C code follow the convention of declaring strings to be length CONSTANT+1?"
- [ ] "Does C code use arrays of characters rather than pointers, when appropriate?"
- [ ] "Does C code initialize strings to NULLs to avoid endless strings?"
- [ ] "Does C code use strncpy() rather than strcpy()? And strncat() and strncmp()?"

## Boolean Variables (p.317)

- [ ] "Does the program use additional boolean variables to document conditional tests?"
- [ ] "Does the program use additional boolean variables to simplify conditional tests?"

## Enumerated Types (p.318)

- [ ] "Does the program use enumerated types instead of named constants for their improved readability, reliability, and modifiability?"
- [ ] "Does the program use enumerated types instead of boolean variables when a variable's use cannot be completely captured with true and false?"
- [ ] "Do tests using enumerated types test for invalid values?"
- [ ] "Is the first entry in an enumerated type reserved for 'invalid'?"

## Named Constants (p.318)

- [ ] "Does the program use named constants for data declarations and loop limits rather than magic numbers?"
- [ ] "Have named constants been used consistently--not used as named constants in some places and as literals in others?"

## Arrays (p.318)

- [ ] "Are all array indexes within the bounds of the array?"
- [ ] "Are array references free of off-by-one errors?"
- [ ] "Are all subscripts on multidimensional arrays in the correct order?"
- [ ] "In nested loops, is the correct variable used as the array subscript, avoiding loop-index cross-talk?"

## Creating Types (p.318)

- [ ] "Does the program use a different type for each kind of data that might change?"
- [ ] "Are type names oriented toward the real-world entities the types represent rather than toward programming-language types?"
- [ ] "Are the type names descriptive enough to help document data declarations?"
- [ ] "Have you avoided redefining predefined types?"
- [ ] "Have you considered creating a new class rather than simply redefining a type?"

## Variable Names (p.288-289)

- [ ] "Does the name fully and accurately describe what the variable represents?"
- [ ] "Does the name refer to the real-world problem rather than the programming-language solution?"
- [ ] "Is the name long enough to be meaningful?"
- [ ] "Are computed-value qualifiers in the conventional position (at end)?"
- [ ] "Does the name use Count or Index instead of ambiguous Num?"

## Structures (p.343)

- [ ] "Have you used structures instead of naked variables to organize and manipulate groups of related data?"
- [ ] "Have you considered creating a class as an alternative to using a structure?"

## Global Data (p.344)

- [ ] "Are all variables local or class scope unless they absolutely need to be global?"
- [ ] "Do variable naming conventions differentiate among local, class, and global data?"
- [ ] "Are all global variables documented?"
- [ ] "Is the code free of pseudoglobal data--mammoth objects containing a mishmash of data that's passed to every routine?"
- [ ] "Are access routines used instead of global data?"
- [ ] "Are access routines and data organized into classes?"
- [ ] "Do access routines provide a level of abstraction beyond the underlying data type implementations?"
- [ ] "Are all related access routines at the same level of abstraction?"

## Pointers (p.344-345)

- [ ] "Are pointer operations isolated in routines?"
- [ ] "Are pointer references valid, or could the pointer be dangling?"
- [ ] "Does the code check pointers for validity before using them?"
- [ ] "Is the variable that the pointer references checked for validity before it's used?"
- [ ] "Are pointers set to null after they're freed?"
- [ ] "Does the code use all the pointer variables needed for the sake of readability?"
- [ ] "Are pointers in linked lists freed in the right order?"
- [ ] "Does the program allocate a reserve parachute of memory so that it can shut down gracefully if it runs out of memory?"
- [ ] "Are pointers used only as a last resort, when no other method is available?"

---

## Modern Data Types (extends Code Complete)

*These sections cover data types not addressed in Code Complete's C-era focus.*

### Concurrent Access

- [ ] "Is shared mutable state explicitly identified and documented?"
- [ ] "Are shared variables accessed only through synchronization-aware access routines?"
- [ ] "Has immutability been considered as an alternative to synchronization?"
- [ ] "Are thread-safety guarantees documented on types that may be accessed concurrently?"
- [ ] "Does the code avoid data races (simultaneous read/write or write/write without synchronization)?"
- [ ] "Are atomic operations used for simple shared counters/flags?"

### Nullable/Optional Types

- [ ] "Are types non-nullable by default, with explicit opt-in for nullability?"
- [ ] "Does the code handle all cases when unwrapping Option/Maybe/nullable types?"
- [ ] "Is null avoided as a sentinel for 'not found' in favor of Option types or result types?"
- [ ] "Are null semantics documented when null is a valid state?"
- [ ] "Does the code use language features for null safety (e.g., `?.`, `??`, exhaustive matching)?"

### Temporal Data

- [ ] "Are timestamps stored and transmitted in UTC?"
- [ ] "Are timezone-aware types used for user-facing dates/times?"
- [ ] "Is time precision explicit in type or variable name (ms, seconds, nanos)?"
- [ ] "Are time magic numbers eliminated (`86400` → `SECONDS_PER_DAY`)?"
- [ ] "Does date arithmetic use library functions rather than manual calculations?"
- [ ] "Are time zones handled correctly for daylight saving transitions?"

### Security-Sensitive Data

- [ ] "Are secrets/tokens/keys cleared from memory after use?"
- [ ] "Is sensitive data excluded from all logging and error messages?"
- [ ] "Do sensitive data types have limited scope (shortest possible lifetime)?"
- [ ] "Are dedicated wrapper types used for sensitive data (preventing accidental exposure)?"
- [ ] "Is sensitive data excluded from serialization unless explicitly required?"

---
Total items: 92 (69 original + 23 modern)
