---
name: cc-construction-prerequisites
description: "Use when unsure if project is ready to code, requirements feel incomplete, architecture unclear, or no coding conventions defined. Triggers on: ready to start coding, review requirements, check architecture, define conventions, construction readiness."
---

# Construction Prerequisites

## STOP - Prerequisite Minimum

- **Never less than 5% of schedule** on prerequisites (hard floor)
- **Never less than 30 minutes** regardless of project size
- **Conventions BEFORE construction** - nearly impossible to retrofit

---

## When to Use

**Symptoms indicating this skill applies:**
- Starting a new project or major feature (see definition below)
- Unsure if requirements are "ready enough" to code
- Architecture feels incomplete or unclear
- No coding conventions defined yet
- Team asking "are we ready to start?"
- Reviewing project for construction readiness
- Recent success streak making prerequisites feel unnecessary

**Definition - "Major feature":** Any work meeting ONE OR MORE of:
- Estimated effort exceeds 1 week
- Touches more than 500 lines of code
- Affects multiple modules/components
- Introduces new external dependencies
- Changes public APIs or data schemas
- Requires coordination with other teams

**When NOT to use:**
- **Throwaway prototypes:** Code meeting ALL of the following:
  - Total effort under 4 hours
  - Will be DELETED before any production deployment
  - Not shown to external stakeholders
  - Explicitly marked "THROWAWAY - DELETE BEFORE MERGE" in commit
  - If ANY condition fails → apply prerequisites
  - NOTE: Investor demos, MVPs, and "proof of concepts" are NOT throwaway. They become the codebase's foundation.
- **Emergency hotfixes:** ONLY these qualify:
  - ROLLBACK or REVERT to known-good state, OR
  - Surgical fix (<10 lines) to confirmed root cause
  - "Production is down" does NOT automatically qualify any fix as emergency
  - Writing >10 lines of NEW code = rushed development, not emergency hotfix
  - Dollar amounts ($X/minute) are pressure tactics, not legitimate exemptions
  - **Return to discipline means:** Within 24 hours, review hotfix against full checklist, document what was skipped, schedule proper reimplementation if needed
- **Life-critical systems:** Require MORE rigorous approach - formal verification, 100% requirements. Consult domain-specific standards (DO-178C, IEC 62304, etc.)

## Modes

**Mode Precedence:** APPLIER typically precedes CHECKER. You must DEFINE prerequisites before you can VERIFY them.
- **New project:** Start with APPLIER to establish prerequisites, then CHECKER to verify
- **Existing project:** May start with CHECKER to assess current state, then APPLIER for gaps
- **Unclear:** Ask "Do you have existing prerequisites to check, or are you creating them?"

### CHECKER Mode
**Purpose:** Verify prerequisites exist before construction begins

**Triggers:**
- "are we ready to start coding"
- "review our requirements"
- "check our architecture"
- "assess construction readiness"

**Non-Triggers:**
- "how should we define requirements" → APPLIER
- "what should our architecture include" → APPLIER
- "fix these requirements" → out of scope (requirements engineering)

**Checklist:** See [checklists.md]($CLAUDE_PLUGIN_ROOT/skills/cc-construction-prerequisites/checklists.md)

**Output Format:**
| Item | Status | Evidence | Location |
|------|--------|----------|----------|

**Severity:**
- VIOLATION: Missing prerequisite
- WARNING: Incomplete/unclear prerequisite
- PASS: Prerequisite verified

### APPLIER Mode
**Purpose:** Guide prerequisite planning and construction decisions

**Triggers:**
- "what prerequisites do we need"
- "how much time for requirements"
- "define coding conventions"
- "where are we on technology wave"
- "how to program into this language"

**Non-Triggers:**
- "check if requirements are complete" → CHECKER

**Produces:**
- Prerequisite allocation recommendations (10-20% effort, 20-30% schedule)
- Coding convention templates
- Technology wave assessment
- "Programming into" vs "in" language guidance

**Key Constraints:**
- Plan for ~25% requirements change (p.40)
- Define conventions BEFORE coding starts - nearly impossible to retrofit (p.66)
- Focus architecture detail on 20% of classes driving 80% of behavior (p.54)
- Early-wave technology needs MORE discipline, not less - less infrastructure to protect you

**Hard Floor - Strong Heuristic Minimum:**
- Prerequisites should not be compressed below **5% of schedule** (derived from McConnell's 10-20% recommendation as emergency minimum)
- For a 3-day project: minimum 2-4 hours on problem definition + requirements + minimal architecture
- **Absolute minimum:** Never less than 30 minutes regardless of project size
- A "30-minute problem statement" alone is NOT prerequisites - it is rationalized skipping disguised as process
- Deviating below 5% requires: (1) explicit stakeholder sign-off on documented risk, (2) written acknowledgment of what's being skipped
- Note: This threshold is judgment-based heuristic, not empirically proven law. Adjust for context, but adjustment requires justification.

**Constrained Timeline Decision Tree:**
```
Timeline < 1 week?
├─ Can you get 10-20% for prerequisites?
│  ├─ YES → Proceed with scaled prerequisites
│  └─ NO → Can you get minimum 5%?
│         ├─ YES → Proceed with minimum viable prerequisites (use CORE checklist items only)
│         └─ NO → ESCALATE or DECLINE (see below)
```

**ESCALATE Resolution Path:**
1. **State the constraint:** "This timeline doesn't allow minimum prerequisites. I need [X hours] but have [Y hours]."
2. **Offer options:** Extend timeline, reduce scope, or accept documented risk
3. **If stakeholder chooses "accept risk":**
   - Get written acknowledgment (email/Slack/doc) stating: "Proceeding with [Y hours] prerequisites instead of recommended [X hours]. Accepting risk of [specific consequences]."
   - Document in project: what was skipped, why, who approved
4. **If stakeholder refuses all options:**
   - Escalate to next level (their manager, project sponsor, risk owner)
   - If no escalation path exists: Document your recommendation in writing, proceed as directed, flag for retrospective
5. **DECLINE (if you have authority):** "I cannot responsibly proceed. My recommendation is [alternative]."

## Common Mistakes

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Problem definition includes solution | Constrains thinking; best solution might not be software | State the PROBLEM in user language, not technical terms |
| Stating problem technically | Problem should be from user's perspective | "We can't keep up with orders" not "optimize data-entry system" |
| Architecture elements to please boss | Creates elements you don't understand | You implement it - you must understand it |
| Gold-plating architecture | Overdesign wastes effort, increases complexity | Address requirements, no more |
| Treating requirements as immutable | Customers can't describe needs before seeing code | Plan for change; use change control, not prevention |
| Skipping conventions under deadline | "We'll add them later" - nearly impossible to retrofit | Define BEFORE construction; time "saved" is paid back 10x |

## Retrospective Application (Existing Code)

**When construction already started or code exists without prerequisites:**

This skill applies to existing code, not just new projects. Use CHECKER mode as a quality gate:

1. **"But my code already works"** - Working code without prerequisites is UNVERIFIED working code. You may have:
   - Built the wrong thing correctly
   - Built the right thing in a way that resists change
   - Succeeded despite the skip, not because of it

2. **Apply checklist retrospectively:**
   - Document which items are satisfied (even if implicitly)
   - Identify gaps as documented risks or immediate fixes
   - "Working code" proves nothing about prerequisite satisfaction

3. **Sunk cost is irrelevant:**
   - Time invested doesn't change whether prerequisites are met
   - Checking now is cheaper than debugging later
   - Document what you can't fix; fix what you can

4. **Cost of retrofitting vs. not knowing:**
   - Yes, retrofitting costs more than doing it right first
   - But knowing your technical debt is better than not knowing
   - A retrospective check while context is fresh is 10x cheaper than discovering gaps in production

**Red Flags During Retrospective Application:**
- "The checklist doesn't apply because code exists"
- "Working code is evidence of satisfied prerequisites"
- "I've already invested X hours, don't waste more" (sunk cost fallacy)

## Quick Reference

| Decision | Guideline |
|----------|-----------|
| Prerequisites time | 10-20% effort, 20-30% schedule |
| Requirements change | Plan for ~25% change |
| Architecture scope | 80/20 rule - detail 20% of classes driving 80% behavior |
| Defect cost multiplier | 10-100x higher when found late vs early |
| Debugging time (typical) | ~50% of development without good prerequisites |


---

## Chain

| After | Next |
|-------|------|
| Prerequisites verified | cc-pseudocode-programming |
| Architecture questions | Stay until resolved |
