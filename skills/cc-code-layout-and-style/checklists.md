# Checklists: cc-code-layout-and-style

Source: Code Complete 2nd Edition, Chapters 31-32

## Layout - General (p.773)

- [ ] "Is formatting done primarily to illuminate the logical structure of the code?"
- [ ] "Can the formatting scheme be used consistently?"
- [ ] "Does the formatting scheme result in code that's easy to maintain?"
- [ ] "Does the formatting scheme improve code readability?"

## Layout - Control Structures (p.773)

- [ ] "Does the code avoid doubly indented begin-end or {} pairs?"
- [ ] "Are sequential blocks separated from each other with blank lines?"
- [ ] "Are complicated expressions formatted for readability?"
- [ ] "Are single-statement blocks formatted consistently?"
- [ ] "Are case statements formatted in a way that's consistent with the formatting of other control structures?"
- [ ] "Have gotos been formatted in a way that makes their use obvious?"

## Layout - Individual Statements (p.774)

- [ ] "Is white space used to make logical expressions, array references, and routine arguments readable?"
- [ ] "Do incomplete statements end the line in a way that's obviously incorrect?"
- [ ] "Are continuation lines indented the standard indentation amount?"
- [ ] "Does each line contain at most one statement?"
- [ ] "Is each statement written without side effects?"
- [ ] "Is there at most one data declaration per line?"

## Layout - Comments (p.774)

- [ ] "Are the comments indented the same number of spaces as the code they comment?"
- [ ] "Is the commenting style easy to maintain?"

## Layout - Routines (p.774)

- [ ] "Are the arguments to each routine formatted so that each argument is easy to read, modify, and comment?"
- [ ] "Are blank lines used to separate parts of a routine?"

## Layout - Classes, Files and Programs (p.774)

- [ ] "Is there a one-to-one relationship between classes and files for most classes and files?"
- [ ] "If a file does contain multiple classes, are all the routines in each class grouped together and is each class clearly identified?"
- [ ] "Are routines within a file clearly separated with blank lines?"
- [ ] "In lieu of a stronger organizing principle, are all routines in alphabetical sequence?"

## Self-Documenting Code - Classes (p.816)

- [ ] "Does the class's interface present a consistent abstraction?"
- [ ] "Is the class well named, and does its name describe its central purpose?"
- [ ] "Does the class's interface make obvious how you should use the class?"
- [ ] "Is the class's interface abstract enough that you don't have to think about how its services are implemented? Can you treat the class as a black box?"

## Self-Documenting Code - Routines (p.816)

- [ ] "Does each routine's name describe exactly what the routine does?"
- [ ] "Does each routine perform one well-defined task?"
- [ ] "Have all parts of each routine that would benefit from being put into their own routines been put into their own routines?"
- [ ] "Is each routine's interface obvious and clear?"

## Self-Documenting Code - Data Names (p.816)

- [ ] "Are type names descriptive enough to help document data declarations?"
- [ ] "Are variables named well?"
- [ ] "Are variables used only for the purpose for which they're named?"
- [ ] "Are loop counters given more informative names than i, j, and k?"
- [ ] "Are well-named enumerated types used instead of makeshift flags or boolean variables?"
- [ ] "Are named constants used instead of magic numbers or magic strings?"
- [ ] "Do naming conventions distinguish among type names, enumerated types, named constants, local variables, class variables, and global variables?"

## Self-Documenting Code - Data Organization (p.817)

- [ ] "Are extra variables used for clarity when needed?"
- [ ] "Are references to variables close together?"
- [ ] "Are data types simple so that they minimize complexity?"
- [ ] "Is complicated data accessed through abstract access routines (abstract data types)?"

## Self-Documenting Code - Control (p.817)

- [ ] "Is the nominal path through the code clear?"
- [ ] "Are related statements grouped together?"
- [ ] "Have relatively independent groups of statements been packaged into their own routines?"
- [ ] "Does the normal case follow the if rather than the else?"
- [ ] "Are control structures simple so that they minimize complexity?"
- [ ] "Does each loop perform one and only one function, as a well-defined routine would?"
- [ ] "Is nesting minimized?"
- [ ] "Have boolean expressions been simplified by using additional boolean variables, boolean functions, and decision tables?"

## Self-Documenting Code - Layout (p.817)

- [ ] "Does the program's layout show its logical structure?"

## Self-Documenting Code - Design (p.817)

- [ ] "Is the code straightforward, and does it avoid cleverness?"
- [ ] "Are implementation details hidden as much as possible?"
- [ ] "Is the program written in terms of the problem domain as much as possible rather than in terms of computer-science or programming-language structures?"

## Good Commenting Technique - General (p.816)

- [ ] "Can someone pick up the code and immediately start to understand it?"
- [ ] "Do comments explain the code's intent or summarize what the code does, rather than just repeating the code?"
- [ ] "Is the Pseudocode Programming Process used to reduce commenting time?"
- [ ] "Has tricky code been rewritten rather than commented?"
- [ ] "Are comments up to date?"
- [ ] "Are comments clear and correct?"
- [ ] "Does the commenting style allow comments to be easily modified?"

## Good Commenting Technique - Statements and Paragraphs (p.816)

- [ ] "Does the code avoid endline comments?"
- [ ] "Do comments focus on why rather than how?"
- [ ] "Do comments prepare the reader for the code to follow?"
- [ ] "Does every comment count? Have redundant, extraneous, and self-indulgent comments been removed or improved?"
- [ ] "Are surprises documented?"
- [ ] "Have abbreviations been avoided?"
- [ ] "Is the distinction between major and minor comments clear?"
- [ ] "Is code that works around an error or undocumented feature commented?"

## Good Commenting Technique - Data Declarations (p.816)

- [ ] "Are units on data declarations commented?"
- [ ] "Are the ranges of values on numeric data commented?"
- [ ] "Are coded meanings commented?"
- [ ] "Are limitations on input data commented?"
- [ ] "Are flags documented to the bit level?"
- [ ] "Has each global variable been commented where it is declared?"
- [ ] "Has each global variable been identified as such at each usage, by a naming convention, a comment, or both?"
- [ ] "Are magic numbers replaced with named constants or variables rather than just documented?"

## Good Commenting Technique - Control Structures (p.817)

- [ ] "Is each control statement commented?"
- [ ] "Are the ends of long or complex control structures commented or, when possible, simplified so that they don't need comments?"

## Good Commenting Technique - Routines (p.817)

- [ ] "Is the purpose of each routine commented?"
- [ ] "Are other facts about each routine given in comments, when relevant, including input and output data, interface assumptions, limitations, error corrections, global effects, and sources of algorithms?"

## Good Commenting Technique - Files, Classes, and Programs (p.817)

- [ ] "Does the program have a short document, such as that described in the Book Paradigm, that gives an overall view of how the program is organized?"
- [ ] "Is the purpose of each file described?"
- [ ] "Are the author's name and contact information in the listing?"

---
Total items: 74
