# Docker Setup for Perspective

## Prerequisites
- Docker installed on your machine
- Docker Compose installed

## Quick Start

1. Clone the repository and navigate to the project root

2. Start all services:
```bash
docker-compose up --build
```

This will:
- Build and start PostgreSQL database
- Build and start the FastAPI backend
- Build and start the React frontend with Nginx

3. Access the application:
- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs

## Environment Variables

Update the environment variables in `docker-compose.yml` before running in production:

- `JWT_SECRET`: Generate a strong secret using: `python -c "import secrets; print(secrets.token_hex(32))"`
- `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`: Get from Google OAuth2 console
- `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET`: Get from GitHub OAuth settings

## Useful Commands

### Start services
```bash
docker-compose up
```

### Start services in detached mode
```bash
docker-compose up -d
```

### Stop services
```bash
docker-compose down
```

### Stop services and remove volumes
```bash
docker-compose down -v
```

### View logs
```bash
docker-compose logs -f
```

### View logs for specific service
```bash
docker-compose logs -f backend
```

### Rebuild a specific service
```bash
docker-compose up -d --build backend
```

## Development Mode

For development with hot-reload:
- The backend is configured with `--reload` flag in docker-compose.yml
- Changes to backend code will automatically restart the container
- Frontend changes require rebuilding the container

## Database

The PostgreSQL data is persisted in a Docker volume named `postgres_data`.

To run database migrations:
```bash
docker-compose exec backend alembic upgrade head
```

To create a new migration:
```bash
docker-compose exec backend alembic revision --autogenerate -m "description"
```

## Troubleshooting

### Port conflicts
If ports 80, 8000, or 5432 are already in use, modify the port mappings in `docker-compose.yml`.

### Database connection issues
Ensure the database service is healthy before the backend starts. The healthcheck is configured to wait for PostgreSQL to be ready.

### Permission issues with uploads
The uploads directory is mounted as a volume. Ensure proper permissions are set on the host machine.
