import asyncio
# This module is responsible for simulating asynchronous background tasks that fetch and update project repository statistics from third-party APIs (like GitHub). It uses SQLModel for database interactions and asyncio for non-blocking operations.
import random

from sqlmodel import Session, create_engine

from database import DATABASE_URL
from models import Project

# Create an isolated connection engine for the background worker thread
bg_engine = create_engine(DATABASE_URL)


async def fetch_mock_repository_stats(project_id: int):
    """Simulates an asynchronous network request to third-party APIs (like GitHub)."""
    print(
        f"\n[BACKGROUND WORKER] 📡 Initiating network sync for Project ID: {project_id}..."
    )

    # 1. Simulate external network API delay latency (3 seconds) without blocking the main loop
    await asyncio.sleep(3)

    # 2. Generate randomized mock repository tracking telemetry data pools
    mock_stars = random.randint(12, 145)
    mock_issues = random.randint(0, 14)
    mock_commits = [
        "feat: secure access interceptor integration complete",
        "fix: localized cryptographic byte boundary truncation layout",
        "docs: complete phase documentation requirements updates",
        "refactor: clean domain query mapping schemas structure",
    ]
    selected_commit = random.choice(mock_commits)

    # 3. Open a dedicated database transaction session scope to save the metrics
    with Session(bg_engine) as session:
        project = session.get(Project, project_id)
        if project:
            # Update the cached metrics values
            project.stars_count = mock_stars
            project.open_issues_count = mock_issues
            project.last_commit_message = selected_commit

            session.add(project)
            session.commit()
            print(
                f"[BACKGROUND WORKER] ✅ Sync complete. Project {project_id} metrics updated successfully.\n"
            )
