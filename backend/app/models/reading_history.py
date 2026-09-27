"""
models/reading_history.py — Reading history model

💡 CONCEPT: Reading History
   Tracks when a user reads a post. This builds a "reading fingerprint"
   showing which posts they've read, when, and which topics they explore.
"""

from sqlalchemy import Column, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class ReadingHistory(Base):
    __tablename__ = "reading_history"
    __table_args__ = (
        # Composite index: user_id + created_at for efficient queries
        Index("ix_reading_history_user_created", "user_id", "created_at"),
        # Index for querying by user and post
        Index("ix_reading_history_user_post", "user_id", "post_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    user = relationship("User", back_populates="reading_history")
    post = relationship("Post")
