"""
routers/users.py — User profile endpoints

Routes:
  GET   /api/users/{user_id}/profile  → Public profile + published posts
  PUT   /api/users/me                 → Update own profile
  POST  /api/users/me/avatar          → Upload avatar image
  DELETE /api/users/me/avatar         → Remove avatar image
"""

import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user, get_optional_user
from app.models.user import User
from app.schemas.user import UserPublic, UserUpdateProfile
from app.schemas.post import PostSummary
from app.repositories import user_repository, post_repository
from app.config import get_settings

router = APIRouter(prefix="/api/users", tags=["Users"])
settings = get_settings()


@router.get("/{user_id}/profile")
def get_profile(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user),
):
    """Public profile — avatar, bio, and all posts (including drafts for own profile)."""
    user = user_repository.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Include drafts only when viewing own profile
    is_own_profile = current_user and current_user.id == user_id
    posts = post_repository.get_user_posts(db, user_id, include_drafts=is_own_profile)
    current_user_id = current_user.id if current_user else None

    return {
        "user": UserPublic.model_validate(user),
        "posts": [PostSummary.model_validate({
            **{c.name: getattr(p, c.name) for c in p.__table__.columns},
            "author": user,
            "tags": p.tags,
            "like_count": post_repository.get_like_count(db, p.id),
            "comment_count": 0,
            "is_liked_by_me": post_repository.is_liked_by_user(db, p.id, current_user_id) if current_user_id else False,
        }) for p in posts],
    }


@router.put("/me", response_model=UserPublic)
def update_profile(
    data: UserUpdateProfile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    updated = user_repository.update_user_profile(db, current_user, data.name, data.bio)
    return UserPublic.model_validate(updated)


@router.post("/me/avatar", response_model=UserPublic)
async def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload profile avatar.

    💡 CONCEPT: File Uploads (multipart/form-data)
       Unlike JSON, files are sent as multipart/form-data.
       FastAPI's UploadFile gives us the file-like object.
       We validate type + size before saving to prevent abuse.
    """
    # Validate content type
    allowed_types = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, GIF, WebP allowed")

    # Read and check size
    content = await file.read()
    max_bytes = settings.max_file_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(status_code=400, detail=f"File too large. Max {settings.max_file_size_mb}MB")

    # Save with a unique filename to prevent overwrites and path traversal
    ext = file.filename.rsplit(".", 1)[-1].lower()
    filename = f"{uuid.uuid4()}.{ext}"
    upload_path = os.path.join(settings.upload_dir, "avatars")
    os.makedirs(upload_path, exist_ok=True)

    filepath = os.path.join(upload_path, filename)
    with open(filepath, "wb") as f:
        f.write(content)

    avatar_url = f"/uploads/avatars/{filename}"
    updated = user_repository.update_user_profile(db, current_user, avatar_url=avatar_url)
    return UserPublic.model_validate(updated)


@router.delete("/me/avatar", response_model=UserPublic)
def remove_avatar(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove the current user's profile avatar."""
    current_user.avatar_url = None
    db.commit()
    db.refresh(current_user)
    return UserPublic.model_validate(current_user)
