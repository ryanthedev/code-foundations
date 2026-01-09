# Checklists: cc-construction-prerequisites

Source: Code Complete 2nd Edition, Chapters 3, 4

## Prioritization Guide

Items are marked with priority tags:
- **[CORE]** - Mandatory for ALL projects, including minimum viable prerequisites (~15 items)
- **[STANDARD]** - Recommended for most projects (~35 items)
- **[COMPREHENSIVE]** - All items, for high-risk or complex projects (all 66 items)

**Usage by timeline:**
- **Minimum viable (5% floor):** Check all [CORE] items only
- **Scaled prerequisites (10-20%):** Check [CORE] + [STANDARD] items
- **Full prerequisites:** Check all items including unmarked

**Complete these sections in order** - each builds on the previous:
1. Requirements (defines what to build)
2. Architecture (defines how to build it)
3. Upstream Prerequisites (verifies readiness)
4. Construction Practices (defines how team will work)

## Contents

- [Requirements - Specific Functional Requirements](#requirements-checklist---specific-functional-requirements-p56)
- [Requirements - Specific Nonfunctional Requirements](#requirements-checklist---specific-nonfunctional-requirements-p56)
- [Requirements - Requirements Quality](#requirements-checklist---requirements-quality-p57)
- [Requirements - Requirements Completeness](#requirements-checklist---requirements-completeness-p57)
- [Architecture - Specific Architectural Topics](#architecture-checklist---specific-architectural-topics-p58)
- [Architecture - General Architectural Quality](#architecture-checklist---general-architectural-quality-p59)
- [Upstream Prerequisites](#upstream-prerequisites-checklist-p59)
- [Construction Practices - Coding](#major-construction-practices---coding-p69)
- [Construction Practices - Teamwork](#major-construction-practices---teamwork-p69)
- [Construction Practices - Quality Assurance](#major-construction-practices---quality-assurance-p69)
- [Construction Practices - Tools](#major-construction-practices---tools-p70)

---

## Requirements Checklist - Specific Functional Requirements (p.56)

- [ ] **[CORE]** Are all the tasks the user wants to perform specified?
- [ ] **[CORE]** Is the data used in each task and the data resulting from each task specified?
- [ ] **[STANDARD]** Are all the inputs to the system specified, including their source, accuracy, range of values, and frequency?
- [ ] **[STANDARD]** Are all the outputs from the system specified, including their destination, accuracy, range of values, frequency, and format?
- [ ] Are all output formats specified for Web pages, reports, and so on?
- [ ] Are all the external hardware and software interfaces specified?
- [ ] Are all the external communication interfaces specified, including handshaking, error-checking, and communication protocols?

## Requirements Checklist - Specific Nonfunctional Requirements (p.56)

- [ ] **[CORE]** Is the definition of success included? Of failure?
- [ ] **[STANDARD]** Is the level of security specified?
- [ ] **[STANDARD]** Is the reliability specified, including the consequences of software failure, the vital information that needs to be protected from failure, and the strategy for error detection and recovery?
- [ ] Is the expected response time, from the user's point of view, specified for all necessary operations?
- [ ] Are other timing considerations specified, such as processing time, data-transfer rate, and system throughput?
- [ ] Are minimum machine memory and free disk space specified?
- [ ] Is the maintainability of the system specified, including its ability to adapt to changes in specific functionality, changes in the operating environment, and changes in its interfaces with other software?

## Requirements Checklist - Requirements Quality (p.57)

- [ ] **[CORE]** Are the requirements clear enough to be turned over to an independent group for construction and still be understood? Do the developers think so?
- [ ] **[CORE]** Is each requirement testable? Will it be possible for independent testing to determine whether each requirement has been satisfied?
- [ ] **[STANDARD]** Are the requirements written in the user's language? Do the users think so?
- [ ] **[STANDARD]** Does each requirement avoid conflicts with other requirements?
- [ ] **[STANDARD]** Do the requirements avoid specifying the design?
- [ ] Are acceptable tradeoffs between competing attributes specified - for example, between robustness and correctness?
- [ ] Are the requirements at a fairly consistent level of detail? Should any requirement be specified in more detail? Should any requirement be specified in less detail?
- [ ] Is each item relevant to the problem and its solution? Can each item be traced to its origin in the problem environment?
- [ ] Are all possible changes to the requirements specified, including the likelihood of each change?

## Requirements Checklist - Requirements Completeness (p.57)

- [ ] **[STANDARD]** Where information isn't available before development begins, are the areas of incompleteness specified?
- [ ] **[STANDARD]** Are the requirements complete in the sense that if the product satisfies every requirement, it will be acceptable?
- [ ] Are you comfortable with all the requirements? Have you eliminated requirements that are impossible to implement and included just to appease your customer or your boss?

## Architecture Checklist - Specific Architectural Topics (p.58)

- [ ] **[CORE]** Is the overall organization of the program clear, including a good architectural overview and justification?
- [ ] **[CORE]** Are major building blocks well defined, including their areas of responsibility and their interfaces to other building blocks?
- [ ] **[CORE]** Is a coherent error-handling strategy provided?
- [ ] **[STANDARD]** Are all the functions listed in the requirements covered sensibly, by neither too many nor too few building blocks?
- [ ] **[STANDARD]** Are the most critical classes described and justified?
- [ ] **[STANDARD]** Is the data design described and justified?
- [ ] **[STANDARD]** Are the architecture's security requirements described?
- [ ] **[STANDARD]** Is the architecture designed to accommodate likely changes?
- [ ] Is the database organization and content specified?
- [ ] Are all key business rules identified and their impact on the system described?
- [ ] Is a strategy for the user interface design described?
- [ ] Is the user interface modularized so that changes in it won't affect the rest of the program?
- [ ] Is a strategy for handling I/O described and justified?
- [ ] Are resource-use estimates and a strategy for resource management described and justified for scarce resources like threads, database connections, handles, network bandwidth, and so on?
- [ ] Does the architecture set space and speed budgets for each class, subsystem, or functionality area?
- [ ] Does the architecture describe how scalability will be achieved?
- [ ] Does the architecture address interoperability?
- [ ] Is a strategy for internationalization/localization described?
- [ ] Is the approach to fault tolerance defined (if any is needed)?
- [ ] Has technical feasibility of all parts of the system been established?
- [ ] Is an approach to overengineering specified?
- [ ] Are necessary buy-vs.-build decisions included?
- [ ] Does the architecture describe how reused code will be made to conform to other architectural objectives?

## Architecture Checklist - General Architectural Quality (p.59)

- [ ] **[CORE]** Are you, as a programmer who will implement the system, comfortable with the architecture?
- [ ] **[STANDARD]** Does the architecture account for all the requirements?
- [ ] **[STANDARD]** Are the motivations for all major decisions provided?
- [ ] Is any part overarchitected or underarchitected? Are expectations in this area set out explicitly?
- [ ] Does the whole architecture hang together conceptually?
- [ ] Is the top-level design independent of the machine and language that will be used to implement it?

## Upstream Prerequisites Checklist (p.59)

**Note:** Complete items 1-4 in order - each depends on the previous.

- [ ] **[CORE]** 1. Have you identified the kind of software project you're working on and tailored your approach appropriately?
- [ ] **[CORE]** 2. Are the requirements sufficiently well defined and stable enough to begin construction?
- [ ] **[CORE]** 3. Is the architecture sufficiently well defined to begin construction?
- [ ] **[CORE]** 4. Have other risks unique to your particular project been addressed, such that construction is not exposed to more risk than necessary?

## Major Construction Practices - Coding (p.69)

- [ ] **[CORE]** Have you defined coding conventions for names, comments, and layout?
- [ ] **[STANDARD]** Have you defined how much design will be done up front and how much will be done at the keyboard, while the code is being written?
- [ ] **[STANDARD]** Have you defined specific coding practices implied by the architecture: how error conditions will be handled, how security will be addressed, what conventions will be used for class interfaces, what standards will apply to reused code, how much to consider performance while coding?
- [ ] Have you identified your location on the technology wave and adjusted your approach to match?
- [ ] If necessary, have you identified how you will program into the language rather than being limited by programming in it?

## Major Construction Practices - Teamwork (p.69)

- [ ] **[STANDARD]** Have you defined an integration procedure (specific steps a programmer must go through before checking code into master sources)?
- [ ] Will programmers program in pairs, or individually, or some combination of the two?

**Solo developer adaptation:** If working alone, convert teamwork items to self-review practices:
- Integration procedure → personal pre-commit checklist
- Pair programming → rubber duck debugging or time-delayed self-review

## Major Construction Practices - Quality Assurance (p.69)

- [ ] **[STANDARD]** Will programmers write unit tests for their code regardless of whether they write them first or last?
- [ ] **[STANDARD]** Will programmers review or inspect each other's code?
- [ ] Will programmers write test cases for their code before writing the code itself?
- [ ] Will programmers step through their code in the debugger before they check it in?
- [ ] Will programmers integration-test their code before they check it in?

## Major Construction Practices - Tools (p.70)

- [ ] **[CORE]** Have you selected a revision control tool?
- [ ] **[CORE]** Have you selected a language and language version or compiler version?
- [ ] **[STANDARD]** Have you selected a framework such as J2EE or Microsoft .NET or explicitly decided not to use a framework?
- [ ] Have you decided whether to allow use of nonstandard language features?
- [ ] Have you identified and acquired other tools you'll be using (editor, refactoring tool, debugger, test framework, syntax checker, etc.)?

---

## Item Counts by Priority

| Priority | Count | When to Use |
|----------|-------|-------------|
| **[CORE]** | 15 | Always - minimum viable prerequisites |
| **[STANDARD]** | 20 | Most projects - scaled prerequisites |
| Unmarked | 31 | Complex/high-risk - comprehensive |
| **Total** | 66 | |

## CORE Items Quick Reference

For minimum viable prerequisites (5% floor), verify these 15 items:

**Requirements (6):**
1. Tasks user wants to perform specified
2. Data for each task specified
3. Definition of success/failure included
4. Requirements clear to independent group
5. Each requirement testable

**Architecture (5):**
6. Overall organization clear with justification
7. Major building blocks defined with interfaces
8. Error-handling strategy provided
9. Implementer comfortable with architecture

**Upstream Prerequisites (4):**
10. Project type identified, approach tailored
11. Requirements sufficiently defined
12. Architecture sufficiently defined
13. Project-specific risks addressed

**Construction Practices (3):**
14. Coding conventions defined
15. Revision control selected
16. Language/version selected
