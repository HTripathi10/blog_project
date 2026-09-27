"""
models/post.py — Post, Tag, and PostTag (join table) models

💡 CONCEPT: Many-to-Many Relationships
   A post can have many tags. A tag can belong to many posts.
   This needs a join table (post_tags) with two foreign keys.
   SQLAlchemy's `secondary` parameter handles this automatically.

💡 CONCEPT: Enum via String Column
   We use a String('draft'/'published') instead of a DB ENUM for portability.
   A CHECK constraint enforces the allowed values at the DB level.
"""

from sqlalchemy import (
    Column, Integer, String, Text, DateTime,
    ForeignKey, Table, CheckConstraint, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

# ── Join table for Post ↔ Tag many-to-many ──────────────────────────────────
post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Post(Base):
    __tablename__ = "posts"
    __table_args__ = (
        CheckConstraint("status IN ('draft', 'published')", name="ck_post_status"),
        # Composite index: when we filter published posts by user, this speeds it up
        Index("ix_posts_user_status", "user_id", "status"),
    )

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False, index=True)
    content = Column(Text, nullable=False)
    cover_image_url = Column(String(500), nullable=True)
    status = Column(String(20), default="draft", nullable=False)  # 'draft' | 'published'
    reading_time_minutes = Column(Integer, default=1)

    # Foreign key — links back to users table
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    author = relationship("User", back_populates="posts")
    tags = relationship("Tag", secondary=post_tags, back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)

    posts = relationship("Post", secondary=post_tags, back_populates="tags")
