# Pattern Reuse Gate

**Mandatory checkpoint before implementing any fix, feature, or refactor.**

> "The best code is code you don't have to write because it already exists." —McConnell (paraphrased)

---

## The Gate

**BEFORE writing any implementation code, answer:**

```
1. SEARCH: How is this done elsewhere in this codebase?
   - Search for similar functionality
   - Check same directory, same module, related files
   - Look for naming conventions, error patterns, data structures

2. IDENTIFY: What patterns exist?
   - Is there an established way to do this?
   - Are there helper functions, utilities, base classes?
   - What conventions are followed?

3. DECIDE: Follow or diverge?
   - IF pattern exists AND is good → FOLLOW IT
   - IF pattern exists AND is bad → DOCUMENT why you're diverging
   - IF no pattern exists → You're establishing one; be deliberate
```

**Do NOT proceed to implementation until this gate passes.**

---

## Search Checklist

| Search | Command/Action |
|--------|----------------|
| Similar functionality | `grep -r "similar_keyword"` or IDE search |
| Same error type | Search for existing error handling of this type |
| Same data structure | How are similar objects created/modified? |
| Same UI pattern | How do other components handle this? |
| Same API pattern | How do other endpoints structure this? |

### Search Quality Requirements

**Minimum viable search (all required):**
1. Search the ENTIRE codebase, not just current directory
2. Use at least 3 different keyword variations
3. Check files in same module/package
4. Look at recent git history for similar changes

**"No results" is suspicious.** If you genuinely find nothing:
- Try broader terms (not `handleUserAuthRetry`, try `error handling`)
- Search for the PROBLEM, not your planned SOLUTION
- Ask a teammate if you're missing something

---

## Decision Matrix

| Situation | Action |
|-----------|--------|
| Pattern exists, is good | **Follow it exactly.** Copy structure, naming, style. |
| Pattern exists, is mediocre | **Follow it anyway** unless actively harmful. Consistency > perfection. |
| Pattern exists, is bad | **Document divergence.** Note why in commit/comment. Consider fixing pattern globally later. |
| No pattern exists | **You're setting precedent.** Be extra careful. This becomes the pattern. |
| Multiple conflicting patterns | **Pick the better one.** Note which and why. Consider consolidating later. |

---

## Red Flags - STOP If You Notice

- Urge to "just implement it my way"
- Skipping search because "I already know how to do this"
- Assuming no patterns exist without searching
- Dismissing existing patterns as "not quite right"
- Creating a new utility when one exists
- Using different naming conventions than surrounding code

---

## Anti-Rationalization Table

| Excuse | Reality |
|--------|---------|
| "I know how to do this better" | Consistency beats local optimization. Follow the pattern. |
| "The existing pattern is slightly different" | Adapt to it. Small differences compound into chaos. |
| "There's no time to search" | 2 minutes searching saves 20 minutes debugging inconsistency. |
| "I'll establish a better pattern" | New patterns need team buy-in. Follow existing unless truly broken. |
| "My way is more modern/idiomatic" | Codebase consistency > language idioms. Match the codebase. |
| "I already searched (in my head)" | Actually search. Memory is unreliable. |
| "This is a special case" | Special cases should still follow patterns where possible. |
| "The pattern doesn't cover this exact scenario" | Extend the pattern, don't invent a parallel one. |
| "I searched but didn't find anything" | Search harder with different keywords. Use broader terms. |
| "This is greenfield code" | Even new projects have patterns emerging. Match early conventions. |
| "I'll search after I get it working" | That's backwards. Search BEFORE implementation, not after. |
| "I found multiple patterns, picked best" | Document which and why. "Best" without justification is cherry-picking. |
| "The pattern has tech debt" | Debt isn't license for MORE inconsistency. Follow or fix globally. |
| "I'm the only one on this module" | Future you is different. Consistency helps your future self. |

---

## Examples

### Example 1: Adding Error Handling

**BAD (skipped gate):**
```python
# Just wrote what seemed right
try:
    result = api.call()
except Exception as e:
    print(f"Error: {e}")
    return None
```

**GOOD (passed gate):**
```python
# Searched: "except" in this module
# Found: All errors use logger.error() and raise custom exceptions
# Following that pattern:
try:
    result = api.call()
except APIError as e:
    logger.error(f"API call failed: {e}", exc_info=True)
    raise ServiceError(f"Failed to fetch data: {e}") from e
```

### Example 2: Adding a New Component

**BAD (skipped gate):**
```tsx
// Just created what I thought was needed
function UserCard({ user }) {
  return <div className="user-card">...</div>
}
```

**GOOD (passed gate):**
```tsx
// Searched: Other card components in components/
// Found: All cards use Card base component, follow naming pattern
// Following that pattern:
import { Card } from './Card'

export function UserCard({ user }: UserCardProps) {
  return <Card variant="user">...</Card>
}
```

### Example 3: Fixing a Bug

**BAD (skipped gate):**
```javascript
// Just fixed the immediate issue
if (value === null) {
  value = defaultValue
}
```

**GOOD (passed gate):**
```javascript
// Searched: How null checks are done elsewhere
// Found: Codebase uses nullish coalescing consistently
// Following that pattern:
value = value ?? defaultValue
```

---

## Integration Points

This gate is referenced by:
- `cc-debugging` - Before forming hypothesis, check how similar bugs were fixed
- `cc-defensive-programming` - Before adding error handling, check existing patterns
- `cc-refactoring-guidance` - Before refactoring, identify target patterns
- `code-foundations` dispatcher - All implementation tasks pass through this gate

---

## Workflow Position

```
TASK RECEIVED
     │
     ▼
┌─────────────────────┐
│  PATTERN REUSE GATE │  ◄── YOU ARE HERE
│  1. Search          │
│  2. Identify        │
│  3. Decide          │
└─────────────────────┘
     │
     ▼
PROCEED TO IMPLEMENTATION
(following identified patterns)
```
