"""
repositories/user_repository.py — All database queries for Users
"""

from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def create_local_user(db: Session, email: str, name: str, hashed_password: str) -> User:
    user = User(email=email, name=name, hashed_password=hashed_password, provider="local")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_oauth_user(
    db: Session, email: str, name: str, avatar_url: Optional[str], provider: str
) -> User:
    user = User(email=email, name=name, avatar_url=avatar_url, provider=provider)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user_profile(
    db: Session,
    user: User,
    name: Optional[str] = None,
    bio: Optional[str] = None,
    avatar_url: Optional[str] = None,
) -> User:
    if name is not None:
        user.name = name
    if bio is not None:
        user.bio = bio
    if avatar_url is not None:
        user.avatar_url = avatar_url
    db.commit()
    db.refresh(user)
    return user
