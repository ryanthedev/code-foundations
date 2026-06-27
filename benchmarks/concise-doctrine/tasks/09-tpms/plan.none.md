# Plan: make the tire-pressure Alarm testable

**Created:** 2026-06-22
**Status:** pending
**Complexity:** simple

---

## Context

A working `tire_pressure_monitoring.py` is provided (copy from `starter/`). The
`Alarm` class is correct but hard to unit-test: it constructs a random `Sensor`
internally, so its alarm logic can't be exercised with controlled values. Refactor
it to be testable while preserving its exact behavior. The build agent under test
produces `outputs/tire_pressure_monitoring.py` + `outputs/test_tire_pressure_monitoring.py`.

---

### Phase 1: Refactor Alarm for testability
**Model:** sonnet
**Gate:** Minimal

**Goal:** Make `Alarm` unit-testable without changing its observable behavior.

**What to build:**

Keep the module self-contained (the `Sensor` class stays in this file). Preserve
the class names `Alarm` and `Sensor` and the `Alarm.check()` / `Alarm.is_alarm_on`
interface.

**Done when:**

- [ ] DW-9.1: After `check()`, `is_alarm_on` is True iff the current pressure reading is below 17 or above 21; a fresh `Alarm` starts with `is_alarm_on == False`. This threshold behavior is unchanged from the original.
- [ ] DW-9.2: `Alarm` accepts an injected pressure source so its logic can be unit-tested with controlled values: `Alarm(sensor=<obj with pop_next_pressure_psi_value()>)`. When no sensor is given, it defaults to the real `Sensor()`.

**Produces:**

- `outputs/tire_pressure_monitoring.py` — the refactored module (copy starter, then refactor)
- `outputs/test_tire_pressure_monitoring.py` — pytest suite (run and confirm passing before finishing)
