# Checklists: cc-developer-character

Source: Code Complete 2nd Edition, Chapters 33-34

---

## Character Traits Self-Assessment (Ch 33)

### Humility Assessment

- [ ] HU-1: "Do I recognize my brain's limitations?"
- [ ] HU-2: "Am I using compensating practices (reviews, conventions, documentation)?"
- [ ] HU-3: "Am I pretending to understand something I don't?" → Red flag: Claiming certainty without evidence

### Curiosity Assessment

- [ ] CU-1: "Am I actively seeking new knowledge?"
- [ ] CU-2: "When did I last experiment with an unfamiliar language feature?"
- [ ] CU-3: "Am I reading 35 pages/week of technical material?" (Good: Regular learning, Bad: Stagnation)

### Intellectual Honesty Assessment

- [ ] IH-1: "Am I admitting mistakes quickly and emphatically?"
- [ ] IH-2: "Am I providing realistic status reports?" → Red flag: "90% complete" claims
- [ ] IH-3: "Am I defending accurate estimates rather than negotiating them?" (Good: Data-driven, Bad: Management-pleasing)
- [ ] IH-4: "Am I understanding compiler warnings before suppressing them?" → Red flag: Ignoring warnings

### Discipline Assessment

- [ ] DI-1: "Am I following conventions even when inconvenient?"
- [ ] DI-2: "Am I analyzing before coding?" → Red flag: Compiling "to see what happens"
- [ ] DI-3: "Am I writing code for human readers first?"

### Enlightened Laziness Assessment

- [ ] EL-1: "Am I doing unpleasant tasks quickly rather than deferring?"
- [ ] EL-2: "Am I automating tedious tasks?"
- [ ] EL-3: "Am I trying alternative approaches when stuck, not persisting stubbornly?" → Red flag: Stuck 15+ minutes with no progress

---

## Complexity Management Checklist (p.837-839, Ch 34)

- [ ] CM-1: "Is system divided into subsystems so brain can focus on smaller amounts at once?"
- [ ] CM-2: "Are class interfaces carefully defined so internal workings can be ignored?"
- [ ] CM-3: "Is abstraction preserved so brain doesn't remember arbitrary details?"
- [ ] CM-4: "Is global data avoided (vastly increases code juggling)?"
- [ ] CM-5: "Are deep inheritance hierarchies avoided (intellectually demanding)?"
- [ ] CM-6: "Is deep nesting of loops/conditionals avoided?"
- [ ] CM-7: "Are gotos avoided (nonlinear, difficult to follow)?"
- [ ] CM-8: "Are monster classes that amount to whole programs avoided?"
- [ ] CM-9: "Are routines kept short?"
- [ ] CM-10: "Are variable names clear and self-explanatory?"
- [ ] CM-11: "Are parameters to routines minimized?" (Good: ≤7 params, Bad: >7)
- [ ] CM-12: "Are conventions used to spare brain from remembering arbitrary differences?"
- [ ] CM-13: "Is error handling defined systematically?"
- [ ] CM-14: "Is exception mechanism use disciplined (can become nonlinear like gotos)?"

---

## Warning Signs Checklist (p.848-850, Ch 34)

### Code Structure Warnings

- [ ] CS-1: "Code described as 'really tricky'?" → Red flag: Usually poor code, consider rewriting
- [ ] CS-2: "Class having more errors than average?" → Error-prone, consider rewriting
- [ ] CS-3: "Class with >7 members?" → Complicated, look skeptically
- [ ] CS-4: "Routine with >10 decision points?" → Warning flag
- [ ] CS-5: ">3 levels of logical nesting?" → Warning flag
- [ ] CS-6: "Unusual number of variables?" → Warning flag
- [ ] CS-7: "High coupling to other classes?" → Warning flag
- [ ] CS-8: "Low class or routine cohesion?" → Warning flag

### Design Warnings

- [ ] DW-1: "Repetitious code or similar modifications in several areas?" → Control not centralized
- [ ] DW-2: "Hard to create scaffolding for test cases?" → Class too tightly coupled
- [ ] DW-3: "Can't reuse code because classes too interdependent?" → Too tightly coupled
- [ ] DW-4: "Difficulty writing comments?" → Need more design thinking
- [ ] DW-5: "Difficulty naming variables?" → Need more design thinking
- [ ] DW-6: "Difficulty decomposing into cohesive classes?" → Need more design thinking

### Naming and Documentation Warnings

- [ ] ND-1: "Wishy-washy names?" → Sign of trouble
- [ ] ND-2: "Difficulty describing code in concise comments?" → Sign of trouble
- [ ] ND-3: "Figuring out code instead of reading it?" → Too complicated

### Process Warnings

- [ ] PW-1: "Abnormal number of defects in program?" → Defective process
- [ ] PW-2: "Lots of debugging on project?" → People not working smart
- [ ] PW-3: "Compiler warnings/errors being ignored?" → Red flag: Fix them, don't ignore

---

## Iteration Checklist (p.850-851, Ch 34)

- [ ] IT-1: "Have requirements been iterated with user until agreement?"
- [ ] IT-2: "Has prototyping been used to develop alternative solutions?"
- [ ] IT-3: "Has more than one design approach been considered?"
- [ ] IT-4: "Has code been measured before optimization (not intuitive)?"
- [ ] IT-5: "Are reviews used to check quality at each stage?"
- [ ] IT-6: "Am I committing to a solution before exploring alternatives?" → Red flag: Premature convergence

---

## Anti-Dogmatism Checklist (p.851-852, Ch 34)

- [ ] AD-1: "Am I treating any technique as 'the one true method'?" → Red flag: Dogmatism
- [ ] AD-2: "Am I using a mixture of methods appropriate to the problem?"
- [ ] AD-3: "Am I giving new methods a fair shake?"
- [ ] AD-4: "Am I also giving old, proven methods their fair shake?"
- [ ] AD-5: "Am I willing to change beliefs based on experiment results?"
- [ ] AD-6: "Have I decided on solution method before fully understanding the problem?" → Red flag: Solution-first thinking

---

## Red Flags - Stop and Reassess

- [ ] RF-1: "About to compile 'to see what happens'?" → Analyze first, compile after thinking
- [ ] RF-2: "Ignoring or suppressing compiler warning?" → Understand warnings before suppressing
- [ ] RF-3: "Feeling 100% certain about something?" → Dangerous overconfidence, seek review
- [ ] RF-4: "Giving estimate management wants rather than accurate one?" → Intellectual dishonesty destroys credibility
- [ ] RF-5: "Stuck for 15+ minutes with no progress?" → Try different approach, ask for help
- [ ] RF-6: "Working past fatigue point (6+ hours focused work)?" → Diminishing returns, introduce defects
- [ ] RF-7: "Claiming '90% complete'?" → False precision, likely hiding uncertainty
- [ ] RF-8: "Refusing to let others see your code?" → Sign of insecurity or poor quality
- [ ] RF-9: "Defensive about code critique?" → Ego over quality
- [ ] RF-10: "Skipping tests to meet deadline?" → Technical debt compounds

---

Total items: 72
