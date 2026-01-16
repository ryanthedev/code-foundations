---
name: prototype
description: "Quick proof-of-concept to validate an idea with minimum code. Use when asking 'can I do X?' before committing to full implementation. Triggers on: prototype, POC, prove this works, quick hack, spike, demo this, can I do X. Produces surgical code that informs production design."
---

# Skill: prototype

**Prove it works. Minimum code. Maximum learning.**

---

## Quick Reference

| Phase | Goal | Output |
|-------|------|--------|
| SCOPE | One thing to prove | Single question |
| CONTEXT | Environment check | Available APIs/tools |
| MINIMUM | Shortest path | Surgical approach |
| EXECUTE | Write clean POC code | Working prototype |
| VERIFY | Did it work? | Yes/No + learnings |
| CAPTURE | Document for production | Prototype log |

---

## Philosophy

**This is NOT production code. This code INFORMS production code.**

| Prototype IS | Prototype is NOT |
|--------------|------------------|
| Proving feasibility | Building the feature |
| Finding the minimum path | Over-engineering |
| Learning constraints | Handling all edge cases |
| Surgical and focused | Comprehensive |
| Disposable but informative | Throwaway spaghetti |

**Key insight:** Write the cleanest minimum. Messy prototypes teach nothing because you can't tell if the mess is the problem or the approach.

---

## Crisis Invariants - NEVER SKIP

| Check | Why Non-Negotiable |
|-------|-------------------|
| **One thing to prove** | Multiple goals = nothing proven |
| **Minimum code only** | Extra code obscures what actually matters |
| **Clean over fast** | Messy prototype = unclear learnings |
| **Capture learnings** | Prototype without documentation = wasted effort |
| **Stay on branch** | Even POC code shouldn't pollute main |

---

## Phase 1: SCOPE (One Question Only)

### The Single Question

Ask: **"What ONE thing are you trying to prove?"**

Good scope:
- "Can I show a system notification using this API?"
- "Can I read from this database with these credentials?"
- "Can I render a window with this framework?"

Bad scope (too broad):
- "Can I build a notification system?" → Too much
- "Can I integrate with the backend?" → Too vague
- "Can I make it work?" → What is "it"?

### Narrow Until Atomic

If scope is too broad, ask:
- "What's the FIRST thing that needs to work for this to be possible?"
- "If you could only prove ONE capability, which one?"
- "What's the smallest thing that would give you confidence to proceed?"

**Output:** One sentence starting with "Can I..."

---

## Phase 2: CONTEXT (Environment Check)

### Quick Assessment

```
1. Where does this code live?
   - [ ] Existing repo (which one?)
   - [ ] New repo/scratch
   - [ ] Standalone script

2. What's already available?
   - [ ] Existing APIs/libraries in the codebase
   - [ ] External dependencies to install
   - [ ] Nothing - starting fresh

3. What constraints exist?
   - [ ] Must use specific language/framework
   - [ ] Must integrate with existing code
   - [ ] No constraints - pure exploration
```

### Reconnaissance (If Existing Repo)

```bash
# What's here?
ls -la
cat package.json  # or equivalent
```

**INVOKE aposd-reviewing-module-design** (light touch):
- What modules exist that might help?
- What patterns does this codebase use?
- What's the simplest integration point?

**Output:** 2-3 sentences on environment and available tools.

---

## Phase 3: MINIMUM (Shortest Path)

### The Minimum Path Question

Ask yourself: **"What is the absolute minimum code to answer the SCOPE question?"**

**INVOKE cc-pseudocode-programming** (abbreviated):
1. Write 3-5 lines of pseudocode for the happy path ONLY
2. No error handling in pseudocode (this is POC)
3. No edge cases (prove the concept first)

### Minimum Path Checklist

- [ ] Can I use an existing function/API? (Don't write what exists)
- [ ] Can I hardcode values? (Don't parameterize yet)
- [ ] Can I skip validation? (Trust input for POC)
- [ ] Can I use the simplest approach? (Not the "right" approach)
- [ ] What can I delete from my mental plan?

### Anti-Scope-Creep Gate

Before proceeding, verify:
- Does this code ONLY answer the SCOPE question?
- Am I adding anything "while I'm here"?
- Is there anything I can remove and still prove the concept?

**If you're writing more than ~50 lines, STOP.** Re-scope or break into smaller POC.

---

## Phase 4: EXECUTE (Surgical Code)

### Branch First

```bash
git checkout -b prototype/<scope-slug>
```

### Write with Discipline

Even though this is POC, use skills to keep it clean:

**INVOKE cc-pseudocode-programming:**
- Pseudocode → Code (even for 20 lines)
- Clear names (you'll read this later)
- One file if possible

**Light quality checks (NOT full gates):**
- Does the code match the pseudocode?
- Could someone else understand what this proves?
- Is there any code that doesn't serve the SCOPE?

### What Clean POC Looks Like

```javascript
// PROTOTYPE: Can I show a system notification?
// SCOPE: Prove notification API works on macOS
// NOT PRODUCTION: No error handling, hardcoded values

const { Notification } = require('electron');

// Minimum: just show it works
const notification = new Notification({
  title: 'POC Test',
  body: 'If you see this, notifications work'
});

notification.show();
// Result: [describe what happened]
```

**Notice:**
- Comment states what this proves
- Explicit "NOT PRODUCTION" marker
- No error handling (intentional for POC)
- Space for result annotation

---

## Phase 5: VERIFY (Did It Work?)

### Binary Answer

The SCOPE question must have a YES or NO answer:

| Result | Meaning |
|--------|---------|
| **YES** | Concept is feasible. Proceed to learnings. |
| **NO** | Concept blocked. Document why. |
| **PARTIAL** | Refine scope. What specifically worked/didn't? |

### If YES - Capture What Worked

- What was the minimum code that worked?
- Any surprises in the API/behavior?
- What would production version need to handle?

### If NO - Capture the Blocker

- What specifically failed?
- Is it a fundamental blocker or solvable?
- Alternative approaches to try?

### If PARTIAL - Narrow Scope

- Split into smaller SCOPE questions
- Run another prototype for the unclear part

---

## Phase 6: CAPTURE (Document for Production)

### Prototype Log

Create or append to `docs/prototypes/YYYY-MM-DD-<scope>.md`:

```markdown
# Prototype: [Scope Question]

**Date:** YYYY-MM-DD
**Branch:** prototype/<scope-slug>
**Result:** YES / NO / PARTIAL

## What We Proved

[1-2 sentences on what was demonstrated]

## Minimum Working Code

```[language]
[the actual working code - keep it minimal]
```

## Key Learnings

- [API behavior discovered]
- [Constraints found]
- [Surprises]

## Production Considerations

- [ ] Error handling needed for: [list]
- [ ] Edge cases to handle: [list]
- [ ] Integration points: [list]
- [ ] Estimated complexity: [simple/medium/complex]

## Next Steps

- [ ] If proceeding: `/whiteboarding` with these learnings
- [ ] If blocked: [alternative to explore]
- [ ] If more POC needed: [next scope question]
```

### Link to Future Work

The prototype log becomes input for `/whiteboarding`:
- Proven: What we know works
- Constraints: What we discovered
- Complexity: Informed estimate

---

## Anti-Rationalization Table

| Rationalization | Reality |
|-----------------|---------|
| "I'll just add error handling quick" | Error handling is production work. Prove concept first. |
| "Let me make it configurable" | Hardcode for POC. Configuration is production work. |
| "I should handle this edge case" | Edge cases are production work. Happy path only. |
| "This is messy but it works" | Messy POC = unclear learnings. Clean it. |
| "I'll remember what I learned" | You won't. Write the prototype log. |
| "It mostly works, close enough" | PARTIAL is not YES. Be precise about what worked. |
| "Let me refactor this prototype" | If it proves the concept, STOP. Refactoring is production. |
| "I need more features to really prove it" | Scope creep. One thing. Prove that one thing. |
| "I'll document later" | You won't. Capture learnings while they're fresh. |
| "This is throwaway, doesn't need a branch" | Prototypes on main = pollution. Branch always. |

---

## Pressure Testing Scenarios

### Scenario 1: Scope Creep

**Situation:** You're proving notification works, and think "let me also test if I can customize the icon."

**Response:** STOP. That's a second SCOPE question. Finish current POC, capture learnings, then start new prototype for icon customization.

### Scenario 2: It Works But It's Ugly

**Situation:** The prototype works but the code is hard to follow.

**Response:** Clean it. Ugly POC = unclear learnings. You're not optimizing for speed, you're optimizing for learning. Take 5 minutes to make it readable.

### Scenario 3: Rabbit Hole

**Situation:** The API doesn't work as expected. You've spent 30 minutes debugging.

**Response:** STOP. Capture what you learned. The POC answer might be "NO - blocked by [issue]". That's valuable information. Don't turn POC into full investigation.

### Scenario 4: It Works, Now What?

**Situation:** Prototype succeeds. You're tempted to keep building.

**Response:** STOP. Capture learnings in prototype log. If you want to build the full feature, use `/whiteboarding` with the prototype learnings as input. Don't evolve POC into production.

---

## Workflow Integration

```
/prototype "can I show a notification?"
  ↓
[Prove concept - minimum code]
[Capture learnings]
  ↓
/whiteboarding "build notification system"
  ↓
[Discovery questions - informed by prototype]
[Approaches - knowing what works]
  ↓
/building
  ↓
[Production implementation]
```

**Prototype feeds whiteboarding:**
- Proven capabilities
- Known constraints
- Realistic complexity estimates

---

## Chaining

- **RECEIVES FROM:** User question, feature idea, technical uncertainty
- **CHAINS TO:** whiteboarding (with prototype learnings), or another prototype
- **SKILLS USED:** cc-pseudocode-programming (light), aposd-reviewing-module-design (reconnaissance)
- **RELATED:** oberhack, spike, technical investigation
