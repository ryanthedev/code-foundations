# Adaptive Questioning

How to question the user without changing what you need to know — only what they have to type.

Used by `clarify` and any whiteboarding gate that asks the user a question (`AskUserQuestion`, free-form, or option-list).

---

## Two Modes

**Exploratory (default).** Open-ended questions targeting the axis of disagreement between hypotheses. The user provides the answer.

**Confirmatory.** You still ask every question you need answered — but you supply your best-guess answer and let the user confirm or correct. The completeness bar usually does not change. Only the cost to the user drops.

| Exploratory | Confirmatory equivalent |
|-------------|------------------------|
| "What should happen when the input is empty?" | "I'm assuming empty input returns 400 with a validation error — correct?" |
| "Should this be async or sync?" | "This looks I/O-bound, so I'll make it async unless you say otherwise." |
| "Which auth flow — OAuth, email/password, SSO?" | "I'll go with OAuth since the codebase already has the provider configured. Push back if you want something different." |

---

## When to Switch

**To confirmatory:** short or terse replies, "just do it," "whatever works," "I don't care," answering a multi-part question with one word, expressing impatience. Don't wait for explicit frustration — early signals are enough.

**Back to exploratory:** the user gives a detailed, engaged answer to a confirmatory question; volunteers new context unprompted; asks you to slow down or explore options.

The transition is per-conversation, not permanent. Read the room each turn.

---

## Inside `AskUserQuestion`

Confirmatory mode still works inside the structured tool — encode your assumption in the option labels and ordering:

- Make your recommended option the first or clearly-labeled choice: `"Use JWT (my recommendation — codebase is stateless)"`
- Keep the other real options selectable so the user can override without typing.
- Keep an "Elaborate" / "Different direction" escape hatch when stakes are high.

This preserves the gate (user still answers) while collapsing the cognitive load.

---

## Honest Caveat

The "bar doesn't change" claim is *usually* true but not absolute. On genuinely low-stakes calls, "just do it" can mean *the user is accepting a lower correctness bar in exchange for speed*. Don't manufacture questions to satisfy a checklist when the user has explicitly traded rigor for velocity. Use judgment:

- **High stakes** (irreversible action, security, data loss, architectural lock-in) → keep every question, just switch to confirmatory.
- **Low stakes** (cosmetic choice, easily reversible, one of several valid options) → drop the question entirely.

When uncertain, prefer confirmatory over silent assumption.

---

## Anti-Patterns

| Pattern | Problem | Instead |
|---------|---------|---------|
| Going silent on "just do it" | Hidden assumptions ship without review | Switch mode, state the assumption, let them object |
| Asking the same question after the user typed "whatever" | Ignores the signal | Confirmatory — supply the answer |
| Confirmatory questions phrased as leading statements | "I assume you want X, right?" with no real out | Offer the alternative: "X unless you'd rather Y" |
| Permanent mode lock | Reading the user once and never re-reading | Re-evaluate each turn; engagement can return |
