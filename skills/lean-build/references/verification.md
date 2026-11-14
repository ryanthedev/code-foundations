# Verification policy in depth

## Contents
1. Choosing the verifier per job
2. Before the verifier: security review and builder self-attack
3. Fix rounds and the two-round limit
4. What the lead checks without a verifier
5. Model tiers for everything else

## 1. Choosing the verifier per job

Mark each job in the plan with `Security-sensitive: yes|no` and the reason. In code-foundations plans that
field already exists.

| The job touches | First verifier | Why |
|---|---|---|
| A trust boundary: socket or wire parsing, untrusted files, sandbox, grants, auth, remote access | top tier (Opus) | On the omni build, every top-tier pass on such a job found at least one real HIGH |
| Concurrency, actors, mailboxes, locks, timing | top tier | Deadlocks and unbounded queues look like load until someone traces them |
| Ordinary product code, rigs, benchmarks, UI not handling untrusted input | mid tier (Sonnet) | Thin evidence: the two mid-tier and low-risk passes found no HIGH. Revisit if one slips through |
| Paper (spec text, result write-ups, wording) | the lead reads it | A session costs more than reading two paragraphs |

## 2. Before the verifier

- **Automated security review on the builder's diff**, run before the verifier starts. On the omni build,
  findings from a post-commit review became two whole extra jobs (brief, builder, top-tier verifier, fix round).
  On the diff, they fold into the first fix round.
- **Builder self-attack checklist**, appended to every builder brief. Before reporting, check your change for:
  - unbounded growth: queues, caches, maps, per-connection resources;
  - a panic, abort or stack overflow on untrusted input: unwraps, recursion depth, duplicate keys, cycles;
  - any write outside the repo, such as the user's data directory, a global cache, or `~/Library`;
  - a gate line that cannot fail or cannot pass (see the gates reference, section 5).

## 3. Fix rounds and the two-round limit

1. FAIL with HIGHs: the job goes to a builder. Use the same one if it is under about 60% context, else a fresh one.
2. The same verifier re-checks. It is idle, already has the context, and reruns its own probes. Ask verifiers
   to leave probes as runnable tests so the re-check is mechanical. A Haiku session or the lead can rerun them
   when the verifier is gone.
3. A new verifier is warranted only if the fix changed the design, not just the code at the finding.
4. After two verifier rounds the lead decides. The options:
   - accept the remaining item and record why;
   - narrow it to a targeted fix and check it personally against the finding;
   - split it into a follow-up job with its own brief.
   code-foundations build allows up to three re-dispatches per phase. For multi-session builds, two is the
   limit because each round costs a full session plus a gate run.

Wording-only fixes after a verifier round are checked by the lead, not a new verifier.

## 4. What the lead checks without a verifier

The lead reruns the full gate before every commit, reads its output and exit code, and commits by path in a
separate command. It never marks a job done from a report alone. The lead also reads any paper deliverable,
and every round of wording fixes.

## 5. Model tiers for everything else

| Work | Tier |
|---|---|
| Builders and code fix rounds | mid (Sonnet) |
| Mechanical: renames, fixture or log collection, file moves, status checks, cleanup | small (Haiku) |
| Search and exploration subagents | small |
| The lead, plan reviews, design reviews, top-tier verifiers | top (Opus) |

To change a running session's model, send `/model <id>` to it instead of restarting, because a restart throws
away what it has read. Brief sessions by file path, not pasted text.
