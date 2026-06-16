"""Deterministic arm-swap for the concise-doctrine full-build A/B.

The benchmark's arm variable is the build-agent.md file itself. For one run the
runner picks an arm ("baseline" or "concise"), and this module copies the matching
variant onto the sandbox agent-file path the runner supplies. The swap is atomic
(write-temp-then-rename) and reversible (baseline is restored on any exit, including
a crash) so a failed run never leaves the agent file holding mutated content.

This module never touches the production `agents/build-agent.md`: the write target is
always a caller-supplied path. The two variant files live next to this module.
"""
from __future__ import annotations

import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Literal

# Directory holding the arm variant files (this file's own directory).
ARMS_DIR = Path(__file__).resolve().parent

Arm = Literal["baseline", "concise"]

# The only valid arm names, each mapped to its variant filename. Membership in this
# dict is the single source of truth for input validation.
_ARM_FILES: dict[str, str] = {
    "baseline": "build-agent.baseline.md",
    "concise": "build-agent.concise.md",
}


def valid_arms() -> tuple[str, ...]:
    """Return the accepted arm names, for callers that build error messages or CLIs."""
    return tuple(_ARM_FILES)


def variant_path(arm: str) -> Path:
    """Resolve an arm name to its variant file path.

    Validates `arm` at the boundary: an arm not in {baseline, concise} raises
    ValueError rather than returning a bogus path. Pure — no filesystem writes.
    """
    if arm not in _ARM_FILES:
        raise ValueError(
            f"unknown arm {arm!r}; expected one of {valid_arms()}"
        )
    path = ARMS_DIR / _ARM_FILES[arm]
    # A missing variant file is a packaging error, not a caller error — surface it
    # distinctly so it is never mistaken for a bad arm name.
    if not path.is_file():
        raise FileNotFoundError(f"arm variant file missing: {path}")
    return path


def set_arm(arm: str, target: str | os.PathLike[str]) -> Path:
    """Point `target` at the chosen arm's variant, atomically; return the target path.

    `target` is the runner's sandbox agent-file path (never the production
    build-agent.md). The variant bytes are written to a temp file in the target's
    directory and then atomically renamed onto `target`, so a crash mid-write leaves
    either the old content or the full new content — never a truncated file.
    """
    source = variant_path(arm)  # validates arm before any write
    target_path = Path(target)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write(target_path, source.read_bytes())
    return target_path


@contextmanager
def arm_session(
    arm: str,
    target: str | os.PathLike[str],
    restore_to: Arm = "baseline",
) -> Iterator[Path]:
    """Set `target` to `arm` for the duration of the block, then restore `restore_to`.

    The restore runs in a finally block, so it happens on a clean exit AND on any
    exception raised inside the block. After the session the target holds the
    `restore_to` arm's content (baseline by default) — a crashed run is left with the
    safe arm, never the mutated one. Re-raises any in-block exception unchanged.
    """
    target_path = set_arm(arm, target)
    try:
        yield target_path
    finally:
        # Always restore; never swallow the in-block exception (no bare except,
        # nothing returned from finally that would suppress propagation).
        set_arm(restore_to, target_path)


def _atomic_write(target: Path, data: bytes) -> None:
    """Write `data` to `target` via a same-directory temp file and atomic rename.

    Same directory guarantees os.replace is a rename (atomic on POSIX), not a
    cross-filesystem copy. The temp file is removed if the rename never happens.
    """
    fd, tmp_name = tempfile.mkstemp(dir=str(target.parent), prefix=".arm-", suffix=".tmp")
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        os.replace(tmp_path, target)  # atomic: target now holds the full new content
    finally:
        # If the rename succeeded the temp file is gone; if it raised, clean it up.
        if tmp_path.exists():
            tmp_path.unlink()
