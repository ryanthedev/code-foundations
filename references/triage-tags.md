# Triage Tags

Tag vocabulary for routing code changes to reviewers.

## Tag → Reviewer Mapping

| Tag | Reviewers |
|-----|-----------|
| `auth` | defensive |
| `validation` | defensive |
| `sanitize` | defensive |
| `injection` | defensive |
| `crypto` | defensive |
| `secrets` | defensive |
| `permissions` | defensive |
| `error-handling` | defensive |
| `catch` | defensive |
| `fallback` | defensive |
| `retry` | defensive, correctness |
| `async` | correctness |
| `concurrency` | correctness |
| `race` | correctness |
| `state` | correctness |
| `boundary` | correctness |
| `edge-case` | correctness |
| `null-check` | correctness |
| `logic` | correctness |
| `loop` | performance |
| `query` | performance |
| `cache` | performance |
| `batch` | performance |
| `memory` | performance |
| `io` | performance |
| `n-squared` | performance |
| `interface` | quality |
| `naming` | quality |
| `structure` | quality |
| `complexity` | quality |
| `cohesion` | quality |
| `coupling` | quality |
| `duplication` | quality |
| `comment` | documentation |
| `readme` | documentation |
| `docstring` | documentation |
| `api-doc` | documentation |
| `changelog` | documentation |

## Output Format

Triage outputs JSON array. Each chunk is an object:

```json
{
  "chunks": [
    {
      "file": "src/auth/login.ts",
      "lines": [15, 42],
      "description": "validates user input before DB query",
      "tags": ["validation", "injection"],
      "reviewers": ["defensive"]
    },
    {
      "file": "src/services/user.ts",
      "lines": [88, 95],
      "description": "retries failed API calls with backoff",
      "tags": ["retry", "async"],
      "reviewers": ["defensive", "correctness"]
    }
  ]
}
```

## Multi-Tag Examples

| Change Description | Tags | Routed To |
|--------------------|------|-----------|
| Validates user input before SQL query | `validation`, `injection`, `query` | defensive, performance |
| Adds retry with exponential backoff | `retry`, `error-handling`, `async` | defensive, correctness |
| Refactors loop to use batch processing | `loop`, `batch`, `structure` | performance, quality |
| New authentication middleware | `auth`, `interface`, `error-handling` | defensive, quality |
| Fixes race condition in cache invalidation | `race`, `cache`, `concurrency` | correctness, performance |

## Tag Selection Guidelines (Research-Backed)

1. **Max 3 tags per chunk** - Cognitive science: 3-4 items for active processing (Miller's Law revision)
2. **Pick the most specific tag** - `injection` over `validation` if SQL involved
3. **Consider the change, not the file** - A logging change in auth code is not `auth`
4. **When uncertain, over-tag** - Better to route to extra reviewer than miss one

**Why these constraints:**
- 3-4 active items is optimal for simultaneous processing (PMC NCBI cognitive research)
- 5 reviewer categories matches code review taxonomy research (Atlassian, Qt studies)
- JSON format provides 100% schema compliance vs legacy delimiters (Humanloop 2024)
