"""
routers/posts.py — Blog post CRUD endpoints

Routes:
  GET    /api/posts              → List published posts (public, paginated, searchable)
  POST   /api/posts              → Create post (auth required)
  GET    /api/posts/{id}         → Get single post (public)
  PUT    /api/posts/{id}         → Update post (owner only)
  DELETE /api/posts/{id}         → Delete post (owner only)
  PATCH  /api/posts/{id}/publish → Toggle draft/published (owner only)

💡 CONCEPT: Ownership Check
   When a user tries to edit/delete a post, we verify post.user_id == current_user.id
   This is enforced in the SERVICE layer (not the route) — separation of concerns.
   The route handles HTTP; the service handles business rules.
"""

import math
import os
import uuid
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session
from typing import Optional

from app.config import get_settings
from app.database import get_db
from app.middleware.auth import get_current_user, get_optional_user
from app.models.user import User
from app.schemas.post import PostCreate, PostUpdate, PostDetail, PostSummary, PaginatedPosts
from app.repositories import post_repository
from app.utils.content_filter import validate_multiple_fields

settings = get_settings()

router = APIRouter(prefix="/api/posts", tags=["Posts"])


def _build_post_summary(post, db: Session, current_user_id: Optional[int] = None) -> dict:
    """Build the response dict with computed fields (like_count, is_liked_by_me)."""
    like_count = post_repository.get_like_count(db, post.id)
    is_liked = (
        post_repository.is_liked_by_user(db, post.id, current_user_id)
        if current_user_id else False
    )
    return {
        **{c.name: getattr(post, c.name) for c in post.__table__.columns},
        "author": post.author,
        "tags": post.tags,
        "like_count": like_count,
        "comment_count": len(post.comments) if hasattr(post, "comments") else 0,
        "is_liked_by_me": is_liked,
    }


@router.get("", response_model=PaginatedPosts)
def list_posts(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=50, description="Posts per page"),
    search: Optional[str] = Query(None, description="Search in title and content"),
    tag: Optional[str] = Query(None, description="Filter by tag name"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """List all published posts. Public endpoint with optional auth for 'is_liked_by_me'."""
    posts, total = post_repository.get_published_posts(db, page, limit, search, tag)
    current_user_id = current_user.id if current_user else None

    items = [
        PostSummary.model_validate(_build_post_summary(post, db, current_user_id))
        for post in posts
    ]
    return PaginatedPosts(
        items=items,
        total=total,
        page=page,
        limit=limit,
        pages=math.ceil(total / limit) if total > 0 else 1,
    )


@router.post("/cover-image")
async def upload_cover_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Upload a header image for a post. Returns a URL to save on the post."""
    allowed_types = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, GIF, WebP allowed")

    content = await file.read()
    max_bytes = settings.max_file_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(status_code=400, detail=f"File too large. Max {settings.max_file_size_mb}MB")

    ext = (file.filename or "jpg").rsplit(".", 1)[-1].lower()
    if ext not in {"jpg", "jpeg", "png", "gif", "webp"}:
        ext = "jpg"
    filename = f"{uuid.uuid4()}.{ext}"
    upload_path = os.path.join(settings.upload_dir, "covers")
    os.makedirs(upload_path, exist_ok=True)

    with open(os.path.join(upload_path, filename), "wb") as handle:
        handle.write(content)

    return {"url": f"/uploads/covers/{filename}"}


@router.post("", response_model=PostDetail, status_code=status.HTTP_201_CREATED)
def create_post(
    data: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # 401 if not logged in
):
    """Create a new post. Defaults to 'draft' status."""
    # Validate content for profanity
    is_valid, error_msg = validate_multiple_fields({
        "title": data.title,
        "content": data.content,
    })
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    post = post_repository.create_post(db, data, current_user.id)
    return PostDetail.model_validate(_build_post_summary(post, db, current_user.id))


@router.get("/{post_id}", response_model=PostDetail)
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Get a single post. Public, but shows 'is_liked_by_me' if authenticated."""
    post = post_repository.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Show drafts only to the author
    current_user_id = current_user.id if current_user else None
    if post.status == "draft" and post.user_id != current_user_id:
        raise HTTPException(status_code=404, detail="Post not found")

    return PostDetail.model_validate(_build_post_summary(post, db, current_user_id))


@router.put("/{post_id}", response_model=PostDetail)
def update_post(
    post_id: int,
    data: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a post. Only the author can do this."""
    post = post_repository.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # 💡 CONCEPT: Ownership check — 403 Forbidden (authenticated but not allowed)
    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You don't own this post")

    # Validate content for profanity
    fields_to_validate = {}
    if data.title is not None:
        fields_to_validate["title"] = data.title
    if data.content is not None:
        fields_to_validate["content"] = data.content

    if fields_to_validate:
        is_valid, error_msg = validate_multiple_fields(fields_to_validate)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

    updated = post_repository.update_post(db, post, data)
    return PostDetail.model_validate(_build_post_summary(updated, db, current_user.id))


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a post. Only the author can do this."""
    post = post_repository.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You don't own this post")

    post_repository.delete_post(db, post)


@router.patch("/{post_id}/publish", response_model=PostDetail)
def toggle_publish(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Toggle between draft and published. Only the author can do this."""
    post = post_repository.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You don't own this post")

    new_status = "published" if post.status == "draft" else "draft"
    updated = post_repository.update_post(db, post, PostUpdate(status=new_status))
    return PostDetail.model_validate(_build_post_summary(updated, db, current_user.id))
