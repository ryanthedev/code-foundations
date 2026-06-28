# Plan: extend password validation

**Created:** 2026-06-19
**Status:** pending
**Complexity:** simple

---

## Context

Extend an existing password validator to add two new rules. Adherence-test task: the build agent under test modifies `password.py` (provided in `starter/`) and produces `outputs/password.py` + `outputs/test_password.py`.

---

### Phase 1: Add digit and uppercase rules to password validator
**Model:** sonnet
**Gate:** Minimal
**Skills:** cc-defensive-programming

**Goal:** Modify the provided `password.py` (copy from `starter/password.py`) to add two new validation rules.

**What to build:**

An existing module `password.py` is provided in your working directory:

```python
def validate(pw: str) -> bool:
    """Return True if the password is acceptable."""
    if len(pw) < 8:
        return False
    return True
```

Add two more rules. (The existing minimum-length rule of 8 characters still applies.)

**Done when:**

- [ ] DW-4.1: A valid password must contain at least one digit. `validate("Password")` → `False` (no digit); `validate("Password1")` → `True`.
- [ ] DW-4.2: A valid password must contain at least one uppercase letter. `validate("password1")` → `False` (no uppercase); `validate("Password1")` → `True`.

**Produces:**

- `outputs/password.py` — the full modified module (copy starter, then modify)
- `outputs/test_password.py` — pytest suite (run and confirm passing before finishing)
