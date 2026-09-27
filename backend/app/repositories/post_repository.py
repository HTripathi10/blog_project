"""
repositories/post_repository.py — All database queries for Posts

💡 CONCEPT: Repository Pattern
   All SQL/ORM queries live here. Routes and services NEVER query the DB directly.
   Benefits:
   - Easy to swap DB (e.g., MongoDB) without touching business logic
   - Easy to test (mock the repository)
   - Single place to add caching, logging, or query optimisation

💡 CONCEPT: Avoiding N+1 Queries
   N+1 problem: fetching 10 posts and then running 10 more queries for author,
   10 for tags, 10 for likes = 31 queries for one page!

   Solution: joinedload / subqueryload — SQLAlchemy fetches related data
   in 1–2 extra queries instead of N queries.
"""

import math
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_

from app.models.post import Post, Tag
from app.models.comment import Comment, Like
from app.models.user import User
from app.schemas.post import PostCreate, PostUpdate
from app.utils.reading_time import calculate_reading_time


def get_post_by_id(db: Session, post_id: int) -> Optional[Post]:
    return (
        db.query(Post)
        .options(
            joinedload(Post.author),                # author in same query (JOIN)
            joinedload(Post.tags),                  # tags via join table
            joinedload(Post.comments).joinedload(Comment.author),  # comments + their authors
        )
        .filter(Post.id == post_id)
        .first()
    )


def get_published_posts(
    db: Session,
    page: int = 1,
    limit: int = 10,
    search: Optional[str] = None,
    tag: Optional[str] = None,
    author_id: Optional[int] = None,
) -> Tuple[List[Post], int]:
    """
    Returns (posts, total_count) for published posts.
    Supports search (title/content), tag filter, and author filter.
    """
    query = (
        db.query(Post)
        .options(joinedload(Post.author), joinedload(Post.tags))
        .filter(Post.status == "published")
    )

    # ── Search: case-insensitive match on title OR content OR author name ─────────
    if search:
        query = query.filter(
            or_(
                Post.title.ilike(f"%{search}%"),
                Post.content.ilike(f"%{search}%"),
                Post.author.has(User.name.ilike(f"%{search}%")),
            )
        )

    # ── Tag filter ────────────────────────────────────────────────────────────
    if tag:
        query = query.join(Post.tags).filter(Tag.name == tag)

    # ── Author filter (for profile page) ─────────────────────────────────────
    if author_id:
        query = query.filter(Post.user_id == author_id)

    total = query.count()
    posts = query.order_by(Post.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    return posts, total


def get_user_posts(
    db: Session, user_id: int, include_drafts: bool = False
) -> List[Post]:
    """Get all posts by a user. include_drafts=True for the author's own dashboard."""
    query = db.query(Post).options(joinedload(Post.tags)).filter(Post.user_id == user_id)
    if not include_drafts:
        query = query.filter(Post.status == "published")
    return query.order_by(Post.created_at.desc()).all()


def create_post(db: Session, data: PostCreate, user_id: int) -> Post:
    reading_time = calculate_reading_time(data.content)

    post = Post(
        title=data.title,
        content=data.content,
        cover_image_url=data.cover_image_url or None,
        status=data.status,
        user_id=user_id,
        reading_time_minutes=reading_time,
    )

    # Handle tags — get existing or create new
    if data.tags:
        post.tags = _get_or_create_tags(db, data.tags)

    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def update_post(db: Session, post: Post, data: PostUpdate) -> Post:
    if data.title is not None:
        post.title = data.title
    if data.content is not None:
        post.content = data.content
        post.reading_time_minutes = calculate_reading_time(data.content)
    # A null cover_image_url is an explicit request to remove the image.
    # Pydantic keeps that distinct from an omitted field in model_fields_set.
    if "cover_image_url" in data.model_fields_set:
        post.cover_image_url = data.cover_image_url or None
    if data.status is not None:
        post.status = data.status
    if data.tags is not None:
        post.tags = _get_or_create_tags(db, data.tags)

    db.commit()
    db.refresh(post)
    return post


def delete_post(db: Session, post: Post) -> None:
    db.delete(post)
    db.commit()


def get_like_count(db: Session, post_id: int) -> int:
    return db.query(func.count(Like.id)).filter(Like.post_id == post_id).scalar() or 0


def is_liked_by_user(db: Session, post_id: int, user_id: int) -> bool:
    return db.query(Like).filter(
        Like.post_id == post_id, Like.user_id == user_id
    ).first() is not None


def _get_or_create_tags(db: Session, tag_names: List[str]) -> List[Tag]:
    """Find existing tags or create them. Returns Tag objects."""
    tags = []
    for name in set(tag_names):  # deduplicate
        name = name.strip().lower()
        if not name:
            continue
        tag = db.query(Tag).filter(Tag.name == name).first()
        if not tag:
            tag = Tag(name=name)
            db.add(tag)
            db.flush()  # Get the ID without committing the transaction
        tags.append(tag)
    return tags
