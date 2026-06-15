# Task: parse_duration

Implement a duration parser in Python.

Apply the **build-doctrine** skill to this task.

## What to build

A module `duration.py` exposing one function:

```python
def parse_duration(s: str) -> int:
    """Parse a duration string like "1h30m" into a total number of seconds."""
```

Units: `h` (hours), `m` (minutes), `s` (seconds).

## Done-When items

- DW-1.1: A string of unit-tagged numbers parses to the summed total in seconds. `"1h30m"` → `5400`, `"45s"` → `45`, `"2h"` → `7200`.
- DW-1.2: A bare number with no unit is invalid → raise `ValueError`. `"90"` → `ValueError`.
- DW-1.3: An empty string is invalid → raise `ValueError`. `""` → `ValueError`.

## Output paths

- Implementation: `outputs/duration.py`
- Tests: `outputs/test_duration.py` (pytest)

Run your tests and make sure they pass before finishing.
