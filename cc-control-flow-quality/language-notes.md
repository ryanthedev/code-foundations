# Language Notes: cc-control-flow-quality

Language-specific guidance extracted from Code Complete chapters 14-19.

## C / C++

- **Case fallthrough**: Requires explicit `break` at end of each case; use `// FALLTHROUGH -- [reason]` comment for intentional fallthrough
- **Short-circuit evaluation**: `&&` and `||` stop evaluating once result is determined; first false in `&&` or first true in `||` ends evaluation
- **Loop index scope**: Varies by compiler implementation; author got three different results from three compilers
- **For loop index**: Never modify the loop index inside the loop body to force termination - use `while` instead
- **For loop header**: Reserve for loop-control code only; don't cram while-loop logic into for header
- **Pointer comparison**: Compare pointers to `NULL` explicitly (`while (bufferPtr != NULL)`) rather than implicitly
- **Character comparison**: Compare to null terminator explicitly (`while (*charPtr != '\0')`) - clearer than `while (*charPtr)`
- **Assignment vs equality**: Consider compiler warnings for `=` vs `==` errors rather than constants-on-left style
- **Preprocessor booleans**: If language version lacks native booleans, create `TRUE`/`FALSE` macros

## Java

- **Object comparison**: Use `a.equals(b)` for logical equality, not `a == b` (which tests object identity)
- **Labeled break**: Supports labeled break for exiting nested loops cleanly
- **Logical operators**: `&` and `|` guarantee full evaluation of all terms; `&&` and `||` use short-circuit evaluation
- **Case fallthrough**: Requires explicit `break` at end of each case, same as C/C++

## C#

- **foreach**: Eliminates loop-housekeeping arithmetic errors; use when iterating containers
- **Case fallthrough**: Requires explicit `break` at end of each case

## Visual Basic

- **Rich case statements**: Supports strings, ranges, and combinations (e.g., `Case 1 To 10`, `Case "A" To "Z"`)
- **Loop constructs**: Multiple loop types with different semantics:
  - `For-Next`: Rigid, test at beginning
  - `While-Wend`: Flexible, test at beginning
  - `Do-Loop-While`: Flexible, test at beginning or end
  - `For-Each`: Rigid, test at beginning
- **Boolean keywords**: Use `True`/`False` rather than 0/1; use `Not` for negation

## General OOP

- **Case to polymorphism**: Case statements testing object type often indicate poorly factored OO code; consider factory methods and polymorphic dispatch
- **Factory methods**: Use for object creation based on type instead of switch/case on type codes
- **Inheritance vs tables**: Don't assume OOP inheritance hierarchy is superior to table-driven approach; evaluate both
- **Subclass proliferation**: Creating subclass per variant when table-driven approach is simpler is an anti-pattern

## Cross-Language Cautions

- **Evaluation order**: Different languages and even different compilers use different boolean evaluation strategies; don't depend on evaluation order
- **Loop terminal value**: Final value of loop index after loop exits varies by language and implementation; capture needed values inside loop
- **Floating-point counters**: Never use floating-point types as loop counters; adding 1.0 to large numbers can fail due to precision limits
