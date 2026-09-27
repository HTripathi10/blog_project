"""
schemas/post.py — Pydantic schemas for Post, Tag, and paginated responses

💡 CONCEPT: Nested schemas
   PostDetail includes the author (UserPublic), tags, and comment count.
   This is one response object — no extra API calls needed from the frontend.
   This is called "eager loading" and we'll implement it in the repository layer.

💡 CONCEPT: Pagination schema
   Every list endpoint returns { items, total, page, limit, pages }.
   This is a standard REST pagination pattern. The frontend uses
   total + pages to render the page numbers.
"""

from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, List
from app.schemas.user import UserPublic


# ── Tag schemas ───────────────────────────────────────────────────────────────

class TagBase(BaseModel):
    name: str

class TagResponse(TagBase):
    id: int
    model_config = {"from_attributes": True}


# ── Post request schemas ──────────────────────────────────────────────────────

class PostCreate(BaseModel):
    title: str
    content: str
    cover_image_url: Optional[str] = None
    status: str = "draft"        # defaults to draft — user must explicitly publish
    tags: List[str] = []         # list of tag names (we create tags if they don't exist)

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v, info):
        # Allow empty title for drafts
        if info.data.get('status') == 'draft':
            return v
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()

    @field_validator("status")
    @classmethod
    def valid_status(cls, v):
        if v not in ("draft", "published"):
            raise ValueError("Status must be 'draft' or 'published'")
        return v

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v, info):
        # Allow empty content for drafts
        if info.data.get('status') == 'draft':
            return v
        if not v.strip():
            raise ValueError("Content cannot be empty")
        return v


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    cover_image_url: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None

    @field_validator("title")
    @classmethod
    def title_not_empty_if_provided(cls, v, info):
        # Allow empty title for drafts
        status = info.data.get('status')
        if status == 'draft':
            return v
        if v is not None and not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip() if v else v

    @field_validator("content")
    @classmethod
    def content_not_empty_if_provided(cls, v, info):
        # Allow empty content for drafts
        status = info.data.get('status')
        if status == 'draft':
            return v
        if v is not None and not v.strip():
            raise ValueError("Content cannot be empty")
        return v


# ── Post response schemas ─────────────────────────────────────────────────────

class PostSummary(BaseModel):
    """Lightweight — used in listing pages. No full content."""
    id: int
    title: str
    content: str          # frontend truncates this to a preview
    cover_image_url: Optional[str] = None
    status: str
    reading_time_minutes: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    author: UserPublic
    tags: List[TagResponse] = []
    like_count: int = 0
    comment_count: int = 0
    is_liked_by_me: bool = False  # Only meaningful when authenticated

    model_config = {"from_attributes": True}


class PostDetail(PostSummary):
    """Full post — used on the single post page."""
    pass  # Same fields for now; extend if needed (e.g., add related posts)


# ── Pagination wrapper ────────────────────────────────────────────────────────

class PaginatedPosts(BaseModel):
    items: List[PostSummary]
    total: int
    page: int
    limit: int
    pages: int              # ceil(total / limit)
