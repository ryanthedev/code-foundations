# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Code-foundations is a Claude Code plugin providing software engineering skills based on *Code Complete* (McConnell) and *A Philosophy of Software Design* (Ousterhout). It includes a build workflow with gated phases (BUILD, REVIEW, orchestrator commit).

## Architecture

### Directory Structure

- `agents/` - Agent templates (build-agent, post-gate-agent); each carries one guarded `alsp Evidence` section that applies only when `alsp` is on PATH and the repo has a `Cargo.toml`
- `evals/` - The regression suite every doctrine edit is checked against: `node evals/validate-structure.mjs` (orphans, paths, anchors, frontmatter, descriptions, the rules registry, the pre-cut inventory), `evals/wordcount.sh`, `evals/dispatch-load.sh`, the CHECKER A/B eval, and the build-workflow smoke fixture. See `evals/README.md`

### Development Workflows

**Choose based on scope:**

| Situation | Command | Ceremony |
|-----------|---------|----------|
| Bug investigation | `/code-foundations:debug` | Minimal |
| Vague idea or unclear requirements | `/code-foundations:research` | Minimal |
| Feature needs planning | `/code-foundations:plan` | Medium |
| Executing approved plan | `/code-foundations:build` | Full |

### Research → Whiteboard → Building Workflow

Three-stage pattern for feature development:

| Command | Purpose | Output |
|---------|---------|--------|
| `/code-foundations:research` | Clarify what the user wants through facilitated conversation | Research doc in `.code-foundations/research/` |
| `/code-foundations:plan` | Plan implementation with phases, models, and skills | Plan file in `.code-foundations/plans/` |
| `/code-foundations:build` | Checklist-based execution | Working code + tests |

**Gate policy:** each phase in the plan carries a `**Gate:**` field (Full | Standard | Minimal) —
required, like `**Model:**`, `**Depends on:**`, and `**Skills:**`; build stops and asks for a re-plan when any
is missing (there are no legacy plans). The gate decides review **timing**, not whether a review
happens — every phase is reviewed. Standard (the default) = BUILD + COMMIT, review deferred to the
next batch. Minimal = BUILD (no discovery) + COMMIT, same deferral. Full = BUILD + blocking REVIEW +
COMMIT, assigned only when the user asks (always runs alone, never in a wave). `**Security-sensitive:** yes`
forces one immediate blocking REVIEW at any gate — never deferred. The planner never picks fable or
Full on its own (v6.6.0): batch review already covers every phase, and one reviewer is enough.

**Review cadence:** the plan header carries `**Review cadence:** N` (default 3, clamped to 1–5).
Standard and Minimal phases commit on a green suite and join an un-reviewed set; a batch REVIEW
covers the whole set at once when N accumulate, before any Full phase opens, and at VERIFY if
anything is still un-reviewed. Batch REVIEW runs against committed code, so a FAIL is fixed forward (a `fix(phase-N)`
commit answering the findings, then a re-run over the whole set) rather than gating a commit —
see `references/gate-failure-protocol.md` → Batch Failures. Reviewing several phases together is
also what buys the cross-phase coherence check that isolated per-phase reviews can't produce.
Commits record `Review: deferred (batch pending)`, paired with a `Covered by batch review`
addendum in the execution log; a deferred trailer with no addendum is a build defect the trust
report must catch.

**Build loop (v6.5.0):** build runs Understand → Act → Inspect → Clarify → Adjust → Act again,
and stays quiet because the user already talked in research and planning. Clarify: a BUILD agent
settles anything the plan leaves open (from the plan, the research doc, the codebase, an experiment,
then the most reversible default) and records it under `### Decisions`. Those rows go into the plan's
`## Decided During Build` log and reach later BUILD prompts as Decisions in Force, never a reviewer.
UPDATE_PLAN is reserved for one-way doors (contracts, scope, security, destructive data, public API);
the question holds only that phase and its dependents, and the build ends its turn to ask only when
nothing else is runnable. Adjust (`references/checkpoint.md`), after each batch PASS and before VERIFY:
the orchestrator fixes misfits in the remaining plan as `plan(adjust)` commits. It may add, split,
reorder or tighten, and never removes or weakens a DW item or changes a contract on its own.
`**Check-ins:**` sets how often the user hears from the build.

**Checkpoint doctrine:** content the user must review (plan summaries, skeletons, approach
comparisons, problem statements) is presented as the turn's final conversation markdown and
answered free-form — dialog previews truncate multi-phase content. `AskUserQuestion` is reserved
for decisive 2-4-option picks (clarify, coverage level, handoff). The draft→ready Status flip is
the structural guard: unconfirmed plans can't build.

**Effort doctrine:** plan at high effort (the reasoning lives there); build at low effort for
all-serial plans, default when any phase carries `File scope` (wave-eligible). Subagent depth is
separate: BUILD/REVIEW agents are steered by dispatch wording (the Agent tool has no effort knob) —
derived from each phase's `Model`, REVIEW never below "think carefully"; build's Effort Alignment
warns (never stops) when a phase's `Model` (effort) and `Gate` (rigor) disagree.

Skills are **workflow-internal** (all 20 carry `user-invocable: false`; `planning` additionally keeps
`disable-model-invocation: true` so the model can't run the planning pipeline ad-hoc). They are
hidden from the user's slash menu but ARE in the model's skill register — model-discoverable and
invocable. Plan/build discover them (alongside external plugin skills) via the register — each
skill's description carries its own when-to-match and sibling-disambiguation (the "not for X (use
Y)" clauses), so matching is done on the descriptions directly. Build (and the
planner's DETAIL step) load each assigned skill via the Skill tool — `Skill(code-foundations:<name>)`
for this plugin's own, `Skill(<plugin>:<name>)` for any other plugin's — and each skill self-loads
its checklists. A subagent doesn't inherit the register, but an explicit `Skill(...)` line in its
dispatch prompt invokes the skill regardless.

The REVIEW dispatch is deliberately stripped of intent-framing (no plan context, no progress
narrative, no discovery file) — the reviewer is an independent critic.

Models are assigned per phase at plan's SAVE step. Cannot proceed to next phase until current
phase passes all gates including REVIEW PASS (Full gate).

## Skill File Structure


Some skills have a `references/` subdirectory (e.g. `gof-design-patterns/references/` for the
23 pattern files; `code-standards/references/` for section-templates.md). Every bundled file
must be linked from SKILL.md or it is a dead orphan. The `hard-data.md` and `language-notes.md`
patterns are not standard — they were removed during the 2026-06 audit (orphan files with
proven drift). Some skills bundle `scripts/` (executed or copied, never loaded into context), e.g.
`lean-build/scripts/gate-skeleton.sh`; `lean-build` is the first skill with a `scripts/` folder.

## Publishing

### Marketplace

Published to `ryanthedev/rtd-claude-inn` marketplace. Marketplace tracks `ref: main`, so publishing is just pushing to origin.

**To publish:**
1. Bump version in `.claude-plugin/plugin.json`
2. Commit and push to `origin/main`

