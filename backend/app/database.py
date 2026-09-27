"""
database.py — SQLAlchemy database connection & session management

💡 CONCEPT: ORM (Object-Relational Mapper)
   Instead of writing raw SQL like:
       SELECT * FROM posts WHERE user_id = 1;
   We write Python:
       db.query(Post).filter(Post.user_id == 1).all()

   SQLAlchemy is our ORM. It translates Python objects ↔ database rows.

💡 CONCEPT: Session / Connection Pooling
   A "session" is a unit of work with the database — like a transaction.
   We use a dependency (get_db) to open a session per request and
   automatically close it when the request is done. This prevents
   connection leaks in production.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

settings = get_settings()

# The engine is the actual connection to PostgreSQL
engine = create_engine(settings.database_url)

# SessionLocal is a factory — every call creates a new session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the parent class all our models will inherit from
Base = declarative_base()


def get_db():
    """
    FastAPI dependency — yields a DB session and guarantees cleanup.

    Usage in a route:
        @router.get("/posts")
        def get_posts(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
