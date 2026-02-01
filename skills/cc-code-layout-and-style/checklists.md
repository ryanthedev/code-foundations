# Checklists: cc-code-layout-and-style

Source: Code Complete 2nd Edition, Chapters 31-32

---

## Layout - General

- [ ] LG-1: "Is formatting done primarily to illuminate the logical structure of the code?" → Good: indentation shows nesting, Bad: decorative formatting
- [ ] LG-2: "Can the formatting scheme be used consistently?"
- [ ] LG-3: "Does the formatting scheme result in code that's easy to maintain?"
- [ ] LG-4: "Does the formatting scheme improve code readability?"

---

## Layout - Control Structures

- [ ] LC-1: "Does the code avoid doubly indented begin-end or {} pairs?" → Red flag: { on new line AND indented
- [ ] LC-2: "Are sequential blocks separated from each other with blank lines?"
- [ ] LC-3: "Are complicated expressions formatted for readability?" (Good: multi-line with aligned operators, Bad: 80-char one-liner)
- [ ] LC-4: "Are single-statement blocks formatted consistently?"
- [ ] LC-5: "Are case statements formatted in a way that's consistent with the formatting of other control structures?"
- [ ] LC-6: "Have gotos been formatted in a way that makes their use obvious?"

---

## Layout - Individual Statements

- [ ] LS-1: "Is white space used to make logical expressions, array references, and routine arguments readable?"
- [ ] LS-2: "Do incomplete statements end the line in a way that's obviously incorrect?" (Good: trailing operator, Bad: looks complete)
- [ ] LS-3: "Are continuation lines indented the standard indentation amount?"
- [ ] LS-4: "Does each line contain at most one statement?" → Red flag: multiple semicolons per line
- [ ] LS-5: "Is each statement written without side effects?" → Red flag: `if (x = getValue())`
- [ ] LS-6: "Is there at most one data declaration per line?" → Red flag: `int x, y, z;`

---

## Layout - Comments

- [ ] LM-1: "Are the comments indented the same number of spaces as the code they comment?"
- [ ] LM-2: "Is the commenting style easy to maintain?"

---

## Layout - Routines

- [ ] LR-1: "Are the arguments to each routine formatted so that each argument is easy to read, modify, and comment?"
- [ ] LR-2: "Are blank lines used to separate parts of a routine?"

---

## Layout - Classes, Files and Programs

- [ ] LF-1: "Is there a one-to-one relationship between classes and files for most classes and files?"
- [ ] LF-2: "If a file does contain multiple classes, are all the routines in each class grouped together and is each class clearly identified?"
- [ ] LF-3: "Are routines within a file clearly separated with blank lines?"
- [ ] LF-4: "In lieu of a stronger organizing principle, are all routines in alphabetical sequence?"

---

## Self-Documenting Code - Classes

- [ ] SC-1: "Does the class's interface present a consistent abstraction?"
- [ ] SC-2: "Is the class well named, and does its name describe its central purpose?"
- [ ] SC-3: "Does the class's interface make obvious how you should use the class?"
- [ ] SC-4: "Is the class's interface abstract enough that you don't have to think about how its services are implemented? Can you treat the class as a black box?"

---

## Self-Documenting Code - Routines

- [ ] SR-1: "Does each routine's name describe exactly what the routine does?" → Red flag: vague verbs (process, handle, manage)
- [ ] SR-2: "Does each routine perform one well-defined task?"
- [ ] SR-3: "Have all parts of each routine that would benefit from being put into their own routines been put into their own routines?"
- [ ] SR-4: "Is each routine's interface obvious and clear?"

---

## Self-Documenting Code - Data Names

- [ ] DN-1: "Are type names descriptive enough to help document data declarations?"
- [ ] DN-2: "Are variables named well?" → Good: `accountBalance`, Bad: `ab`, `data`, `temp`
- [ ] DN-3: "Are variables used only for the purpose for which they're named?"
- [ ] DN-4: "Are loop counters given more informative names than i, j, and k?" (Exception: simple 1-5 line loops)
- [ ] DN-5: "Are well-named enumerated types used instead of makeshift flags or boolean variables?"
- [ ] DN-6: "Are named constants used instead of magic numbers or magic strings?" → Red flag: literal numbers in logic
- [ ] DN-7: "Do naming conventions distinguish among type names, enumerated types, named constants, local variables, class variables, and global variables?"

---

## Self-Documenting Code - Data Organization

- [ ] DO-1: "Are extra variables used for clarity when needed?" (Good: `isEligible = age > 18 && hasLicense`, Bad: inline complex condition)
- [ ] DO-2: "Are references to variables close together?" → Red flag: variable declared then unused for 50+ lines
- [ ] DO-3: "Are data types simple so that they minimize complexity?"
- [ ] DO-4: "Is complicated data accessed through abstract access routines (abstract data types)?"

---

## Self-Documenting Code - Control

- [ ] CT-1: "Is the nominal path through the code clear?" → Good: happy path first, error cases nested
- [ ] CT-2: "Are related statements grouped together?"
- [ ] CT-3: "Have relatively independent groups of statements been packaged into their own routines?"
- [ ] CT-4: "Does the normal case follow the if rather than the else?"
- [ ] CT-5: "Are control structures simple so that they minimize complexity?"
- [ ] CT-6: "Does each loop perform one and only one function, as a well-defined routine would?"
- [ ] CT-7: "Is nesting minimized?" → Red flag: 4+ levels of nesting
- [ ] CT-8: "Have boolean expressions been simplified by using additional boolean variables, boolean functions, and decision tables?"

---

## Self-Documenting Code - Layout

- [ ] SL-1: "Does the program's layout show its logical structure?"

---

## Self-Documenting Code - Design

- [ ] SD-1: "Is the code straightforward, and does it avoid cleverness?" → Red flag: code golf, one-liners, obscure language features
- [ ] SD-2: "Are implementation details hidden as much as possible?"
- [ ] SD-3: "Is the program written in terms of the problem domain as much as possible rather than in terms of computer-science or programming-language structures?"

---

## Good Commenting Technique - General

- [ ] CG-1: "Can someone pick up the code and immediately start to understand it?"
- [ ] CG-2: "Do comments explain the code's intent or summarize what the code does, rather than just repeating the code?" → Bad: `i++; // increment i`
- [ ] CG-3: "Is the Pseudocode Programming Process used to reduce commenting time?"
- [ ] CG-4: "Has tricky code been rewritten rather than commented?" → Red flag: "Here's how this works..." comment
- [ ] CG-5: "Are comments up to date?" → Red flag: code contradicts comment
- [ ] CG-6: "Are comments clear and correct?"
- [ ] CG-7: "Does the commenting style allow comments to be easily modified?"

---

## Good Commenting Technique - Statements and Paragraphs

- [ ] CS-1: "Does the code avoid endline comments?" (Exception: data declarations with units/ranges)
- [ ] CS-2: "Do comments focus on why rather than how?"
- [ ] CS-3: "Do comments prepare the reader for the code to follow?"
- [ ] CS-4: "Does every comment count? Have redundant, extraneous, and self-indulgent comments been removed or improved?"
- [ ] CS-5: "Are surprises documented?" → Flag: non-obvious behavior, side effects, performance characteristics
- [ ] CS-6: "Have abbreviations been avoided?"
- [ ] CS-7: "Is the distinction between major and minor comments clear?"
- [ ] CS-8: "Is code that works around an error or undocumented feature commented?"

---

## Good Commenting Technique - Data Declarations

- [ ] CD-1: "Are units on data declarations commented?" (Good: `timeout // milliseconds`, Bad: undocumented units)
- [ ] CD-2: "Are the ranges of values on numeric data commented?" (Good: `score // 0-100`, Bad: undocumented range)
- [ ] CD-3: "Are coded meanings commented?" (Good: `status // 0=pending, 1=active, 2=closed`)
- [ ] CD-4: "Are limitations on input data commented?"
- [ ] CD-5: "Are flags documented to the bit level?"
- [ ] CD-6: "Has each global variable been commented where it is declared?"
- [ ] CD-7: "Has each global variable been identified as such at each usage, by a naming convention, a comment, or both?"
- [ ] CD-8: "Are magic numbers replaced with named constants or variables rather than just documented?"

---

## Good Commenting Technique - Control Structures

- [ ] CC-1: "Is each control statement commented?" (For complex conditions and non-obvious loops)
- [ ] CC-2: "Are the ends of long or complex control structures commented or, when possible, simplified so that they don't need comments?"

---

## Good Commenting Technique - Routines

- [ ] CR-1: "Is the purpose of each routine commented?"
- [ ] CR-2: "Are other facts about each routine given in comments, when relevant, including input and output data, interface assumptions, limitations, error corrections, global effects, and sources of algorithms?"

---

## Good Commenting Technique - Files, Classes, and Programs

- [ ] CF-1: "Does the program have a short document, such as that described in the Book Paradigm, that gives an overall view of how the program is organized?"
- [ ] CF-2: "Is the purpose of each file described?"
- [ ] CF-3: "Are the author's name and contact information in the listing?"

---

## Red Flags

- [ ] RF-1: "Clever code?" - One-liners, code golf, obscure features → Rewrite for clarity
- [ ] RF-2: "Deep nesting?" - 4+ levels of indentation → Extract routines, invert conditions
- [ ] RF-3: "Magic numbers?" - Literal values in logic → Replace with named constants
- [ ] RF-4: "Vague names?" - `data`, `temp`, `process()`, `handle()` → Use domain-specific names
- [ ] RF-5: "Multiple statements per line?" - `x++; y++; z++;` → One statement per line
- [ ] RF-6: "Side effects in conditions?" - `if (x = getValue())` → Separate assignment from test
- [ ] RF-7: "Stale comments?" - Code contradicts comment → Update or remove
- [ ] RF-8: "Comment explains how?" - Instead of why → Refactor code or rewrite comment for intent
- [ ] RF-9: "Variables with distant references?" - Declared then unused for 50+ lines → Move declaration closer to use
- [ ] RF-10: "Undocumented units/ranges?" - Numeric data without context → Add inline comments with units and valid ranges

---

Total items: 85
