"""
routers/likes.py — Like/Unlike toggle endpoint

Routes:
  POST /api/posts/{post_id}/like → Toggle like (like if not liked, unlike if liked)

💡 CONCEPT: Idempotent Toggle
   Calling this endpoint twice should result in the same state as calling it once.
   First call: like is created  → returns { liked: true,  like_count: N+1 }
   Second call: like is deleted → returns { liked: false, like_count: N }
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.comment import Like
from app.models.post import Post
from app.repositories.post_repository import get_like_count

router = APIRouter(prefix="/api/posts/{post_id}/like", tags=["Likes"])


@router.post("")
def toggle_like(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify post exists
    post = db.query(Post).filter(Post.id == post_id, Post.status == "published").first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Check if already liked
    existing_like = db.query(Like).filter(
        Like.post_id == post_id, Like.user_id == current_user.id
    ).first()

    if existing_like:
        # Unlike — remove the row
        db.delete(existing_like)
        db.commit()
        liked = False
    else:
        # Like — add the row
        like = Like(post_id=post_id, user_id=current_user.id)
        db.add(like)
        try:
            db.commit()
            liked = True
        except IntegrityError:
            # Race condition: two requests at the same time, DB unique constraint fired
            db.rollback()
            liked = True  # Already liked, treat as success

    return {"liked": liked, "like_count": get_like_count(db, post_id)}
