import hashlib
import hmac
from typing import Optional


def generate_verification_code(key: str, secret_key: Optional[str] = None) -> str:
    """Return a stable 6-digit verification code derived from confirmation key."""
    if secret_key is None:

        from django.conf import settings

        secret_key = getattr(settings, "SECRET_KEY", "foo")

    digest = hmac.new(secret_key.encode("utf-8"), key.encode("utf-8"), hashlib.sha256)
    numeric_digits = "".join(filter(str.isdigit, digest.hexdigest()))[:6]
    return numeric_digits.zfill(6)
