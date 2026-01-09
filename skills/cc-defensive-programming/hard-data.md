# Evidence: Defensive Programming

Source: Code Complete 2nd Edition, Chapter 8

## Key Points (Author-Marked)

| # | Claim | Page | Qualifier |
|---|-------|------|-----------|
| 1 | If a routine is passed bad data, it won't be hurt, even if the bad data is another routine's fault | p.187 | KEY POINT |
| 2 | "Garbage in, garbage out" is the mark of a sloppy, nonsecure program | p.188 | KEY POINT |
| 3 | Assertions are especially useful in large, complicated programs and in high-reliability programs | p.189 | KEY POINT |
| 4 | Error handling affects correctness, robustness, and other nonfunctional attributes - it's an architectural decision | p.197 | KEY POINT |
| 5 | Trade speed and resource usage during development for debugging aids | p.205 | KEY POINT |

## Empirical Evidence

| Claim | Source | Evidence Type | Limitation |
|-------|--------|---------------|------------|
| Dead program does less damage than crippled one | Hunt & Thomas (Pragmatic Programmer) | Expert opinion | Not empirical |
| Design by Contract methodology | Meyer 1997 | Formal method | Adoption varies by language |
| Offensive programming makes errors obvious | Howard & LeBlanc 2003 | Best practice | Security-focused |
| Mars Pathfinder remote diagnosis via debug code | McConnell p.209 | Case study | Single case |

## Anti-Patterns (CODING HORROR)

### 1. Exception Abstraction Mismatch
- **Pattern:** Throwing implementation-level exceptions through class interface
- **Example:** `EOFException` from `Employee.GetTaxId()`
- **Why Wrong:** Breaks encapsulation, couples client code to implementation details
- **Fix:** Wrap in domain-appropriate exception (`EmployeeDataNotAvailable`)

### 2. Empty Catch Blocks
- **Pattern:** `try { ... } catch (Exception e) { }` with no handling
- **Why Wrong:** Either try block is wrong (raises exception it shouldn't) or catch is wrong (doesn't handle valid exception)
- **Fix:** At minimum, log. Better: handle or remove try block.

### 3. Executable Code in Assertions
- **Pattern:** `Assert(PerformAction())` - putting side effects in assertion
- **Why Wrong:** Code disappears when assertions disabled in production
- **Fix:** `result = PerformAction(); Assert(result);`

### 4. Assertions for Anticipated Conditions
- **Pattern:** Using assertions to check user input or external data
- **Why Wrong:** Assertions disabled in production; anticipated errors need actual handling
- **Fix:** Use error handling for anticipated conditions, assertions for bugs only

### 5. "Garbage In, Garbage Out" Mentality
- **Pattern:** Accepting invalid data and producing invalid output
- **Why Wrong:** Propagates errors, creates security vulnerabilities
- **Fix:** Validate input, reject or handle bad data explicitly

## Qualifiers and Scope

| Claim | Qualifier | Scope |
|-------|-----------|-------|
| Safety-critical apps favor correctness | "tend to" | Medical, aviation, nuclear |
| Consumer apps favor robustness | "tend to", "usually" | Games, word processors |
| Normally don't show assertions to users | "normally", "primarily" | Production builds |
| Little conventional wisdom on exceptions | Time-bound (2004) | May be outdated |

## Cross-References

| Topic | Location |
|-------|----------|
| Information hiding | Section 5.3 |
| Design for change | Section 5.3 |
| Software architecture | Section 3.5 |
| Design in Construction | Chapter 5 |
| Debugging | Chapter 23 |
| Preconditions/postconditions | Meyer 1997 |
| Stubs | Section 22.5 |
| Configuration Management | Section 28.2 |
| Preprocessors | Section 30.3 |

## Additional Resources

### Security
- Howard & LeBlanc, *Writing Secure Code*, 2d ed., Microsoft Press, 2003

### Assertions
- Maguire, *Writing Solid Code*, Microsoft Press, 1993 (Chapter 2)
- Stroustrup, *The C++ Programming Language*, 3d ed., 1997 (Section 24.3.7.2)
- Meyer, *Object-Oriented Software Construction*, 2d ed., 1997

### Exceptions
- Meyer, *Object-Oriented Software Construction*, 2d ed., 1997 (Chapter 12)
- Stroustrup, *The C++ Programming Language*, 3d ed., 1997 (Chapter 14)
- Meyers, *More Effective C++*, 1996 (Items 9-15)
- Bloch, *Effective Java*, 2001 (Items 39-47)
