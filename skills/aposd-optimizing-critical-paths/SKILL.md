---
name: aposd-optimizing-critical-paths
description: "Use when code is 'too slow', needs 'optimization', has performance issues, 'takes forever', 'hangs', 'laggy', timeouts, OOM errors, high CPU/memory, or 'doesn't scale'. Emphasizes measure-first approach. Very similar to cc-performance-tuning."
---

# Skill: aposd-optimizing-critical-paths

## Metadata
Source: A Philosophy of Software Design (Ousterhout)
Chapter: 20
Key Point Anchor: "Before making any changes, measure the system's existing behavior."
Skill Type: APPLIER
APOSD Foundation: simplicity-performance relationship
CC Complement: cc-performance-tuning (very similar—both emphasize measure-first)

## Overview

**Core Principle:** Clean design and high performance are compatible. Simpler code usually runs faster because there are fewer special cases to check and fewer layer crossings.

**Key Insight:** Don't optimize based on intuition—measure first. Intuitions about performance are unreliable, even for experienced developers.

## When to Use

- Code is "too slow" or has performance issues
- Optimizing hot paths or critical sections
- Analyzing system bottlenecks
- Choosing between equally clean alternatives
- **Symptom keywords:** "optimize", "make faster", "too slow", "performance", "bottleneck", "takes forever", "hangs", "laggy", "timeout", "OOM", "memory issues", "high CPU", "doesn't scale"

## When NOT to Use

- Creating new modules (see: aposd-designing-deep-modules)
- Evaluating design quality (see: aposd-reviewing-module-design)
- Simplifying without performance focus (see: aposd-simplifying-complexity)
- Improving clarity (see: aposd-improving-code-clarity)
- Modifying behavior (see: aposd-maintaining-design-quality)

---

## The Simplicity-Performance Relationship

| Myth | Reality |
|------|---------|
| "Performance requires complexity" | Simpler code usually runs faster |
| "Clean design sacrifices speed" | Clean design and high performance are compatible |
| "Optimization means adding code" | Optimization often means removing code |

**Why simplicity improves performance:**
- Fewer special cases = no code to check for those cases
- Deep classes = more work per call, fewer layer crossings
- Each layer crossing adds overhead
- Complicated code does extraneous or redundant work

---

## Expensive Operations Reference

Know these costs when choosing between alternatives:

| Operation | Cost | Context |
|-----------|------|---------|
| Network (datacenter) | 10–50 μs | Tens of thousands of instructions |
| Network (wide-area) | 10–100 ms | Millions of instructions |
| Disk I/O | 5–10 ms | Millions of instructions |
| Flash storage | 10–100 μs | Thousands of instructions |
| Dynamic memory allocation | Significant | malloc/new, freeing, GC overhead |
| Cache miss | Few hundred cycles | Often determines overall performance |

---

## Performance Optimization Workflow

### Stage 1: Measurement First (MANDATORY GATE)

```
BEFORE making any performance changes:

1. MEASURE existing system behavior
   - Where does the system spend most time?
   - Not just "system is slow" — identify specific locations

2. IDENTIFY small number of very specific places
   - With ideas for improvement
   - Focus on what matters most

3. ESTABLISH baseline
   - You'll need this to verify improvements
```

**What counts as valid measurement:**
- Actual profiling data (timing, call counts, memory usage)
- Multiple runs to account for variance
- Specific hotspot identification, not just "it's slow"

**What does NOT count:**
- "User said it's slow" (user perception ≠ bottleneck location)
- Pattern-matching to Expensive Operations table
- "This is obviously expensive" (intuition)
- "I'll measure after I make the change" (confirmation bias)

**⚠️ Stage 1 is a GATE, not a suggestion.** You cannot proceed to Stage 2 without completing measurement.

**Performance Dimensions:**
When measuring, identify WHICH dimension is the problem:
- **Throughput:** Operations per second
- **Latency:** Time per operation
- **Memory:** Peak/average usage, allocation rate
- **CPU:** Utilization percentage

Different problems require different solutions.

### Stage 2: Look for Fundamental Fixes

```
FIRST, check for fundamental fixes (preferred over code tweaks):

□ Can you add a cache?
□ Can you use a different algorithm? (e.g., balanced tree vs. list)
□ Can you bypass layers? (e.g., kernel bypass for networking)

IF fundamental fix exists → implement using standard design techniques
IF NOT → proceed to critical path redesign
```

### Stage 3: Critical Path Redesign (Last Resort)

```
ONLY when no fundamental fix is available:

1. ASK: What is the smallest amount of code for the common case?

2. DISREGARD existing code structure entirely
   - Imagine writing a new method that implements JUST the critical path

3. IGNORE special cases in current code
   - Consider only data needed for critical path
   - Choose most convenient data structure

4. DEFINE "the ideal"
   - The simplest and fastest code assuming complete redesign freedom
   - Even if not practically achievable, it's your target

5. DESIGN the rest of the class around these critical paths
```

---

## After Making Changes

```
1. RE-MEASURE to verify measurable performance difference

2. EVALUATE the tradeoff:
   - Did changes provide significant speedup (with data)? → Keep
   - Did changes make system simpler AND at least as fast? → Keep
   - Neither? → BACK THEM OUT
```

**⚠️ "Simpler" alone is not enough.** You must verify the simpler version is at least as fast.

---

## Anti-Rationalization Table

| Rationalization | Counter |
|-----------------|---------|
| "User said it's slow, that's my measurement" | User perception ≠ bottleneck location. Measure to find WHERE. |
| "Looking at the table, this is obviously expensive" | Pattern-matching isn't profiling. Measure actual time. |
| "I'll make the change then measure to verify" | Confirmation bias. Measure FIRST to find the real bottleneck. |
| "Setting up profiling is too complex" | If you can't measure, you can't verify improvement. Do the work. |
| "This scope is too small to measure" | Micro-optimizations without measurement add complexity for nothing. |
| "I checked the fundamental fix checklist" | Checklist is for ideas AFTER measurement shows the bottleneck. |
| "The code is simpler now, so it's faster" | Simpler doesn't automatically mean faster. Verify with measurement. |
| "I found a red flag pattern" | Red flags are descriptive, not prescriptive. Measure if it's actually slow. |
| "I already profiled extensively" | Share the data. Without data, it's still intuition. |

---

## Red Flags

| Red Flag | Symptom | Performance Impact |
|----------|---------|-------------------|
| **Death by Thousand Cuts** | Many small inefficiencies everywhere | System 5–10x slower; no single fix helps |
| **Pass-Through Methods** | Method with identical signature to caller | Unnecessary layer crossing overhead |
| **Shallow Layers** | Multiple layers providing same abstraction | Each call adds overhead |
| **Repeated Special Cases** | Same conditions checked multiple times | Redundant work on every call |
| **Premature Optimization** | Optimizing without measurement | Adds complexity without verified benefit |
| **Intuition-Based Changes** | "This should be faster" without data | Unreliable even for experts |

---

## Performance-Aware Development

**Default approach during normal development:**

1. Develop awareness of fundamentally expensive operations
2. Choose naturally efficient alternatives when equally clean options exist
3. If performance turns out to be a problem, optimize later
4. **Exception:** Clear evidence performance is critical → implement faster approach immediately

### When to Optimize Immediately

| Situation | Action |
|-----------|--------|
| Clear evidence performance is critical | Implement faster approach now |
| Faster design adds only small, hidden complexity | May be worthwhile |
| Faster design adds lot of complexity OR complicates interfaces | Start simple, optimize later |

---

## Consolidation Techniques

When optimizing critical paths, look for ways to consolidate:

| Technique | Example |
|-----------|---------|
| **Encode multiple conditions in single value** | Variable that is 0 when any of several special cases apply |
| **Single test for multiple cases** | Replace 6 individual checks with 1 combined check |
| **Combine layers into single method** | Critical path handled in one method, not three |
| **Merge variables** | Combine multiple values into single structure |

---

## Quick Reference

```
PERFORMANCE OPTIMIZATION PRIORITY:

1. MEASURE (MANDATORY GATE)
   - Actual profiling data, not intuition
   - Identify which dimension: throughput, latency, memory, CPU
   - Establish baseline before any changes
   - No measurement = no optimization

2. FUNDAMENTAL FIX - Preferred approach
   - Cache? Better algorithm? Bypass layers?
   - Only consider AFTER measurement shows the bottleneck

3. CRITICAL PATH - Last resort
   - What's the minimum code for common case?
   - Disregard existing structure
   - Define "the ideal"

4. VERIFY - After changes
   - Re-measure with same methodology
   - Faster with data? Keep
   - Simpler AND at least as fast? Keep
   - Neither? BACK OUT

THE RULE:
Measure → Identify → Fix → Verify
Never skip steps. Never assume.
```

---

## Chaining

- **Complements:** cc-performance-tuning (very similar—both measure-first)
- **Follow-ons:** aposd-reviewing-module-design (verify design didn't degrade)

## References
- Foundations: [aposd-foundations.md](../../references/aposd-foundations.md)
- CC complement: cc-performance-tuning (similar approach, different framing)
