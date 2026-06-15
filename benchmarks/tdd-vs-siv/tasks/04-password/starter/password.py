def validate(pw: str) -> bool:
    """Return True if the password is acceptable."""
    if len(pw) < 8:
        return False
    return True
