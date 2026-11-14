# Plan speed review

Run this on a new plan before any builder starts. Use a top-tier reviewer session or the lead. The output is a
ranked table written next to the plan:

| # | Change | Evidence (file:line, measurement, or "unverified") | Saving (ratio or count, never a duration) | Risk |

Tag each row **verified**, meaning a measurement, a file read or a command output, or **proposal**. Only verified
rows become rules for the build. Proposals get tried, measured, then promoted.

## Questions

Answer each with a row, or with "no change" and the evidence.

**Gates**
1. How many times does one full gate run build the workspace and run the full test suite? Count fresh targets
   and test passes. Anything over one of each is the first row.
2. Do builders and verifiers run lower phases on every gate run? What share of a run is that? Time one run's
   steps from log modification times.
3. Do any functional gate steps have timing thresholds? Which ones will flake at the machine's typical load?
4. Is there a quiet runner for timing verdicts, and does it refuse to measure nothing?

**Disk and scratch**
5. What does one gate run leave on disk, and who deletes it? Multiply by the expected number of runs: count
   phases × jobs × (builder + verifier + fix rounds + lead) runs.
6. Is there a free-disk floor in every gate, and a recurring disk check for the lead?
7. Can any test write outside the repo (user data dirs, global caches)?

**Load and concurrency**
8. What caps concurrent heavy work: a session count, a lock, or measured load? Is the planned builder count
   affordable on this machine's cores while other work runs on it?
9. Can two jobs edit the same files, or can a gate pick up another job's untracked files? Is there a freeze on
   files under verification?

**Verification and models**
10. Which jobs cross a trust boundary or involve concurrency or timing? Do exactly those get the top-tier
    verifier and a security review of the diff before it?
11. What happens after a verifier FAIL? A plan that starts a new builder **and** a new verifier each round, or
    loops "until PASS", gets a row: the same verifier re-checks by rerunning its probes, and the lead decides
    after two rounds.
12. Is each job's model the cheapest tier that does it well? Check builders, mechanical jobs and searches.
13. Which bug classes will recur across jobs? Panics on untrusted input and unbounded growth are typical. Is
    there a fuzz harness or test kit for them?

**Devices**
14. Which tests need a real device, and why? Everything else goes to the Simulator. Is the device work one
    rehearsed script, dry-run on the Simulator?
15. Whose device is it, and when is it free?

**Order**
16. Which jobs are unblocked now but queued behind a cap that the changes above would lift?
17. Which risky assumption (lowest-confidence item in the plan) could be tested by a small early job instead of
    being found late?

Close with any questions only the owner can answer (spending, devices, security defaults), each with a
recommended default.
