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

### Case Studies

**Microsoft Word Debug Mode (p.395)**
- In debug mode, Word contains code in idle loop checking integrity of Document object every few seconds
- Helps detect data corruption quickly, makes error diagnosis easier
- Demonstrates: Trade speed for debugging capability during development

**Mars Pathfinder Remote Diagnosis (p.209)**
- Engineers left debug code in by design
- After landing, an error occurred
- Using debug aids left in, JPL engineers diagnosed problem remotely, uploaded revised code
- Pathfinder completed mission perfectly
- Demonstrates: Debug code in production can enable remote diagnosis and recovery

**Seattle Floating Bridge (Figure 8-1, p.187)**
- Part of Interstate-90 floating bridge sank during storm
- Flotation tanks were left uncovered, filled with water
- Bridge became too heavy to float
- Demonstrates: Protecting against small stuff matters more than you might think

**Spreadsheet Program Priority Example (p.209)**
- Screen update: Can afford undetected errors (penalty = messy screen)
- Calculation engine: Cannot afford errors (penalty = incorrect tax calculations, IRS audit)
- Demonstrates: Prioritize defensive code based on error consequences

**Radiation Machine Example (p.204)**
- If software controlling radiation equipment receives bad dosage input:
  - NOT: Use same value as last time
  - NOT: Use closest legal value
  - NOT: Use neutral value
  - YES: Shut down - better to reboot than risk wrong dosage
- Demonstrates: Safety-critical applications must favor correctness over robustness

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

### 6. Exceptions for Normal Processing Flow (p.199)
- **Pattern:** Using exceptions as part of normal control flow
- **Why Wrong:** Creates spaghetti code with readability/maintainability problems
- **Source:** Hunt & Thomas (Pragmatic Programmer)
- **Fix:** Reserve exceptions for exceptional circumstances; use normal control flow for anticipated paths

### 7. Carrying Data of Questionable Type (p.203)
- **Pattern:** Keeping input data in external/string format for extended processing
- **Why Wrong:** Increases complexity and chance of crashes from unexpected input
- **Fix:** Convert input data to proper type at input time

### 8. Verbose Error Messages to Users (p.210)
- **Pattern:** Error messages that reveal system internals or help attackers
- **Why Wrong:** Attackers sometimes use error messages to discover how to attack a system
- **Fix:** Use generic "internal error" with contact info; don't reveal stack traces or paths

### 9. Centralized Error Handler After Buffer Overrun (p.197)
- **Pattern:** Calling centralized error handler routine after detecting buffer overrun
- **Why Wrong:** Attacker may have compromised the handler routine/object address via the overrun
- **Security Implication:** Buffer overrun can corrupt the error handler's address
- **Fix:** For security-critical code, handle buffer overrun errors inline or shut down immediately

### 10. Throwing Exceptions in Constructors/Destructors (p.199)
- **Pattern:** Exceptions thrown from constructors or destructors without local catch
- **Why Wrong:** Rules for exception processing become very complicated; in C++, destructors aren't called unless object is fully constructed, creating potential resource leaks
- **Fix:** Avoid exceptions in constructors/destructors; if must use, catch in same place

## Qualifiers and Scope

| Claim | Qualifier | Scope | Page |
|-------|-----------|-------|------|
| Safety-critical apps favor correctness | "tend to" | Medical, aviation, nuclear | p.197 |
| Consumer apps favor robustness | "tend to", "usually" | Games, word processors | p.197 |
| Normally don't show assertions to users | "normally", "primarily" | Production builds | p.191 |
| Little conventional wisdom on exceptions | Time-bound (2004) | May be outdated | p.198 |
| For highly robust code, assert AND handle | "highly robust code" | Large, long-lasting, complex systems | p.193 |
| Exceptions similar to inheritance in complexity tradeoff | No qualifier | All exception usage | p.198 |
| Too much defensive programming creates problems | No qualifier | Fat/slow programs, added complexity | p.210 |
| Best form of defensive coding is not inserting errors | "should be" | Recommendation for priorities | p.188 |

## Cross-References

### Internal (Code Complete)

| Topic | Location | Relevance |
|-------|----------|-----------|
| Information hiding | Section 5.3 | Barricades implement information hiding |
| Design for change | Section 5.3 | Defensive coding anticipates modifications |
| Software architecture | Section 3.5 | Error-handling strategy is architectural |
| Design in Construction | Chapter 5 | Defensive programming context |
| Good Abstraction | Section 6.2 | Exception abstraction levels |
| Case statements | Section 15.2 | Default/else clause handling |
| Stubs | Section 22.5 | Debug stub pattern |
| Debugging | Chapter 23 | Debug aids in production |
| Configuration Management | Section 28.2 | Debug code management |
| Preprocessors | Section 30.3 | Conditional compilation |
| Multiple statements per line | Section 31.5 | Assertion formatting |
| Programming into language | Section 34.4 | Language-specific assertion support |

### External Sources

| Topic | Source | Year |
|-------|--------|------|
| Preconditions/postconditions (Design by Contract) | Meyer, *Object-Oriented Software Construction* | 1997 |
| Offensive programming | Howard & LeBlanc, *Writing Secure Code* | 2003 |
| Dead program vs crippled program | Hunt & Thomas, *Pragmatic Programmer* | 1999 |
| Assertions in C++ | Stroustrup, *The C++ Programming Language* (Section 24.3.7.2) | 1997 |
| Solid assertion practices | Maguire, *Writing Solid Code* (Chapter 2) | 1993 |
| Exception handling in C++ | Meyers, *More Effective C++* (Items 9-15) | 1996 |
| Exception handling in Java | Bloch, *Effective Java* (Items 39-47) | 2001 |
| Java language exceptions | Arnold/Gosling/Holmes, *The Java Programming Language* (Chapter 8) | 2000 |

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
