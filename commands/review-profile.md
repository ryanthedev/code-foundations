---
description: "Manage custom review profiles"
argument-hint: "[--setup [name] | --list | --delete <name>]"
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Write", "AskUserQuestion"]
---

# Review Profile Management

Create and manage custom review profiles.

```
/code-foundations:review-profile --setup           # Create/edit default profile
/code-foundations:review-profile --setup security  # Create/edit named profile
/code-foundations:review-profile --list            # List all profiles
/code-foundations:review-profile --delete security # Delete a profile
```

---

## PROFILE STRUCTURE

```yaml
# .code-foundations/profiles/my-profile.yaml
name: my-profile
description: "My custom review configuration"

checklists:
  # Use a skill's built-in checklist with its persona
  - path: skills/cc-defensive-programming/checklists.md
    skills: [cc-defensive-programming]

  # Use a custom checklist with a skill's persona
  - path: .code-foundations/checklists/owasp-top-10.md
    skills: [cc-defensive-programming]

  # Use a custom checklist with multiple skill personas
  - path: .code-foundations/checklists/api-security.md
    skills: [cc-defensive-programming, aposd-simplifying-complexity]

  # Use a self-contained checklist (no skill persona)
  - path: .code-foundations/checklists/team-standards.md
    skills: []
```

**Each checklist = 1 checking agent** during review.

---

## STEP 1: PARSE ARGUMENTS

```python
PROFILE_DIR = ".code-foundations/profiles"

if "--setup" in args:
    PROFILE_NAME = args.get("--setup") or "default"
    goto STEP 2: INTERACTIVE SETUP

if "--list" in args:
    goto STEP 5: LIST PROFILES

if "--delete" in args:
    PROFILE_NAME = args["--delete"]
    goto STEP 6: DELETE PROFILE

# No args - show help
print("""
Usage:
  /code-foundations:review-profile --setup [name]  Create or edit a profile
  /code-foundations:review-profile --list          List all profiles
  /code-foundations:review-profile --delete <name> Delete a profile

Built-in profiles (read-only):
  sanity  - 99 critical checks (agents/profiles/sanity.yaml)
  pr      - 614 checks, 10 skills (agents/profiles/pr.yaml)
""")
```

---

## STEP 2: INTERACTIVE SETUP

### 2.1 Setup Directory

```bash
mkdir -p .code-foundations/profiles
mkdir -p .code-foundations/checklists
```

### 2.2 Load Existing (if editing)

```python
PROFILE_PATH = f".code-foundations/profiles/{PROFILE_NAME}.yaml"
if file_exists(PROFILE_PATH):
    existing = Read(PROFILE_PATH)
    # Parse existing checklists for editing
else:
    existing = None
```

### 2.3 Choose Starting Point

```
AskUserQuestion(
  questions: [
    {
      header: "Start from",
      question: "How do you want to build this profile?",
      options: [
        {label: "From scratch", description: "Empty profile, add checklists one by one"},
        {label: "Copy sanity", description: "Start with 99-check quick checklist"},
        {label: "Copy pr", description: "Start with all 10 skill checklists (614 checks)"},
        {label: "Pick skills", description: "Choose which skill checklists to include"}
      ]
    }
  ]
)
```

**Map selection:**

| Selection | Initial Checklists |
|-----------|-------------------|
| From scratch | `[]` |
| Copy sanity | `[{path: "agents/quick-checklist.md", skills: []}]` |
| Copy pr | All 10 skill checklists |
| Pick skills | → Ask follow-up |

### 2.4 Pick Skills (if selected)

```
AskUserQuestion(
  questions: [
    {
      header: "Skills",
      question: "Which skill checklists do you want to include?",
      multiSelect: true,
      options: [
        {label: "cc-defensive-programming", description: "Error handling, input validation (31 checks)"},
        {label: "aposd-simplifying-complexity", description: "Exception design, error reduction (44 checks)"},
        {label: "aposd-reviewing-module-design", description: "Module interfaces, information hiding (42 checks)"},
        {label: "cc-code-layout-and-style", description: "Formatting, visual structure (85 checks)"}
      ]
    }
  ]
)
```

For each selected skill, add:
```yaml
- path: skills/{skill}/checklists.md
  skills: [{skill}]
```

---

## STEP 3: ADD CUSTOM CHECKLISTS (Optional)

```
AskUserQuestion(
  questions: [
    {
      header: "Custom",
      question: "Do you want to add custom checklists?",
      options: [
        {label: "No", description: "Use only the skill checklists selected above"},
        {label: "Yes", description: "Add paths to custom checklist files"}
      ]
    }
  ]
)
```

**If "Yes":**

```
AskUserQuestion(
  questions: [
    {
      header: "Path",
      question: "Enter the path to your custom checklist (relative to repo root):",
      options: [
        {label: ".code-foundations/checklists/", description: "Standard location for custom checklists"},
        {label: "Browse", description: "I'll type a custom path"}
      ]
    }
  ]
)
```

Then ask which skills to associate:

```
AskUserQuestion(
  questions: [
    {
      header: "Skills",
      question: "Which skill personas should inform this checklist?",
      multiSelect: true,
      options: [
        {label: "None", description: "Self-contained checklist, no skill persona"},
        {label: "cc-defensive-programming", description: "Security/error handling mindset"},
        {label: "aposd-simplifying-complexity", description: "Complexity reduction mindset"},
        {label: "Other", description: "I'll specify a different skill"}
      ]
    }
  ]
)
```

Repeat until user is done adding custom checklists.

---

## STEP 4: REVIEW & SAVE

### 4.1 Show Summary

```markdown
## Profile: {PROFILE_NAME}

**Checklists:** {N} checklists, ~{TOTAL_CHECKS} checks

| # | Checklist | Skills | Checks |
|---|-----------|--------|--------|
| 1 | skills/cc-defensive-programming/checklists.md | cc-defensive-programming | 31 |
| 2 | .code-foundations/checklists/owasp.md | cc-defensive-programming | ~50 |
| **Total** | | | **~81** |
```

### 4.2 Offer Changes

```
AskUserQuestion(
  questions: [
    {
      header: "Action",
      question: "What would you like to do?",
      options: [
        {label: "Save", description: "Save profile to .code-foundations/profiles/{PROFILE_NAME}.yaml"},
        {label: "Add checklist", description: "Add another checklist"},
        {label: "Remove checklist", description: "Remove a checklist"},
        {label: "Start over", description: "Reset and begin again"}
      ]
    }
  ]
)
```

Loop until "Save" selected.

### 4.3 Save Profile

```yaml
# .code-foundations/profiles/{PROFILE_NAME}.yaml
name: {PROFILE_NAME}
description: "{DESCRIPTION}"
created: {DATE}
modified: {DATE}

checklists:
  - path: skills/cc-defensive-programming/checklists.md
    skills: [cc-defensive-programming]
  - path: .code-foundations/checklists/owasp.md
    skills: [cc-defensive-programming]
```

```
Write(.code-foundations/profiles/{PROFILE_NAME}.yaml, content)
```

**Confirm:**

```markdown
Profile saved: `.code-foundations/profiles/{PROFILE_NAME}.yaml`

Use with:
  /code-foundations:review --profile {PROFILE_NAME}
```

---

## STEP 5: LIST PROFILES

```bash
# Built-in profiles
echo "Built-in profiles:"
ls -la agents/profiles/

# User profiles
echo "User profiles:"
ls -la .code-foundations/profiles/ 2>/dev/null || echo "  (none)"
```

**Output:**

```markdown
## Available Profiles

### Built-in (read-only)

| Profile | Checklists | Checks | Description |
|---------|------------|--------|-------------|
| sanity | 1 | 99 | Quick pre-commit sanity check |
| pr | 10 | 614 | Full PR review |

### User Profiles

| Profile | Checklists | Checks | Modified |
|---------|------------|--------|----------|
| security | 3 | ~120 | 2026-01-30 |
| quick-defensive | 2 | ~75 | 2026-01-29 |

**Create new:** `/code-foundations:review-profile --setup <name>`
```

---

## STEP 6: DELETE PROFILE

```
AskUserQuestion(
  questions: [
    {
      header: "Confirm",
      question: "Delete profile '{PROFILE_NAME}'?",
      options: [
        {label: "Yes, delete it", description: "Remove .code-foundations/profiles/{PROFILE_NAME}.yaml"},
        {label: "No, keep it", description: "Cancel"}
      ]
    }
  ]
)
```

**If confirmed:**

```bash
rm .code-foundations/profiles/{PROFILE_NAME}.yaml
```

```markdown
Profile deleted: {PROFILE_NAME}
```

---

## AVAILABLE SKILLS

Reference for profile creation:

| Skill | Checks | Focus |
|-------|--------|-------|
| cc-defensive-programming | 31 | Error handling, assertions, input validation |
| aposd-simplifying-complexity | 44 | Exception design, complexity reduction |
| aposd-reviewing-module-design | 42 | Module interfaces, information hiding |
| cc-code-layout-and-style | 85 | Formatting, visual structure |
| cc-control-flow-quality | 94 | Loops, conditionals, nesting |
| aposd-verifying-correctness | 39 | Requirements, edge cases |
| cc-quality-practices | 107 | Testing, debugging, reviews |
| cc-performance-tuning | 40 | Optimization, profiling |
| aposd-optimizing-critical-paths | 40 | Performance design |
| cc-documentation-quality | 26 | Comments, README, API docs |

**3rd party skills:** Use `plugin-name:skill-name` format if installed.

---

## CUSTOM CHECKLIST FORMAT

Create custom checklists in `.code-foundations/checklists/`:

```markdown
# My Custom Checklist

## Category Name

- [ ] ID-1: Check description
- [ ] ID-2: Another check
- [ ] ID-3: Third check

## Another Category

- [ ] ID-4: More checks
```

**Requirements:**
- Each check starts with `- [ ]`
- Include an ID prefix (e.g., `SEC-1`, `PERF-2`)
- One check per line
