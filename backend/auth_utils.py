"""
TRUVEX Cryptographic Authentication & Password Utilities.
Uses PBKDF2 HMAC-SHA256 and python-jose for secure JWT tokens.
"""

from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import os
import secrets
from typing import Optional
from jose import JWTError, jwt

SECRET_KEY = os.getenv("JWT_SECRET") or os.getenv("SECRET_KEY", "")
if not SECRET_KEY:
    import warnings
    SECRET_KEY = secrets.token_urlsafe(64)
    warnings.warn(
        "JWT_SECRET is not set — using an ephemeral random key. "
        "Tokens will NOT survive server restarts. Set JWT_SECRET in production.",
        stacklevel=2,
    )
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 120))


def hash_password(password: str) -> str:
    """Hashes a password with a random 16-byte salt using PBKDF2 HMAC-SHA256."""
    salt = secrets.token_bytes(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return f"pbkdf2_sha256$100000${salt.hex()}${key.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a password against the stored PBKDF2 hash using timing-safe comparison."""
    try:
        parts = hashed_password.split("$")
        if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
            return False
        iterations = int(parts[1])
        salt = bytes.fromhex(parts[2])
        expected_key = bytes.fromhex(parts[3])
        actual_key = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(expected_key, actual_key)
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generates a signed JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """Decodes and validates a signed JWT access token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
