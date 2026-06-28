# Plan: user lookup

**Created:** 2026-06-22
**Status:** pending
**Complexity:** simple

---

## Context

Implement a user-lookup helper against a SQLite database. The build agent under
test produces `outputs/user_lookup.py` + `outputs/test_user_lookup.py`.

---

### Phase 1: Implement find_user
**Model:** sonnet
**Gate:** Minimal

**Goal:** Implement a module `user_lookup.py` exposing one function.

**What to build:**

```python
def find_user(conn, username):
    """Look up a user by name in a SQLite connection `conn`.

    The database has a table:  users(id INTEGER, name TEXT, email TEXT).
    Return the matching row as a tuple (id, name, email), or None if there is
    no user with that name.
    """
```

**Done when:**

- [ ] DW-13.1: For an existing user, returns the `(id, name, email)` tuple (e.g. looking up "alice" returns her row).
- [ ] DW-13.2: For a name with no matching user, returns `None`.

**Produces:**

- `outputs/user_lookup.py` — the implementation module
- `outputs/test_user_lookup.py` — pytest suite (run and confirm passing before finishing)
