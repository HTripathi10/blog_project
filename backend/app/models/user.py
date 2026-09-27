"""
models/user.py — User database model

💡 CONCEPT: SQLAlchemy Model
   A model is a Python class that maps to a database table.
   Each class attribute = a column. SQLAlchemy handles CREATE TABLE,
   INSERT, SELECT, etc. for us.

💡 CONCEPT: provider field
   Supports both local (email/password) and OAuth users in one table.
   If provider='local', we use hashed_password.
   If provider='google'/'github', password is NULL — they auth via OAuth.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)

    # Auth provider: 'local' | 'google' | 'github'
    provider = Column(String(50), default="local", nullable=False)
    # Only set for local accounts
    hashed_password = Column(String(255), nullable=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships — SQLAlchemy will auto-join these
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")
    reading_history = relationship("ReadingHistory", back_populates="user", cascade="all, delete-orphan")
