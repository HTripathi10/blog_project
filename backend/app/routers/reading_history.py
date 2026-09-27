"""
routers/reading_history.py — Reading history endpoints

Routes:
  GET    /api/reading-history/me     → Get current user's reading history
  GET    /api/reading-history/me/stats → Get reading statistics
  POST   /api/reading-history        → Record a post read
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.repositories import reading_history_repository

router = APIRouter(prefix="/api/reading-history", tags=["Reading History"])


@router.get("/me")
def get_my_reading_history(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current user's reading history."""
    records, total = reading_history_repository.get_user_reading_history(
        db, current_user.id, limit, offset
    )
    return {
        "items": records,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/me/stats")
def get_my_reading_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current user's reading statistics."""
    stats = reading_history_repository.get_reading_stats(db, current_user.id)
    return stats


@router.post("")
def record_reading(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Record that the current user has read a post."""
    record = reading_history_repository.add_reading_record(db, current_user.id, post_id)
    return {"success": True, "recorded_at": record.created_at}
