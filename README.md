# Perspective

Perspective is a full-stack blogging platform for discovering articles, publishing posts, and tracking what you read. Readers can browse and search posts, while signed-in users can create articles, join discussions, like posts, manage a profile, and view reading history.

## Features

- Browse published posts, search by title/content/author, filter by tag, and paginate results.
- Create and edit rich-text articles with Tiptap formatting, inline images, tags, and a cover image.
- Save articles as drafts or publish them. Authors can edit or delete their own posts.
- Like posts and add or delete comments when signed in.
- Register and sign in with email/password or Google OAuth.
- View public profiles and edit your own name, bio, and avatar.
- Upload or remove an avatar; upload or remove post cover images.
- Track signed-in reads of other authors' posts and view reading statistics and popular topics.
- Switch between light and dark themes; the selected theme is saved in the browser.
- Reject post and comment text containing profanity using the `better-profanity` Python library.

## Tech stack

| Area | Technology |
|---|---|
| Frontend | React 19, Vite, React Router |
| Data and forms | TanStack Query, Axios, React Hook Form |
| Rich text | Tiptap |
| Backend API | Python 3.12, FastAPI, Pydantic |
| Database | PostgreSQL 15, SQLAlchemy, Alembic |
| Authentication | bcrypt password hashing, JWT, Google OAuth |
| Containers and web serving | Docker Compose, Nginx |

## Run with Docker Compose

### Prerequisites

- Docker Desktop or Docker Engine with the Compose plugin
- A Google OAuth client if you want Google sign-in (email/password login works without it)

### 1. Configure environment variables

Copy the example environment file:

```bash
cp .env.example .env
```

Set `JWT_SECRET` to a long, random value. To enable Google sign-in, set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` to credentials from your Google OAuth configuration. For local Compose use, the redirect URI should be:

```text
http://localhost:8000/api/auth/google/callback
```

Keep `.env` private; do not commit secrets or production credentials.

### 2. Build and start the services

```bash
docker compose up --build
```

Then open:

- App: [http://localhost](http://localhost)
- API: [http://localhost:8000](http://localhost:8000)
- Interactive API docs: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)

Stop the services with `Ctrl+C`, or run `docker compose down` in another terminal. To also delete the database volume and its data, run `docker compose down -v`.

## Services and persistence

Docker Compose starts three services:

- **`frontend`** builds the React app and serves its static files with Nginx on port 80. Nginx forwards `/api` and `/uploads` requests to the backend.
- **`backend`** runs FastAPI/Uvicorn on port 8000 and waits for PostgreSQL to become healthy.
- **`db`** runs PostgreSQL on port 5432. Database files live in the named `postgres_data` volume.

Uploaded avatars and cover images are saved as files under `backend/uploads/`. The Compose bind mount keeps those files on the host between container rebuilds. The database stores the image URLs. Images inserted into article bodies are embedded in the article content as base64 data URLs instead of being saved in the uploads directory.

## Local development without Docker

You will need Python 3.12, Node.js, and a running PostgreSQL instance. The backend needs these environment variables (see `.env.example`): `DATABASE_URL`, `JWT_SECRET`, and optionally the Google OAuth settings.

Start the backend from the `backend` directory:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

In another terminal, install and start the frontend:

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173). Vite proxies API and upload requests to `http://localhost:8000` during development.

## How a few features work

- **Authentication:** the backend hashes local passwords with bcrypt. Successful login or registration returns a signed JWT. The frontend stores it in local storage and sends it as a Bearer token on API requests. Google OAuth returns a Perspective JWT after Google verifies the user.
- **Image uploads:** avatar and cover image files are checked for allowed image types and the configured size limit, stored under `backend/uploads/`, and served from `/uploads`. Their URLs are saved in PostgreSQL. Article body images are embedded into the saved Tiptap content.
- **Reading history:** opening another user's post while signed in creates a reading-history record. The signed-in author's own views are excluded. Repeated reads can create multiple records.
- **Profanity check:** the backend checks post titles/content and comment text using `better-profanity`. Flagged submissions are rejected with an error; the app does not automatically rewrite them.
- **Theme:** light/dark mode is controlled in the frontend and persisted in browser local storage.

## Project layout

```text
.
├── backend/
│   ├── app/
│   │   ├── middleware/  # JWT authentication dependencies
│   │   ├── models/      # SQLAlchemy database models
│   │   ├── repositories/# Database queries
│   │   ├── routers/     # FastAPI endpoints
│   │   ├── schemas/     # Pydantic request/response models
│   │   └── utils/       # JWT, password, reading-time, content-filter helpers
│   ├── alembic/         # Database migration configuration and revisions
│   └── uploads/         # Local avatar and cover image storage
├── frontend/
│   ├── src/
│   │   ├── api/         # Axios API wrappers
│   │   ├── components/  # Shared UI components
│   │   ├── context/     # Authentication and theme state
│   │   └── pages/       # Route-level screens
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
└── .env.example
```

## Useful commands

```bash
# Follow logs
docker compose logs -f

# Follow only backend logs
docker compose logs -f backend

# Run backend API tests
docker compose exec backend pytest

# Build frontend locally
cd frontend && npm run build
```

## Notes

- The backend creates database tables at startup for this project setup. Alembic configuration and revisions are also present for schema changes.
- Google sign-in requires valid OAuth credentials and a matching redirect URI. GitHub OAuth is not currently implemented.
- This Compose configuration is intended for local development. Use managed secrets, secure production settings, and production-ready hosting/storage before deploying publicly.
