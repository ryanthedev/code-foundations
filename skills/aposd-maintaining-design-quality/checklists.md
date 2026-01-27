# Checklists: aposd-maintaining-design-quality

Source: A Philosophy of Software Design (Ousterhout), Chapters 1, 3, 19

---

## Urgency Tier Assessment

- [ ] UT-1: "Trivial change (typo, whitespace, comment correction)?" → No analysis needed
- [ ] UT-2: "Minor change (bug fix <5 lines, config tweak, dependency bump)?" → Quick check: does this fit cleanly?
- [ ] UT-3: "Standard change (new feature, refactoring, multi-file)?" → Full workflow required
- [ ] UT-4: "Emergency (production down, security breach, data loss)?" → Minimal fix + TODO + 24hr follow-up

---

## Strategic Modification Workflow

- [ ] SM-1: "Did I RESIST the temptation to make a quick fix?"
- [ ] SM-2: "Did I ASK: 'Is the current system design still the best one, given this change?'"
- [ ] SM-3: "IF NO: Am I refactoring so the system ends up with the best possible design?"
- [ ] SM-4: "IF YES: Does my change fit cleanly within the existing design?"
- [ ] SM-5: "BEFORE COMMIT: Did I scan all changes to verify documentation reflects them?"

---

## Investment Mindset

- [ ] IM-1: "Am I investing 10-20% of development time on design improvements?"
- [ ] IM-2: "Am I thinking strategically (10-20% slower now → faster forever)?"
- [ ] IM-3: "Am I avoiding tactical shortcuts (quick fix now → 20%+ slower forever)?"

---

## When Refactoring Seems Impractical

- [ ] RP-1: "Is this the best I can possibly do to create a clean design, given constraints?"
- [ ] RP-2: "If large refactoring is impractical: did I look for almost-as-clean alternatives?"
- [ ] RP-3: "If cannot do proper cleanup now: did I create accountability plan?"

---

## Accountability for Deferred Refactoring

- [ ] AD-1: "Did I CREATE a ticket/issue with specific scope?"
- [ ] AD-2: "Did I TIMEBOX: must be addressed within 2 sprints (or equivalent)?"
- [ ] AD-3: "Did I ADD a code comment: `// TODO(YYYY-MM-DD): [ticket-id] - [what needs fixing]`?"
- [ ] AD-4: "If 3+ deferrals exist in same area: is refactoring now MANDATORY?"

---

## When NOT to Refactor

- [ ] NR-1: "Chesterton's Fence code?" - Looks bad but handles subtle edge cases → Investigate WHY first
- [ ] NR-2: "Performance-critical paths?" - Clean abstractions add overhead → Document why it's intentionally ugly
- [ ] NR-3: "Regulatory/audited code?" - Changes trigger expensive re-certification → Get explicit approval first
- [ ] NR-4: "Legacy with no tests?" - Refactoring without tests is dangerous → Add tests first, or freeze
- [ ] NR-5: "Code with external quirk dependencies?" - Other systems rely on undocumented behavior → Coordinate with dependents
- [ ] NR-6: "Near end-of-life systems?" - Investing in dying code is waste → Document, don't improve
- [ ] NR-7: "During incident response?" - Changing more increases blast radius → Minimal fix only
- [ ] NR-8: "When you don't understand domain?" - "Better design" reflects misunderstanding → Learn first

---

## Red Flags

- [ ] RF-1: "Quick Fix Mentality?" - 'Just make it work for now' → Tactical programming - design will degrade
- [ ] RF-2: "Complexity Creep?" - Adding special cases, conditionals, dependencies → Design getting worse
- [ ] RF-3: "Patch Stacking?" - Workarounds on top of workarounds → Technical debt accumulating
- [ ] RF-4: "Tactical Tornado?" - Very fast developer leaving messes → Others will pay for speed
- [ ] RF-5: "Stale Comments?" - Comments no longer match code → Trust erosion
- [ ] RF-6: "Deferred Cleanup?" - 'We'll refactor later' → Later never comes

---

## Comment Maintenance

- [ ] CM-1: "Are comments positioned close to code they describe?"
- [ ] CM-2: "Am I avoiding duplicating documentation?"
- [ ] CM-3: "Is each decision documented exactly once?"
- [ ] CM-4: "Did I scan all changes before commit to catch stale comments?"

---

## Emergency Bypass (ALL must be true)

- [ ] EB-1: "Is production down RIGHT NOW?"
- [ ] EB-2: "Are users actively impacted, security breach in progress, OR data loss occurring?"
- [ ] EB-3: "Is the fix minimal (rollback or single-line change)?"
- [ ] EB-4: "Am I committing to return for proper implementation within 24 hours?"

---

Total items: 42
