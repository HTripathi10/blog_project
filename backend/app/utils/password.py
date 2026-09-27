"""
utils/password.py — Password hashing with bcrypt directly

💡 CONCEPT: Why bcrypt?
   You NEVER store plain passwords. If your DB is leaked, users are exposed.
   bcrypt is a "slow" hash function — deliberately slow to make brute-force
   attacks take years instead of seconds.

   bcrypt also adds a random "salt" to every hash, so two users with the
   same password will have different hashes. This prevents rainbow table attacks.
"""

import bcrypt


def hash_password(plain_password: str) -> str:
    """Hash a plain-text password using bcrypt. Returns a bcrypt hash string."""
    pwd_bytes = plain_password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a stored bcrypt hash."""
    try:
        pwd_bytes = plain_password.encode("utf-8")[:72]
        hash_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except Exception:
        return False
