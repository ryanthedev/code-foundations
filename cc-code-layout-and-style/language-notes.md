# Language Notes: cc-code-layout-and-style

## C / C++

- **Side effects**: Avoid multiple operations with ++ or assignment in single expression. Order of evaluation is undefined - results vary by compiler.
- **Pointer declarations**: Put asterisk next to variable name, not type, when multiple declarations possible. `char *a, b` declares pointer a and char b.
- **File organization**: Follow order: file comment, includes, constants, enums, macros, typedefs, imports, exports, private items, classes.

## Java

- **Block style**: Pure-block indentation is standard practice. Opening brace at end of control statement line.
- **Documentation**: Use Javadoc for public APIs. Keep routine documentation proportional to complexity.

## Visual Basic

- **Pure blocks**: Language has built-in block terminators (If-Then-End If, While-Wend). Use them - IDE makes it hard not to.

## General OOP

- **Class interface documentation**: Document what class does, not how. Hide implementation details (cardinal rule of encapsulation).
- **Class layout order**: Header comment, constructors/destructors, public routines, protected routines, private routines and data.

## Dynamic Languages (Python, JavaScript)

- **Formatters**: Use standard formatters (Black for Python, Prettier for JS). Let tool handle layout debates.
- **Comments**: Same principles apply - explain intent, not mechanics. Dynamically typed code may need more type hints in comments.
