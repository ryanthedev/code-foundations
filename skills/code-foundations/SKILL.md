---
name: code-foundations
description: Use when doing ANY code task - writing, debugging, reviewing, fixing,
  implementing, optimizing, or refactoring. Symptoms that trigger this skill include
  seeing code, being asked to implement something, fix a bug, review code, or improve
  performance. This skill dispatches to specific skills based on task type.
---

## First Action

**Execute immediately:**
```bash
python3 ~/.claude/bin/log-skill-load.py code-foundations
```

# Code Foundations

## DEFAULT: YES - Load This Skill

**When in doubt, load this skill. When NOT in doubt, load it anyway.**

The default answer to "does this need code-foundations?" is **YES**. The only exceptions are activities that:
1. Touch ZERO files that could ever be executed, compiled, or imported
2. Have ZERO chance of affecting runtime behavior, build, or tests
3. Are PURE prose (README content, not code comments)

**If you're asking yourself "does this need the skill?"** — the answer is YES. The question itself proves you're touching something that could matter.

**If you think "this is obviously exempt"** — you're rationalizing. Load the skill. Let IT decide if it's exempt.

**The skill applies to:**
- ANY file with code (`.js`, `.ts`, `.py`, `.go`, `.rs`, `.java`, `.c`, `.cpp`, `.rb`, `.swift`, `.kt`, etc.)
- ANY config file that affects runtime (`.json`, `.yaml`, `.toml`, `.env`, `.xml`, `Dockerfile`, etc.)
- ANY build/package file (`package.json`, `Cargo.toml`, `requirements.txt`, `pom.xml`, etc.)
- ANY change to file location, name, or structure
- ANY change to imports, exports, or module boundaries
- ANY comment that might be parsed (JSDoc, docstrings, type hints in comments)
- ANY lockfile regeneration (`package-lock.json`, `yarn.lock`, `Cargo.lock`, `poetry.lock`, etc.)
- ANY file permission change (chmod affects whether code can execute)
- ANY symlink creation or modification (affects what code/config is loaded)
- ANY new file creation, even empty files (empty `.ts` files get compiled)
- ANY file deletion (verify it's actually unused before deleting)
- ANYTHING you're about to commit

**The ONLY things exempt:**
- Pure prose in documentation files (not code examples within them)
- Whitespace-only formatting by automated tools (not manual formatting)
- Git operations that don't touch files (branching, tagging, viewing history)
- Pure legal/administrative files (LICENSE, CODEOWNERS, CONTRIBUTING.md)

**NOT exempt (these affect what code exists or how it's processed):**
- `.gitignore` - wrong patterns exclude source files or include secrets
- `.gitattributes` - affects line endings, merge drivers, diff behavior
- Any file that affects what files are in the repo or how they're processed
- `npm install` / `pip install` / any package manager command - can modify lockfiles, change dependency versions
- `chmod` / permission changes - affects whether scripts can execute
- Symlink operations - affects what code/config is actually loaded at runtime
- Creating new files (even empty ones) - they become part of the codebase and may be compiled/imported

**When you rationalize, you violate.** The skill exists because your confidence is wrong.

## STOP - Classify Before Acting

**You MUST classify the task before ANY other action.**

Do NOT:
- Start analyzing the code
- Start writing a solution
- Say "Let me look at this"
- Skip to a specific skill you "already know" is right

**Classification is mandatory. No exceptions.**

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

1. **Load code-foundations FIRST** (you already did - you're reading this)
2. **Then ask clarifying questions** - "Are you looking for a review, debugging help, or something else?"
3. **After clarification, classify and continue the chain**

**WRONG order:** Ask questions → then load skills
**RIGHT order:** Load code-foundations → ask questions → classify → invoke chain

The skill comes BEFORE clarification because the skill tells you HOW to clarify.

## cc-developer-character is NON-NEGOTIABLE

For WRITE, DEBUG, and REFACTOR tasks, you MUST invoke cc-developer-character FIRST.

**Why:** Baseline testing showed agents skip mindset checks and rationalize "I already know how to do this." The skill exists because knowing and doing are different.

**No exceptions for:**
- "Simple" tasks
- Tasks you've "done before"
- Time pressure
- Small codebases

## Red Flags - STOP If You Think This

These are the EXACT rationalizations observed in baseline testing. If you think any of these, you are about to violate the skill:

| If you think... | Reality |
|-----------------|---------|
| "I can already see the issue" | Seeing ≠ systematic verification. Load the skill anyway. |
| "This is simple enough / overkill" | Simple tasks have HIGHEST error rates (Weinberg 1983). |
| "Skills would add overhead/latency" | 30 seconds of checklist prevents 30 minutes of debugging. |
| "I already know how to do this" | Knowing ≠ executing checklist. Experts make errors too. |
| "Not worth loading for a 5-line function" | 5-line functions have bugs. Load the skill. |
| "I'll just fix it directly" | Direct fixes without process have >50% error rate (Yourdon). |
| "This is genuinely trivial" | **NEW:** You don't get to decide triviality. Load the skill. It decides. |
| "The CRITICAL language is aspirational" | **NEW:** It's literal. "ANY code activity" means ANY. No interpretation. |
| "I'm following the spirit without the letter" | **NEW:** Violating the letter IS violating the spirit. Load the skill. |
| "Loading skills for this is cargo culting" | **NEW:** Process exists for edge cases you can't predict. Load anyway. |
| "I've done this exact thing 1000 times" | **NEW:** Expertise creates blind spots. The 1001st time can fail. |
| "The code already works / is battle-tested" | **NEW:** Your CHANGE can break what worked. 2 years of success doesn't protect today's edit. |
| "Skills are for new/broken code, not working code" | **NEW:** You're MODIFYING it. The modification is new code. Load the skill. |
| "Production validates correctness" | **NEW:** Production validates PAST code. Your change is FUTURE code. Load the skill. |
| "It's config, not code" | **NEW:** Config that affects runtime behavior IS code activity. Feature flags, deps, env vars need verification. |
| "Dependency version bump is just a number" | **NEW:** Version changes can introduce breaking changes, security patches, or behavior changes. Review it. |
| "I'm just resolving merge conflicts" | **NEW:** Combining code paths IS writing code. Conflicts often involve design decisions. Load the skill. |
| "Both versions already work" | **NEW:** They work SEPARATELY. Merging them is NEW code that hasn't been tested together. |
| "I'm just commenting out code temporarily" | **NEW:** Commenting out `processPayment()` can break checkout. Commented code IS modified code. Load the skill. |
| "It's temporary for debugging" | **NEW:** "Temporary" changes that break production aren't temporary - they're incidents. Verify before committing. |
| "Someone already reviewed/prescribed these changes" | **NEW:** Review validates the DESIGN. You can still IMPLEMENT it wrong. >50% error rate on ANY change applies. |
| "I'm just implementing code review feedback" | **NEW:** Implementing prescribed changes still has error rate. The reviewer approved the design, not your keystrokes. |
| "The senior developer said exactly what to do" | **NEW:** Authority doesn't prevent typos, wrong files, or missed edge cases. Skill chain catches implementation errors. |
| "I'm just moving code between files" | **NEW:** Moving code affects imports, dependencies, initialization order. "No logic change" ≠ "no risk". Load the skill. |
| "It's purely syntactic / mechanical" | **NEW:** "Syntactic" changes (imports, file moves, renames) break runtime when wrong. Verify all references. |
| "I'm just updating an import path" | **NEW:** Wrong path = runtime crash. Missing one file = partial failure. Case sensitivity varies by OS. Load the skill. |
| "The code itself isn't changing" | **NEW:** Code LOCATION matters. Moving, renaming, re-exporting changes how the system connects. These are structural changes. |
| "It's just `npm install` / package management" | **NEW:** Package managers modify lockfiles. Different lockfile = different versions = different runtime behavior. |
| "I'm just reinstalling dependencies" | **NEW:** `npm install` can update `package-lock.json`. A changed lockfile is a changed codebase. Verify it. |
| "It's an isolated dependency installation" | **NEW:** There's no such thing as "isolated" npm install. ANY npm install can change lockfiles. Load the skill. |
| "It's just changing file permissions" | **NEW:** `chmod +x` determines if a script can run. No execute bit = failed deployment. Permissions ARE code activity. |
| "I'm just making a script executable" | **NEW:** If the script can't execute, the build/deploy fails. Permission changes affect runtime. Load the skill. |
| "I'm just creating a symlink" | **NEW:** Symlinks determine WHAT file is loaded. Wrong symlink = wrong config = production incident. Verify it. |
| "The symlink is a simple operation" | **NEW:** Symlinks affect file resolution at runtime. `config.json -> config.prod.json` means prod config loads. |
| "I'm just creating an empty file" | **NEW:** Empty `.ts`/`.py`/`.js` files get compiled. They affect the build. They can be imported. Load the skill. |
| "The file has no code yet" | **NEW:** An empty file IS part of the codebase. It may be imported, compiled, or cause module resolution issues. |
| "It's just bumping a version number" | **NEW:** Version numbers affect npm publish, CI tagging, release artifacts. Wrong version = overwritten packages or broken releases. |
| "It's a trivial single-field edit" | **NEW:** Single-field edits in config files break production. DATABASE_URL, API_KEY, VERSION - all "single fields" that cause incidents. |
| "It's purely mechanical" | **NEW:** "Mechanical" changes need MORE verification, not less. Mechanical = easy to make typos. Load the skill. |
| "I'm just adding an npm script" | **NEW:** npm scripts in package.json affect builds, tests, and deployments. A typo in a script breaks CI. Load the skill. |
| "It's just a script entry in package.json" | **NEW:** package.json IS a build file. Script changes are code changes. The skill explicitly lists package.json. |
| "I'm just deleting an unused file" | **NEW:** How do you KNOW it's unused? Verify all imports first. Deletion is irreversible. Load the skill. |
| "It's a simple file deletion" | **NEW:** Deleting code files IS a structural change. The skill says "ANY change to file location, name, or structure" applies. |

**All of these mean:** Load the skill anyway. Your confidence is the problem, not the solution.

**The Rationalization Death Spiral:**
Every loophole in this list was discovered because an agent said NO when they should have said YES. They weren't lying - they genuinely believed their reasoning. That's why your belief doesn't matter. **If you can construct ANY argument for why this task is exempt, that argument is the rationalization.**

The skill doesn't ask "are you sure?" It asks "did you load it?" Load first. Decide after.

**The "Trivial Task" Trap (Observed in Testing):**
Agents rationalized skipping skills for "trivial" tasks like getters and variable renames. They said:
- "The task is genuinely trivial"
- "The 'CRITICAL' language is aspirational, not practical"
- "Loading skills for every keystroke would be cargo-culting"

These are the EXACT thoughts that precede bugs. A 2-line getter can have bugs. A variable rename can break tests. **You are not the judge of triviality - the skill is.**

**The "Working Code" Trap (Observed in Testing):**
Agents rationalized skipping skills when modifying production code. They said:
- "The code has empirical validation - two years of production use"
- "Working production code has already passed the ultimate review: reality"
- "Skills are for NEW code or BROKEN code. This is neither."

**These rationalizations are dangerous because they're half-true.** Yes, the EXISTING code works. But you're not evaluating the existing code - you're ADDING to it. Your addition is new code. The 2 years of production success doesn't validate your new logging statement, your new parameter, your new error handler. **Every modification is new code that needs the skill chain.**

**The "It's Just Config" Trap (Observed in Testing):**
Agents rationalized skipping skills for configuration file changes. They said:
- "It's a configuration file, not code"
- "A version bump is just changing a number"
- "Environment variables are data entry, not programming"

**Configuration that affects runtime behavior IS a code activity:**
- **Feature flags** enable/disable code paths - wrong value = production bug
- **Dependency versions** can introduce breaking changes or security issues
- **Environment variables** control database connections, API endpoints, secrets
- **Build configs** affect what code gets compiled/bundled

If a configuration change can cause your application to behave differently, it needs the same verification as a code change. At minimum, verify: What behavior changes? What could break? How will you test?

**The "Just Resolving Conflicts" Trap (Observed in Testing):**
Agents rationalized skipping skills for merge conflict resolution. They said:
- "I'm not writing code, just choosing between existing code"
- "Both versions already work - I'm just picking one"
- "This is selection, not creation"

**Merge conflicts ARE code writing:**
- Choosing which version to keep is a **design decision**
- Combining versions creates **new code** that was never tested
- Each branch worked in **isolation** - merging tests them **together** for the first time
- Subtle incompatibilities between branches are common bug sources

Classify as WRITE and load the skill chain.

**The "Just Commenting Out Code" Trap (Observed in Testing):**
Agents rationalized skipping skills for temporary code commenting. They said:
- "It's a trivial, temporary debugging modification"
- "The change is intentionally reversible"
- "It's a mechanical, diagnostic action"

**Commenting out code IS a code change:**
- Commenting out `processPayment()` breaks the entire checkout flow
- "Temporary" changes that get committed can reach production
- Even debugging changes need verification: What depends on this code? What will break?
- If you commit a "temporary" comment and deploy it, it's not temporary - it's an incident

The distinction between "production code" and "debugging" is false when you're committing changes. Load the skill chain.

**The "Already Reviewed/Prescribed" Trap (Observed in Testing):**
Agents rationalized skipping skills when implementing changes someone else specified. They said:
- "A senior developer already made the design decisions"
- "I'm simply executing prescribed changes, not making choices"
- "The review has already happened; I'm just implementing the approved feedback"

**This conflates two different activities:**
- **Design review** validates WHAT should change (the senior approved this)
- **Implementation** is HOW you make the change (your keystrokes, your files)

The >50% first-attempt error rate applies to implementation regardless of who designed it. You can:
- Implement in the wrong file
- Make a typo in the variable name
- Miss one of the locations that needs changing
- Misunderstand the prescribed change

**Code review feedback validates the approach, not your execution.** Load the skill chain to verify your implementation.

**The "Just Moving/Renaming Code" Trap (Observed in Testing):**
Agents rationalized skipping skills for structural changes. They said:
- "It's a mechanical refactoring task, not design or implementation"
- "The function's logic remains unchanged - just a cut-paste operation"
- "This is purely syntactic, not conceptual"
- "Updating an import path is a trivial mechanical edit"

**Structural changes ARE code changes:**
- **Moving a function** requires updating imports in EVERY file that uses it
- **Renaming files** breaks all import paths referencing the old name
- **Changing import paths** can introduce case sensitivity bugs across OSes
- **Re-exporting from different locations** can break circular dependency assumptions

The "logic stays the same" rationalization ignores that **code location IS part of the system**. A function that works in `utils.js` might fail if moved to a circular dependency, or if consumers have relative imports that break.

Classify structural changes as REFACTOR and load the skill chain.

**The "Just Running npm install" Trap (Observed in Testing):**
Agents rationalized skipping skills for package management. They said:
- "It's a simple shell command"
- "It's package management, not code"
- "I'm just reinstalling dependencies"

**Package manager commands ARE code activity:**
- `npm install` can modify `package-lock.json` - different lockfile = different versions
- Different dependency versions = different runtime behavior
- A "clean reinstall" that changes lockfile versions has broken production
- `pip install`, `cargo build`, `go mod tidy` all potentially modify lockfiles
- **There is no "isolated" vs "part of a larger task" distinction** - the lockfile changes regardless of context

Load the skill. Verify lockfile changes before committing. The command being "standalone" doesn't make it exempt.

**The "Just Changing Permissions" Trap (Observed in Testing):**
Agents rationalized skipping skills for chmod operations. They said:
- "It's a simple shell command"
- "File permissions aren't code"
- "I'm just making it executable"

**Permission changes ARE code activity:**
- `chmod +x deploy.sh` determines whether deployment works
- Missing execute bit = CI/CD failure
- Permission changes affect whether code can run AT ALL
- This is especially critical for scripts in build pipelines

If the permission affects whether code executes, load the skill.

**The "Just Creating a Symlink" Trap (Observed in Testing):**
Agents rationalized skipping skills for symlink operations. They said:
- "It's a simple shell command"
- "Symlinks are filesystem operations, not code"
- "I'm just linking config files"

**Symlink operations ARE code activity:**
- Symlinks determine WHAT file is loaded at runtime
- `config.json -> config.prod.json` means prod config loads everywhere
- Wrong symlink = loading wrong database, wrong API keys, wrong feature flags
- Circular symlinks can crash applications

If the symlink affects what code or config loads, load the skill.

**The "Just Creating an Empty File" Trap (Observed in Testing):**
Agents rationalized skipping skills for creating empty files. They said:
- "It's a trivial filesystem operation"
- "The file has no code in it"
- "I'm just creating a placeholder"

**Creating files IS code activity:**
- Empty `.ts`, `.py`, `.js` files get compiled
- Empty files can be imported (causing subtle bugs when imports expect exports)
- Files affect module resolution (a new `index.ts` changes how directories resolve)
- "Placeholder" files often stay empty and cause issues later

If the file could ever be executed, compiled, or imported, load the skill.

**The "Just a Version Bump" Trap (Observed in Testing):**
Agents rationalized skipping skills for version changes. They said:
- "It's a trivial single-field edit"
- "It's purely mechanical"
- "No design decisions required"

**Version changes ARE code activity:**
- Wrong version in package.json = npm publish overwrites existing package
- Version mismatch = CI/CD tagging fails or creates wrong tags
- Semantic versioning violations = breaking changes shipped as patch
- Users install wrong versions, report bugs against wrong releases

"Single-field edit" is one of the most dangerous rationalizations. Single fields control database connections, API keys, feature flags, and versions. Load the skill.

## Crisis Minimum (Time Pressure)

Production down? Urgent fix needed? You STILL must:

1. **Classify the task** (5 seconds)
2. **State what you're skipping and why** (explicit, not implicit)
3. **After crisis:** Return within 24 hours to apply full skill chain

**What you may NOT skip even in crisis:**
- Input validation on external data
- Verifying fix actually works (not just "looks right")
- One sentence explaining WHY the fix works

**Baseline testing showed:** Under time pressure, agents skipped ALL skills and later admitted "skills would have prompted me to think about the actual problem." Crisis makes process MORE important, not less.

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

- **WRITE:** Before claiming "done", run cc-routine-and-class-design CHECKER and cc-defensive-programming CHECKER on your code
- **DEBUG:** After identifying fix, invoke cc-refactoring-guidance for safe fix process
- **REVIEW:** If violations found, invoke cc-refactoring-guidance for fix recommendations
- **OPTIMIZE:** After changes, verify with cc-control-flow-quality that structure wasn't degraded

**Do not claim task complete until CHECKER gates pass.**
