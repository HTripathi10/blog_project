"""
repositories/reading_history_repository.py — Reading history data access layer
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from app.models.reading_history import ReadingHistory
from app.models.post import Post


def add_reading_record(db: Session, user_id: int, post_id: int) -> ReadingHistory:
    """Add a new reading record for a user and post (allows multiple reads)."""
    # Always create a new record to count multiple reads of the same article
    record = ReadingHistory(user_id=user_id, post_id=post_id)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_user_reading_history(
    db: Session,
    user_id: int,
    limit: int = 50,
    offset: int = 0
) -> tuple[List[dict], int]:
    """Get user's reading history with post details."""
    query = (
        db.query(ReadingHistory, Post)
        .join(Post, ReadingHistory.post_id == Post.id)
        .filter(ReadingHistory.user_id == user_id)
        .order_by(desc(ReadingHistory.created_at))
    )
    
    total = query.count()
    records = query.offset(offset).limit(limit).all()
    
    results = []
    for history, post in records:
        results.append({
            "id": history.id,
            "post_id": post.id,
            "post_title": post.title,
            "post_content": post.content,
            "cover_image_url": post.cover_image_url,
            "post_status": post.status,
            "post_created_at": post.created_at,
            "read_at": history.created_at,
            "author": post.author,
            "tags": post.tags,
        })
    
    return results, total


def get_reading_stats(db: Session, user_id: int) -> dict:
    """Get reading statistics for a user."""
    total_reads = db.query(ReadingHistory).filter(
        ReadingHistory.user_id == user_id
    ).count()
    
    # Get unique posts read
    unique_posts = db.query(ReadingHistory.post_id).filter(
        ReadingHistory.user_id == user_id
    ).distinct().count()
    
    # Get most read tags (join with post_tags)
    from app.models.post import post_tags, Tag
    
    tag_counts = (
        db.query(Tag.name, func.count(ReadingHistory.id).label('count'))
        .join(Post, ReadingHistory.post_id == Post.id)
        .join(post_tags, Post.id == post_tags.c.post_id)
        .join(Tag, post_tags.c.tag_id == Tag.id)
        .filter(ReadingHistory.user_id == user_id)
        .group_by(Tag.name)
        .order_by(desc('count'))
        .limit(10)
        .all()
    )
    
    return {
        "total_reads": total_reads,
        "unique_posts": unique_posts,
        "top_tags": [{"name": tag, "count": count} for tag, count in tag_counts],
    }
