# Checklists: aposd-optimizing-critical-paths

Source: A Philosophy of Software Design (Ousterhout), Chapter 20

---

## Stage 1: Measurement First (MANDATORY GATE)

- [ ] M-1: "Did I MEASURE existing system behavior (not just 'user said it's slow')?"
- [ ] M-2: "Did I IDENTIFY where the system spends most time (specific locations)?"
- [ ] M-3: "Did I ESTABLISH a baseline for comparison?"
- [ ] M-4: "Do I have actual profiling data (timing, call counts, memory usage)?"
- [ ] M-5: "Did I run multiple times to account for variance?"
- [ ] M-6: "Did I identify WHICH dimension is the problem (throughput, latency, memory, CPU)?"

---

## Measurement Validity

- [ ] MV-1: "Is this actual profiling data?" (Valid)
- [ ] MV-2: "Not just 'user said it's slow'?" (User perception ≠ bottleneck location)
- [ ] MV-3: "Not just pattern-matching to expensive operations table?" (Not profiling)
- [ ] MV-4: "Not just 'this is obviously expensive'?" (Intuition is unreliable)
- [ ] MV-5: "Not 'I'll measure after I make the change'?" (Confirmation bias)

---

## Stage 2: Fundamental Fixes (Preferred)

- [ ] FF-1: "Can I add a cache?"
- [ ] FF-2: "Can I use a different algorithm? (e.g., balanced tree vs list)"
- [ ] FF-3: "Can I bypass layers? (e.g., kernel bypass for networking)"
- [ ] FF-4: "If fundamental fix exists: am I implementing with standard design techniques?"
- [ ] FF-5: "If no fundamental fix: am I proceeding to critical path redesign?"

---

## Stage 3: Critical Path Redesign (Last Resort)

- [ ] CR-1: "What is the smallest amount of code for the common case?"
- [ ] CR-2: "Did I disregard existing code structure entirely?"
- [ ] CR-3: "Did I ignore special cases in current code?"
- [ ] CR-4: "Did I consider only data needed for critical path?"
- [ ] CR-5: "Did I choose the most convenient data structure?"
- [ ] CR-6: "Did I define 'the ideal' (simplest and fastest with complete redesign freedom)?"
- [ ] CR-7: "Did I design the rest of the class around these critical paths?"

---

## After Making Changes

- [ ] AM-1: "Did I RE-MEASURE to verify measurable performance difference?"
- [ ] AM-2: "Did changes provide significant speedup (with data)?" → Keep
- [ ] AM-3: "Did changes make system simpler AND at least as fast?" → Keep
- [ ] AM-4: "Neither speedup nor simpler?" → BACK THEM OUT

---

## Red Flags

- [ ] RF-1: "Death by Thousand Cuts?" - Many small inefficiencies everywhere (5-10x slower; no single fix helps)
- [ ] RF-2: "Pass-Through Methods?" - Method with identical signature to caller (layer crossing overhead)
- [ ] RF-3: "Shallow Layers?" - Multiple layers providing same abstraction (each call adds overhead)
- [ ] RF-4: "Repeated Special Cases?" - Same conditions checked multiple times (redundant work)
- [ ] RF-5: "Premature Optimization?" - Optimizing without measurement (complexity without verified benefit)
- [ ] RF-6: "Intuition-Based Changes?" - 'This should be faster' without data (unreliable even for experts)

---

## Consolidation Techniques

- [ ] CT-1: "Can I encode multiple conditions in single value?" (0 when any special case applies)
- [ ] CT-2: "Can I use single test for multiple cases?" (Replace 6 checks with 1)
- [ ] CT-3: "Can I combine layers into single method?" (Critical path in one method, not three)
- [ ] CT-4: "Can I merge variables?" (Combine multiple values into single structure)

---

## When to Optimize Immediately

- [ ] OI-1: "Is there clear evidence performance is critical?" → Implement faster approach now
- [ ] OI-2: "Does faster design add only small, hidden complexity?" → May be worthwhile
- [ ] OI-3: "Does faster design add lot of complexity OR complicate interfaces?" → Start simple, optimize later

---

Total items: 40
