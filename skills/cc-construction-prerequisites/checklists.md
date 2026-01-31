# Checklists: cc-construction-prerequisites

Source: Code Complete 2nd Edition, Chapters 3, 4

---

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

- [ ] RF-1: **[CORE]** "Are all the tasks the user wants to perform specified?" → Red flag: Vague user stories without concrete tasks
- [ ] RF-2: **[CORE]** "Is the data used in each task and the data resulting from each task specified?" (Good: Input schemas + output contracts, Bad: Assumptions about data)
- [ ] RF-3: **[STANDARD]** "Are all the inputs to the system specified, including their source, accuracy, range of values, and frequency?"
- [ ] RF-4: **[STANDARD]** "Are all the outputs from the system specified, including their destination, accuracy, range of values, frequency, and format?"
- [ ] RF-5: "Are all output formats specified for Web pages, reports, and so on?"
- [ ] RF-6: "Are all the external hardware and software interfaces specified?"
- [ ] RF-7: "Are all the external communication interfaces specified, including handshaking, error-checking, and communication protocols?"

---

## Requirements Checklist - Specific Nonfunctional Requirements (p.56)

- [ ] NF-1: **[CORE]** "Is the definition of success included? Of failure?" → Red flag: No clear acceptance criteria
- [ ] NF-2: **[STANDARD]** "Is the level of security specified?"
- [ ] NF-3: **[STANDARD]** "Is the reliability specified, including the consequences of software failure, the vital information that needs to be protected from failure, and the strategy for error detection and recovery?"
- [ ] NF-4: "Is the expected response time, from the user's point of view, specified for all necessary operations?"
- [ ] NF-5: "Are other timing considerations specified, such as processing time, data-transfer rate, and system throughput?"
- [ ] NF-6: "Is minimum machine memory and free disk space specified?"
- [ ] NF-7: "Is the maintainability of the system specified, including its ability to adapt to changes in specific functionality, changes in the operating environment, and changes in its interfaces with other software?"

---

## Requirements Checklist - Requirements Quality (p.57)

- [ ] RQ-1: **[CORE]** "Are the requirements clear enough to be turned over to an independent group for construction and still be understood? Do the developers think so?" (Good: Standalone docs, Bad: Tribal knowledge)
- [ ] RQ-2: **[CORE]** "Is each requirement testable? Will it be possible for independent testing to determine whether each requirement has been satisfied?" → Red flag: Untestable requirements
- [ ] RQ-3: **[STANDARD]** "Are the requirements written in the user's language? Do the users think so?"
- [ ] RQ-4: **[STANDARD]** "Does each requirement avoid conflicts with other requirements?"
- [ ] RQ-5: **[STANDARD]** "Do the requirements avoid specifying the design?" → Red flag: Solution disguised as requirement
- [ ] RQ-6: "Are acceptable tradeoffs between competing attributes specified - for example, between robustness and correctness?"
- [ ] RQ-7: "Are the requirements at a fairly consistent level of detail? Should any requirement be specified in more detail? Should any requirement be specified in less detail?"
- [ ] RQ-8: "Is each item relevant to the problem and its solution? Can each item be traced to its origin in the problem environment?"
- [ ] RQ-9: "Are all possible changes to the requirements specified, including the likelihood of each change?"

---

## Requirements Checklist - Requirements Completeness (p.57)

- [ ] RC-1: **[STANDARD]** "Where information isn't available before development begins, are the areas of incompleteness specified?" (Good: Known unknowns documented, Bad: Gaps ignored)
- [ ] RC-2: **[STANDARD]** "Are the requirements complete in the sense that if the product satisfies every requirement, it will be acceptable?"
- [ ] RC-3: "Are you comfortable with all the requirements? Have you eliminated requirements that are impossible to implement and included just to appease your customer or your boss?"

---

## Architecture Checklist - Specific Architectural Topics (p.58)

- [ ] AT-1: **[CORE]** "Is the overall organization of the program clear, including a good architectural overview and justification?" → Red flag: No high-level structure documented
- [ ] AT-2: **[CORE]** "Are major building blocks well defined, including their areas of responsibility and their interfaces to other building blocks?" (Good: Clear module boundaries, Bad: Tangled dependencies)
- [ ] AT-3: **[CORE]** "Is a coherent error-handling strategy provided?" → Red flag: Ad-hoc error handling per module
- [ ] AT-4: **[STANDARD]** "Are all the functions listed in the requirements covered sensibly, by neither too many nor too few building blocks?"
- [ ] AT-5: **[STANDARD]** "Are the most critical classes described and justified?"
- [ ] AT-6: **[STANDARD]** "Is the data design described and justified?"
- [ ] AT-7: **[STANDARD]** "Are the architecture's security requirements described?"
- [ ] AT-8: **[STANDARD]** "Is the architecture designed to accommodate likely changes?" (Good: Change points identified, Bad: Rigid design)
- [ ] AT-9: "Is the database organization and content specified?"
- [ ] AT-10: "Are all key business rules identified and their impact on the system described?"
- [ ] AT-11: "Is a strategy for the user interface design described?"
- [ ] AT-12: "Is the user interface modularized so that changes in it won't affect the rest of the program?"
- [ ] AT-13: "Is a strategy for handling I/O described and justified?"
- [ ] AT-14: "Are resource-use estimates and a strategy for resource management described and justified for scarce resources like threads, database connections, handles, network bandwidth, and so on?"
- [ ] AT-15: "Does the architecture set space and speed budgets for each class, subsystem, or functionality area?"
- [ ] AT-16: "Does the architecture describe how scalability will be achieved?"
- [ ] AT-17: "Does the architecture address interoperability?"
- [ ] AT-18: "Is a strategy for internationalization/localization described?"
- [ ] AT-19: "Is the approach to fault tolerance defined (if any is needed)?"
- [ ] AT-20: "Has technical feasibility of all parts of the system been established?"
- [ ] AT-21: "Is an approach to overengineering specified?"
- [ ] AT-22: "Are necessary buy-vs.-build decisions included?"
- [ ] AT-23: "Does the architecture describe how reused code will be made to conform to other architectural objectives?"

---

## Architecture Checklist - General Architectural Quality (p.59)

- [ ] AQ-1: **[CORE]** "Are you, as a programmer who will implement the system, comfortable with the architecture?" → Red flag: Implementers confused or uncomfortable
- [ ] AQ-2: **[STANDARD]** "Does the architecture account for all the requirements?"
- [ ] AQ-3: **[STANDARD]** "Are the motivations for all major decisions provided?" (Good: ADRs or design rationale, Bad: Unexplained choices)
- [ ] AQ-4: "Is any part overarchitected or underarchitected? Are expectations in this area set out explicitly?"
- [ ] AQ-5: "Does the whole architecture hang together conceptually?"
- [ ] AQ-6: "Is the top-level design independent of the machine and language that will be used to implement it?"

---

## Upstream Prerequisites Checklist (p.59)

**Note:** Complete items 1-4 in order - each depends on the previous.

- [ ] UP-1: **[CORE]** "Have you identified the kind of software project you're working on and tailored your approach appropriately?" (Good: Methodology matches project type, Bad: One-size-fits-all)
- [ ] UP-2: **[CORE]** "Are the requirements sufficiently well defined and stable enough to begin construction?" → Red flag: Major requirements still changing
- [ ] UP-3: **[CORE]** "Is the architecture sufficiently well defined to begin construction?" → Red flag: Key architectural decisions deferred
- [ ] UP-4: **[CORE]** "Have other risks unique to your particular project been addressed, such that construction is not exposed to more risk than necessary?"

---

## Major Construction Practices - Coding (p.69)

- [ ] CD-1: **[CORE]** "Have you defined coding conventions for names, comments, and layout?" → Red flag: Each developer using different style
- [ ] CD-2: **[STANDARD]** "Have you defined how much design will be done up front and how much will be done at the keyboard, while the code is being written?"
- [ ] CD-3: **[STANDARD]** "Have you defined specific coding practices implied by the architecture: how error conditions will be handled, how security will be addressed, what conventions will be used for class interfaces, what standards will apply to reused code, how much to consider performance while coding?"
- [ ] CD-4: "Have you identified your location on the technology wave and adjusted your approach to match?"
- [ ] CD-5: "If necessary, have you identified how you will program into the language rather than being limited by programming in it?"

---

## Major Construction Practices - Teamwork (p.69)

- [ ] TW-1: **[STANDARD]** "Have you defined an integration procedure (specific steps a programmer must go through before checking code into master sources)?" (Good: Checklist or automation, Bad: Informal process)
- [ ] TW-2: "Will programmers program in pairs, or individually, or some combination of the two?"

**Solo developer adaptation:** If working alone, convert teamwork items to self-review practices:
- Integration procedure → personal pre-commit checklist
- Pair programming → rubber duck debugging or time-delayed self-review

---

## Major Construction Practices - Quality Assurance (p.69)

- [ ] QA-1: **[STANDARD]** "Will programmers write unit tests for their code regardless of whether they write them first or last?"
- [ ] QA-2: **[STANDARD]** "Will programmers review or inspect each other's code?"
- [ ] QA-3: "Will programmers write test cases for their code before writing the code itself?"
- [ ] QA-4: "Will programmers step through their code in the debugger before they check it in?"
- [ ] QA-5: "Will programmers integration-test their code before they check it in?"

---

## Major Construction Practices - Tools (p.70)

- [ ] TL-1: **[CORE]** "Have you selected a revision control tool?" → Red flag: No version control
- [ ] TL-2: **[CORE]** "Have you selected a language and language version or compiler version?" → Red flag: Multiple incompatible versions
- [ ] TL-3: **[STANDARD]** "Have you selected a framework such as J2EE or Microsoft .NET or explicitly decided not to use a framework?"
- [ ] TL-4: "Have you decided whether to allow use of nonstandard language features?"
- [ ] TL-5: "Have you identified and acquired other tools you'll be using (editor, refactoring tool, debugger, test framework, syntax checker, etc.)?"

---

## Red Flags

- [ ] RFL-1: "Starting coding without requirements?" - Construction begins before problem is understood → Complete requirements checklist first
- [ ] RFL-2: "Starting coding without architecture?" - No high-level design documented → Complete architecture checklist first
- [ ] RFL-3: "Untestable requirements?" - Acceptance criteria vague or subjective → Rewrite with measurable criteria
- [ ] RFL-4: "Requirements specify implementation?" - Design decisions disguised as requirements → Separate what from how
- [ ] RFL-5: "Architecture has no error strategy?" - Each module handles errors differently → Define coherent error-handling approach
- [ ] RFL-6: "Implementers uncomfortable with design?" - Team doesn't understand or trust architecture → Revise or explain architecture
- [ ] RFL-7: "No coding standards?" - Each developer using different conventions → Define and document standards
- [ ] RFL-8: "Requirements still changing?" - Major requirements unstable during construction → Stabilize requirements or adjust methodology
- [ ] RFL-9: "Key decisions deferred?" - Critical architectural choices postponed → Resolve before construction
- [ ] RFL-10: "No version control?" - Code not tracked in repository → Set up revision control immediately

---

## Item Counts by Priority

| Priority | Count | When to Use |
|----------|-------|-------------|
| **[CORE]** | 16 | Always - minimum viable prerequisites |
| **[STANDARD]** | 20 | Most projects - scaled prerequisites |
| Unmarked | 31 | Complex/high-risk - comprehensive |
| **Total** | 66 | |

## CORE Items Quick Reference

For minimum viable prerequisites (5% floor), verify these 15 items:

**Requirements (6):**
1. RF-1: Tasks user wants to perform specified
2. RF-2: Data for each task specified
3. NF-1: Definition of success/failure included
4. RQ-1: Requirements clear to independent group
5. RQ-2: Each requirement testable

**Architecture (5):**
6. AT-1: Overall organization clear with justification
7. AT-2: Major building blocks defined with interfaces
8. AT-3: Error-handling strategy provided
9. AQ-1: Implementer comfortable with architecture

**Upstream Prerequisites (4):**
10. UP-1: Project type identified, approach tailored
11. UP-2: Requirements sufficiently defined
12. UP-3: Architecture sufficiently defined
13. UP-4: Project-specific risks addressed

**Construction Practices (3):**
14. CD-1: Coding conventions defined
15. TL-1: Revision control selected
16. TL-2: Language/version selected

---

Total items: 66
