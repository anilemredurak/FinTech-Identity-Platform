import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, Any

import jwt

from app.core.config import settings


def _load_private_key() -> str:
    with open(settings.JWT_PRIVATE_KEY_PATH, "r") as f:
        return f.read()


def _load_public_key() -> str:
    with open(settings.JWT_PUBLIC_KEY_PATH, "r") as f:
        return f.read()


def create_access_token(subject: str, expires_in: int | None = None, extra: Dict[str, Any] | None = None) -> str:
    expires = expires_in or settings.ACCESS_TOKEN_EXPIRE_SECONDS
    now = int(time.time())
    payload = {
        "sub": str(subject),
        "iat": now,
        "exp": now + int(expires),
    }
    if extra:
        payload.update(extra)
    token = jwt.encode(payload, _load_private_key(), algorithm=settings.JWT_ALGORITHM)
    return token


def decode_access_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, _load_public_key(), algorithms=[settings.JWT_ALGORITHM])


def make_refresh_token() -> str:
    # Strong random token from SHA256 of time+randomness
    rnd = hashlib.sha256(f"{time.time()}-{hashlib.sha256().hexdigest()}".encode()).hexdigest()
    return rnd


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
