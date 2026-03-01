# d:\PythonProjects\GroceryStoreInventoryPOS\auth\passwords.py
from __future__ import annotations

import base64
import hashlib
import hmac
import os


_PBKDF2_PREFIX = "pbkdf2_sha256"


def hash_password(password: str, iterations: int = 200_000) -> str:
    """
    Returns a self-contained password hash string suitable for storage in user_account.PasswordHash.

    Format:
      pbkdf2_sha256$<iterations>$<salt_b64>$<hash_b64>
    """
    if password is None or password == "":
        raise ValueError("Password is required.")

    if iterations < 50_000:
        raise ValueError("Iterations must be at least 50000.")

    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations, dklen=32)

    salt_b64 = base64.b64encode(salt).decode("ascii")
    hash_b64 = base64.b64encode(dk).decode("ascii")
    return f"{_PBKDF2_PREFIX}${iterations}${salt_b64}${hash_b64}"


def verify_password(password: str, stored_hash: str) -> bool:
    """
    Verifies a password against the stored hash.

    Supported formats:
      1) pbkdf2_sha256$<iterations>$<salt_b64>$<hash_b64>
      2) Plaintext fallback: stored_hash is treated as the password itself.
         This exists only to let your current seed data work immediately.
    """
    if password is None:
        return False
    if stored_hash is None:
        return False

    stored_hash = stored_hash.strip()
    if stored_hash == "":
        return False

    parts = stored_hash.split("$")
    if len(parts) == 4 and parts[0] == _PBKDF2_PREFIX:
        try:
            iterations = int(parts[1])
            salt = base64.b64decode(parts[2].encode("ascii"))
            expected = base64.b64decode(parts[3].encode("ascii"))
        except Exception:
            return False

        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations, dklen=len(expected))
        return hmac.compare_digest(actual, expected)

    # Temporary fallback for your current seed strings.
    return hmac.compare_digest(password, stored_hash)