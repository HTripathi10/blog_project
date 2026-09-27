"""
schemas/comment.py — Pydantic schemas for Comment
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.schemas.user import UserPublic


class CommentCreate(BaseModel):
    content: str


class CommentUpdate(BaseModel):
    content: str


class CommentResponse(BaseModel):
    id: int
    content: str
    post_id: int
    author: UserPublic
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_mine: bool = False  # True when the requesting user authored this comment

    model_config = {"from_attributes": True}
