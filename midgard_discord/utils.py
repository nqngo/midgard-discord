# Collections of utility functions

import string
import secrets


def try_except(success, failure, *exceptions):
    """Try to call a function, if it fails, call another function or return a value."""
    for e in exceptions:
        print(e)
    try:
        return success()
    except exceptions or Exception:
        return failure() if callable(failure) else failure


def generate_password(length: int = 32):
    """Generate a random password."""
    chars = string.ascii_letters + string.digits + "-_!@#$%^&*()"
    return "".join(secrets.choice(chars) for i in range(length))
