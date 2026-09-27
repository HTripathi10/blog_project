"""
routers/auth.py — Authentication endpoints

Routes:
  POST /api/auth/register     → Email/password registration
  POST /api/auth/login        → Email/password login
  GET  /api/auth/google       → Redirect to Google OAuth
  GET  /api/auth/google/callback → Google OAuth callback
  GET  /api/auth/me           → Get current user profile

💡 CONCEPT: OAuth2 Authorization Code Flow
   Step 1: We redirect user to Google with our client_id + desired scopes
   Step 2: User logs in at Google and approves
   Step 3: Google redirects back to our callback URL with a `code`
   Step 4: We exchange `code` for an access_token (server-to-server, secret!)
   Step 5: We use access_token to fetch the user's profile from Google API
   Step 6: Create/find user in our DB, issue our own JWT
"""

from urllib.parse import urlencode, urlparse

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserRegister, UserLogin, TokenResponse, UserPublic
from app.repositories import user_repository
from app.utils.password import hash_password, verify_password
from app.utils.jwt import create_access_token
from app.middleware.auth import get_current_user
from app.models.user import User
from app.config import get_settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
settings = get_settings()


def _safe_frontend_origin(candidate: str | None) -> str:
    """Only allow local frontend origins so OAuth cannot bounce to a random host."""
    fallback = settings.frontend_url.rstrip("/")
    if not candidate:
        return fallback
    parsed = urlparse(candidate)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return fallback
    if parsed.hostname not in {"localhost", "127.0.0.1"}:
        return fallback
    return f"{parsed.scheme}://{parsed.netloc}"


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, db: Session = Depends(get_db)):
    """Register with email + password."""
    # Check if email is already taken
    existing = user_repository.get_user_by_email(db, data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(data.password)
    user = user_repository.create_local_user(db, data.email, data.name, hashed)
    token = create_access_token(user.id)
    return TokenResponse(access_token=token, user=UserPublic.model_validate(user))


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    """Login with email + password, returns JWT."""
    user = user_repository.get_user_by_email(db, data.email)

    # ⚠️ Return same error for "user not found" and "wrong password"
    # Never reveal which one — that's a security best practice (enumeration attack)
    if not user or not user.hashed_password or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    token = create_access_token(user.id)
    return TokenResponse(access_token=token, user=UserPublic.model_validate(user))


@router.get("/google")
def google_login(next: str | None = Query(default=None)):
    """Redirect the browser to Google's OAuth consent screen."""
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "state": _safe_frontend_origin(next),
    }
    query = urlencode(params)
    return RedirectResponse(f"https://accounts.google.com/o/oauth2/v2/auth?{query}")


@router.get("/google/callback")
async def google_callback(
    code: str,
    db: Session = Depends(get_db),
    state: str | None = Query(default=None),
):
    """Exchange Google auth code for user profile, issue our JWT."""
    async with httpx.AsyncClient() as client:
        # Step 4: Exchange code for tokens
        token_resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        token_data = token_resp.json()
        access_token = token_data.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to obtain Google access token")

        # Step 5: Fetch user profile
        profile_resp = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        profile = profile_resp.json()

    email = profile.get("email")
    name = profile.get("name", email)
    avatar_url = profile.get("picture")

    # Step 6: Upsert user and issue JWT
    user = user_repository.get_user_by_email(db, email)
    if not user:
        user = user_repository.create_oauth_user(db, email, name, avatar_url, "google")

    jwt_token = create_access_token(user.id)
    frontend = _safe_frontend_origin(state)
    return RedirectResponse(f"{frontend}/oauth/callback?token={jwt_token}")


@router.get("/me", response_model=UserPublic)
def get_me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return current_user
