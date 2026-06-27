"""Behavior-preservation suite for the TPMS (welc) kata.

The refactor must make Alarm unit-testable by injecting a pressure source while
preserving the alarm logic: is_alarm_on becomes True iff a reading is < 17 or > 21.
The contract (pinned in the plan): Alarm accepts an injected sensor exposing
pop_next_pressure_psi_value(); it defaults to the real Sensor when none is given.
"""
from tire_pressure_monitoring import Alarm


class _FakeSensor:
    """Deterministic stand-in for the random Sensor — the seam under test."""
    def __init__(self, value):
        self._value = value

    def pop_next_pressure_psi_value(self):
        return self._value


def _alarm_with(value):
    return Alarm(sensor=_FakeSensor(value))


def test_dw_low_pressure_triggers():
    a = _alarm_with(16)          # below 17 -> alarm on
    a.check()
    assert a.is_alarm_on is True


def test_dw_high_pressure_triggers():
    a = _alarm_with(22)          # above 21 -> alarm on
    a.check()
    assert a.is_alarm_on is True


def test_dw_in_range_stays_off():
    a = _alarm_with(19)          # within [17,21] -> alarm off
    a.check()
    assert a.is_alarm_on is False


def test_offdw_low_boundary_17_off():
    a = _alarm_with(17)          # 17 is not < 17 -> off
    a.check()
    assert a.is_alarm_on is False


def test_offdw_high_boundary_21_off():
    a = _alarm_with(21)          # 21 is not > 21 -> off
    a.check()
    assert a.is_alarm_on is False


def test_offdw_starts_off():
    a = _alarm_with(19)
    assert a.is_alarm_on is False  # before any check()
