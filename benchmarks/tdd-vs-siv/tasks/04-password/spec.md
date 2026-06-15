# Task: extend password validation

Apply the **build-doctrine** skill. This is a MODIFY-EXISTING task.

An existing module `password.py` is provided in your working directory:

```python
def validate(pw: str) -> bool:
    """Return True if the password is acceptable."""
    if len(pw) < 8:
        return False
    return True
```

Add two more rules.

## Done-When items

- DW-4.1: A valid password must contain at least one digit. `validate("Password")` -> `False` (no digit); `validate("Password1")` -> `True`.
- DW-4.2: A valid password must contain at least one uppercase letter. `validate("password1")` -> `False` (no uppercase); `validate("Password1")` -> `True`.

(The existing minimum-length rule of 8 characters still applies.)

## Output paths

- Implementation: `outputs/password.py` (the full modified module)
- Tests: `outputs/test_password.py` (pytest)

Run your tests and make sure they pass before finishing.
