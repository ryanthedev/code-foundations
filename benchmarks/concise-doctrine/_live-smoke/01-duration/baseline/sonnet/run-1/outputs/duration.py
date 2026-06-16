"""duration.py — parse human-readable duration strings into total seconds."""

import re

_UNIT_SECONDS = {"h": 3600, "m": 60, "s": 1}
_TOKEN = re.compile(r"(\d+)([hms])")


def parse_duration(s: str) -> int:
    """Parse a duration string like "1h30m" into a total number of seconds.

    Valid input is one or more unit-tagged integers using h (hours),
    m (minutes), and s (seconds) in any order.  Examples::

        parse_duration("1h30m")  # 5400
        parse_duration("45s")    # 45
        parse_duration("2h")     # 7200

    Raises:
        ValueError: if the string is empty or contains no recognised
                    unit-tagged tokens (e.g. a bare number like "90").
    """
    if not s:
        raise ValueError(f"Duration string must not be empty.")

    tokens = _TOKEN.findall(s)
    if not tokens:
        raise ValueError(
            f"No valid duration tokens found in {s!r}. "
            "Expected unit-tagged numbers such as '1h30m', '45s', '2h'."
        )

    return sum(int(value) * _UNIT_SECONDS[unit] for value, unit in tokens)
