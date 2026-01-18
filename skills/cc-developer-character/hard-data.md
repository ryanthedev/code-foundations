# Evidence: cc-developer-character

## Key Points (Author-Marked)

### Chapter 33 - Personal Character (p.819-835)

- [KEY POINT p.819] "Your personal character directly affects your ability to write computer programs."
- [KEY POINT p.821] "The characteristics that matter most are humility, curiosity, intellectual honesty, creativity and discipline, and enlightened laziness."
- [KEY POINT p.833] "The characteristics of a superior programmer have almost nothing to do with talent and everything to do with a commitment to personal development."
- [KEY POINT p.833] "Surprisingly, raw intelligence, experience, persistence, and guts hurt as much as they help."
- [KEY POINT p.834] "Good character is mainly a matter of having the right habits."

### Core Concepts

#### The Humble Programmer (p.821)
Dijkstra's 1972 concept: Most of programming is an attempt to compensate for the strictly limited size of our skulls. The best programmers realize how small their brains are—they are humble. [XREF: Section 5.2]

#### Egoless Programming (p.821)
Review techniques (reviews, inspections, tests) originated as part of "egoless programming" (Weinberg 1998)—compensating for anticipated human fallibilities by augmenting limited intellectual capacity with others'.

#### Character vs Intelligence (p.819-821)
- "You can't do anything about your intelligence...but you can do something about your character. And it turns out that character is the more decisive factor in the makeup of a superior programmer."
- Great intelligence is only "loosely connected" to being a good programmer.
- The way you focus your intelligence is more important than how much intelligence you have.

#### Professional Development Ladder (p.825)
- **Level 1: Beginning** - Can use basic capabilities of one language (classes, routines, loops, conditionals)
- **Level 2: Introductory** - Basic capabilities of multiple languages, very comfortable in at least one
- **Level 3: Competency** - Expertise in a language or environment or both; many programmers never move beyond this level
- **Level 4: Leadership** - Recognizes programming is only 15% communicating with computer and 85% communicating with people; writes code for an audience of people rather than machines

#### Three Types of Laziness (p.830)
1. **True laziness** - Deferring unpleasant tasks (harmful)
2. **Enlightened laziness** - Doing unpleasant tasks quickly to get them out of the way (beneficial)
3. **Long-term laziness** - Writing tools to automate unpleasant tasks (most productive)

#### Programming is Communication (p.825)
- Programming is only 15% communicating with the computer and 85% communicating with people.
- "Programming is communicating with another programmer first and communicating with the computer second."

#### Thinking > Busy-ness (p.820)
- "The most important work in effective programming is thinking, and people tend not to look busy when they're thinking."
- "It's easy to confuse motion with progress, busy-ness with being productive."

### Chapter 34 - Themes in Software Craftsmanship (p.853)

- [KEY POINT p.853] "One primary goal of programming is managing complexity."
- [KEY POINT p.853] "The programming process significantly affects the final product."
- [KEY POINT p.853] "Team programming is more an exercise in communicating with people than in communicating with a computer."
- [KEY POINT p.853] "Paying attention to intellectual warning signs like the 'irritation of doubt' is especially important in programming."
- [KEY POINT p.853] "The more you iterate in each development activity, the better the product will be."
- [KEY POINT p.853] "Dogmatic methodologies and high-quality software development don't mix."

## Empirical Evidence

### 10:1 Programmer Variation
- [HARD DATA: Sackman, Erikson, Grant 1968; Curtis 1981; Mills 1983; DeMarco and Lister 1985; Curtis et al. 1986; Card 1987; Valett and McGarry 1989] "10:1 variation in programmer performance in time, debugging, size, speed, error rate, and errors detected." (p.819-820)
  - Study after study has found differences on the order of 10 to 1 in:
    - Time required to create a program
    - Time required to debug a program
    - Resulting size, speed, error rate, and number of errors detected
  - Context: Multiple independent studies confirming large individual variation
  - Confidence: High (multiple independent studies)

### Communication and Collaboration
- [HARD DATA: McCue 1978 p.825] "Only 30% of programmer time is spent working alone."
  - Context: Programming is primarily communication with people

### Reading and Professional Development
- [HARD DATA: DeMarco and Lister 1999 p.824] "One book is more than most programmers read each year."
  - Context: Reading distinguishes professional programmers
  - Implication: Reading one good programming book every two months (~35 pages/week) will "distinguish yourself from nearly everyone around you"

### Knowledge Half-Life (p.824)
- "In a competitive software market, half of what you now need to know to do your job will be out of date in three years."
- Technical environment changes every 5 to 10 years.
- [QUALIFIER: "competitive software market"]
- Confidence: Medium (author's estimate)

### Humility Produces Better Code (p.821)
- "Humble programmers who compensate for their fallibilities write code that's easier for themselves and others to understand and that has fewer errors."
- [QUALIFIER: "empirically...been shown"]
- Confidence: High

### Discipline and Standards
- [HARD DATA: McGarry and Pajerski 1990 p.829] "Methods emphasizing human discipline have been especially effective." (NASA SEL 15-year retrospective)
  - Context: Discipline-focused methods outperform others
  - "Without standards and conventions on large projects, project completion itself is impossible. Creativity isn't even imaginable."
  - "Form is liberating."

### Estimation
- [HARD DATA: Weimer in Metzger and Boddie 1996 p.828] "Technical people were good at estimating but bad at defending estimates."
  - Context: IBM's Bill Weimer on estimate negotiation
  - "Estimates aren't negotiable. He can revise an estimate to be more accurate, but negotiating with his boss won't change the time it takes to develop a software project."

### Habits and Early Career
- [HARD DATA: Bill Gates, Lammers 1986 p.834] "Any programmer who will ever be good is good in the first few years. After that, whether a programmer is good or not is cast in concrete."
  - Context: Habits form early; character development is time-sensitive
  - [QUALIFIER: Paraphrase of Gates' view]
  - Confidence: Medium

### Experience Quality (p.832)
- "If you work for 10 years, do you get 10 years of experience or do you get 1 year of experience 10 times?"
- "You have to reflect on your activities to get true experience."
- "If you can't shake the habits of thinking you developed while using your former programming language or the code-tuning techniques that worked on your old machine, your experience will be worse than none at all."

### Persistence (p.831)
- "Most of the time, persistence in software development is pigheadedness—it has little value."
- Give up on debugging error after ~15 minutes with no progress.
- [QUALIFIER: "Most of the time"]
- Confidence: Medium

### Unreadable Code (p.826)
- "In my experience, the main reason people write unreadable code is that their code is bad. They don't say to themselves, 'My code is bad, so I'll make it hard to read.' They just don't understand their code well enough to make it readable."
- [QUALIFIER: "In my experience"]
- Confidence: Medium (author's experience)

### Code Complexity and Readability
- [HARD DATA: Brooks 1995 p.837] "The biggest single gain in computer science was jump from machine language to higher-level languages."
  - Context: Abstraction as complexity management

- [HARD DATA: Thomas 1984 p.842] "10 generations of maintenance programmers work on an average program before rewrite."
  - Context: Code is read far more than written

- [HARD DATA: Parikh and Zvegintzov 1983 p.842] "Maintenance programmers spend 50-60% of time trying to understand code."
  - Context: Readability directly impacts productivity

### Error Detection
- [HARD DATA: Myers 1978b p.850] "The single most common cause of not finding errors was simply overlooking them."
  - Context: Visible on output but not noticed; attention is crucial

## Anti-Patterns (CODING HORROR)

### Burnout Pattern (p.820)
[CODING HORROR] Working 6+ focused hours (8AM-2PM), then 3 more despite diminishing returns (2PM-5PM), requiring a week to fix the defects introduced during the 3-hour push.
- **WARNING SIGNS:** After 6+ hours of focused work, noticing increased frustration, re-reading same code multiple times, simple mistakes appearing.
- **LESSON:** Demonstrates cost of pushing through fatigue vs. stopping when effectiveness drops.

### Uncooperative Programmer (p.825)
[CODING HORROR] Code with variables x, xx, xxx, xx1, xx2 (all global, uncommented). Manager thought she was great because she "fixed errors quickly"—the poor code gave her abundant opportunities.
- **LESSON:** Obfuscated code creates a self-perpetuating cycle of "heroic" bug fixing.

### Estimate Negotiation (p.827)
[CODING HORROR] Bert estimates 8 programmers, 6 months. Manager asks for shorter. Bert "negotiates" to 6 programmers, 4 months (cutting training, vacation, adding overtime). Manager says "no overtime allowed." Result: Bert will lose credibility delivering in 6 months when he promised 4.
- **LESSON:** "He'll lose credibility by compromising, and he'll gain respect by standing firm on his estimate."

### Ignoring/Misinterpreting Compiler Warnings (p.826-827)
[CODING HORROR] People claim "clean compile," describe symptoms. Expert: "sounds like uninitialized pointer, but compiler should warn." Response: "Oh yeah—it did warn. We thought it meant something else."
- **LESSON:** Don't ignore or misinterpret compiler warnings. You'll spend MORE time debugging from scratch while compiler waves solution at you.

### Gonzo Programming (p.830)
[CODING HORROR] 16-hour days, all-nighters feel heroic but produce defects requiring weeks to fix. "Excitement is no substitute for competency."
- **LESSON:** Those all-night programming stints make you feel like the greatest programmer in the world, but then you have to spend several weeks correcting the defects.

### "Tricky Code" (p.848)
[CODING HORROR] When code is described as "really tricky," that's a code phrase for "bad code." Rewrite it.

### Compiling to Test Understanding (p.823)
[CODING HORROR] "Just compile it to see if it works" when you don't understand the program. Running program to determine whether to use < or <=.
- **WARNING SIGN:** "Feeling tempted to compile a program to 'see what happens' is a warning sign."
- **REASON:** "It doesn't really matter whether the program works because you don't understand it well enough to know why it works...If you don't understand the program, you can't test it thoroughly."
- **LESSON:** "Make sure you have a strong intellectual grip on the program before you relinquish it to the compiler."

### "90% Complete" Status Reporting (p.828)
[CODING HORROR] Telling management the program is "90 percent complete" when it isn't. Saying what management wants to hear instead of the truth.
- **REASON:** "Management needs to have accurate information to coordinate development activities."

### Refusing to Admit Mistakes (p.826)
[CODING HORROR] "The only person she'll fool is herself. Everyone else will learn that they're working with a prideful programmer who's not completely honest. That's a more damning fault than making a simple error."
- **LESSON:** "If you make a mistake, admit it quickly and emphatically."

### Pretending Expertise You Lack (p.822)
[CODING HORROR] Refuse to pretend you're an expert when you're not.
- **REASON:** "How can you learn anything new if you pretend that you know everything already?"
- **BETTER:** "Pretend that you don't know anything. Listen to people's explanations, learn something new from them."

### Underestimating to Get Approval (p.828)
[CODING HORROR] Underestimating a project to get management to "buy in."
- **REASON:** "Tricking management into making the wrong decision could literally cost the company hundreds of thousands of dollars."
- **CONSEQUENCE:** "If it costs you your job, you'll have gotten what you deserve."

## Qualifiers and Scope

### Scope Limitations
- **Character vs Intelligence:** "loosely connected" - not zero correlation between intelligence and programming skill; just not as decisive as character. [p.821]
- **Knowledge Half-Life:** Applies to "competitive software market" specifically. Stable domains may have longer knowledge validity. [p.824]
- **Persistence:** "Most of the time" persistence is pigheadedness - there are cases where persistence is appropriate, particularly when clear progress is being made. [p.831]
- **Experience harm:** Experience "can be" harmful - conditional on inability to adapt; not inherently harmful. [p.832]
- **Habits cast early:** Bill Gates' view, presented as paraphrase; author does not fully endorse this determinism. [p.834]
- **Standards enabling creativity:** Applies to large projects with multiple contributors; solo exploratory work may benefit from less structure. [p.829]

### Counter-Indicators
- **Skipping "mental crutches":** Trivial one-off scripts with no future maintenance burden may not require full decomposition/review process.
- **Compiling to experiment:** Deliberate experimentation with isolated test programs to learn language features is encouraged (see Curiosity section). This is categorically different from compiling production code to "see if it works."
- **Admitting uncertainty:** High-stakes presentations where admitting uncertainty would undermine necessary credibility may require deferring questions and researching afterward.
- **Learning during crunch:** Currently in crunch mode on critical deadline - defer learning activities, don't skip them entirely.
- **Career self-assessment:** Very early in career (first 1-2 years) where rapid skill acquisition naturally dominates; self-assessment framework may not apply.

## Procedures

### Experimentation Process for Learning (p.822-823)
1. When you don't know how a language feature works, write a short program to exercise the feature
2. Watch the program execute in the debugger
3. If the feature doesn't work as expected, that's what you wanted to find out
4. Better to find out in small program than in larger program with feature you don't understand

**KEY INSIGHT:** "One key to effective programming is learning to make mistakes quickly, learning from them each time. Making a mistake is no sin. Failing to learn from a mistake is."

### Handling Time Pressure on Estimates (p.828)
1. Receive pressure to reduce estimate
2. Respond: "This is how much it's going to cost. I can't say whether it's worth this price to the company—that's your job. But I can tell you how long it takes to develop software—that's my job."
3. Offer alternatives: "We can negotiate other aspects of the project that affect the schedule and then reestimate"
4. Options to negotiate: eliminate features, reduce performance, develop in increments, adjust team size/schedule tradeoff

### Setting Parameters When Stuck (p.831)
1. Notice you're frustrated (signal to evaluate)
2. Ask: should I give up on this approach?
3. Set explicit parameters: "If I don't solve this using this approach within the next 30 minutes, I'll take 10 minutes to brainstorm about different approaches and try the best one for the next hour"

### Changing Bad Habits (p.834)
1. Cannot replace a bad habit with no habit at all
2. Must substitute a new habit for the old one
3. Example: Develop habit of writing pseudocode before coding; carefully reading code before compiling
4. Bad habits will "naturally drop by the wayside as new habits take their places"

## Positive Examples

### Michelangelo's Sistine Chapel (p.829)
Divided ceiling into symmetric collections of geometric forms (triangles, circles, squares). Designed in three zones corresponding to three Platonic stages. "Without this self-imposed structure and discipline, the 300 human figures would have been merely chaotic rather than the coherent elements of an artistic masterpiece."
- **LESSON:** Discipline enables rather than stifles creativity.

## Cross-References

### Internal Chapter References
- [XREF: Section 5.2] The Humble Programmer concept (Dijkstra 1972) - design practices
- [XREF: Chapter 34] Themes in Software Craftsmanship - complexity management, iteration, communication

### Related Skills
- **cc-quality-practices** - Review techniques that compensate for human fallibility
- **cc-defensive-programming** - Coding practices that account for limited brain capacity
- **cc-construction-prerequisites** - Readiness assessment and upstream work
- **cc-pseudocode-programming** - "Writing before compiling" habit formation
- **aposd-reviewing-module-design** - Humility-driven design review

### Key Sources Referenced
| Source | Topic | Page |
|--------|-------|------|
| Dijkstra 1972 | Humble Programmer | p.821 |
| Weinberg 1998 | Egoless Programming | p.821 |
| Sackman et al. 1968 | 10:1 programmer variation | p.819 |
| McCue 1978 | 30% time alone | p.825 |
| DeMarco and Lister 1999 | Reading habits | p.824 |
| McGarry and Pajerski 1990 | NASA SEL discipline study | p.829 |
| Metzger and Boddie 1996 | Weimer on estimates | p.828 |
| Lammers 1986 | Gates on early habits | p.834 |
| Brooks 1995 | Machine to HLL gain | p.837 |
| Thomas 1984 | 10 maintenance generations | p.842 |
| Parikh and Zvegintzov 1983 | 50-60% time understanding | p.842 |
| Myers 1978b | Overlooking errors | p.850 |
