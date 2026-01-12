---
name: code-foundations
description: "Use when doing ANY code task - writing, debugging, reviewing, fixing, implementing, optimizing, or refactoring. Symptoms that trigger this skill include seeing code, being asked to implement something, fix a bug, review code, or improve performance. This skill dispatches to specific skills based on task type."
---

# Code Foundations

## DEFAULT: YES - Load This Skill

**When in doubt, load this skill. When NOT in doubt, load it anyway.**

The default answer to "does this need code-foundations?" is **YES**. The only exceptions are activities that:
1. Touch ZERO files that could ever be executed, compiled, or imported
2. Have ZERO chance of affecting runtime behavior, build, or tests
3. Are PURE prose (README content, not code comments)

## What This Skill Applies To

**Any file or change that affects runtime, build, or test behavior:**

| Category | Examples |
|----------|----------|
| **Code files** | `.js`, `.ts`, `.py`, `.go`, `.rs`, `.java`, `.c`, `.cpp`, `.rb`, `.swift`, `.kt`, `.sh`, `.sql` |
| **Config that affects runtime** | `.json`, `.yaml`, `.toml`, `.env`, `Dockerfile`, K8s manifests, nginx/Apache config |
| **Build/package files** | `package.json`, `Cargo.toml`, `requirements.txt`, `go.mod`, `Gemfile`, lockfiles |
| **Type definitions** | `.d.ts`, `.proto`, GraphQL schemas, OpenAPI specs |
| **Infrastructure as Code** | Terraform, Pulumi, CloudFormation, Ansible, docker-compose |
| **CI/CD** | GitHub Actions, GitLab CI, deployment scripts, git hooks |
| **Test artifacts** | Test files, fixtures, mocks, snapshots |
| **Any structural change** | File moves, renames, import changes, permission changes, symlinks |

**The ONLY things exempt:**
- Pure prose in documentation files (not code examples within them)
- Whitespace-only formatting by automated tools
- Git operations that don't touch files (branching, tagging, viewing history)
- Pure legal/administrative files (LICENSE, CODEOWNERS)

## STOP - Classify Before Acting

**You MUST classify the task before ANY other action.**

### Task Classification

| User Intent Signals | Task Type | INVOKE NEXT |
|---------------------|-----------|-------------|
| "implement", "write", "build", "add", "create" | WRITE | cc-developer-character → cc-construction-prerequisites |
| "debug", "fix bug", "failing", "broken", "error" | DEBUG | cc-developer-character → cc-quality-practices |
| "review", "check", "audit", "evaluate quality" | REVIEW | cc-quality-practices (CHECKER mode) |
| "optimize", "slow", "performance", "faster" | OPTIMIZE | cc-performance-tuning |
| "refactor", "clean up", "improve structure" | REFACTOR | cc-developer-character → cc-refactoring-guidance |
| "secure", "vulnerability", "validate input" | SECURE | cc-defensive-programming (CHECKER mode) |

**After classifying:** State the task type, then INVOKE the indicated skill(s).

### Ambiguous Requests

When the task type is unclear (e.g., "take a look at this code"):
1. **Ask clarifying questions** - "Are you looking for a review, debugging help, or something else?"
2. **After clarification, classify and continue the chain**

## cc-developer-character is NON-NEGOTIABLE

For WRITE, DEBUG, and REFACTOR tasks, you MUST invoke cc-developer-character FIRST.

**No exceptions for:**
- "Simple" tasks
- Tasks you've "done before"
- Time pressure
- Small codebases

## Red Flags - STOP If You Think This

These thoughts precede bugs. If you think any of these, load the skill anyway:

| Rationalization | Reality |
|-----------------|---------|
| "This is simple/trivial" | Simple tasks have HIGHEST error rates. "Trivial" changes cause production incidents. |
| "I can already see the issue" | Seeing ≠ systematic verification. |
| "I already know how to do this" | Knowing ≠ executing checklist. Experts make errors too. |
| "It's just config, not code" | Config that affects runtime IS code activity. |
| "The code already works" | Your CHANGE can break what worked. |
| "It's just a version bump/number change" | Single-field edits control database connections, API keys, versions. |
| "I'm just moving/renaming code" | Structural changes require updating ALL references. |
| "I'm just resolving merge conflicts" | Combining code paths IS writing new code. |
| "Someone already reviewed this" | Review validates design, not your implementation keystrokes. |
| "It's temporary for debugging" | "Temporary" changes that get committed become incidents. |
| "I'm just running npm install" | Package managers can modify lockfiles = different versions = different behavior. |
| "I'm just creating an empty file" | Empty files get compiled, can be imported, affect module resolution. |

**The pattern:** If you're constructing ANY argument for why this task is exempt, that argument IS the rationalization. Load the skill.

## Crisis Minimum (Time Pressure)

Production down? You STILL must:

1. **Classify the task** (5 seconds)
2. **State what you're skipping and why** (explicit)
3. **After crisis:** Return within 24 hours to apply full skill chain

**What you may NOT skip even in crisis:**
- Input validation on external data
- Verifying fix actually works
- One sentence explaining WHY the fix works

## Phase Skills (Chain After Classification)

| Task Type | Primary Skills | Follow-up Skills |
|-----------|----------------|------------------|
| WRITE | cc-construction-prerequisites → cc-pseudocode-programming | cc-routine-and-class-design (CHECKER), cc-defensive-programming (CHECKER) |
| DEBUG | cc-quality-practices (Scientific Method) | cc-refactoring-guidance (for the fix) |
| REVIEW | cc-quality-practices, cc-routine-and-class-design | cc-refactoring-guidance (if issues found) |
| OPTIMIZE | cc-performance-tuning | cc-refactoring-guidance (if structure degraded) |
| REFACTOR | cc-refactoring-guidance | cc-control-flow-quality (CHECKER), cc-routine-and-class-design (CHECKER) |
| SECURE | cc-defensive-programming | cc-data-organization (input validation) |

## Chain Completion

After completing primary skill work, invoke follow-up skills as CHECKER gates:

- **WRITE:** Before claiming "done", run cc-routine-and-class-design CHECKER and cc-defensive-programming CHECKER
- **DEBUG:** After identifying fix, invoke cc-refactoring-guidance for safe fix process
- **REVIEW:** If violations found, invoke cc-refactoring-guidance for fix recommendations
- **OPTIMIZE:** After changes, verify with cc-control-flow-quality that structure wasn't degraded
