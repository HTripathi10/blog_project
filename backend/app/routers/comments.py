"""
routers/comments.py — Comment CRUD endpoints

Routes:
  GET    /api/posts/{post_id}/comments         → List comments on a post (public)
  POST   /api/posts/{post_id}/comments         → Add comment (auth required)
  PUT    /api/posts/{post_id}/comments/{id}    → Edit comment (owner only)
  DELETE /api/posts/{post_id}/comments/{id}    → Delete comment (owner only)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.middleware.auth import get_current_user, get_optional_user
from app.models.user import User
from app.models.comment import Comment
from app.models.post import Post
from app.schemas.comment import CommentCreate, CommentUpdate, CommentResponse
from app.utils.content_filter import validate_content

router = APIRouter(prefix="/api/posts/{post_id}/comments", tags=["Comments"])


def _get_post_or_404(db: Session, post_id: int) -> Post:
    post = db.query(Post).filter(Post.id == post_id, Post.status == "published").first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


def _get_comment_or_404(db: Session, comment_id: int, post_id: int) -> Comment:
    comment = db.query(Comment).filter(
        Comment.id == comment_id, Comment.post_id == post_id
    ).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


@router.get("", response_model=List[CommentResponse])
def list_comments(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    _get_post_or_404(db, post_id)
    comments = (
        db.query(Comment)
        .filter(Comment.post_id == post_id)
        .order_by(Comment.created_at.asc())
        .all()
    )
    current_user_id = current_user.id if current_user else None
    result = []
    for c in comments:
        data = CommentResponse.model_validate(c)
        data.is_mine = (c.user_id == current_user_id)
        result.append(data)
    return result


@router.post("", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def add_comment(
    post_id: int,
    data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_post_or_404(db, post_id)
    if not data.content.strip():
        raise HTTPException(status_code=400, detail="Comment cannot be empty")

    # Validate content for profanity
    is_valid, error_msg = validate_content(data.content, "comment")
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    comment = Comment(content=data.content, user_id=current_user.id, post_id=post_id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    response = CommentResponse.model_validate(comment)
    response.is_mine = True
    return response


@router.put("/{comment_id}", response_model=CommentResponse)
def edit_comment(
    post_id: int,
    comment_id: int,
    data: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = _get_comment_or_404(db, comment_id, post_id)
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You don't own this comment")

    # Validate content for profanity
    is_valid, error_msg = validate_content(data.content, "comment")
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    comment.content = data.content
    db.commit()
    db.refresh(comment)
    response = CommentResponse.model_validate(comment)
    response.is_mine = True
    return response


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    post_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = _get_comment_or_404(db, comment_id, post_id)
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You don't own this comment")
    db.delete(comment)
    db.commit()
