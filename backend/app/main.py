"""
main.py — FastAPI application entry point

💡 CONCEPT: Application Factory Pattern
   We create the app in a function (or at module level) and register:
   - Routers: groups of related endpoints
   - Middleware: CORS headers so the React frontend can call the API
   - Static files: serves uploaded images
   - Event handlers: runs code on startup/shutdown

💡 CONCEPT: CORS (Cross-Origin Resource Sharing)
   Browsers block JavaScript from calling APIs on different origins (different domain/port).
   Our React app runs on localhost:5173, our API on localhost:8000 — different ports = different origins.
   The CORSMiddleware adds headers to API responses that tell the browser "this origin is allowed".
   Never use allow_origins=["*"] in production — always whitelist specific origins.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, text
import os

from app.config import get_settings
from app.database import engine
from app import models  # Imports all models so Base.metadata knows about them
from app.routers import auth, posts, comments, likes, users, reading_history

settings = get_settings()

# ── Create tables (dev convenience — use Alembic in production) ───────────────
models.Base.metadata.create_all(bind=engine)


def _ensure_cover_image_column():
    """Add cover_image_url to existing databases created before the column existed."""
    inspector = inspect(engine)
    if not inspector.has_table("posts"):
        return
    columns = {col["name"] for col in inspector.get_columns("posts")}
    if "cover_image_url" in columns:
        return
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE posts ADD COLUMN cover_image_url VARCHAR(500)"))


_ensure_cover_image_column()

# ── Create upload directory ────────────────────────────────────────────────────
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(os.path.join(settings.upload_dir, "avatars"), exist_ok=True)
os.makedirs(os.path.join(settings.upload_dir, "covers"), exist_ok=True)

# ── FastAPI app ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="BlogAPI",
    description="Production-grade blog platform — AI Bootcamp Week 1",
    version="1.0.0",
    docs_url="/api/docs",       # Swagger UI at /api/docs
    redoc_url="/api/redoc",     # ReDoc at /api/redoc
)

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static files (uploaded avatars/images) ─────────────────────────────────────
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

# ── Register routers ───────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(likes.router)
app.include_router(users.router)
app.include_router(reading_history.router)


# ── Health check ───────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health_check():
    """
    Simple health check endpoint.
    Used by Docker, load balancers, and monitoring tools to verify the app is alive.
    """
    return {"status": "ok", "service": "BlogAPI"}


@app.get("/", tags=["Health"])
def root():
    return {"message": "BlogAPI is running. Visit /api/docs for Swagger UI."}
