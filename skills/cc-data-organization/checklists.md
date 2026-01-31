# Checklists: cc-data-organization

Source: Code Complete 2nd Edition, Chapters 10-13

---

## Initializing Variables (p.257)

- [ ] IV-1: "Does each routine check input parameters for validity?" → Red flag: Trusting external data without validation
- [ ] IV-2: "Does the code declare variables close to where they're first used?" (Good: Within 5 lines, Bad: 50+ lines apart)
- [ ] IV-3: "Does the code initialize variables as they're declared, if possible?"
- [ ] IV-4: "Are counters and accumulators initialized properly and reinitialized each time they are used?" → Red flag: Stale values from previous iteration
- [ ] IV-5: "Are variables reinitialized properly in code that's executed repeatedly?"
- [ ] IV-6: "Does the code compile with no warnings from the compiler?"
- [ ] IV-7: "If your language uses implicit declarations, have you compensated for the problems they cause?"

---

## Scope and Purpose (p.258-259)

- [ ] SP-1: "Do all variables have the smallest scope possible?" (Good: Function-local, Bad: Global)
- [ ] SP-2: "Are references to variables as close together as possible?" → Cognitive load indicator
- [ ] SP-3: "Are all the declared variables being used?"
- [ ] SP-4: "Does each variable have one and only one purpose?" → Red flag: Variable reuse for unrelated purposes
- [ ] SP-5: "Is each variable's meaning explicit, with no hidden meanings?" → Red flag: Dual-purpose flags
- [ ] SP-6: "Are you striking a conscious balance between flexibility and complexity in binding times?"

---

## Numbers in General (p.316)

- [ ] NG-1: "Does the code avoid magic numbers?" → Red flag: Literals like 86400, 365 without named constants
- [ ] NG-2: "Does the code anticipate divide-by-zero errors?"
- [ ] NG-3: "Are type conversions obvious?"
- [ ] NG-4: "If variables with two different types are used in the same expression, will the expression be evaluated as you intend it to be?"
- [ ] NG-5: "Does the code avoid mixed-type comparisons?" → Red flag: Comparing int to float
- [ ] NG-6: "Does the program compile with no warnings?"

---

## Integers (p.316)

- [ ] IN-1: "Do expressions that use integer division work the way they're meant to?" (Good: Explicit truncation, Bad: Accidental loss)
- [ ] IN-2: "Do integer expressions avoid integer-overflow problems?" → Red flag: Unbounded addition/multiplication

---

## Floating-Point Numbers (p.317)

- [ ] FP-1: "Does the code avoid additions and subtractions on numbers with greatly different magnitudes?" → Precision loss
- [ ] FP-2: "Does the code systematically prevent rounding errors?"
- [ ] FP-3: "Does the code avoid comparing floating-point numbers for equality?" → Red flag: `if (x == 0.1)`

---

## Characters and Strings (p.317)

- [ ] CS-1: "Does the code avoid magic characters and strings?" → Red flag: Hard-coded paths, error codes
- [ ] CS-2: "Are references to strings free of off-by-one errors?"
- [ ] CS-3: "Does C code treat string pointers and character arrays differently?"
- [ ] CS-4: "Does C code follow the convention of declaring strings to be length CONSTANT+1?"
- [ ] CS-5: "Does C code use arrays of characters rather than pointers, when appropriate?"
- [ ] CS-6: "Does C code initialize strings to NULLs to avoid endless strings?" → Red flag: Unterminated buffers
- [ ] CS-7: "Does C code use strncpy() rather than strcpy()? And strncat() and strncmp()?" → Security critical

---

## Boolean Variables (p.317)

- [ ] BV-1: "Does the program use additional boolean variables to document conditional tests?" (Good: `isValid`, Bad: `if (x > 0 && y < 10)`)
- [ ] BV-2: "Does the program use additional boolean variables to simplify conditional tests?"

---

## Enumerated Types (p.318)

- [ ] ET-1: "Does the program use enumerated types instead of named constants for their improved readability, reliability, and modifiability?"
- [ ] ET-2: "Does the program use enumerated types instead of boolean variables when a variable's use cannot be completely captured with true and false?"
- [ ] ET-3: "Do tests using enumerated types test for invalid values?" → Defensive programming
- [ ] ET-4: "Is the first entry in an enumerated type reserved for 'invalid'?"

---

## Named Constants (p.318)

- [ ] NC-1: "Does the program use named constants for data declarations and loop limits rather than magic numbers?"
- [ ] NC-2: "Have named constants been used consistently--not used as named constants in some places and as literals in others?" → Red flag: Inconsistent constant use

---

## Arrays (p.318)

- [ ] AR-1: "Are all array indexes within the bounds of the array?" → Red flag: Buffer overflow vulnerability
- [ ] AR-2: "Are array references free of off-by-one errors?"
- [ ] AR-3: "Are all subscripts on multidimensional arrays in the correct order?"
- [ ] AR-4: "In nested loops, is the correct variable used as the array subscript, avoiding loop-index cross-talk?" → Red flag: Using `i` when you need `j`

---

## Creating Types (p.318)

- [ ] CT-1: "Does the program use a different type for each kind of data that might change?"
- [ ] CT-2: "Are type names oriented toward the real-world entities the types represent rather than toward programming-language types?" (Good: `Customer`, Bad: `StringData`)
- [ ] CT-3: "Are the type names descriptive enough to help document data declarations?"
- [ ] CT-4: "Have you avoided redefining predefined types?"
- [ ] CT-5: "Have you considered creating a new class rather than simply redefining a type?"

---

## Variable Names (p.288-289)

- [ ] VN-1: "Does the name fully and accurately describe what the variable represents?" (Good: `customerCount`, Bad: `x`, `temp`)
- [ ] VN-2: "Does the name refer to the real-world problem rather than the programming-language solution?"
- [ ] VN-3: "Is the name long enough to be meaningful?" (Good: 8-20 chars for important vars, Bad: Single letter except loop vars)
- [ ] VN-4: "Are computed-value qualifiers in the conventional position (at end)?" (Good: `revenueTotal`, Bad: `totalRevenue`)
- [ ] VN-5: "Does the name use Count or Index instead of ambiguous Num?" → Red flag: `customerNum` (ID? Count? Index?)

---

## Structures (p.343)

- [ ] ST-1: "Have you used structures instead of naked variables to organize and manipulate groups of related data?" → Red flag: Parallel arrays
- [ ] ST-2: "Have you considered creating a class as an alternative to using a structure?"

---

## Global Data (p.344)

- [ ] GD-1: "Are all variables local or class scope unless they absolutely need to be global?" → Red flag: Global by default
- [ ] GD-2: "Do variable naming conventions differentiate among local, class, and global data?"
- [ ] GD-3: "Are all global variables documented?"
- [ ] GD-4: "Is the code free of pseudoglobal data--mammoth objects containing a mishmash of data that's passed to every routine?" → Red flag: God objects
- [ ] GD-5: "Are access routines used instead of global data?"
- [ ] GD-6: "Are access routines and data organized into classes?"
- [ ] GD-7: "Do access routines provide a level of abstraction beyond the underlying data type implementations?"
- [ ] GD-8: "Are all related access routines at the same level of abstraction?"

---

## Pointers (p.344-345)

- [ ] PT-1: "Are pointer operations isolated in routines?"
- [ ] PT-2: "Are pointer references valid, or could the pointer be dangling?" → Red flag: Use-after-free
- [ ] PT-3: "Does the code check pointers for validity before using them?"
- [ ] PT-4: "Is the variable that the pointer references checked for validity before it's used?"
- [ ] PT-5: "Are pointers set to null after they're freed?" → Defensive practice
- [ ] PT-6: "Does the code use all the pointer variables needed for the sake of readability?"
- [ ] PT-7: "Are pointers in linked lists freed in the right order?" → Red flag: Memory leaks
- [ ] PT-8: "Does the program allocate a reserve parachute of memory so that it can shut down gracefully if it runs out of memory?"
- [ ] PT-9: "Are pointers used only as a last resort, when no other method is available?"

---

## Modern Data Types (extends Code Complete)

*These sections cover data types not addressed in Code Complete's C-era focus.*

---

### Concurrent Access

- [ ] CA-1: "Is shared mutable state explicitly identified and documented?" → Red flag: Hidden shared state
- [ ] CA-2: "Are shared variables accessed only through synchronization-aware access routines?"
- [ ] CA-3: "Has immutability been considered as an alternative to synchronization?" (Good: Immutable by default, Bad: Locks everywhere)
- [ ] CA-4: "Are thread-safety guarantees documented on types that may be accessed concurrently?"
- [ ] CA-5: "Does the code avoid data races (simultaneous read/write or write/write without synchronization)?" → Red flag: Race conditions
- [ ] CA-6: "Are atomic operations used for simple shared counters/flags?"

---

### Nullable/Optional Types

- [ ] NO-1: "Are types non-nullable by default, with explicit opt-in for nullability?"
- [ ] NO-2: "Does the code handle all cases when unwrapping Option/Maybe/nullable types?" → Red flag: Unchecked null access
- [ ] NO-3: "Is null avoided as a sentinel for 'not found' in favor of Option types or result types?"
- [ ] NO-4: "Are null semantics documented when null is a valid state?"
- [ ] NO-5: "Does the code use language features for null safety (e.g., `?.`, `??`, exhaustive matching)?"

---

### Temporal Data

- [ ] TD-1: "Are timestamps stored and transmitted in UTC?" → Red flag: Local time zones in storage
- [ ] TD-2: "Are timezone-aware types used for user-facing dates/times?"
- [ ] TD-3: "Is time precision explicit in type or variable name (ms, seconds, nanos)?" (Good: `timeoutMs`, Bad: `timeout`)
- [ ] TD-4: "Are time magic numbers eliminated (`86400` → `SECONDS_PER_DAY`)?"
- [ ] TD-5: "Does date arithmetic use library functions rather than manual calculations?" → Red flag: Rolling your own date math
- [ ] TD-6: "Are time zones handled correctly for daylight saving transitions?"

---

### Security-Sensitive Data

- [ ] SS-1: "Are secrets/tokens/keys cleared from memory after use?" → Red flag: Passwords in heap
- [ ] SS-2: "Is sensitive data excluded from all logging and error messages?" → Red flag: API keys in logs
- [ ] SS-3: "Do sensitive data types have limited scope (shortest possible lifetime)?"
- [ ] SS-4: "Are dedicated wrapper types used for sensitive data (preventing accidental exposure)?"
- [ ] SS-5: "Is sensitive data excluded from serialization unless explicitly required?" → Red flag: Secrets in JSON

---

## Red Flags

- [ ] RF-1: "Uninitialized variables?" - Reading before assignment → Initialize at declaration or enforce initialization
- [ ] RF-2: "Magic numbers everywhere?" - Hard-coded constants scattered → Extract to named constants
- [ ] RF-3: "Global variables proliferating?" - Everything accessible everywhere → Minimize scope, use access routines
- [ ] RF-4: "Null pointer dereferences?" - Using pointers without validation → Check validity or use non-nullable types
- [ ] RF-5: "Mixed types in expressions?" - `int + float` or `string == number` → Explicit conversions only
- [ ] RF-6: "Variables with dual purposes?" - Same var reused for unrelated data → One variable, one purpose
- [ ] RF-7: "Secrets in plaintext?" - API keys, passwords visible in memory/logs → Wrapper types, clear after use
- [ ] RF-8: "God objects passed everywhere?" - Massive context objects to all routines → Break into cohesive structures
- [ ] RF-9: "Buffer overflows possible?" - Array access without bounds checking → Validate indices
- [ ] RF-10: "Race conditions on shared data?" - Concurrent access without synchronization → Use locks or immutability

---

Total items: 102 (69 original + 23 modern + 10 red flags)
