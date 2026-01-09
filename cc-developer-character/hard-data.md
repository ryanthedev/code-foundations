# Evidence: cc-developer-character

## Key Points

### Chapter 33 - Personal Character (p.819-835)

- [KEY POINT p.819] "Your personal character directly affects your ability to write computer programs."
- [KEY POINT p.821] "The characteristics that matter most are humility, curiosity, intellectual honesty, creativity and discipline, and enlightened laziness."
- [KEY POINT p.833] "The characteristics of a superior programmer have almost nothing to do with talent and everything to do with a commitment to personal development."
- [KEY POINT p.833] "Surprisingly, raw intelligence, experience, persistence, and guts hurt as much as they help."
- [KEY POINT p.834] "Good character is mainly a matter of having the right habits."

### Chapter 34 - Themes in Software Craftsmanship (p.853)

- [KEY POINT p.853] "One primary goal of programming is managing complexity."
- [KEY POINT p.853] "The programming process significantly affects the final product."
- [KEY POINT p.853] "Team programming is more an exercise in communicating with people than in communicating with a computer."
- [KEY POINT p.853] "Paying attention to intellectual warning signs like the 'irritation of doubt' is especially important in programming."
- [KEY POINT p.853] "The more you iterate in each development activity, the better the product will be."
- [KEY POINT p.853] "Dogmatic methodologies and high-quality software development don't mix."

## Empirical Findings

- [HARD DATA: Sackman, Erikson, Grant 1968; Curtis 1981; Mills 1983; DeMarco and Lister 1985; Curtis et al. 1986; Card 1987; Valett and McGarry 1989] "10:1 variation in programmer performance in time, debugging, size, speed, error rate, and errors detected."
  - Context: Multiple independent studies confirming large individual variation

- [HARD DATA: McCue 1978] "Only 30% of programmer time is spent working alone."
  - Context: Programming is primarily communication with people

- [HARD DATA: DeMarco and Lister 1999] "One book is more than most programmers read each year."
  - Context: Reading distinguishes professional programmers

- [HARD DATA: McGarry and Pajerski 1990] "Methods emphasizing human discipline have been especially effective." (NASA SEL 15-year retrospective)
  - Context: Discipline-focused methods outperform others

- [HARD DATA: Weimer in Metzger and Boddie 1996] "Technical people were good at estimating but bad at defending estimates."
  - Context: IBM's Bill Weimer on estimate negotiation

- [HARD DATA: Bill Gates, Lammers 1986] "Any programmer who will ever be good is good in the first few years."
  - Context: Habits form early; character development is time-sensitive

- [HARD DATA: Brooks 1995 p.837] "The biggest single gain in computer science was jump from machine language to higher-level languages."
  - Context: Abstraction as complexity management

- [HARD DATA: Thomas 1984 p.842] "10 generations of maintenance programmers work on an average program before rewrite."
  - Context: Code is read far more than written

- [HARD DATA: Parikh and Zvegintzov 1983 p.842] "Maintenance programmers spend 50-60% of time trying to understand code."
  - Context: Readability directly impacts productivity

- [HARD DATA: Myers 1978b p.850] "The single most common cause of not finding errors was simply overlooking them."
  - Context: Visible on output but not noticed; attention is crucial

## Anti-Patterns

- [ANTI-PATTERN: Burnout Pattern p.820] Working 6+ focused hours, then 3 more despite diminishing returns, requiring a week to fix the defects introduced during the 3-hour push.

- [ANTI-PATTERN: Uncooperative Programmer p.825] Code with variables x, xx, xxx, xx1, xx2 (all global, uncommented). Manager thought she was great because she "fixed errors quickly"—the poor code gave her abundant opportunities.

- [ANTI-PATTERN: Estimate Negotiation p.827] Bert estimates 8 programmers, 6 months. Manager asks for shorter. Bert "negotiates" to 6 programmers, 4 months. Result: loses credibility delivering in 6 months when promised 4.

- [ANTI-PATTERN: Ignoring Warnings p.826-827] People claim "clean compile," describe symptoms. Expert: "sounds like uninitialized pointer, but compiler should warn." Response: "Oh yeah—it did warn. We thought it meant something else."

- [ANTI-PATTERN: Gonzo Programming p.830] 16-hour days, all-nighters feel heroic but produce defects requiring weeks to fix. "Excitement is no substitute for competency."

- [ANTI-PATTERN: "Tricky Code" p.848] When code is described as "really tricky," that's a code phrase for "bad code." Rewrite it.
