import secrets

_TEMP_PASSWORD_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789"


def generate_temp_password(length=12):
    """Random password avoiding visually ambiguous characters (0/O, 1/l/I)."""
    return "".join(secrets.choice(_TEMP_PASSWORD_CHARS) for _ in range(length))
