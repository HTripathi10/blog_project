"""
models/__init__.py — Imports all models so Alembic can discover them

💡 CONCEPT: Why import here?
   Alembic scans Base.metadata to generate migrations.
   If a model file is never imported, its table won't be in Base.metadata,
   and Alembic will think the table doesn't exist → migration will be wrong.
   This file guarantees all models are loaded before Alembic inspects.
"""

from app.database import Base          # noqa: F401
from app.models.user import User       # noqa: F401
from app.models.post import Post, Tag  # noqa: F401
from app.models.comment import Comment, Like  # noqa: F401
from app.models.reading_history import ReadingHistory  # noqa: F401

