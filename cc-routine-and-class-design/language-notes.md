# Language Notes: cc-routine-and-class-design

## C / C++

- **Input parameters**: Declare const to prevent modification within routine
- **Macros**: Avoid as alternative to routines; use const, inline, template, enum, typedef instead
- **Macro safety**: If macros required, fully parenthesize expressions: `#define Cube(a) ((a)*(a)*(a))`
- **Multi-statement macros**: Wrap in curly braces to ensure all statements execute in control structures
- **Inline routines**: Only use after profiling proves performance benefit justifies encapsulation loss
- **Return pointers**: Never return references/pointers to local data; save as class member instead

## Java / C#

- **Inheritance**: Favor containment by default; use inheritance only when "is-a" is literally true
- **Protected data**: Avoid in base classes; use private data with protected accessors if needed
- **Final/sealed**: Consider making classes non-inheritable when inheritance not designed for
- **Interface abstraction**: Each public member must be consistent with class's stated abstraction

## General OOP

- **ADT approach**: Think of classes as abstract data types first; focus on what operations make sense
- **Inheritance depth**: Keep < 3 levels (definitely < 6); deep hierarchies correlate with faults
- **LSP compliance**: Derived class must be usable through base interface without caller knowing difference
- **Law of Demeter**: Only call methods on direct collaborators, not on objects returned by collaborators
- **Empty overrides**: Never override a routine to do nothing; indicates base class design error
