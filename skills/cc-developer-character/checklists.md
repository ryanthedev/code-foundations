# Checklists: cc-developer-character

Source: Code Complete 2nd Edition, Chapters 33-34

## Red Flags - Stop and Reassess (Ch 33, synthesized)

When you notice any of these, STOP immediately:

- [ ] About to compile to "see what happens"
- [ ] Ignoring or suppressing compiler warning
- [ ] Feeling 100% certain about something
- [ ] Giving estimate management wants rather than accurate one
- [ ] Stuck for 15+ minutes with no progress
- [ ] Working past fatigue point (6+ hours focused work)
- [ ] Claiming "90% complete"
- [ ] Refusing to let others see your code

## Character Traits Self-Assessment (Ch 33)

### Humility Assessment
- [ ] Do I recognize my brain's limitations?
- [ ] Am I using compensating practices (reviews, conventions, documentation)?
- [ ] Am I pretending to understand something I don't?

### Curiosity Assessment
- [ ] Am I actively seeking new knowledge?
- [ ] When did I last experiment with an unfamiliar language feature?
- [ ] Am I reading 35 pages/week of technical material?

### Intellectual Honesty Assessment
- [ ] Am I admitting mistakes quickly and emphatically?
- [ ] Am I providing realistic status reports?
- [ ] Am I defending accurate estimates rather than negotiating them?
- [ ] Am I understanding compiler warnings before suppressing them?

### Discipline Assessment
- [ ] Am I following conventions even when inconvenient?
- [ ] Am I analyzing before coding?
- [ ] Am I writing code for human readers first?

### Enlightened Laziness Assessment
- [ ] Am I doing unpleasant tasks quickly rather than deferring?
- [ ] Am I automating tedious tasks?
- [ ] Am I trying alternative approaches when stuck, not persisting stubbornly?

## Complexity Management Checklist (p.837-839, Ch 34)

- [ ] Is system divided into subsystems so brain can focus on smaller amounts at once?
- [ ] Are class interfaces carefully defined so internal workings can be ignored?
- [ ] Is abstraction preserved so brain doesn't remember arbitrary details?
- [ ] Is global data avoided (vastly increases code juggling)?
- [ ] Are deep inheritance hierarchies avoided (intellectually demanding)?
- [ ] Is deep nesting of loops/conditionals avoided?
- [ ] Are gotos avoided (nonlinear, difficult to follow)?
- [ ] Are monster classes that amount to whole programs avoided?
- [ ] Are routines kept short?
- [ ] Are variable names clear and self-explanatory?
- [ ] Are parameters to routines minimized?
- [ ] Are conventions used to spare brain from remembering arbitrary differences?
- [ ] Is error handling defined systematically?
- [ ] Is exception mechanism use disciplined (can become nonlinear like gotos)?

## Warning Signs Checklist (p.848-850, Ch 34)

When you notice any of these, investigate immediately:

### Code Structure Warnings
- [ ] Code described as "really tricky" (= usually poor code, consider rewriting)
- [ ] Class having more errors than average (error-prone, consider rewriting)
- [ ] Class with >7 members (complicated, look skeptically)
- [ ] Routine with >10 decision points (warning flag)
- [ ] >3 levels of logical nesting (warning flag)
- [ ] Unusual number of variables (warning flag)
- [ ] High coupling to other classes (warning flag)
- [ ] Low class or routine cohesion (warning flag)

### Design Warnings
- [ ] Repetitious code or similar modifications in several areas (control not centralized)
- [ ] Hard to create scaffolding for test cases (class too tightly coupled)
- [ ] Can't reuse code because classes too interdependent (too tightly coupled)
- [ ] Difficulty writing comments (need more design thinking)
- [ ] Difficulty naming variables (need more design thinking)
- [ ] Difficulty decomposing into cohesive classes (need more design thinking)

### Naming and Documentation Warnings
- [ ] Wishy-washy names (sign of trouble)
- [ ] Difficulty describing code in concise comments (sign of trouble)
- [ ] Figuring out code instead of reading it (too complicated)

### Process Warnings
- [ ] Abnormal number of defects in program (defective process)
- [ ] Lots of debugging on project (people not working smart)
- [ ] Compiler warnings/errors being ignored (fix them, don't ignore)

## Iteration Checklist (p.850-851, Ch 34)

- [ ] Have requirements been iterated with user until agreement?
- [ ] Has prototyping been used to develop alternative solutions?
- [ ] Has more than one design approach been considered?
- [ ] Has code been measured before optimization (not intuitive)?
- [ ] Are reviews used to check quality at each stage?
- [ ] Am I committing to a solution before exploring alternatives?

## Anti-Dogmatism Checklist (p.851-852, Ch 34)

- [ ] Am I treating any technique as "the one true method"?
- [ ] Am I using a mixture of methods appropriate to the problem?
- [ ] Am I giving new methods a fair shake?
- [ ] Am I also giving old, proven methods their fair shake?
- [ ] Am I willing to change beliefs based on experiment results?
- [ ] Have I decided on solution method before fully understanding the problem?

---
Total items: 70
