"""
utils/jwt.py — JWT token creation and verification

💡 CONCEPT: JSON Web Token (JWT)
   A JWT has 3 parts: Header.Payload.Signature
   - Header: algorithm used (HS256)
   - Payload: the data (user_id, expiry) — readable by anyone, NOT encrypted!
   - Signature: HMAC of Header+Payload using JWT_SECRET — proves authenticity

   The server creates a JWT on login. The client stores it and sends it
   with every request. The server verifies the signature — no DB lookup needed.
   That's why JWTs are "stateless".

   ⚠️ NEVER put sensitive data in the payload (passwords, credit cards).
      Anyone can base64-decode it without the secret.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from app.config import get_settings

settings = get_settings()


def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT containing the user's ID."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload = {
        "sub": str(user_id),   # "sub" (subject) is a JWT standard claim
        "exp": expire,          # "exp" (expiry) — jose validates this automatically
        "iat": datetime.now(timezone.utc),  # "iat" = issued at
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> Optional[int]:
    """
    Decode and verify a JWT. Returns user_id if valid, None if invalid/expired.
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("sub")
        if user_id is None:
            return None
        return int(user_id)
    except JWTError:
        return None
