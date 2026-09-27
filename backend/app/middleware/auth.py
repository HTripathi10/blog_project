"""
middleware/auth.py — FastAPI dependency for extracting the current user from JWT

💡 CONCEPT: FastAPI Dependencies (Depends)
   Instead of repeating JWT validation logic in every route, we define it once
   as a "dependency". FastAPI injects it automatically.

   get_current_user  → raises 401 if no valid token (protected routes)
   get_optional_user → returns None if no token (public routes that can
                        optionally show personalised data like "is_liked_by_me")

💡 CONCEPT: OAuth2PasswordBearer
   This tells FastAPI to look for the token in the Authorization header:
       Authorization: Bearer eyJhbGci...
   It's part of the OpenAPI spec, so Swagger UI gets a "Authorize" button for free.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.utils.jwt import decode_access_token
from app.models.user import User

# tokenUrl is the endpoint that issues tokens (used by Swagger UI)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Requires authentication. Raises HTTP 401 if token is missing or invalid.
    Use this on any route that must be logged in.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception

    user_id = decode_access_token(token)
    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if user is None:
        raise credentials_exception

    return user


def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    Optional authentication. Returns the User if logged in, None otherwise.
    Use this on public routes that need to personalise output for logged-in users.
    Example: showing 'is_liked_by_me' on a public post listing.
    """
    if not token:
        return None
    user_id = decode_access_token(token)
    if user_id is None:
        return None
    return db.query(User).filter(User.id == user_id, User.is_active == True).first()
