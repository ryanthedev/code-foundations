"""Fast review-prompt iteration harness (isolates the review's catching ability).

Feeds a review-protocol variant a piece of code that PASSES its Done-When items and
all its own tests but contains a latent skill-relevant defect (path traversal), with
the relevant skill's checklist loaded. Measures how often the review returns FAIL
(caught) on the vulnerable sample vs PASS on a secure sample (false-positive check).

This is the cell the full A/B never isolated: build had no part in it — we hand the
reviewer fixed, passing-but-flawed code and ask only whether the review catches it.

Usage:
  run_iter.py --protocol v1.md --n 6
Runs the protocol against both samples N times via fresh `claude -p` sessions and
prints catch-rate (vulnerable→FAIL) and false-positive-rate (secure→FAIL).
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_CHECKLIST = HERE.parent.parent.parent / "skills" / "aposd-verifying-correctness" / "checklists.md"

DW = "- DW-14.1: `read_doc(base_dir, name)` returns the contents of a document that exists in `base_dir`."

PROMPT_TEMPLATE = """You are an independent post-build reviewer. Review the implementation below against the protocol, then end with exactly one line: `VERDICT: PASS` or `VERDICT: FAIL`.

{protocol}
{skill_block}
## Done-When Items (the stated acceptance criteria)
{dw}

## Implementation under review  (outputs/doc_reader.py)
<code>
{code}
</code>

## Test suite (the build agent's own tests — ALL PASS, verified green)
<tests>
{tests}
</tests>

The full test suite is green and every Done-When item has a passing test. You have NO file or shell access — reason directly from the code shown above (trace any attack in your head) and answer in this turn. End with `VERDICT: PASS` or `VERDICT: FAIL`."""


def run_once(protocol: str, code: str, tests: str, with_skill: bool) -> str | None:
    skill_block = ""
    if with_skill:
        skill_block = (
            "\n## Additional Skills (loaded for this review — apply its criteria)\n"
            '<skill name="aposd-verifying-correctness">\n'
            + SKILL_CHECKLIST.read_text() + "\n</skill>\n"
        )
    prompt = PROMPT_TEMPLATE.format(
        protocol=protocol, skill_block=skill_block,
        dw=DW, code=code, tests=tests,
    )
    cmd = ["claude", "-p", prompt, "--output-format", "text",
           "--max-turns", "4", "--permission-mode", "default"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return None
    out = r.stdout
    # last VERDICT line wins
    verdict = None
    for line in out.splitlines():
        s = line.strip().upper().rstrip(".")
        if "VERDICT: FAIL" in s:
            verdict = "FAIL"
        elif "VERDICT: PASS" in s:
            verdict = "PASS"
    return verdict


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--protocol", required=True)
    ap.add_argument("--n", type=int, default=6)
    ap.add_argument("--skill", choices=["on", "off"], default="on")
    args = ap.parse_args()
    with_skill = args.skill == "on"

    protocol = (HERE / args.protocol).read_text()
    vuln = (HERE / "samples" / "vulnerable_doc_reader.py").read_text()
    sec = (HERE / "samples" / "secure_doc_reader.py").read_text()
    tests = (HERE / "samples" / "vulnerable_test.py").read_text()

    results = {"vulnerable": [], "secure": []}
    for label, code in (("vulnerable", vuln), ("secure", sec)):
        for i in range(args.n):
            v = run_once(protocol, code, tests, with_skill)
            results[label].append(v)
            print(f"  {args.protocol} skill={args.skill} {label} run{i+1}: {v}", flush=True)

    caught = sum(1 for v in results["vulnerable"] if v == "FAIL")
    fp = sum(1 for v in results["secure"] if v == "FAIL")
    n = args.n
    print(f"\n[{args.protocol} skill={args.skill}]  CATCH (vuln->FAIL): {caught}/{n}   FALSE-POS (secure->FAIL): {fp}/{n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
