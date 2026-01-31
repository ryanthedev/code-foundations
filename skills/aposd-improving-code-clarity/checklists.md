# Checklists: aposd-improving-code-clarity

Source: A Philosophy of Software Design (Ousterhout), Chapters 12-15, 18

---

## Comments-First Workflow

- [ ] CF-1: "Did I write class interface comment BEFORE implementation?"
- [ ] CF-2: "Did I write interface comments for public methods (signatures + comments, empty bodies)?"
- [ ] CF-3: "Did I iterate on comments until structure feels right?"
- [ ] CF-4: "Did I write instance variable declarations with comments?"
- [ ] CF-5: "For new methods discovered during implementation: did I comment before body?"
- [ ] CF-6: "For new variables: did I comment at same time as declaration?"

---

## What Counts as New Code

- [ ] NC-1: "Writing from scratch?" → Comments-first applies
- [ ] NC-2: "Copy-paste-modify?" → Comments-first applies (new context)
- [ ] NC-3: "Extending existing function (>5 lines)?" → Comments-first applies
- [ ] NC-4: "Refactoring that changes interfaces?" → Comments-first applies
- [ ] NC-5: "Converting prototype to production?" → Comments-first applies
- [ ] NC-6: "Test methods?" → Comments-first applies
- [ ] NC-7: "Lambda functions with non-trivial logic (>1 expression)?" → Comments-first applies

---

## Comment Quality Requirements

- [ ] CQ-1: "Does comment describe the abstraction (not just 'does the thing')?"
- [ ] CQ-2: "Does comment include non-obvious details?"
- [ ] CQ-3: "Does comment use different words than code (not just repeat function name)?"
- [ ] CQ-4: "For variables: does comment include precision (units, bounds, null, ownership)?"

---

## Variable Comment Checklist

- [ ] VC-1: "What are the units? (seconds? milliseconds? bytes?)"
- [ ] VC-2: "Are boundaries inclusive or exclusive?"
- [ ] VC-3: "What does null mean, if permitted?"
- [ ] VC-4: "Who owns the resource (responsible for freeing/closing)?"
- [ ] VC-5: "What invariants always hold?"

---

## Naming - Precision

- [ ] NP-1: "Can someone seeing this name in isolation guess what it refers to?"
- [ ] NP-2: "Could this name refer to multiple things?" → Too vague
- [ ] NP-3: "Does this name imply narrower usage than actual?" → Too specific
- [ ] NP-4: "Does name match actual scope exactly?"

---

## Naming - Consistency

- [ ] NC-1: "Is this name used everywhere for this purpose?"
- [ ] NC-2: "Is this name used ONLY for this purpose?"
- [ ] NC-3: "Do all variables with this name behave identically?"

---

## Common Naming Mistakes

- [ ] NM-1: "Vague status words?" (e.g., `blinkStatus` → `cursorVisible`)
- [ ] NM-2: "Too generic?" (e.g., `getCount()` → `numActiveIndexlets`)
- [ ] NM-3: "Too specific for actual usage?" (e.g., `selection` → `range` if method works on any range)
- [ ] NM-4: "Similar names for different things?" (e.g., `socket` vs `sock`)
- [ ] NM-5: "Type in name?" (e.g., `strName` → `name`)
- [ ] NM-6: "Repeating class in variable?" (e.g., `File.fileBlock` → `File.block`)

---

## Red Flags

- [ ] RF-1: "Comment Repeats Code?" - Same words in comment as entity name → Rewrite with different words
- [ ] RF-2: "Hard to Describe?" - Difficulty writing simple, complete comment → **Design problem** - fix the design
- [ ] RF-3: "Hard to Pick Name?" - Can't find simple name that creates clear image → **Design smell**
- [ ] RF-4: "Vague Name?" - Name could refer to many things (status, flag, data) → Conveys little information
- [ ] RF-5: "Interface Describes Implementation?" - Interface comment must explain internals → Class/method is shallow
- [ ] RF-6: "Implementation Contaminates Interface?" - Interface docs include internal details → Violates separation

---

## Interface vs Implementation Comments

- [ ] IC-1: "Does interface comment describe externally visible behavior (not internals)?"
- [ ] IC-2: "Does interface comment define the abstraction (not how it works)?"
- [ ] IC-3: "Does interface comment tell what user needs to use it (not maintainer details)?"
- [ ] IC-4: "Does interface comment NEVER include implementation details?"

---

Total items: 44
