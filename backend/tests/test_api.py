import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

# In-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register_login_and_full_crud_flow(client):
    # 1. Register
    reg_res = client.post(
        "/api/auth/register",
        json={
            "name": "Alex Dev",
            "email": "alex@example.com",
            "password": "secretpassword123",
        },
    )
    assert reg_res.status_code == 201
    reg_data = reg_res.json()
    assert "access_token" in reg_data
    assert reg_data["user"]["email"] == "alex@example.com"
    token = reg_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Login
    login_res = client.post(
        "/api/auth/login",
        json={
            "email": "alex@example.com",
            "password": "secretpassword123",
        },
    )
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()

    # 3. Create post (published)
    post_res = client.post(
        "/api/posts",
        headers=headers,
        json={
            "title": "Introduction to Fast Modern Web Apps",
            "content": "Here is the full markdown content of the blog post.",
            "status": "published",
            "tags": ["python", "fastapi", "react"],
        },
    )
    assert post_res.status_code == 201
    post_data = post_res.json()
    assert post_data["title"] == "Introduction to Fast Modern Web Apps"
    post_id = post_data["id"]

    # 4. Get post by ID
    get_res = client.get(f"/api/posts/{post_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == post_id

    # 5. List published posts
    list_res = client.get("/api/posts")
    assert list_res.status_code == 200
    assert list_res.json()["total"] == 1
    assert len(list_res.json()["items"]) == 1

    # 6. Add comment
    comment_res = client.post(
        f"/api/posts/{post_id}/comments",
        headers=headers,
        json={"content": "Awesome article! Very helpful."},
    )
    assert comment_res.status_code == 201
    assert comment_res.json()["content"] == "Awesome article! Very helpful."

    # 7. List comments
    comments_list = client.get(f"/api/posts/{post_id}/comments")
    assert comments_list.status_code == 200
    assert len(comments_list.json()) == 1

    # 8. Toggle Like
    like_res = client.post(f"/api/posts/{post_id}/like", headers=headers)
    assert like_res.status_code == 200
    assert like_res.json()["liked"] is True
    assert like_res.json()["like_count"] == 1

    # 9. Toggle Like off (unlike)
    unlike_res = client.post(f"/api/posts/{post_id}/like", headers=headers)
    assert unlike_res.status_code == 200
    assert unlike_res.json()["liked"] is False
    assert unlike_res.json()["like_count"] == 0
