# units.jsonl Specification

Version: 1.0
Status: Draft

---

## 1. Overview

### Purpose

`units.jsonl` is the central data model for code review. It represents **semantic units** (functions, methods, classes) extracted from changed files, enriched with metadata that enables:

1. **Intelligent batching** - Group related units for efficient parallel checking
2. **Check skipping** - Skip N/A checks based on unit characteristics (50+ checks avoided per unit)
3. **Context optimization** - 69% token savings via smart batching strategies

### How It Works

```
                                    ┌─────────────────┐
   git diff                         │  units.jsonl    │
      │                             │  ───────────    │
      ▼                             │  • identity     │
┌─────────────┐   tree-sitter       │  • change info  │
│ Changed     │ ────────────────►   │  • layer        │
│ Files       │   + LLM fallback    │  • visibility   │
└─────────────┘                     │  • signature    │
                                    │  • relations    │
                                    │  • behavior     │
                                    │  • I/O patterns │
                                    └────────┬────────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    │                        │                        │
                    ▼                        ▼                        ▼
           ┌───────────────┐       ┌─────────────────┐      ┌─────────────────┐
           │ Check Skipping│       │ Smart Batching  │      │ Context Budget  │
           │ ─────────────│        │ ─────────────── │      │ ──────────────  │
           │ no loops →   │        │ same dir        │      │ ~4k tokens/     │
           │   skip LOGIC │        │ test pairs      │      │   batch         │
           │ no async →   │        │ call graph      │      │ prioritize diff │
           │   skip SA-*  │        │ layer affinity  │      │ over full code  │
           └───────────────┘       └─────────────────┘      └─────────────────┘
```

---

## 2. Unit Model Schema

### JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["file", "name", "type", "lines", "diff", "summary"],
  "properties": {

    "file":           { "type": "string", "description": "Relative file path" },
    "name":           { "type": "string", "description": "Unit name (function/class/method name)" },
    "type":           { "type": "string", "description": "function | method | class | interface | test | arrow | generator" },
    "lines":          { "type": "array", "items": { "type": "integer" }, "minItems": 2, "maxItems": 2, "description": "[startLine, endLine] 1-indexed" },
    "containingType": { "type": "string", "description": "Parent class/interface name if method" },

    "changeStatus":   { "type": "string", "enum": ["added", "modified", "deleted"], "description": "Type of change" },
    "diff":           { "type": "string", "description": "Unified diff hunk for this unit" },
    "summary":        { "type": "string", "maxLength": 80, "description": "What changed (<10 words)" },
    "lineCount":      { "type": "integer", "description": "Total lines in unit (end - start + 1)" },

    "layer":          { "type": "string", "enum": ["api", "service", "domain", "data", "integration", "infra", "test", "config", "unknown"], "description": "Inferred from path" },

    "visibility":     { "type": "string", "enum": ["public", "private", "protected", "internal", "exported"], "description": "Access modifier" },
    "modifiers":      { "type": "array", "items": { "type": "string" }, "description": "async, static, abstract, final, arrow, decorated" },

    "params":         { "type": "string", "description": "Parameter signature string" },
    "paramCount":     { "type": "integer", "description": "Number of parameters" },
    "returnType":     { "type": "string", "description": "Return type annotation if present" },

    "calls":          { "type": "array", "items": { "type": "string" }, "description": "Function/method names called" },
    "implements":     { "type": "array", "items": { "type": "string" }, "description": "Interface names implemented" },

    "hasLoops":       { "type": "boolean", "default": false, "description": "Contains for/while/do-while" },
    "hasTryCatch":    { "type": "boolean", "default": false, "description": "Contains try-catch block" },
    "hasAsync":       { "type": "boolean", "default": false, "description": "Contains async/await/Promise" },
    "hasThrow":       { "type": "boolean", "default": false, "description": "Contains throw statement" },
    "hasRecursion":   { "type": "boolean", "default": false, "description": "Calls itself directly" },
    "nestingDepth":   { "type": "integer", "description": "Max control flow nesting depth" },

    "hasExternalInput": { "type": "boolean", "default": false, "description": "Reads from request/stdin/env/args" },
    "hasDatabaseCalls": { "type": "boolean", "default": false, "description": "Contains DB queries" },

    "contentHash":    { "type": "string", "description": "SHA256 of normalized source (catches duplication)" },

    "isTest":         { "type": "boolean", "default": false, "description": "Is a test function" },
    "testsUnit":      { "type": "string", "description": "Name of unit this test covers (if inferrable)" }
  }
}
```

### Field Reference

| Category | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| **Identity** | `file` | string | Yes | Relative file path |
| | `name` | string | Yes | Unit identifier |
| | `type` | string | Yes | Semantic type |
| | `lines` | [int, int] | Yes | Start/end lines (1-indexed) |
| | `containingType` | string | No | Parent class for methods |
| **Change** | `changeStatus` | enum | No | added/modified/deleted |
| | `diff` | string | Yes | Unified diff hunk |
| | `summary` | string | Yes | <10 word description |
| | `lineCount` | int | No | End - start + 1 |
| **Layer** | `layer` | enum | No | Inferred architectural layer |
| **Visibility** | `visibility` | enum | No | Access level |
| | `modifiers` | string[] | No | async, static, etc. |
| **Signature** | `params` | string | No | Parameter signature |
| | `paramCount` | int | No | Param count for complexity |
| | `returnType` | string | No | Return type if typed |
| **Relations** | `calls` | string[] | No | Outgoing calls |
| | `implements` | string[] | No | Implemented interfaces |
| **Behavior** | `hasLoops` | bool | No | Contains iteration |
| | `hasTryCatch` | bool | No | Contains error handling |
| | `hasAsync` | bool | No | Async patterns |
| | `hasThrow` | bool | No | Throws exceptions |
| | `hasRecursion` | bool | No | Self-referential |
| | `nestingDepth` | int | No | Max nesting level |
| **I/O** | `hasExternalInput` | bool | No | External data sources |
| | `hasDatabaseCalls` | bool | No | DB interactions |
| **Duplication** | `contentHash` | string | No | Normalized content hash |
| **Testing** | `isTest` | bool | No | Test function flag |
| | `testsUnit` | string | No | Tested unit name |

### Layer Inference Rules

| Path Pattern | Layer |
|-------------|-------|
| `**/api/**`, `**/routes/**`, `**/handlers/**`, `**/controllers/**` | api |
| `**/services/**`, `**/usecases/**`, `**/App/**` | service |
| `**/domain/**`, `**/models/**`, `**/entities/**`, `**/Core/**` | domain |
| `**/data/**`, `**/repositories/**`, `**/dal/**`, `**/persistence/**` | data |
| `**/adapters/**`, `**/providers/**`, `**/clients/**`, `**/gateways/**`, `**/external/**` | integration |
| `**/infra/**`, `**/infrastructure/**`, `**/middleware/**`, `**/extensions/**`, `**/hosting/**` | infra |
| `**/*.test.*`, `**/*.spec.*`, `**/tests/**`, `**/__tests__/**`, `**.Tests.**` | test |
| `**/config/**`, `**/constants/**`, `*.config.*` | config |
| (default) | unknown |

**Layer definitions:**
- **api** - HTTP endpoints, request/response handling
- **service** - Business logic, use cases, application services
- **domain** - Core business entities, value objects, domain logic
- **data** - Database access, repositories, persistence
- **integration** - External system adapters (APIs, message queues, third-party services)
- **infra** - Cross-cutting concerns (middleware, DI, logging, caching)
- **test** - Test files
- **config** - Configuration, constants

---

## 3. Check Skipping Matrix

Unit characteristics enable automatic skipping of inapplicable checks, reducing noise and agent cost.

### Characteristic-Based Skipping

| Characteristic | Skip These Check Prefixes | Rationale |
|---------------|--------------------------|-----------|
| `hasLoops: false` | LOGIC-1, NS-2, NS-4, LS-*, LE-*, LI-*, LX-* | No loops to check |
| `hasAsync: false` | SA-1, SA-2, SA-3, CONC-2, CONC-3 | No async/concurrency |
| `hasTryCatch: false` | EC-1, EC-2, EC-3, EH-1 to EH-4 | No exception handling |
| `hasThrow: false` | EC-1, EC-2 | No exceptions thrown |
| `hasRecursion: false` | LOGIC-6, NS-5 | No recursion to check |
| `hasDatabaseCalls: false` | PERF-1 | No N+1 query risk |
| `hasExternalInput: false` | SO-1, SM-1 to SM-6, GC-1 | No external input to validate |
| `isTest: true` | GC-3, GS-3, SM-* | Tests have different standards |
| `nestingDepth < 3` | NS-1, LI-6, EM-1 | Already within limits |
| `paramCount <= 7` | Param count checks | Already within limits |

### Estimated Savings

From analysis of 5 checklists (245 checks):
- Average unit skips **50+ checks** based on characteristics
- ~20% of all checks skippable for typical units
- Tests skip additional 15-20 checks (security/defensive checks)

### Example Skip Logic

```
Unit: createUser (function)
  hasLoops: false
  hasAsync: true
  hasTryCatch: true
  hasRecursion: false
  hasDatabaseCalls: true
  hasExternalInput: true

14 Core Checks Applied:
  ERR-3:   CHECK (has try-catch)
  ERR-8:   CHECK (has try-catch)
  NULL-2:  CHECK (always)
  NULL-4:  SKIP  (no loops → no array iteration)
  NULL-5:  SKIP  (no loops → no array iteration)
  NULL-6:  CHECK (always)
  LOGIC-1: SKIP  (no loops)
  LOGIC-6: SKIP  (no recursion)
  LOGIC-11: CHECK (always)
  LOGIC-15: CHECK (always)
  CONC-2:  CHECK (has async)
  CONC-3:  CHECK (has async)
  RES-1:   CHECK (always)
  PERF-1:  CHECK (has database calls)

Result: 10 checks run, 4 skipped (29% savings)
```

---

## 4. Batching Rules

Units are grouped into batches for parallel checking. Each batch goes to one checker agent.

### Priority Order

1. **Skip lockfiles and generated code** (never batch)
   - `*.lock`, `*-lock.json`
   - `*.generated.*`, `*.pb.*`, `*_generated.*`
   - `*.min.js`, `*.bundle.js`
   - `__snapshots__/*`, `vendor/*`, `node_modules/*`

2. **Keep test pairs together**
   - `foo.ts` + `foo.test.ts` → same batch
   - `UserService.java` + `UserServiceTest.java` → same batch

3. **Group by directory**
   - Units from same directory share imports/context
   - Reduces context tokens needed

4. **Group by call relationships**
   - If `A.calls` includes `B.name` → same batch
   - Enables cross-unit analysis

5. **Group by layer**
   - `api` layer units together
   - `service` layer units together
   - Same layer = similar check relevance

6. **Respect size limits**
   - Target ~4000 tokens of diff per batch
   - Split large units into own batch
   - Combine small units until limit

### Batching Algorithm

```
function createBatches(units):
  batches = []
  remaining = units.filter(not skippable)

  # Phase 1: Test pairs
  for unit in remaining where isTest:
    testedUnit = findUnit(unit.testsUnit)
    if testedUnit:
      batches.add([unit, testedUnit])
      remaining.remove(unit, testedUnit)

  # Phase 2: Call graph clusters
  clusters = clusterByCallGraph(remaining)
  for cluster in clusters where cluster.totalTokens < 4000:
    batches.add(cluster)
    remaining.remove(cluster.units)

  # Phase 3: Directory groups
  for dir in uniqueDirectories(remaining):
    dirUnits = remaining.filter(u => dirname(u.file) == dir)
    batches.add(...chunkByTokens(dirUnits, 4000))
    remaining.remove(dirUnits)

  # Phase 4: Remaining by layer
  for layer in ["api", "service", "domain", "data", "integration", "infra"]:
    layerUnits = remaining.filter(u => u.layer == layer)
    batches.add(...chunkByTokens(layerUnits, 4000))

  return batches
```

---

## 5. Context Budget

Each checking batch has a target context budget of ~4000 tokens.

### Token Allocation

| Content Type | Allocation | Notes |
|-------------|------------|-------|
| Checklist | ~500 tokens | Fixed per batch |
| Skill context | ~1000 tokens | 1-3 skills loaded |
| Unit diffs | ~2000 tokens | Primary analysis target |
| Source context | ~500 tokens | Surrounding lines when needed |
| **Total** | **~4000 tokens** | Per batch |

### Prioritization Within Budget

1. **Diff hunks** - Always include (primary analysis target)
2. **Unit signatures** - Always include (name, params, return type)
3. **Characteristics** - Always include (enables skip logic)
4. **Surrounding context** - Include for complex units (>50 lines)
5. **Full source** - Only on demand for investigation

### Token Estimation

```
Rough token estimates:
- 1 line of code ≈ 10 tokens
- 1 diff hunk line ≈ 12 tokens (includes +/- markers)
- Average function ≈ 200-400 tokens
- Average diff hunk ≈ 150 tokens

4000 token budget ≈ 25-30 small functions OR 5-8 medium functions
```

---

## 6. Implementation Tiers

### Tier 1: High Value, Easy (Implement First)

| Field | Extraction Method | Value |
|-------|------------------|-------|
| `file`, `name`, `type`, `lines` | tree-sitter AST | Core identity |
| `diff`, `summary` | git diff + LLM | Change context |
| `hasLoops`, `hasTryCatch`, `hasAsync` | tree-sitter patterns | Check skipping |
| `visibility`, `modifiers` | tree-sitter captures | Batching |
| `isTest` | Filename pattern | Test pairing |

**Estimated impact:** Enables 80% of check skipping, basic batching

### Tier 2: High Value, Moderate Effort

| Field | Extraction Method | Value |
|-------|------------------|-------|
| `layer` | Path pattern matching | Layer-based batching |
| `calls` | tree-sitter call captures | Call graph batching |
| `testsUnit` | Test naming conventions | Test pairing |
| `params`, `paramCount`, `returnType` | tree-sitter signature capture | Signature checks |
| `hasThrow`, `hasRecursion` | tree-sitter patterns | More skip rules |
| `nestingDepth` | tree-sitter depth counting | Complexity checks |

**Estimated impact:** Enables intelligent batching, 90% of skip logic

### Tier 3: Nice to Have

| Field | Extraction Method | Value |
|-------|------------------|-------|
| `contentHash` | Normalized source hash | Duplication detection |
| `hasExternalInput`, `hasDatabaseCalls` | Pattern matching + imports | Security check targeting |
| `implements` | tree-sitter inheritance | Interface compliance |
| `containingType` | tree-sitter parent scope | Method context |
| `changeStatus` | git diff analysis | Change-specific checks |
| `lineCount` | Arithmetic | Size-based batching |

**Estimated impact:** Edge cases, optimization

---

## 7. Examples

### Example 1: API Handler with Database Access

```json
{
  "file": "src/api/users/createUser.ts",
  "name": "createUser",
  "type": "function",
  "lines": [15, 67],
  "containingType": null,

  "changeStatus": "modified",
  "diff": "@@ -15,6 +15,20 @@\n async function createUser(req: Request) {\n+  const { email, name } = req.body;\n+  if (!email || !validateEmail(email)) {\n+    throw new ValidationError('Invalid email');\n+  }\n+  const user = await db.users.create({ email, name });",
  "summary": "Added email validation before user creation",
  "lineCount": 53,

  "layer": "api",

  "visibility": "exported",
  "modifiers": ["async"],

  "params": "req: Request",
  "paramCount": 1,
  "returnType": "Promise<User>",

  "calls": ["validateEmail", "db.users.create"],
  "implements": [],

  "hasLoops": false,
  "hasTryCatch": true,
  "hasAsync": true,
  "hasThrow": true,
  "hasRecursion": false,
  "nestingDepth": 2,

  "hasExternalInput": true,
  "hasDatabaseCalls": true,

  "contentHash": "a1b2c3d4e5f6...",

  "isTest": false,
  "testsUnit": null
}
```

**Skipped checks:** LOGIC-1, LOGIC-6, NS-2, NS-5, loop-related (no loops, no recursion)
**Applicable checks:** ERR-*, NULL-*, CONC-*, RES-1, PERF-1, SM-* (has async, try-catch, DB, external input)

### Example 2: Test Function

```json
{
  "file": "src/api/users/createUser.test.ts",
  "name": "should validate email before creation",
  "type": "test",
  "lines": [22, 35],
  "containingType": "createUser",

  "changeStatus": "added",
  "diff": "@@ -21,0 +22,14 @@\n+  it('should validate email before creation', async () => {\n+    const req = mockRequest({ body: { email: 'invalid' } });\n+    await expect(createUser(req)).rejects.toThrow(ValidationError);",
  "summary": "Added test for email validation",
  "lineCount": 14,

  "layer": "test",

  "visibility": "private",
  "modifiers": ["async"],

  "params": "",
  "paramCount": 0,
  "returnType": "Promise<void>",

  "calls": ["mockRequest", "createUser", "expect"],
  "implements": [],

  "hasLoops": false,
  "hasTryCatch": false,
  "hasAsync": true,
  "hasThrow": false,
  "hasRecursion": false,
  "nestingDepth": 1,

  "hasExternalInput": false,
  "hasDatabaseCalls": false,

  "contentHash": "f6e5d4c3b2a1...",

  "isTest": true,
  "testsUnit": "createUser"
}
```

**Batching:** Paired with `createUser` function in same batch
**Skipped checks:** All security (SM-*), defensive (GC-3, GS-3), most error handling (test code)

### Example 3: Domain Entity (Simple)

```json
{
  "file": "src/domain/entities/User.ts",
  "name": "User",
  "type": "class",
  "lines": [5, 28],
  "containingType": null,

  "changeStatus": "modified",
  "diff": "@@ -10,3 +10,8 @@\n   email: string;\n+  createdAt: Date;\n+  updatedAt: Date;",
  "summary": "Added timestamp fields to User entity",
  "lineCount": 24,

  "layer": "domain",

  "visibility": "exported",
  "modifiers": [],

  "params": "",
  "paramCount": 0,
  "returnType": null,

  "calls": [],
  "implements": ["Entity"],

  "hasLoops": false,
  "hasTryCatch": false,
  "hasAsync": false,
  "hasThrow": false,
  "hasRecursion": false,
  "nestingDepth": 0,

  "hasExternalInput": false,
  "hasDatabaseCalls": false,

  "contentHash": "1a2b3c4d5e6f...",

  "isTest": false,
  "testsUnit": null
}
```

**Skipped checks:** Nearly all behavioral checks (no loops, async, try-catch, recursion, I/O)
**Applicable checks:** Basic null checks, interface compliance
**Batching:** Grouped with other domain entities

---

## Appendix: JSONL Format

Each line in `units.jsonl` is a single JSON object (no array wrapper):

```jsonl
{"file":"src/api/users/createUser.ts","name":"createUser","type":"function","lines":[15,67],"diff":"@@ -15,6 +15,20 @@...","summary":"Added email validation","hasLoops":false,"hasAsync":true,"hasTryCatch":true}
{"file":"src/api/users/createUser.test.ts","name":"should validate email","type":"test","lines":[22,35],"diff":"@@ -21,0 +22,14 @@...","summary":"Added test","isTest":true,"testsUnit":"createUser"}
```

Benefits:
- Stream processing (no need to load entire file)
- Append-only writes (agents can add units incrementally)
- Easy grep/jq filtering
