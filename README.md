# DevPulse Backend

The DevPulse backend is a RESTful API service built with FastAPI. It handles authentication, project and task management, automated session timing, and integrates with external services (like GitHub) to generate accurate progress metrics.

This repository contains the server-side code, built with a focus on type safety, clear data modeling, and reliable data persistence.

## Tech Stack

The backend utilizes the following core technologies:

- **Framework**: FastAPI
- **Language**: Python 3.14+
- **Package Manager**: uv
- **ORM**: SQLModel (built on SQLAlchemy and Pydantic)
- **Database**: PostgreSQL (`psycopg2-binary`)
- **Migrations**: Alembic
- **Authentication**: JWT (`PyJWT`), Password Hashing (`passlib[bcrypt]`)
- **HTTP Client**: HTTPX (for asynchronous external API requests)
- **Email Service**: FastAPI-Mail

## Architecture & Directory Structure

The codebase follows a modular, single-responsibility pattern to ensure maintainability and separation of concerns.

```text
backend/
├── alembic.ini            # Alembic configuration for database migrations
├── pyproject.toml         # Project dependencies and configurations managed by uv
├── aggregator.py          # Service module for handling external API requests (e.g., GitHub)
├── database.py            # Database engine configuration and session dependency injection
├── email_service.py       # Handles transactional email communications (e.g., password resets)
├── main.py                # FastAPI application entry point and route definitions
├── models.py              # SQLModel schema definitions (User, Project, Task, DailyLog)
├── security.py            # JWT token generation, validation, and password hashing logic
├── seed.py                # Utility script for injecting mock data during local development
└── migrations/            # Alembic migration scripts reflecting schema changes over time
```

## Core Workflow & Data Flow

DevPulse connects local developer productivity with remote version control. The architectural flow operates as follows:

1. **Project Initialization**: When a user creates a project via the frontend, the backend validates the repository URL and instantly dispatches a background task (`aggregator.py`) to fetch baseline telemetry (e.g., total stars, open issues) without blocking the HTTP response.
2. **Session Tracking**: Users start a task timer on the frontend. The backend records a precision UTC timestamp. When the timer is stopped, the backend calculates the exact duration delta.
3. **Real-Time Webhook Pipeline**: While the session runs, the user writes code locally and pushes it to a remote GitHub repository. GitHub triggers a push event to the backend's `POST /webhooks/github` endpoint.
4. **Data Ingestion & Extraction**: The backend validates the webhook's HMAC SHA-256 signature, extracts the latest commit message, and dynamically polls the GitHub API for exact line addition counts for each commit in the payload. It then updates the project state and persists the added lines to the `DailyProjectMetric` table.
5. **Log Generation**: When the user concludes their session on the frontend, the client immediately requests the current state of the `DailyProjectMetric` table. The backend returns the pre-calculated metrics, allowing the frontend to generate a comprehensive Daily Log without manual data entry.

## Key Features & Implementations

1. **Robust Authentication**: Implements OAuth2 with Password (and hashing) for secure JWT-based stateless authentication (`security.py`).
2. **Database Modeling**: Strict schema definition and validation using SQLModel, tracking relations between Users, Projects, Tasks, and Logs (`models.py`).
3. **Session Time Tracking**: Endpoints to start and stop task timers, computing exact durations (deltas) accurately via UTC timestamps.
4. **GitHub Webhook Integration (Real-Time)**: Instead of slow API polling, the backend exposes a secure `POST /webhooks/github` endpoint. When a user pushes code to GitHub, GitHub instantly sends a webhook payload. The backend uses HMAC SHA-256 signature validation to ensure security, dynamically calculates the lines of code added, and persists this metric in a `DailyProjectMetric` table for instant frontend retrieval.
5. **Database Migrations**: Utilizes Alembic to safely handle schema evolution and database state transitions.
6. **Mock Data Seeding**: Provides a `seed.py` script to rapidly populate a local PostgreSQL instance with test data for streamlined frontend UI development.

## Local Development

To run the backend locally, ensure you have Python 3.14+ and `uv` installed. You will also need a running instance of PostgreSQL.

1. **Install Dependencies via UV**
   ```bash
   uv sync
   ```

2. **Environment Configuration**
   Copy the example environment file and configure your database credentials.
   ```bash
   cp .env.example .env
   ```

3. **Run Database Migrations**
   Ensure your database is up to date with the latest schema definitions.
   ```bash
   alembic upgrade head
   ```

4. **(Optional) Seed the Database**
   Inject dummy data to test the UI quickly.
   ```bash
   uv run seed.py
   ```

5. **Start the Development Server**
   Start the FastAPI server using Uvicorn.
   ```bash
   uv run uvicorn main:app --reload --port 8000
   ```

## Development Notes

- **Dependency Management**: This project strictly uses `uv` for package management. Add new dependencies via `uv add <package>` to keep the `pyproject.toml` and lockfile synchronized.
- **Async Operations**: Any function calling external services (like the GitHub API via `httpx`) must be defined as `async def` to prevent blocking the main thread. Database operations currently utilize standard synchronous SQLModel sessions.
- **Migrations**: If you make modifications to `models.py`, you must generate a new migration script using `alembic revision --autogenerate -m "description"` before applying it.
