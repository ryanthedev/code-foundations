"""Multi-skill gauntlet for the generic review mechanism.

The skill-as-acceptance-criteria mechanism was validated on ONE skill (security /
path traversal). The claim is that it's GENERIC — any loaded skill's criteria gain
FAIL standing. This runs it across diverse skills + defect KINDS to see where the
mechanism fires, where it correctly stays restrained, and where it has gaps.

Per case: a piece of code that passes its Done-When item and its own tests but
violates the paired skill's criteria. We run the generic base review (v2.md) with
the skill loaded (catch?) and without (delta), plus a clean variant (false-positive
check). Reasoning-only (claude -p, no tools) — tests whether the prompt induces the
right verdict.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILLS = HERE.parent.parent.parent / "skills"
V2 = (HERE / "v2.md").read_text()


def skill_text(name: str) -> str:
    d = SKILLS / name
    f = d / "checklists.md"
    return (f if f.is_file() else d / "SKILL.md").read_text()


PROMPT = """You are an independent post-build reviewer. Review the implementation against the protocol, then end with exactly one line: `VERDICT: PASS` or `VERDICT: FAIL`.

{protocol}
{skill_block}
## Done-When Items (the stated acceptance criteria)
{dw}

## Implementation under review
<code>
{code}
</code>

The full test suite is green and every Done-When item has a passing test. You have NO file or shell access — reason from the code shown (trace any case in your head) and answer in this turn. End with `VERDICT: PASS` or `VERDICT: FAIL`."""


# Each case: skill, DW, a flawed impl (passes DW+tests, violates the skill), and a
# clean impl (satisfies the skill) for the false-positive check.
CASES = [
    {
        "name": "defensive/silent-except",
        "skill": "cc-defensive-programming",
        "expect": "FAIL",
        "dw": "- DW: `load_config(path)` returns the parsed dict from a JSON file at `path`.",
        "flawed": '''import json
def load_config(path):
    """Return the parsed config dict from the JSON file at path."""
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return {}
''',
        "clean": '''import json
def load_config(path):
    """Return the parsed config dict from the JSON file at path."""
    with open(path) as f:
        return json.load(f)
''',
    },
    {
        "name": "clarity/lying-docstring",
        "skill": "code-clarity-and-docs",
        "expect": "FAIL",
        "dw": "- DW: `top_scores(scores)` returns the three highest scores from the list.",
        "flawed": '''def top_scores(scores):
    """Return the three highest scores, sorted in ASCENDING order (lowest of the three first)."""
    return sorted(scores, reverse=True)[:3]
''',  # docstring claims ascending; code returns descending -> doc lies
        "clean": '''def top_scores(scores):
    """Return the three highest scores, in descending order (highest first)."""
    return sorted(scores, reverse=True)[:3]
''',
    },
    {
        "name": "routine/too-many-params",
        "skill": "cc-routine-and-class-design",
        "expect": "FAIL",
        "dw": "- DW: `make_report(...)` returns a formatted one-line report string.",
        "flawed": '''def make_report(title, author, date, body, footer, theme, font, margin, columns):
    """Return a formatted report string."""
    return f"{title} by {author} ({date}): {body}"
''',
        "clean": '''def make_report(spec):
    """Return a formatted report string. `spec` carries title, author, date, body."""
    return f"{spec.title} by {spec.author} ({spec.date}): {spec.body}"
''',
    },
    {
        "name": "control-flow/deep-nesting (restraint)",
        "skill": "cc-control-flow-quality",
        "expect": "PASS",  # matter-of-degree, correct code -> must NOT false-FAIL
        "dw": "- DW: `classify(n)` returns 'neg','zero','small','big' per the rules.",
        "flawed": '''def classify(n):
    """Classify n."""
    if n < 0:
        return "neg"
    else:
        if n == 0:
            return "zero"
        else:
            if n < 100:
                return "small"
            else:
                return "big"
''',
        "clean": '''def classify(n):
    if n < 0:
        return "neg"
    if n == 0:
        return "zero"
    return "small" if n < 100 else "big"
''',
    },
]


def verdict(code: str, skill: str | None, dw: str) -> str | None:
    block = ""
    if skill:
        block = f'\n## Additional Skills (loaded for this review — apply its criteria)\n<skill name="{skill}">\n{skill_text(skill)}\n</skill>\n'
    prompt = PROMPT.format(protocol=V2, skill_block=block, dw=dw, code=code)
    try:
        r = subprocess.run(["claude", "-p", prompt, "--output-format", "text",
                            "--max-turns", "4", "--permission-mode", "default"],
                           capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return None
    v = None
    for line in r.stdout.splitlines():
        s = line.strip().upper().rstrip(".")
        if "VERDICT: FAIL" in s:
            v = "FAIL"
        elif "VERDICT: PASS" in s:
            v = "PASS"
    return v


def main() -> int:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    print(f"{'case':36}{'expect':8}{'skill-on flawed':18}{'skill-off flawed':18}{'skill-on clean':16}")
    for c in CASES:
        on_f = [verdict(c["flawed"], c["skill"], c["dw"]) for _ in range(n)]
        off_f = [verdict(c["flawed"], None, c["dw"]) for _ in range(n)]
        on_c = [verdict(c["clean"], c["skill"], c["dw"]) for _ in range(n)]
        fail = lambda lst: f"{sum(1 for x in lst if x=='FAIL')}/{n} FAIL"
        print(f"{c['name']:36}{c['expect']:8}{fail(on_f):18}{fail(off_f):18}{fail(on_c):16}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
