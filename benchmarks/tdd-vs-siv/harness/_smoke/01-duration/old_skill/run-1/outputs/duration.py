import re

_MULT = {"h": 3600, "m": 60, "s": 1}


def parse_duration(s: str) -> int:
    s = s.strip().lower()
    if not s:
        raise ValueError("empty duration")
    if not re.fullmatch(r"(\d+[hms])+", s):
        raise ValueError(f"invalid duration: {s!r}")
    total = 0
    for num, unit in re.findall(r"(\d+)([hms])", s):
        total += int(num) * _MULT[unit]
    return total
